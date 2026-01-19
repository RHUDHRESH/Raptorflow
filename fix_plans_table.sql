-- Fix for missing 'plans' table and data
-- Migration: 20260112_fix_plans_table.sql

-- 1. Create billing_cycle enum if not exists
DO $$ BEGIN
    CREATE TYPE billing_cycle AS ENUM (
      'monthly',
      'yearly'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Create Plans table
CREATE TABLE IF NOT EXISTS plans (
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

-- 3. Seed Data
INSERT INTO plans (id, name, description, price_monthly_paise, price_yearly_paise, storage_limit_bytes, features, api_calls_limit, projects_limit, team_members_limit, display_order) 
VALUES
('starter', 'Starter', 'Perfect for individuals and small projects', 500000, 5000000, 5368709120, '{"projects": 3, "team_members": 1, "support": "email"}', 10000, 3, 1, 1),
('pro', 'Pro', 'For growing teams and businesses', 700000, 7000000, 53687091200, '{"projects": 10, "team_members": 5, "support": "priority", "analytics": true}', 100000, 10, 5, 2),
('enterprise', 'Enterprise', 'Custom solution for large organizations', 1000000, 10000000, 107374182400, '{"projects": -1, "team_members": -1, "support": "24/7", "analytics": true, "custom": true}', -1, -1, -1, 3)
ON CONFLICT (id) DO UPDATE SET 
    price_monthly_paise = EXCLUDED.price_monthly_paise,
    price_yearly_paise = EXCLUDED.price_yearly_paise;

-- 4. Set Popular
UPDATE plans SET popular = true WHERE id = 'pro';

-- 5. Enable RLS and Policies
ALTER TABLE plans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public can view active plans" ON plans;
CREATE POLICY "Public can view active plans" ON plans FOR SELECT USING (is_active = true);
