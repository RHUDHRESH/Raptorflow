-- Initial Database Schema for Authentication & Onboarding System
-- This creates all necessary tables with proper constraints and indexes

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE onboarding_status AS ENUM (
  'pending_workspace',
  'pending_storage', 
  'pending_plan_selection',
  'pending_payment',
  'active',
  'suspended',
  'cancelled'
);

CREATE TYPE subscription_status AS ENUM (
  'pending',
  'active',
  'past_due',
  'cancelled',
  'expired'
);

CREATE TYPE billing_cycle AS ENUM (
  'monthly',
  'yearly'
);

-- Users table - Core user information
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  phone TEXT,
  
  -- Onboarding state (THIS IS THE SOURCE OF TRUTH)
  onboarding_status onboarding_status NOT NULL DEFAULT 'pending_workspace',
  
  -- User role and permissions
  role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'super_admin', 'support', 'billing_admin')),
  
  -- Account status
  is_active BOOLEAN DEFAULT true,
  is_banned BOOLEAN DEFAULT false,
  ban_reason TEXT,
  banned_at TIMESTAMPTZ,
  banned_by UUID REFERENCES users(id),
  
  -- Admin notes
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_login_at TIMESTAMPTZ
);

-- Workspaces table - One per user
CREATE TABLE workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  
  -- GCS Storage information
  gcs_bucket_name TEXT,
  gcs_folder_path TEXT,
  storage_quota_bytes BIGINT DEFAULT 5368709120, -- 5GB default
  storage_used_bytes BIGINT DEFAULT 0,
  
  -- Status
  status TEXT NOT NULL DEFAULT 'provisioning' CHECK (status IN ('provisioning', 'active', 'suspended', 'deleted')),
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Plans table - Available subscription plans
CREATE TABLE plans (
  id TEXT PRIMARY KEY, -- 'starter', 'pro', 'enterprise'
  name TEXT NOT NULL,
  description TEXT,
  price_monthly_paise INTEGER NOT NULL,
  price_yearly_paise INTEGER NOT NULL,
  
  -- Features (JSON for flexibility)
  features JSONB NOT NULL DEFAULT '{}',
  
  -- Limits
  storage_limit_bytes BIGINT NOT NULL,
  api_calls_limit INTEGER,
  projects_limit INTEGER,
  team_members_limit INTEGER,
  
  -- Display settings
  is_active BOOLEAN DEFAULT TRUE,
  display_order INTEGER DEFAULT 0,
  popular BOOLEAN DEFAULT FALSE,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscriptions table - User subscription information
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Plan details
  plan_id TEXT NOT NULL REFERENCES plans(id),
  plan_name TEXT NOT NULL,
  price_monthly_paise INTEGER NOT NULL,
  
  -- Billing cycle
  billing_cycle billing_cycle NOT NULL DEFAULT 'monthly',
  
  -- PhonePe specific
  phonepe_subscription_id TEXT,
  phonepe_customer_id TEXT,
  phonepe_transaction_id TEXT,
  
  -- Status
  status subscription_status NOT NULL DEFAULT 'pending',
  
  -- Dates
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancelled_at TIMESTAMPTZ,
  trial_end TIMESTAMPTZ,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Payment transactions table - Track all payment attempts
CREATE TABLE payment_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  transaction_id TEXT UNIQUE NOT NULL, -- PhonePe transaction ID
  amount_paise INTEGER NOT NULL,
  currency TEXT DEFAULT 'INR',
  
  -- Related entities
  subscription_id UUID REFERENCES subscriptions(id) ON DELETE CASCADE,
  plan_id TEXT REFERENCES plans(id),
  billing_cycle billing_cycle,
  
  -- Status and details
  status TEXT NOT NULL DEFAULT 'initiated' CHECK (status IN (
    'initiated', 'pending', 'completed', 'failed', 'refunded', 'cancelled'
  )),
  
  -- PhonePe response
  phonepe_response JSONB,
  
  -- Refund information
  refund_amount_paise INTEGER DEFAULT 0,
  refund_id TEXT,
  refund_reason TEXT,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- User sessions table - Track active sessions
CREATE TABLE user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  session_token TEXT UNIQUE NOT NULL,
  
  -- Session details
  ip_address INET,
  user_agent TEXT,
  device_fingerprint TEXT,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  revoked_at TIMESTAMPTZ,
  revoked_reason TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL
);

-- Audit logs table - Track all important actions
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Actor information
  actor_id UUID REFERENCES users(id),
  actor_cin TEXT, -- Corporate Identification Number
  actor_role TEXT,
  
  -- Action details
  action TEXT NOT NULL,
  action_category TEXT NOT NULL DEFAULT 'user',
  description TEXT,
  
  -- Target information
  target_type TEXT,
  target_id UUID,
  target_cin TEXT,
  
  -- Changes
  changes JSONB,
  
  -- Status
  status TEXT DEFAULT 'success',
  error_message TEXT,
  
  -- Metadata
  ip_address INET,
  user_agent TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Admin actions table - Specific admin operations
CREATE TABLE admin_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Admin information
  admin_id UUID NOT NULL REFERENCES users(id),
  admin_cin TEXT,
  admin_email TEXT,
  
  -- Action details
  action_type TEXT NOT NULL,
  target_user_id UUID REFERENCES users(id),
  target_user_cin TEXT,
  target_user_email TEXT,
  
  -- Details
  description TEXT,
  reason TEXT,
  changes JSONB,
  
  -- Metadata
  ip_address INET,
  user_agent TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Security events table - Track security-related events
