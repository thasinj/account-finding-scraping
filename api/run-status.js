import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  try {
    const { id } = req.query;
    if (!id) {
      res.status(400).json({ message: "Missing query 'id'" });
      return;
    }

    const { rows } = await sql`select * from runs where id = ${id}`;
    if (rows.length === 0) {
      res.status(404).json({ message: 'Run not found' });
      return;
    }

    const run = rows[0];
    const profiles = await sql`
      select rp.layer, rp.discovery_method, rp.found_from, p.username, p.full_name, p.follower_count
      from run_profiles rp
      join profiles p on p.id = rp.profile_id
      where rp.run_id = ${id}
      order by rp.layer asc, p.follower_count desc
    `;

    res.status(200).json({ run, profiles: profiles.rows });
  } catch (err) {
    res.status(500).json({ message: 'Failed to get status', error: String(err) });
  }
}




