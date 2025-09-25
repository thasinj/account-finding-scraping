// Background job pattern - processes discoveries in chunks
export const config = {
  runtime: 'edge',
};

import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ message: 'Method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const body = await req.json();
    const { run_id, chunk_index = 0, chunk_size = 10 } = body;
    
    if (!run_id) {
      return new Response(JSON.stringify({ message: 'Missing run_id' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    console.log(`🔄 Processing chunk ${chunk_index} for run: ${run_id}`);
    
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

    // Update progress
    await supabase
      .from('runs')
      .update({ 
        status: 'running',
        current_layer: chunk_index,
        updated_at: new Date().toISOString()
      })
      .eq('id', run_id);

    const { input, params } = run;
    const { minFollowers = 5000, similarCount = 50 } = params || {};
    
    // If this is the first chunk, get similar accounts
    let similarAccounts = [];
    
    if (chunk_index === 0) {
      console.log(`📊 Getting similar accounts for: ${input}`);
      
      const apiKey = process.env.INSTAGRAM_API_KEY;
      const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
      const similarUrl = `${baseUrl}/get_ig_similar_accounts.php?username_or_url=${encodeURIComponent(input)}`;
      
      const response = await fetch(similarUrl, {
        headers: {
          'X-RapidAPI-Key': apiKey,
          'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
        }
      });
      
      similarAccounts = await response.json();
      
      // Store the similar accounts for future chunks
      await supabase
        .from('runs')
        .update({ 
          stats: { 
            ...run.stats,
            similarAccounts: similarAccounts.slice(0, similarCount),
            totalChunks: Math.ceil(Math.min(similarAccounts.length, similarCount) / chunk_size)
          }
        })
        .eq('id', run_id);
        
    } else {
      // Get similar accounts from previous chunk processing
      similarAccounts = run.stats?.similarAccounts || [];
    }
    
    if (!Array.isArray(similarAccounts) || similarAccounts.length === 0) {
      // Complete the run - no accounts to process
      await supabase
        .from('runs')
        .update({ 
          status: 'completed',
          completed_at: new Date().toISOString()
        })
        .eq('id', run_id);
        
      return new Response(JSON.stringify({ 
        success: true, 
        completed: true,
        message: 'No similar accounts found'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Process current chunk
    const startIndex = chunk_index * chunk_size;
    const endIndex = Math.min(startIndex + chunk_size, similarAccounts.length);
    const currentChunk = similarAccounts.slice(startIndex, endIndex);
    
    console.log(`📦 Processing chunk ${chunk_index}: accounts ${startIndex}-${endIndex-1} (${currentChunk.length} accounts)`);
    
    // Process profiles in parallel for this chunk
    const apiKey = process.env.INSTAGRAM_API_KEY;
    const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
    const headers = {
      'X-RapidAPI-Key': apiKey,
      'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
    };
    
    const profilePromises = currentChunk.map(async (similar) => {
      if (!similar.username) return null;
      
      try {
        const profileUrl = `${baseUrl}/ig_get_fb_profile_hover.php?username_or_url=${encodeURIComponent(similar.username)}`;
        const response = await fetch(profileUrl, { headers });
        const profileData = await response.json();
        const profile = profileData?.user_data;
        
        if (!profile || !profile.follower_count || profile.follower_count < minFollowers) {
          return null;
        }
        
        return {
          username: profile.username,
          full_name: profile.full_name,
          follower_count: profile.follower_count,
          following_count: profile.following_count,
          media_count: profile.media_count,
          verified: profile.is_verified || false,
          private: profile.is_private || false
        };
      } catch (error) {
        console.error(`Error processing ${similar.username}:`, error);
        return null;
      }
    });
    
    const profiles = (await Promise.allSettled(profilePromises))
      .filter(result => result.status === 'fulfilled' && result.value !== null)
      .map(result => result.value);
    
    // Save profiles to database in parallel
    let chunkInserted = 0;
    
    if (profiles.length > 0) {
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
            
          if (profileError) return null;
          
          // Link to run
          const { error: linkError } = await supabase
            .from('run_profiles')
            .upsert({
              run_id: run_id,
              profile_id: savedProfile.id,
              layer: chunk_index + 1,
              discovery_method: 'similar_accounts',
              found_from: `similar:${input}`
            }, { onConflict: 'run_id,profile_id' });
            
          return linkError ? null : savedProfile;
          
        } catch (error) {
          return null;
        }
      });
      
      const savedResults = (await Promise.allSettled(savePromises))
        .filter(result => result.status === 'fulfilled' && result.value !== null);
      
      chunkInserted = savedResults.length;
    }
    
    // Update run progress
    const currentStats = run.stats || {};
    const totalInserted = (currentStats.totalInserted || 0) + chunkInserted;
    
    await supabase
      .from('runs')
      .update({ 
        stats: {
          ...currentStats,
          totalInserted,
          chunksProcessed: chunk_index + 1,
          lastChunkInserted: chunkInserted
        }
      })
      .eq('id', run_id);
    
    // Check if we're done
    const totalChunks = currentStats.totalChunks || Math.ceil(similarAccounts.length / chunk_size);
    const isComplete = (chunk_index + 1) >= totalChunks || endIndex >= similarAccounts.length;
    
    if (isComplete) {
      // Complete the run
      await supabase
        .from('runs')
        .update({ 
          status: 'completed',
          completed_at: new Date().toISOString(),
          stats: {
            ...currentStats,
            totalInserted,
            chunksProcessed: chunk_index + 1,
            layersCompleted: 1
          }
        })
        .eq('id', run_id);
        
      console.log(`✅ Run completed! Total inserted: ${totalInserted}`);
      
      return new Response(JSON.stringify({ 
        success: true, 
        completed: true,
        totalInserted,
        chunksProcessed: chunk_index + 1
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      // More chunks to process
      console.log(`🔄 Chunk ${chunk_index} complete. ${chunkInserted} profiles saved. Next chunk: ${chunk_index + 1}`);
      
      return new Response(JSON.stringify({ 
        success: true, 
        completed: false,
        chunkInserted,
        totalInserted,
        nextChunk: chunk_index + 1,
        totalChunks
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
  } catch (error) {
    console.error('Chunked execution error:', error);
    
    return new Response(JSON.stringify({ 
      message: 'Chunk processing failed', 
      error: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
