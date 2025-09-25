import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

// Helper function to chunk arrays
const chunk = (arr, size) => {
  const out = [];
  for (let i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
  return out;
};

// Helper function to update run status
async function updateRunStatus(runId, status, stats = null) {
  await supabase
    .from('runs')
    .update({ 
      status, 
      updated_at: new Date().toISOString(),
      ...(stats && { stats }),
      ...(status === 'completed' && { completed_at: new Date().toISOString() })
    })
    .eq('id', runId);
}

// Helper function to fetch similar accounts
async function fetchSimilarAccounts(username, maxCount = 10) {
  try {
    const apiKey = process.env.INSTAGRAM_API_KEY;
    const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
    const url = `${baseUrl}/get_ig_similar_accounts.php?username_or_url=${encodeURIComponent(username)}`;
    
    const response = await fetch(url, {
      headers: {
        'X-RapidAPI-Key': apiKey,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
      },
      timeout: 30000
    });
    
    if (response.ok) {
      const data = await response.json();
      return Array.isArray(data) ? data.slice(0, maxCount) : [];
    }
    return [];
  } catch (error) {
    console.error(`Error fetching similar accounts for ${username}:`, error);
    return [];
  }
}

// Helper function to fetch profile details
async function fetchProfileDetails(username) {
  try {
    const apiKey = process.env.INSTAGRAM_API_KEY;
    const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
    const url = `${baseUrl}/ig_get_fb_profile_hover.php?username_or_url=${encodeURIComponent(username)}`;
    
    const response = await fetch(url, {
      headers: {
        'X-RapidAPI-Key': apiKey,
        'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
      },
      timeout: 30000
    });
    
    if (response.ok) {
      const data = await response.json();
      return data?.user_data || null;
    }
    return null;
  } catch (error) {
    console.error(`Error fetching profile details for ${username}:`, error);
    return null;
  }
}

// Helper function to fetch hashtag posts
async function fetchHashtagPosts(hashtag, maxPages = 2) {
  try {
    const apiKey = process.env.INSTAGRAM_API_KEY;
    const baseUrl = 'https://instagram-scraper-stable-api.p.rapidapi.com';
    let allPosts = [];
    let paginationToken = null;
    
    for (let page = 0; page < maxPages; page++) {
      const params = new URLSearchParams({ hashtag });
      if (paginationToken) params.set('pagination_token', paginationToken);
      
      const url = `${baseUrl}/search_hashtag.php?${params.toString()}`;
      const response = await fetch(url, {
        headers: {
          'X-RapidAPI-Key': apiKey,
          'X-RapidAPI-Host': 'instagram-scraper-stable-api.p.rapidapi.com'
        },
        timeout: 30000
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data?.posts) allPosts.push(...data.posts);
        paginationToken = data?.pagination_token;
        if (!paginationToken) break;
      } else {
        break;
      }
    }
    
    return allPosts;
  } catch (error) {
    console.error(`Error fetching hashtag posts for ${hashtag}:`, error);
    return [];
  }
}

// Helper function to ingest profiles to database
async function ingestProfiles(runId, profiles, layer, discoveredFrom, discoveryMethod, category) {
  try {
    // Import the database functions directly
    const { upsertProfileFromApi } = await import('./_db.js');
    
    let totalInserted = 0;
    
    for (const profile of profiles) {
      try {
        console.log(`Processing profile: ${profile.username} with ${profile.follower_count} followers`);
        
        // Save profile to database
        const savedProfile = await upsertProfileFromApi(
          { user_data: profile }, 
          discoveredFrom, 
          category
        );
        
        console.log(`Upsert result for ${profile.username}:`, savedProfile ? `ID ${savedProfile.id}` : 'null');
        
        if (savedProfile) {
          // Create run_profiles relationship
          const { error: linkError } = await supabase
            .from('run_profiles')
            .upsert({
              run_id: runId,
              profile_id: savedProfile.id,
              layer: layer || 0,
              discovery_method: discoveryMethod || 'unknown',
              found_from: discoveredFrom || 'unknown'
            }, { onConflict: 'run_id,profile_id' });
            
          if (!linkError) {
            totalInserted++;
            console.log(`Successfully linked ${profile.username} to run ${runId}`);
          } else {
            console.error(`Link error for ${profile.username}:`, linkError);
          }
        } else {
          console.error(`Failed to save profile ${profile.username}`);
        }
      } catch (profileError) {
        console.error(`Error processing profile ${profile.username}:`, profileError);
      }
    }
    
    return totalInserted;
  } catch (error) {
    console.error('Error ingesting profiles:', error);
    return 0;
  }
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { run_id, chunk = 0 } = req.body;
  if (!run_id) {
    return res.status(400).json({ message: 'Missing run_id' });
  }

  try {
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

    // Mark run as running
    await updateRunStatus(run_id, 'running');
    
    const { type, input, params } = run;
    const { 
      pages = 2, 
      similarCount = 10, 
      minFollowers = 10000, 
      maxLayers = 1 
    } = params || {};

    let totalInserted = 0;
    let seedUsernames = [];

    // Phase 1: Collect initial seeds (simplified for timeout)
    if (type === 'combined') {
      // Skip hashtag posts for now to avoid timeout
      // Use input as direct seed
      seedUsernames = [input];
    } else {
      // Similar only mode - use input as seed
      seedUsernames = [input];
    }

    // Phase 2: Single layer similar account discovery (optimized for serverless timeout)
    let currentLayer = 1;
    let currentSeeds = seedUsernames.slice(0, 5); // Reduce to 5 seeds max for timeout
    
    while (currentLayer <= Math.min(maxLayers, 1) && currentSeeds.length > 0) {
      const layerProfiles = [];
      
      // Process only first 3 seeds to stay within timeout
      const limitedSeeds = currentSeeds.slice(0, 3);
      
       for (const seed of limitedSeeds) {
         console.log(`Processing seed: ${seed}`);
         const similarAccounts = await fetchSimilarAccounts(seed, Math.min(similarCount, 5));
         console.log(`Found ${similarAccounts.length} similar accounts for ${seed}`);
         
         // Process only first 5 similar accounts to avoid timeout
         for (const similar of similarAccounts.slice(0, 5)) {
           if (similar.username) {
             console.log(`Fetching profile for: ${similar.username}`);
             const profile = await fetchProfileDetails(similar.username);
             if (profile && profile.follower_count) {
               console.log(`Profile ${similar.username}: ${profile.follower_count} followers (min: ${minFollowers})`);
               if (profile.follower_count >= minFollowers) {
                 const profileToAdd = { username: similar.username, ...profile };
                 layerProfiles.push(profileToAdd);
                 console.log(`Added ${similar.username} to layer profiles`);
               } else {
                 console.log(`Skipped ${similar.username} - below follower threshold`);
               }
             } else {
               console.log(`No profile data for ${similar.username}`);
             }
           }
         }
       }
      
      // Remove duplicates
      console.log(`Before deduplication: ${layerProfiles.length} profiles`);
      const uniqueProfiles = layerProfiles.reduce((acc, profile) => {
        if (!acc.some(p => p.username === profile.username)) {
          acc.push(profile);
        }
        return acc;
      }, []);
      console.log(`After deduplication: ${uniqueProfiles.length} unique profiles`);
      
      if (uniqueProfiles.length === 0) {
        console.log('No profiles to ingest, breaking...');
        break;
      }
      
      // Ingest layer profiles
      console.log(`Attempting to ingest ${uniqueProfiles.length} unique profiles`);
      const inserted = await ingestProfiles(
        run_id,
        uniqueProfiles,
        currentLayer,
        currentLayer === 1 ? `similar:${input}` : `layer_${currentLayer - 1}`,
        'similar_accounts',
        input
      );
      console.log(`Successfully inserted ${inserted} profiles`);
      
      totalInserted += inserted;
      currentLayer++;
      break; // Force single layer for now to avoid timeout
    }

    // Mark run as completed
    await updateRunStatus(run_id, 'completed', {
      mode: type,
      input,
      pages,
      similarCount,
      minFollowers,
      maxLayers,
      totalInserted,
      layersCompleted: currentLayer - 1
    });

    res.status(200).json({ 
      success: true, 
      totalInserted,
      layersCompleted: currentLayer - 1
    });

  } catch (error) {
    console.error('Discovery execution error:', error);
    
    // Mark run as failed
    await updateRunStatus(run_id, 'failed', {
      error: error.message,
      timestamp: new Date().toISOString()
    });
    
    res.status(500).json({ 
      message: 'Discovery execution failed', 
      error: error.message 
    });
  }
}
