import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

export default async function handler(req, res) {
  try {
    if (req.method !== 'GET') {
      res.status(405).json({ message: 'Method not allowed' });
      return;
    }

    // Get all runs with profile counts
    const { data: runs, error } = await supabase
      .from('runs')
      .select(`
        id,
        type,
        input,
        status,
        created_at,
        completed_at,
        total_api_calls,
        stats
      `)
      .order('created_at', { ascending: false })
      .limit(50);

    if (error) {
      throw error;
    }

    // Get profile counts for each run separately
    const transformedRuns = await Promise.all(runs.map(async (run) => {
      const { count, error: countError } = await supabase
        .from('run_profiles')
        .select('*', { count: 'exact', head: true })
        .eq('run_id', run.id);

      return {
        ...run,
        profile_count: countError ? 0 : (count || 0)
      };
    }));

    res.status(200).json({ runs: transformedRuns });
  } catch (err) {
    console.error('Error fetching runs:', err);
    res.status(500).json({ message: 'Failed to fetch runs', error: String(err) });
  }
}
