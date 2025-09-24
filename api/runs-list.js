import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  try {
    if (req.method !== 'GET') {
      res.status(405).json({ message: 'Method not allowed' });
      return;
    }

    // Get all runs with profile counts
    const { rows } = await sql`
      select 
        r.id,
        r.type,
        r.input,
        r.status,
        r.created_at,
        r.completed_at,
        r.total_api_calls,
        r.stats,
        count(rp.id) as profile_count
      from runs r
      left join run_profiles rp on r.id = rp.run_id
      group by r.id, r.type, r.input, r.status, r.created_at, r.completed_at, r.total_api_calls, r.stats
      order by r.created_at desc
      limit 50
    `;

    res.status(200).json({ runs: rows });
  } catch (err) {
    console.error('Error fetching runs:', err);
    res.status(500).json({ message: 'Failed to fetch runs', error: String(err) });
  }
}
