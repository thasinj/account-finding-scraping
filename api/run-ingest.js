import { createClient } from '@supabase/supabase-js';
import { ensureSchema, upsertProfileFromApi } from './_db.js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

export default async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      res.status(405).json({ message: 'Method not allowed' });
      return;
    }

    await ensureSchema();

    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};
    const { run_id, layer = 0, discovered_from, discovery_method = 'unknown', profiles, category } = body;
    if (!run_id || !Array.isArray(profiles)) {
      res.status(400).json({ message: "Missing 'run_id' or 'profiles' (array)" });
      return;
    }

    // Extract discovery vector from discovered_from (e.g., "#edm" or "similar:username")
    const discoveryVector = discovered_from;
    
    const inserted = [];
    for (const p of profiles) {
      const saved = await upsertProfileFromApi(p, discoveryVector, category);
      if (!saved) continue;
      
      // Insert run_profiles relationship
      try {
        await supabase
          .from('run_profiles')
          .upsert({
            run_id,
            profile_id: saved.id,
            discovery_method,
            found_from: discovered_from || null,
            layer,
            post_url: p.post_url || null
          }, { 
            onConflict: 'run_id,profile_id,discovery_method,found_from',
            ignoreDuplicates: true 
          });
      } catch (runProfileError) {
        console.error('Error inserting run_profile:', runProfileError);
        // Continue with other profiles even if one fails
      }
      
      inserted.push(saved.username);
    }

    res.status(200).json({ inserted_count: inserted.length, usernames: inserted });
  } catch (err) {
    res.status(500).json({ message: 'Failed to ingest profiles', error: String(err) });
  }
}




