-- Fix the run_profiles table to add unique constraint
-- Run this in your Supabase SQL Editor

-- First, check if the constraint already exists
SELECT constraint_name 
FROM information_schema.table_constraints 
WHERE table_name = 'run_profiles' 
AND constraint_type = 'UNIQUE';

-- Add the unique constraint if it doesn't exist
ALTER TABLE run_profiles 
ADD CONSTRAINT run_profiles_run_id_profile_id_unique 
UNIQUE (run_id, profile_id);

-- Verify the constraint was added
SELECT constraint_name 
FROM information_schema.table_constraints 
WHERE table_name = 'run_profiles' 
AND constraint_type = 'UNIQUE';