CREATE TABLE security_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Event details
  event_type TEXT NOT NULL,
  severity TEXT DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'critical')),
  
  -- User information
  user_id UUID REFERENCES users(id),
  user_cin TEXT,
  user_email TEXT,
  
  -- Event details
  description TEXT,
  details JSONB,
  
  -- Metadata
  ip_address INET,
  user_agent TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_auth_user_id ON users(auth_user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_onboarding_status ON users(onboarding_status);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);

CREATE INDEX idx_workspaces_user_id ON workspaces(user_id);
CREATE INDEX idx_workspaces_slug ON workspaces(slug);
CREATE INDEX idx_workspaces_status ON workspaces(status);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_plan_id ON subscriptions(plan_id);
CREATE INDEX idx_subscriptions_current_period_end ON subscriptions(current_period_end);

CREATE INDEX idx_payment_transactions_user_id ON payment_transactions(user_id);
CREATE INDEX idx_payment_transactions_transaction_id ON payment_transactions(transaction_id);
CREATE INDEX idx_payment_transactions_status ON payment_transactions(status);
CREATE INDEX idx_payment_transactions_created_at ON payment_transactions(created_at);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_session_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

CREATE INDEX idx_audit_logs_actor_id ON audit_logs(actor_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_target_id ON audit_logs(target_id);

CREATE INDEX idx_admin_actions_admin_id ON admin_actions(admin_id);
CREATE INDEX idx_admin_actions_target_user_id ON admin_actions(target_user_id);
CREATE INDEX idx_admin_actions_created_at ON admin_actions(created_at);

CREATE INDEX idx_security_events_user_id ON security_events(user_id);
CREATE INDEX idx_security_events_event_type ON security_events(event_type);
CREATE INDEX idx_security_events_created_at ON security_events(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON workspaces FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payment_transactions_updated_at BEFORE UPDATE ON payment_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to handle user creation from auth trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRigger AS $$
BEGIN
  INSERT INTO public.users (auth_user_id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to automatically create user record on signup
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create RLS policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth_user_id = auth.uid());
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth_user_id = auth.uid());
CREATE POLICY "Admins can view all users" ON users FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM users 
    WHERE auth_user_id = auth.uid() 
    AND role IN ('admin', 'super_admin', 'support', 'billing_admin')
  )
);
CREATE POLICY "Admins can update users" ON users FOR UPDATE USING (
  EXISTS (
    SELECT 1 FROM users 
    WHERE auth_user_id = auth.uid() 
    AND role IN ('admin', 'super_admin')
  )
);

-- Workspaces policies
CREATE POLICY "Users can view own workspace" ON workspaces FOR SELECT USING (
  user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
);
CREATE POLICY "Users can update own workspace" ON workspaces FOR UPDATE USING (
  user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

-- Subscriptions policies
CREATE POLICY "Users can view own subscription" ON subscriptions FOR SELECT USING (
  user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
);
CREATE POLICY "Admins can view all subscriptions" ON subscriptions FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM users 
    WHERE auth_user_id = auth.uid() 
    AND role IN ('admin', 'super_admin', 'billing_admin')
  )
);

-- Payment transactions policies
CREATE POLICY "Users can view own transactions" ON payment_transactions FOR SELECT USING (
  user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
);
CREATE POLICY "Admins can view all transactions" ON payment_transactions FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM users 
    WHERE auth_user_id = auth.uid() 
    AND role IN ('admin', 'super_admin', 'billing_admin')
  )
);

-- User sessions policies
CREATE POLICY "Users can manage own sessions" ON user_sessions FOR ALL USING (
  user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
);

-- Seed initial plans
INSERT INTO plans (id, name, description, price_monthly_paise, price_yearly_paise, storage_limit_bytes, features, api_calls_limit, projects_limit, team_members_limit, display_order) VALUES
('starter', 'Starter', 'Perfect for individuals and small projects', 49900, 499000, 5368709120, '{"projects": 3, "team_members": 1, "support": "email"}', 10000, 3, 1, 1),
('pro', 'Pro', 'For growing teams and businesses', 149900, 1499000, 53687091200, '{"projects": 10, "team_members": 5, "support": "priority", "analytics": true}', 100000, 10, 5, 2),
('enterprise', 'Enterprise', 'Custom solution for large organizations', 499900, 4999000, 107374182400, '{"projects": -1, "team_members": -1, "support": "24/7", "analytics": true, "custom": true}', -1, -1, -1, 3);

-- Update Pro plan to be popular
UPDATE plans SET popular = true WHERE id = 'pro';

-- Create helper functions
CREATE OR REPLACE FUNCTION get_user_by_auth_uid(uid UUID)
RETURNS TABLE (
  id UUID,
  email TEXT,
  full_name TEXT,
  onboarding_status onboarding_status,
  role TEXT,
  is_active BOOLEAN,
  is_banned BOOLEAN
) AS $$
BEGIN
  RETURN QUERY
  SELECT u.id, u.email, u.full_name, u.onboarding_status, u.role, u.is_active, u.is_banned
  FROM users u
  WHERE u.auth_user_id = get_current_uid();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
