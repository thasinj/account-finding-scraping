import { createClient } from '@supabase/supabase-js';
import { ensureSchema, newRunId } from './_db.js';

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_KEY);

export default async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      res.status(405).json({ message: 'Method not allowed' });
      return;
    }

    await ensureSchema();

    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};
    const { type, input, params } = body;

    if (!type || !input) {
      res.status(400).json({ message: "Missing 'type' or 'input' in body" });
      return;
    }

    const id = newRunId();
    
    const { error } = await supabase
      .from('runs')
      .insert({
        id,
        type,
        input,
        params: params || {},
        status: 'pending'
      });

    if (error) {
      throw new Error(`Database error: ${error.message}`);
    }

    res.status(200).json({ id });
  } catch (err) {
    res.status(500).json({ message: 'Failed to start run', error: String(err) });
  }
}




