export function getSupabase() {
  const url = import.meta.env.VITE_SUPABASE_URL;
  const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
  if (!url || !anonKey) {
    throw new Error('Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY');
  }
  // Lazy import to avoid bundling if not used
  const { createClient } = require('@supabase/supabase-js');
  return createClient(url, anonKey);
}
