-- Fix for missing billing tables
-- Migration: 20260112_fix_billing_tables.sql

-- 1. Create ENUMs
DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM (
      'pending',
      'completed',
      'failed',
      'refunded',
      'cancelled'
    );
    CREATE TYPE subscription_status AS ENUM (
      'pending',
      'active',
      'past_due',
      'cancelled',
      'expired'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Create Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  plan_id TEXT NOT NULL REFERENCES plans(id),
  plan_name TEXT NOT NULL,
  
  -- Billing details
  billing_cycle billing_cycle NOT NULL,
  price_monthly_paise INTEGER NOT NULL,
  status subscription_status NOT NULL DEFAULT 'pending',
  
  -- Period
  current_period_start TIMESTAMPTZ DEFAULT NOW(),
  current_period_end TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  UNIQUE(user_id) -- One active subscription per user for now
);

-- 3. Create Payments Table
CREATE TABLE IF NOT EXISTS payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  subscription_id UUID REFERENCES subscriptions(id),
  
  -- Transaction Details
  amount_paise INTEGER NOT NULL,
  currency TEXT DEFAULT 'INR',
  status payment_status NOT NULL DEFAULT 'pending',
  
  -- PhonePe Specific
  provider_transaction_id TEXT, -- PhonePe Transaction ID
  merchant_transaction_id TEXT UNIQUE NOT NULL,
  payment_instrument_type TEXT,
  
  -- Metadata
  cin TEXT, -- Customer Identification Number
  invoice_url TEXT,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Create Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id UUID REFERENCES users(id),
  action TEXT NOT NULL,
  action_category TEXT,
  description TEXT,
  ip_address TEXT,
  user_agent TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Enable RLS
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 6. RLS Policies
-- Subscriptions: Users can read own
CREATE POLICY "Users can view own subscription" ON subscriptions
    FOR SELECT USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

-- Payments: Users can read own
CREATE POLICY "Users can view own payments" ON payments
    FOR SELECT USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));

-- Audit Logs: Insert only for users (via API), Read for Admins only
CREATE POLICY "Users can insert audit logs" ON audit_logs
    FOR INSERT WITH CHECK (actor_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));
