export const config = {
  runtime: 'edge',
};

import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

// Parallel API call helper
async function fetchWithRetry(url, options, retries = 2) {
  for (let i = 0; i <= retries; i++) {
    try {
      const response = await fetch(url, { ...options, signal: AbortSignal.timeout(30000) });
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      if (i === retries) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))); // Exponential backoff
    }
  }
}

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ message: 'Method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const body = await req.json();
    const { run_id } = body;
    
    if (!run_id) {
      return new Response(JSON.stringify({ message: 'Missing run_id' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    console.log(`🚀 Starting optimized execution for run: ${run_id}`);
    
    // Get run details
    const { data: run, error: runError } = await supabase
      .from('runs')
      .select('*')
      .eq('id', run_id)
      .single();
    
    if (runError || !run) {
      return new Response(JSON.stringify({ message: 'Run not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    if (run.status !== 'pending') {
      return new Response(JSON.stringify({ message: 'Run already in progress or completed' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Mark as running
    await supabase
      .from('runs')
      .update({ status: 'running', updated_at: new Date().toISOString() })
      .eq('id', run_id);

    const { input, params } = run;
    const { minFollowers = 5000, similarCount = 10 } = params || {};
    
    console.log(`📊 Processing similar accounts for: ${input} (limit: ${similarCount})`);
    
    // Step 1: Get similar accounts
    const apiKey = process.env.INSTAGRAM_API_KEY;
    const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
    const headers = {
      'X-RapidAPI-Key': apiKey,
      'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    };
    
    const similarUrl = `${baseUrl}/get_ig_similar_accounts.php?username_or_url=${encodeURIComponent(input)}`;
    const similarAccounts = await fetchWithRetry(similarUrl, { headers });
    
    if (!Array.isArray(similarAccounts) || similarAccounts.length === 0) {
      console.log('❌ No similar accounts found');
      await supabase
        .from('runs')
        .update({ 
          status: 'completed',
          completed_at: new Date().toISOString(),
          stats: { totalInserted: 0, message: 'No similar accounts found' }
        })
        .eq('id', run_id);
        
      return new Response(JSON.stringify({ 
        success: true, 
        totalInserted: 0,
        message: 'No similar accounts found'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log(`✅ Found ${similarAccounts.length} similar accounts`);
    
    // Step 2: Parallel profile fetching (limit to avoid overwhelming API)
    const accountsToProcess = similarAccounts.slice(0, Math.min(similarCount, 20));
    
    console.log(`🔄 Fetching ${accountsToProcess.length} profiles in parallel...`);
    
    const profilePromises = accountsToProcess.map(async (similar, index) => {
      if (!similar.username) return null;
      
      try {
        const profileUrl = `${baseUrl}/ig_get_fb_profile_hover.php?username_or_url=${encodeURIComponent(similar.username)}`;
        const profileData = await fetchWithRetry(profileUrl, { headers });
        const profile = profileData?.user_data;
        
        if (!profile || !profile.follower_count || profile.follower_count < minFollowers) {
          console.log(`⏭️  Skipping ${similar.username}: ${profile?.follower_count || 0} followers`);
          return null;
        }
        
        console.log(`✅ ${similar.username}: ${profile.follower_count.toLocaleString()} followers`);
        return {
          username: profile.username,
          full_name: profile.full_name,
          follower_count: profile.follower_count,
          following_count: profile.following_count,
          media_count: profile.media_count,
          verified: profile.is_verified || false,
          private: profile.is_private || false,
          original_username: similar.username
        };
      } catch (error) {
        console.error(`❌ Error fetching ${similar.username}:`, error.message);
        return null;
      }
    });
    
    // Wait for all profile fetches to complete
    const profiles = (await Promise.allSettled(profilePromises))
      .filter(result => result.status === 'fulfilled' && result.value !== null)
      .map(result => result.value);
    
    console.log(`📥 Successfully fetched ${profiles.length} valid profiles`);
    
    if (profiles.length === 0) {
      await supabase
        .from('runs')
        .update({ 
          status: 'completed',
          completed_at: new Date().toISOString(),
          stats: { totalInserted: 0, message: 'No profiles met criteria' }
        })
        .eq('id', run_id);
        
      return new Response(JSON.stringify({ 
        success: true, 
        totalInserted: 0,
        message: 'No profiles met criteria'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Step 3: Parallel database operations
    console.log(`💾 Saving ${profiles.length} profiles to database...`);
    
    const savePromises = profiles.map(async (profile) => {
      try {
        // Save profile
        const { data: savedProfile, error: profileError } = await supabase
          .from('profiles')
          .upsert({
            username: profile.username,
            full_name: profile.full_name || null,
            follower_count: profile.follower_count || 0,
            following_count: profile.following_count || 0,
            media_count: profile.media_count || 0,
            verified: profile.verified || false,
            private: profile.private || false,
            profile_url: `https://instagram.com/${profile.username}`,
            last_seen_at: new Date().toISOString(),
            discovery_vectors: [`similar:${input}`],
            primary_category: input,
            discovery_count: 1
          }, { onConflict: 'username' })
          .select()
          .single();
          
        if (profileError) {
          console.error(`❌ Profile save error for ${profile.username}:`, profileError.message);
          return null;
        }
        
        // Check if link already exists
        const { data: existingLink } = await supabase
          .from('run_profiles')
          .select('id')
          .eq('run_id', run_id)
          .eq('profile_id', savedProfile.id)
          .single();
        
        let linkError = null;
        if (!existingLink) {
          // Link to run
          const { error } = await supabase
            .from('run_profiles')
            .insert({
              run_id: run_id,
              profile_id: savedProfile.id,
              layer: 1,
              discovery_method: 'similar_accounts',
              found_from: `similar:${input}`
            });
          linkError = error;
        }
          
        if (linkError) {
          console.error(`❌ Link error for ${profile.username}:`, linkError.message);
          return null;
        }
        
        console.log(`✅ Saved and linked ${profile.username} (ID: ${savedProfile.id})`);
        return savedProfile;
        
      } catch (error) {
        console.error(`❌ Database error for ${profile.username}:`, error.message);
        return null;
      }
    });
    
    // Wait for all database operations to complete
    const savedResults = (await Promise.allSettled(savePromises))
      .filter(result => result.status === 'fulfilled' && result.value !== null);
    
    const totalInserted = savedResults.length;
    
    console.log(`🎉 Successfully saved ${totalInserted} profiles`);
    
    // Mark as completed
    await supabase
      .from('runs')
      .update({ 
        status: 'completed',
        completed_at: new Date().toISOString(),
        stats: {
          mode: run.type,
          input,
          minFollowers,
          similarCount,
          totalInserted,
          layersCompleted: 1,
          processingTime: Date.now() - new Date(run.created_at).getTime()
        }
      })
      .eq('id', run_id);

    console.log(`✅ Run completed successfully. Inserted ${totalInserted} profiles.`);
    
    return new Response(JSON.stringify({ 
      success: true, 
      totalInserted,
      layersCompleted: 1,
      profilesFound: profiles.length,
      profilesSaved: totalInserted
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('💥 Optimized execution error:', error);
    
    // Mark as failed
    try {
      await supabase
        .from('runs')
        .update({ 
          status: 'failed',
          stats: { error: error.message }
        })
        .eq('id', run_id);
    } catch (updateError) {
      console.error('Failed to update run status:', updateError);
    }
    
    return new Response(JSON.stringify({ 
      message: 'Discovery execution failed', 
      error: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
