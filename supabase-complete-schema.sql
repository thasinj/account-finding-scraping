-- Complete Supabase Schema for Instagram Discovery App
-- Run this in your Supabase SQL Editor

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  full_name TEXT,
  follower_count INT DEFAULT 0,
  following_count INT DEFAULT 0,
  media_count INT DEFAULT 0,
  verified BOOLEAN DEFAULT false,
  private BOOLEAN DEFAULT false,
  profile_url TEXT,
  last_seen_at TIMESTAMPTZ DEFAULT NOW(),
  discovery_vectors TEXT[], -- Array of hashtags/seeds that led to this profile
  primary_category TEXT, -- Primary discovery category (e.g., 'edm', 'luxury', 'gaming')
  discovery_count INT DEFAULT 1 -- How many times this profile was discovered
);

-- Create runs table
CREATE TABLE IF NOT EXISTS runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type TEXT NOT NULL, -- 'hashtag', 'similar', 'combined'
  input TEXT NOT NULL, -- hashtag or username input
  params JSONB, -- search parameters
  status TEXT DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
  current_layer INT DEFAULT 0,
  total_api_calls INT DEFAULT 0,
  stats JSONB, -- run statistics
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Create run_profiles junction table
CREATE TABLE IF NOT EXISTS run_profiles (
  id SERIAL PRIMARY KEY,
  run_id UUID REFERENCES runs(id) ON DELETE CASCADE,
  profile_id INT REFERENCES profiles(id) ON DELETE CASCADE,
  layer INT DEFAULT 0, -- which discovery layer this profile was found in
  discovery_method TEXT, -- 'hashtag', 'similar', 'seed'
  found_from TEXT, -- which hashtag/username led to this discovery
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(run_id, profile_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_username ON profiles(username);
CREATE INDEX IF NOT EXISTS idx_profiles_follower_count ON profiles(follower_count);
CREATE INDEX IF NOT EXISTS idx_profiles_primary_category ON profiles(primary_category);
CREATE INDEX IF NOT EXISTS idx_runs_status ON runs(status);
CREATE INDEX IF NOT EXISTS idx_runs_created_at ON runs(created_at);
CREATE INDEX IF NOT EXISTS idx_run_profiles_run_id ON run_profiles(run_id);
CREATE INDEX IF NOT EXISTS idx_run_profiles_profile_id ON run_profiles(profile_id);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE run_profiles ENABLE ROW LEVEL SECURITY;

-- Create policies to allow all operations (adjust as needed for your security requirements)
CREATE POLICY "Enable all operations for profiles" ON profiles FOR ALL USING (true);
CREATE POLICY "Enable all operations for runs" ON runs FOR ALL USING (true);
CREATE POLICY "Enable all operations for run_profiles" ON run_profiles FOR ALL USING (true);
