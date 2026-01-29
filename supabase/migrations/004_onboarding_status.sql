-- Migration: Add onboarding status tracking to users table
-- Description: Critical for tracking user progress through 23-step onboarding journey

-- Add onboarding status enum field with constraints
ALTER TABLE users
  ADD COLUMN onboarding_status TEXT DEFAULT 'pending'
  CHECK (onboarding_status IN ('pending', 'payment_confirmed', 'in_progress', 'completed', 'abandoned'));

-- Add completion timestamp field
ALTER TABLE users
  ADD COLUMN onboarding_completed_at TIMESTAMPTZ;

-- Create performance index for status queries
CREATE INDEX idx_users_onboarding_status ON users(onboarding_status);

-- Create index for completion tracking
CREATE INDEX idx_users_onboarding_completed_at ON users(onboarding_completed_at) WHERE onboarding_completed_at IS NOT NULL;

-- RLS Policy: Allow users to update their own onboarding status
CREATE POLICY "Users can update own onboarding status" ON users
  FOR UPDATE USING (auth.uid() = id);

-- RLS Policy: Allow users to read their own onboarding status
CREATE POLICY "Users can read own onboarding status" ON users
  FOR SELECT USING (auth.uid() = id);

-- RLS Policy: Allow service role to update onboarding status (for backend processes)
CREATE POLICY "Service role can update onboarding status" ON users
  FOR UPDATE USING (role() = 'service_role');

-- Trigger to automatically set completion timestamp when status changes to 'completed'
CREATE OR REPLACE FUNCTION set_onboarding_completed_at()
RETURNS TRIGGER AS $$
BEGIN
  -- Set completion timestamp when status becomes 'completed'
  IF NEW.onboarding_status = 'completed' AND OLD.onboarding_status != 'completed' THEN
    NEW.onboarding_completed_at = NOW();
  END IF;

  -- Clear completion timestamp if status changes away from 'completed'
  IF NEW.onboarding_status != 'completed' AND OLD.onboarding_status = 'completed' THEN
    NEW.onboarding_completed_at = NULL;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to automatically manage completion timestamp
CREATE TRIGGER trigger_set_onboarding_completed_at
  BEFORE UPDATE ON users
  FOR EACH ROW
  EXECUTE FUNCTION set_onboarding_completed_at();

-- Add comment for documentation
COMMENT ON COLUMN users.onboarding_status IS 'Tracks user progress through onboarding: pending, payment_confirmed, in_progress, completed, abandoned';
COMMENT ON COLUMN users.onboarding_completed_at IS 'Timestamp when user completed onboarding, set automatically via trigger';
