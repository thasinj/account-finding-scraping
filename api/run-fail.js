import { sql } from '@vercel/postgres';

export default async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      res.status(405).json({ message: 'Method not allowed' });
      return;
    }

    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};
    const { id, error_message, stats } = body;
    if (!id) {
      res.status(400).json({ message: "Missing 'id'" });
      return;
    }

    // Mark run as failed but preserve all data found so far
    await sql`
      update runs 
      set 
        status = 'failed', 
        updated_at = now(), 
        stats = ${JSON.stringify({
          ...stats,
          error_message,
          failed_at: new Date().toISOString()
        })}
      where id = ${id}
    `;

    res.status(200).json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: 'Failed to mark run as failed', error: String(err) });
  }
}
