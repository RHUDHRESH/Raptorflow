-- Payment Tables for PhonePe Integration
-- Tables for one-time payments, autopay subscriptions, and billing history
-- Run this after 005_subscriptions_and_onboarding.sql

-- Billing History Table (one-time payments and subscription charges)
CREATE TABLE IF NOT EXISTS billing_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  workspace_id UUID NOT NULL,
  transaction_id VARCHAR(100),
  merchant_transaction_id VARCHAR(100) UNIQUE NOT NULL,
  amount INTEGER NOT NULL CHECK (amount > 0),  -- Amount in paise (1/100th of rupee)
  currency VARCHAR(3) DEFAULT 'INR',
  payment_method VARCHAR(50) DEFAULT 'upi',
  plan VARCHAR(50),  -- Subscription plan (ascent, glide, soar, one-time)
  billing_period VARCHAR(20),  -- monthly, yearly, one-time
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed', 'cancelled', 'refunded')),
  failure_reason TEXT,
  receipt_url TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for billing_history
CREATE INDEX IF NOT EXISTS idx_billing_history_user ON billing_history(user_id);
CREATE INDEX IF NOT EXISTS idx_billing_history_workspace ON billing_history(workspace_id);
CREATE INDEX IF NOT EXISTS idx_billing_history_merchant_txn ON billing_history(merchant_transaction_id);
CREATE INDEX IF NOT EXISTS idx_billing_history_status ON billing_history(status);
CREATE INDEX IF NOT EXISTS idx_billing_history_created ON billing_history(created_at);
CREATE INDEX IF NOT EXISTS idx_billing_history_plan ON billing_history(plan);

-- Trigger for updated_at
CREATE TRIGGER update_billing_history_updated_at
  BEFORE UPDATE ON billing_history
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- RLS Policy for billing_history
ALTER TABLE billing_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their billing history"
  ON billing_history FOR SELECT
  USING (user_id = auth.uid() OR workspace_id = get_user_workspace_id());

CREATE POLICY "Service can insert billing history"
  ON billing_history FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Service can update billing history"
  ON billing_history FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());


-- Autopay Subscriptions Table (recurring payment mandates)
CREATE TABLE IF NOT EXISTS autopay_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  workspace_id UUID NOT NULL,
  subscription_id VARCHAR(100),
  merchant_subscription_id VARCHAR(100) UNIQUE NOT NULL,
  plan VARCHAR(50) NOT NULL CHECK (plan IN ('ascent', 'glide', 'soar')),
  billing_period VARCHAR(20) NOT NULL CHECK (billing_period IN ('monthly', 'yearly')),
  billing_frequency VARCHAR(20),
  amount INTEGER NOT NULL CHECK (amount > 0),  -- Amount in paise
  currency VARCHAR(3) DEFAULT 'INR',
  mobile_number VARCHAR(20),
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'paused', 'cancelled', 'expired', 'failed')),
  start_date DATE,
  end_date DATE,
  next_billing_date DATE,
  activated_at TIMESTAMP,
  paused_at TIMESTAMP,
  pause_reason TEXT,
  resumed_at TIMESTAMP,
  cancelled_at TIMESTAMP,
  cancellation_reason TEXT,
  total_payments INTEGER DEFAULT 0,
  successful_payments INTEGER DEFAULT 0,
  failed_payments INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for autopay_subscriptions
CREATE INDEX IF NOT EXISTS idx_autopay_subs_user ON autopay_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_autopay_subs_workspace ON autopay_subscriptions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_autopay_subs_merchant_id ON autopay_subscriptions(merchant_subscription_id);
CREATE INDEX IF NOT EXISTS idx_autopay_subs_status ON autopay_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_autopay_subs_plan ON autopay_subscriptions(plan);
CREATE INDEX IF NOT EXISTS idx_autopay_subs_next_billing ON autopay_subscriptions(next_billing_date);
CREATE INDEX IF NOT EXISTS idx_autopay_subs_created ON autopay_subscriptions(created_at);

-- Trigger for updated_at
CREATE TRIGGER update_autopay_subs_updated_at
  BEFORE UPDATE ON autopay_subscriptions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- RLS Policy for autopay_subscriptions
ALTER TABLE autopay_subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their subscriptions"
  ON autopay_subscriptions FOR SELECT
  USING (user_id = auth.uid() OR workspace_id = get_user_workspace_id());

CREATE POLICY "Service can insert subscriptions"
  ON autopay_subscriptions FOR INSERT
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Service can update subscriptions"
  ON autopay_subscriptions FOR UPDATE
  USING (workspace_id = get_user_workspace_id())
  WITH CHECK (workspace_id = get_user_workspace_id());

CREATE POLICY "Service can delete subscriptions"
  ON autopay_subscriptions FOR DELETE
  USING (workspace_id = get_user_workspace_id());


-- Autopay Payments Table (individual charges from subscriptions)
CREATE TABLE IF NOT EXISTS autopay_payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  merchant_subscription_id VARCHAR(100) NOT NULL REFERENCES autopay_subscriptions(merchant_subscription_id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  payment_id VARCHAR(100) UNIQUE NOT NULL,
  amount INTEGER NOT NULL CHECK (amount > 0),  -- Amount in paise
  currency VARCHAR(3) DEFAULT 'INR',
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed', 'processing', 'refunded')),
  failure_reason TEXT,
  failure_code VARCHAR(50),
  payment_method VARCHAR(50) DEFAULT 'upi',
  upi_transaction_ref VARCHAR(100),
  payment_date TIMESTAMP,
  retry_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for autopay_payments
CREATE INDEX IF NOT EXISTS idx_autopay_payments_subscription ON autopay_payments(merchant_subscription_id);
CREATE INDEX IF NOT EXISTS idx_autopay_payments_user ON autopay_payments(user_id);
CREATE INDEX IF NOT EXISTS idx_autopay_payments_payment_id ON autopay_payments(payment_id);
CREATE INDEX IF NOT EXISTS idx_autopay_payments_status ON autopay_payments(status);
CREATE INDEX IF NOT EXISTS idx_autopay_payments_date ON autopay_payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_autopay_payments_created ON autopay_payments(created_at);

-- Trigger for updated_at
CREATE TRIGGER update_autopay_payments_updated_at
  BEFORE UPDATE ON autopay_payments
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- RLS Policy for autopay_payments
ALTER TABLE autopay_payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their payment history"
  ON autopay_payments FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "Service can insert payments"
  ON autopay_payments FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Service can update payments"
  ON autopay_payments FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());
