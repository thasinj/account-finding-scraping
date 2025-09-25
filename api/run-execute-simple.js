import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { run_id } = req.body;
  if (!run_id) {
    return res.status(400).json({ message: 'Missing run_id' });
  }

  try {
    console.log(`Starting simple execution for run: ${run_id}`);
    
    // Get run details
    const { data: run, error: runError } = await supabase
      .from('runs')
      .select('*')
      .eq('id', run_id)
      .single();
    
    if (runError || !run) {
      return res.status(404).json({ message: 'Run not found' });
    }

    if (run.status !== 'pending') {
      return res.status(400).json({ message: 'Run already in progress or completed' });
    }

    // Mark as running
    await supabase
      .from('runs')
      .update({ status: 'running' })
      .eq('id', run_id);

    const { input, params } = run;
    const { minFollowers = 5000, similarCount = 5 } = params || {};
    
    console.log(`Processing similar accounts for: ${input}`);
    
    // Step 1: Get similar accounts
    const apiKey = process.env.INSTAGRAM_API_KEY;
    const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
    const similarUrl = `${baseUrl}/get_ig_similar_accounts.php?username_or_url=${encodeURIComponent(input)}`;
    
    const similarResponse = await fetch(similarUrl, {
      headers: {
        'X-RapidAPI-Key': apiKey,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
      }
    });
    
    const similarAccounts = await similarResponse.json();
    console.log(`Found ${similarAccounts.length} similar accounts`);
    
    let totalInserted = 0;
    
    // Step 2: Process first 5 similar accounts
    for (let i = 0; i < Math.min(similarAccounts.length, similarCount); i++) {
      const similar = similarAccounts[i];
      if (!similar.username) continue;
      
      console.log(`Processing: ${similar.username}`);
      
      // Get profile details
      const profileUrl = `${baseUrl}/ig_get_fb_profile_hover.php?username_or_url=${encodeURIComponent(similar.username)}`;
      const profileResponse = await fetch(profileUrl, {
        headers: {
          'X-RapidAPI-Key': apiKey,
          'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
        }
      });
      
      const profileData = await profileResponse.json();
      const profile = profileData?.user_data;
      
      if (!profile || !profile.follower_count) {
        console.log(`No valid profile data for ${similar.username}`);
        continue;
      }
      
      console.log(`${similar.username}: ${profile.follower_count} followers`);
      
      if (profile.follower_count < minFollowers) {
        console.log(`Skipping ${similar.username} - below ${minFollowers} threshold`);
        continue;
      }
      
      // Step 3: Save to database
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
            verified: profile.is_verified || false,
            private: profile.is_private || false,
            profile_url: `https://instagram.com/${profile.username}`,
            last_seen_at: new Date().toISOString(),
            discovery_vectors: [`similar:${input}`],
            primary_category: input,
            discovery_count: 1
          }, { onConflict: 'username' })
          .select()
          .single();
          
        if (profileError) {
          console.error(`Profile save error for ${similar.username}:`, profileError);
          continue;
        }
        
        console.log(`Saved profile ${similar.username} with ID ${savedProfile.id}`);
        
        // Link to run
        const { error: linkError } = await supabase
          .from('run_profiles')
          .upsert({
            run_id: run_id,
            profile_id: savedProfile.id,
            layer: 1,
            discovery_method: 'similar_accounts',
            found_from: `similar:${input}`
          }, { onConflict: 'run_id,profile_id' });
          
        if (!linkError) {
          totalInserted++;
          console.log(`Successfully linked ${similar.username} to run. Total: ${totalInserted}`);
        } else {
          console.error(`Link error for ${similar.username}:`, linkError);
        }
        
      } catch (dbError) {
        console.error(`Database error for ${similar.username}:`, dbError);
      }
    }
    
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
          layersCompleted: 1
        }
      })
      .eq('id', run_id);

    console.log(`Run completed successfully. Inserted ${totalInserted} profiles.`);
    
    res.status(200).json({ 
      success: true, 
      totalInserted,
      layersCompleted: 1
    });

  } catch (error) {
    console.error('Simple execution error:', error);
    
    // Mark as failed
    await supabase
      .from('runs')
      .update({ 
        status: 'failed',
        stats: { error: error.message }
      })
      .eq('id', run_id);
    
    res.status(500).json({ 
      message: 'Discovery execution failed', 
      error: error.message 
    });
  }
}
