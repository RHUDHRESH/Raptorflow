-- ============================================
-- MIGRATION 005: Subscriptions and Onboarding Tables
-- Purpose: Track user subscriptions and onboarding completion
-- ============================================

-- ============================================
-- 1. SUBSCRIPTIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
  
  -- Subscription Details
  plan VARCHAR(50) NOT NULL DEFAULT 'free', -- 'free', 'Ascent', 'Surge', 'Raptor'
  status VARCHAR(50) NOT NULL DEFAULT 'active', -- 'active', 'past_due', 'canceled', 'trialing'
  
  -- Stripe Integration (optional)
  stripe_customer_id VARCHAR(255),
  stripe_subscription_id VARCHAR(255),
  stripe_price_id VARCHAR(255),
  
  -- Billing
  billing_period VARCHAR(50) DEFAULT 'monthly', -- 'monthly', 'yearly'
  current_period_start TIMESTAMP WITH TIME ZONE,
  current_period_end TIMESTAMP WITH TIME ZONE,
  
  -- Trial
  trial_start TIMESTAMP WITH TIME ZONE,
  trial_end TIMESTAMP WITH TIME ZONE,
  
  -- Metadata
  metadata JSONB DEFAULT '{}'::jsonb,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  canceled_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for subscriptions
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_workspace_id ON public.subscriptions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer ON public.subscriptions(stripe_customer_id);

-- ============================================
-- 2. ONBOARDING_RESPONSES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.onboarding_responses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
  
  -- Onboarding Data
  answers JSONB NOT NULL DEFAULT '{}'::jsonb,
  generated_icps JSONB DEFAULT '[]'::jsonb,
  positioning_insights JSONB DEFAULT '{}'::jsonb,
  
  -- Progress Tracking
  completed_at TIMESTAMP WITH TIME ZONE,
  progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
  current_step VARCHAR(100),
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for onboarding_responses
CREATE INDEX IF NOT EXISTS idx_onboarding_responses_user_id ON public.onboarding_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_responses_workspace_id ON public.onboarding_responses(workspace_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_responses_completed ON public.onboarding_responses(completed_at);

-- ============================================
-- 3. USER_PROFILES TABLE (Extended User Info)
-- ============================================
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Profile Info
  full_name VARCHAR(255),
  avatar_url TEXT,
  bio TEXT,
  
  -- Preferences
  preferences JSONB DEFAULT '{}'::jsonb,
  
  -- Onboarding Status
  onboarding_completed BOOLEAN DEFAULT FALSE,
  onboarding_skipped BOOLEAN DEFAULT FALSE,
  
  -- Feature Flags
  features JSONB DEFAULT '{}'::jsonb,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for user_profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_onboarding ON public.user_profiles(onboarding_completed);

-- ============================================
-- 4. TRIGGER FUNCTIONS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers for updated_at
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
  BEFORE UPDATE ON public.subscriptions
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_onboarding_responses_updated_at ON public.onboarding_responses;
CREATE TRIGGER update_onboarding_responses_updated_at
  BEFORE UPDATE ON public.onboarding_responses
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON public.user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================
-- 5. FUNCTION: Create User Profile on Signup
-- ============================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Create user profile
  INSERT INTO public.user_profiles (id, full_name, avatar_url)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', NEW.email),
    COALESCE(NEW.raw_user_meta_data->>'avatar_url', NEW.raw_user_meta_data->>'picture')
  );
  
  -- Create default free subscription
  INSERT INTO public.subscriptions (user_id, plan, status)
  VALUES (NEW.id, 'free', 'active');
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on new user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- 6. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Enable RLS
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.onboarding_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Subscriptions Policies
DROP POLICY IF EXISTS "Users can view own subscriptions" ON public.subscriptions;
CREATE POLICY "Users can view own subscriptions"
  ON public.subscriptions
  FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own subscriptions" ON public.subscriptions;
CREATE POLICY "Users can update own subscriptions"
  ON public.subscriptions
  FOR UPDATE
  USING (auth.uid() = user_id);

-- Onboarding Responses Policies
DROP POLICY IF EXISTS "Users can view own onboarding responses" ON public.onboarding_responses;
CREATE POLICY "Users can view own onboarding responses"
  ON public.onboarding_responses
  FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own onboarding responses" ON public.onboarding_responses;
CREATE POLICY "Users can insert own onboarding responses"
  ON public.onboarding_responses
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own onboarding responses" ON public.onboarding_responses;
CREATE POLICY "Users can update own onboarding responses"
  ON public.onboarding_responses
  FOR UPDATE
  USING (auth.uid() = user_id);

-- User Profiles Policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
CREATE POLICY "Users can view own profile"
  ON public.user_profiles
  FOR SELECT
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
CREATE POLICY "Users can update own profile"
  ON public.user_profiles
  FOR UPDATE
  USING (auth.uid() = id);

-- ============================================
-- 7. HELPER FUNCTIONS
-- ============================================

-- Function to get user's active subscription
CREATE OR REPLACE FUNCTION public.get_user_subscription(p_user_id UUID)
RETURNS TABLE (
  plan VARCHAR(50),
  status VARCHAR(50),
  current_period_end TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT s.plan, s.status, s.current_period_end
  FROM public.subscriptions s
  WHERE s.user_id = p_user_id
    AND s.status IN ('active', 'trialing')
  ORDER BY s.created_at DESC
  LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user has completed onboarding
CREATE OR REPLACE FUNCTION public.has_completed_onboarding(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  v_completed BOOLEAN;
BEGIN
  SELECT onboarding_completed INTO v_completed
  FROM public.user_profiles
  WHERE id = p_user_id;
  
  RETURN COALESCE(v_completed, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 8. GRANT PERMISSIONS
-- ============================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO anon, authenticated;

-- Grant permissions on tables
GRANT SELECT, INSERT, UPDATE ON public.subscriptions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.onboarding_responses TO authenticated;
GRANT SELECT, UPDATE ON public.user_profiles TO authenticated;

-- Grant execute on functions
GRANT EXECUTE ON FUNCTION public.get_user_subscription(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION public.has_completed_onboarding(UUID) TO authenticated;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================

-- To verify the migration, run:
-- SELECT * FROM public.subscriptions;
-- SELECT * FROM public.onboarding_responses;
-- SELECT * FROM public.user_profiles;



