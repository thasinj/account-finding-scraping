import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  try {
    if (req.method !== 'GET') {
      res.status(405).json({ message: 'Method not allowed' });
      return;
    }

    const { category, minFollowers, limit = 100, offset = 0 } = req.query;

    let whereClause = '1=1';
    let params = [];
    let paramIndex = 1;

    // Filter by category if provided
    if (category && category !== 'all') {
      whereClause += ` AND primary_category = $${paramIndex}`;
      params.push(category);
      paramIndex++;
    }

    // Filter by minimum followers if provided
    if (minFollowers && Number(minFollowers) > 0) {
      whereClause += ` AND follower_count >= $${paramIndex}`;
      params.push(Number(minFollowers));
      paramIndex++;
    }

    // Get profiles with discovery information
    const profilesQuery = `
      SELECT 
        p.*,
        array_agg(DISTINCT rp.discovery_method) as discovery_methods,
        array_agg(DISTINCT r.input) as run_inputs,
        count(DISTINCT rp.run_id) as run_count,
        max(rp.created_at) as last_discovered_at
      FROM profiles p
      LEFT JOIN run_profiles rp ON p.id = rp.profile_id
      LEFT JOIN runs r ON rp.run_id = r.id
      WHERE ${whereClause}
      GROUP BY p.id
      ORDER BY p.follower_count DESC, p.last_seen_at DESC
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `;

    params.push(Number(limit), Number(offset));

    const { rows } = await sql.query(profilesQuery, params);

    // Get total count for pagination
    const countQuery = `
      SELECT count(DISTINCT p.id) as total 
      FROM profiles p 
      LEFT JOIN run_profiles rp ON p.id = rp.profile_id
      LEFT JOIN runs r ON rp.run_id = r.id
      WHERE ${whereClause}
    `;

    const countParams = params.slice(0, -2); // Remove limit and offset
    const { rows: countRows } = await sql.query(countQuery, countParams);
    const total = Number(countRows[0].total);

    // Get available categories
    const categoriesQuery = `
      SELECT primary_category, count(*) as count 
      FROM profiles 
      WHERE primary_category IS NOT NULL 
      GROUP BY primary_category 
      ORDER BY count DESC
    `;
    const { rows: categoryRows } = await sql.query(categoriesQuery);

    res.status(200).json({ 
      profiles: rows,
      total,
      categories: categoryRows,
      pagination: {
        limit: Number(limit),
        offset: Number(offset),
        hasMore: Number(offset) + Number(limit) < total
      }
    });
  } catch (err) {
    console.error('Error fetching profiles:', err);
    res.status(500).json({ message: 'Failed to fetch profiles', error: String(err) });
  }
}
