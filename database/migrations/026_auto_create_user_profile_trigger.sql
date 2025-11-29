-- ============================================
-- RAPTORFLOW MIGRATION 026
-- Description: Auto-create user profile trigger
-- ============================================

-- Function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Insert into user_profiles
  -- Note: We use user_profiles because AuthContext currently relies on it.
  -- If user_profiles is a view to profiles, this might need adjustment, but assuming table for now.
  INSERT INTO public.user_profiles (id, full_name, avatar_url, email)
  VALUES (
    NEW.id,
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'avatar_url',
    NEW.email
  )
  ON CONFLICT (id) DO UPDATE SET
    full_name = EXCLUDED.full_name,
    avatar_url = EXCLUDED.avatar_url,
    email = EXCLUDED.email,
    updated_at = NOW();

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Optional: Backfill for existing users who might be missing profiles
-- This is safe because of ON CONFLICT DO UPDATE/NOTHING
-- We only insert if missing.
INSERT INTO public.user_profiles (id, full_name, avatar_url, email)
SELECT 
  id, 
  raw_user_meta_data->>'full_name', 
  raw_user_meta_data->>'avatar_url', 
  email
FROM auth.users
ON CONFLICT (id) DO NOTHING;
