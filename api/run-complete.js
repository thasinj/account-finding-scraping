import { createClient } from '@supabase/supabase-js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

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

    const { error } = await supabase
      .from('runs')
      .update({
        status: 'completed',
        updated_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
        stats: stats || {}
      })
      .eq('id', id);

    if (error) {
      throw error;
    }

    res.status(200).json({ ok: true });
  } catch (err) {
    res.status(500).json({ message: 'Failed to complete run', error: String(err) });
  }
}




