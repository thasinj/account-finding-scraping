-- Supabase Schema Fix
-- Run this in your Supabase SQL Editor to add missing columns

-- Add missing columns to profiles table
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS discovery_vectors text[],
ADD COLUMN IF NOT EXISTS primary_category text,
ADD COLUMN IF NOT EXISTS discovery_count int DEFAULT 1;

-- Verify the schema
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'profiles' 
ORDER BY ordinal_position;

-- Also verify runs table exists
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'runs' 
ORDER BY ordinal_position;

-- And run_profiles table
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'run_profiles' 
ORDER BY ordinal_position;
