import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

export default async function handler(req, res) {
  try {
    if (req.method !== 'GET') {
      res.status(405).json({ message: 'Method not allowed' });
      return;
    }

    const { category, minFollowers, limit = 100, offset = 0 } = req.query;

    // Build query with filters
    let query = supabase
      .from('profiles')
      .select(`
        *,
        run_profiles!inner(
          discovery_method,
          runs!inner(input)
        )
      `)
      .order('follower_count', { ascending: false });

    // Apply filters
    if (category && category !== 'all') {
      query = query.eq('primary_category', category);
    }

    if (minFollowers && Number(minFollowers) > 0) {
      query = query.gte('follower_count', Number(minFollowers));
    }

    // Apply pagination
    const { data: profiles, error } = await query
      .range(Number(offset), Number(offset) + Number(limit) - 1);

    if (error) {
      throw error;
    }

    // Get total count for pagination
    let countQuery = supabase
      .from('profiles')
      .select('id', { count: 'exact', head: true });

    if (category && category !== 'all') {
      countQuery = countQuery.eq('primary_category', category);
    }

    if (minFollowers && Number(minFollowers) > 0) {
      countQuery = countQuery.gte('follower_count', Number(minFollowers));
    }

    const { count: total, error: countError } = await countQuery;

    if (countError) {
      throw countError;
    }

    // Get available categories
    const { data: categoryData, error: categoryError } = await supabase
      .from('profiles')
      .select('primary_category')
      .not('primary_category', 'is', null);

    if (categoryError) {
      throw categoryError;
    }

    // Count categories
    const categoryCount = categoryData.reduce((acc, item) => {
      acc[item.primary_category] = (acc[item.primary_category] || 0) + 1;
      return acc;
    }, {});

    const categories = Object.entries(categoryCount)
      .map(([primary_category, count]) => ({ primary_category, count }))
      .sort((a, b) => b.count - a.count);

    // Transform profiles data
    const transformedProfiles = profiles.map(profile => ({
      ...profile,
      discovery_methods: [...new Set(profile.run_profiles?.map(rp => rp.discovery_method) || [])],
      run_inputs: [...new Set(profile.run_profiles?.map(rp => rp.runs?.input) || [])],
      run_count: profile.run_profiles?.length || 0,
      last_discovered_at: profile.last_seen_at
    }));

    res.status(200).json({ 
      profiles: transformedProfiles,
      total: total || 0,
      categories,
      pagination: {
        limit: Number(limit),
        offset: Number(offset),
        hasMore: Number(offset) + Number(limit) < (total || 0)
      }
    });
  } catch (err) {
    console.error('Error fetching profiles:', err);
    res.status(500).json({ message: 'Failed to fetch profiles', error: String(err) });
  }
}
