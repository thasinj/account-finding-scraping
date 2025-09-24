import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      res.status(405).json({ message: 'Method not allowed' });
      return;
    }

    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};
    const { id, stats } = body;
    if (!id) {
      res.status(400).json({ message: "Missing 'id'" });
      return;
    }

    await sql`
      update runs set status = 'completed', updated_at = now(), completed_at = now(), stats = ${stats || {}}
      where id = ${id}
    `;

    res.status(200).json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: 'Failed to complete run', error: String(err) });
  }
}




