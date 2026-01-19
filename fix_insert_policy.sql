-- Fix for 'creation_failed' RLS error
-- Migration: 20260112_add_insert_policy.sql

-- Enable users to insert their own profile
CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth_user_id = auth.uid());
