-- =====================================================
-- RAPTORFLOW DATABASE SCHEMA
-- Users, Plans, Payments, Subscriptions
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- PROFILES TABLE (extends auth.users)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  avatar_url TEXT,
  
  -- Plan & Subscription
  plan TEXT DEFAULT 'none' CHECK (plan IN ('none', 'ascent', 'glide', 'soar')),
  plan_status TEXT DEFAULT 'inactive' CHECK (plan_status IN ('inactive', 'active', 'expired', 'cancelled')),
  plan_started_at TIMESTAMPTZ,
  plan_expires_at TIMESTAMPTZ,
  
  -- Payment info
  payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'completed', 'failed', 'refunded')),
  last_payment_id TEXT,
  last_payment_amount INTEGER, -- in paise (INR smallest unit)
  last_payment_date TIMESTAMPTZ,
  
  -- PhonePe specific
  phonepe_merchant_user_id TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- PAYMENTS TABLE (payment history)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.payments (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
  
  -- Payment details
  amount INTEGER NOT NULL, -- in paise
  currency TEXT DEFAULT 'INR',
  plan TEXT NOT NULL CHECK (plan IN ('ascent', 'glide', 'soar')),
  
  -- PhonePe transaction details
  phonepe_transaction_id TEXT,
  phonepe_merchant_transaction_id TEXT UNIQUE,
  phonepe_payment_instrument_type TEXT,
  
  -- Status
  status TEXT DEFAULT 'initiated' CHECK (status IN ('initiated', 'pending', 'success', 'failed', 'refunded')),
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  
  -- Response data
  response_code TEXT,
  response_message TEXT,
  raw_response JSONB
);

-- =====================================================
-- PLAN PRICES (reference table)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.plan_prices (
  plan TEXT PRIMARY KEY CHECK (plan IN ('ascent', 'glide', 'soar')),
  price_inr INTEGER NOT NULL, -- in rupees
  price_paise INTEGER NOT NULL, -- in paise (price_inr * 100)
  name TEXT NOT NULL,
  description TEXT,
  features JSONB,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert plan prices
INSERT INTO public.plan_prices (plan, price_inr, price_paise, name, description, features) VALUES
('ascent', 5000, 500000, 'Ascent', 'Start building your strategy', '["Complete 7-pillar strategy intake", "1 strategic workspace", "AI-powered plan generation", "90-day war map creation", "PDF & Notion export", "Email support", "30-day methodology access"]'),
('glide', 7000, 700000, 'Glide', 'For founders who mean business', '["Everything in Ascent", "3 strategic workspaces", "Advanced AI strategy engine", "Real-time collaboration (up to 3)", "Integrations: Notion, Slack, Linear", "Priority support", "90-day methodology access", "Monthly strategy review call"]'),
('soar', 10000, 1000000, 'Soar', 'The complete strategic arsenal', '["Everything in Glide", "Unlimited workspaces", "Team collaboration (up to 10)", "White-label exports", "API access", "Dedicated success manager", "1-on-1 strategy onboarding call", "Lifetime methodology access", "Quarterly strategy sessions"]')
ON CONFLICT (plan) DO UPDATE SET
  price_inr = EXCLUDED.price_inr,
  price_paise = EXCLUDED.price_paise,
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  features = EXCLUDED.features;

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.plan_prices ENABLE ROW LEVEL SECURITY;

-- Profiles policies
CREATE POLICY "Users can view own profile" 
  ON public.profiles FOR SELECT 
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" 
  ON public.profiles FOR UPDATE 
  USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" 
  ON public.profiles FOR INSERT 
  WITH CHECK (auth.uid() = id);

-- Payments policies
CREATE POLICY "Users can view own payments" 
  ON public.payments FOR SELECT 
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own payments" 
  ON public.payments FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

-- Plan prices are public (read-only)
CREATE POLICY "Anyone can view plan prices" 
  ON public.plan_prices FOR SELECT 
  TO PUBLIC 
  USING (true);

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name'),
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for profile updates
DROP TRIGGER IF EXISTS profiles_updated_at ON public.profiles;
CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- Function to activate plan after successful payment
CREATE OR REPLACE FUNCTION public.activate_plan(
  p_user_id UUID,
  p_plan TEXT,
  p_payment_id TEXT,
  p_amount INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
  v_duration_days INTEGER;
BEGIN
  -- Set duration based on plan
  v_duration_days := CASE p_plan
    WHEN 'ascent' THEN 30
    WHEN 'glide' THEN 90
    WHEN 'soar' THEN 365 * 10 -- "Lifetime" = 10 years
    ELSE 30
  END;

  -- Update profile with plan info
  UPDATE public.profiles
  SET
    plan = p_plan,
    plan_status = 'active',
    plan_started_at = NOW(),
    plan_expires_at = NOW() + (v_duration_days || ' days')::INTERVAL,
    payment_status = 'completed',
    last_payment_id = p_payment_id,
    last_payment_amount = p_amount,
    last_payment_date = NOW()
  WHERE id = p_user_id;

  RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- INDEXES for performance
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_plan ON public.profiles(plan);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON public.payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON public.payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_phonepe_txn ON public.payments(phonepe_merchant_transaction_id);

