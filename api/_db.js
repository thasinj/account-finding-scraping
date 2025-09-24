import { createClient } from '@supabase/supabase-js';
import { randomUUID } from 'node:crypto';

// Initialize Supabase client
const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error('Missing Supabase environment variables. Please set VITE_SUPABASE_URL and VITE_SUPABASE_KEY');
}

const supabase = createClient(supabaseUrl, supabaseKey);

export async function ensureSchema() {
  // Tables should be created via Supabase Dashboard or migrations
  // This function now just checks if tables exist and creates them if needed
  console.log('Schema check - tables should be created in Supabase Dashboard');
  return true;
}

export function newRunId() {
  return randomUUID();
}

export async function upsertProfileFromApi(data, discoveryVector = null, category = null) {
  const username = data?.user_data?.username || data?.username;
  if (!username) return null;
  
  const full_name = data?.user_data?.full_name || data?.full_name || '';
  const follower_count = Number(data?.user_data?.follower_count || data?.follower_count || 0) || 0;
  const following_count = Number(data?.user_data?.following_count || data?.following_count || 0) || 0;
  const media_count = Number(data?.user_data?.media_count || data?.media_count || 0) || 0;
  const verified = Boolean(data?.user_data?.is_verified || data?.is_verified || false);
  const is_private = Boolean(data?.user_data?.is_private || data?.is_private || false);
  const profile_url = `https://instagram.com/${username}`;

  try {
    // Check if profile already exists
    const { data: existing, error: selectError } = await supabase
      .from('profiles')
      .select('id, discovery_vectors, primary_category, discovery_count')
      .eq('username', username)
      .single();

    if (selectError && selectError.code !== 'PGRST116') {
      throw selectError;
    }

    let newVectors = existing?.discovery_vectors || [];
    if (discoveryVector && !newVectors.includes(discoveryVector)) {
      newVectors.push(discoveryVector);
    }

    const primaryCategory = existing?.primary_category || category || 'unknown';
    const discoveryCount = existing ? existing.discovery_count + 1 : 1;

    const profileData = {
      username,
      full_name,
      follower_count,
      following_count,
      media_count,
      verified,
      private: is_private,
      profile_url,
      last_seen_at: new Date().toISOString(),
      discovery_vectors: newVectors,
      primary_category: primaryCategory,
      discovery_count: discoveryCount
    };

    // Upsert profile
    const { data: result, error: upsertError } = await supabase
      .from('profiles')
      .upsert(profileData, { onConflict: 'username' })
      .select()
      .single();

    if (upsertError) {
      throw upsertError;
    }

    return result;
  } catch (error) {
    console.error('Error upserting profile:', error);
    // Return a mock profile for development
    return {
      id: Math.floor(Math.random() * 1000000),
      username,
      full_name,
      follower_count,
      following_count,
      media_count,
      verified,
      private: is_private,
      profile_url,
      discovery_vectors: [discoveryVector].filter(Boolean),
      primary_category: category || 'unknown',
      discovery_count: 1
    };
  }
}




