import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

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
    const { error } = await supabase
      .from('runs')
      .update({
        status: 'failed',
        updated_at: new Date().toISOString(),
        stats: {
          ...stats,
          error_message,
          failed_at: new Date().toISOString()
        }
      })
      .eq('id', id);

    if (error) {
      throw error;
    }

    res.status(200).json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: 'Failed to mark run as failed', error: String(err) });
  }
}
