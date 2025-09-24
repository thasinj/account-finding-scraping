import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

export default async function handler(req, res) {
  try {
    const { id } = req.query;
    if (!id) {
      res.status(400).json({ message: "Missing query 'id'" });
      return;
    }

    // Get run details
    const { data: run, error: runError } = await supabase
      .from('runs')
      .select('*')
      .eq('id', id)
      .single();

    if (runError || !run) {
      res.status(404).json({ message: 'Run not found' });
      return;
    }

    // Get profiles for this run
    const { data: profiles, error: profilesError } = await supabase
      .from('run_profiles')
      .select(`
        layer,
        discovery_method,
        found_from,
        profiles!inner(
          username,
          full_name,
          follower_count
        )
      `)
      .eq('run_id', id)
      .order('layer', { ascending: true });

    if (profilesError) {
      throw profilesError;
    }

    // Transform profiles data to match expected format
    const transformedProfiles = profiles.map(rp => ({
      layer: rp.layer,
      discovery_method: rp.discovery_method,
      found_from: rp.found_from,
      username: rp.profiles.username,
      full_name: rp.profiles.full_name,
      follower_count: rp.profiles.follower_count
    }));

    res.status(200).json({ run, profiles: transformedProfiles });
  } catch (err) {
    res.status(500).json({ message: 'Failed to get status', error: String(err) });
  }
}




