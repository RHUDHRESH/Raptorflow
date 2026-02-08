-- RaptorFlow Canonical Schema v3.0
-- Scorched earth rebuild: 12 lean tables, workspace_id everywhere
-- Date: 2026-02-08

-- =====================================
-- 1. EXTENSIONS
-- =====================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================
-- 2. WORKSPACES
-- =====================================
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 3. WORKSPACE MEMBERS
-- =====================================
CREATE TABLE workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(workspace_id, user_id)
);

CREATE INDEX idx_workspace_members_workspace ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id);

-- =====================================
-- 4. PROFILES
-- =====================================
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    phone TEXT,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    subscription_plan TEXT DEFAULT 'free',
    subscription_status TEXT DEFAULT 'none',
    onboarding_status TEXT DEFAULT 'pending',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_profiles_workspace ON profiles(workspace_id);
CREATE INDEX idx_profiles_email ON profiles(email);

-- =====================================
-- 5. FOUNDATIONS (Business context from onboarding)
-- =====================================
CREATE TABLE foundations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    company_info JSONB DEFAULT '{}',
    mission TEXT,
    vision TEXT,
    value_proposition TEXT,
    brand_voice JSONB DEFAULT '{}',
    messaging JSONB DEFAULT '{}',
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(workspace_id)
);

CREATE INDEX idx_foundations_workspace ON foundations(workspace_id);

-- =====================================
-- 6. BUSINESS CONTEXT MANIFESTS (BCM)
-- =====================================
CREATE TABLE business_context_manifests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    manifest JSONB NOT NULL,
    source_context JSONB,
    checksum TEXT NOT NULL,
    token_estimate INTEGER,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(workspace_id, version)
);

CREATE INDEX idx_bcm_workspace_version ON business_context_manifests(workspace_id, version DESC);

-- =====================================
-- 7. ICP PROFILES
-- =====================================
CREATE TABLE icp_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    demographics JSONB DEFAULT '{}',
    psychographics JSONB DEFAULT '{}',
    pain_points JSONB DEFAULT '[]',
    goals JSONB DEFAULT '[]',
    objections JSONB DEFAULT '[]',
    market_sophistication INTEGER DEFAULT 3 CHECK (market_sophistication >= 1 AND market_sophistication <= 5),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_icp_profiles_workspace ON icp_profiles(workspace_id);

-- =====================================
-- 8. CAMPAIGNS
-- =====================================
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    objective TEXT DEFAULT 'acquire' CHECK (objective IN ('acquire', 'convert', 'launch', 'proof', 'retain', 'reposition')),
    status TEXT DEFAULT 'planned' CHECK (status IN ('planned', 'active', 'paused', 'wrapup', 'archived')),
    bcm_version INTEGER,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    budget_allocated NUMERIC DEFAULT 0,
    budget_spent NUMERIC DEFAULT 0,
    kpi_targets JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_campaigns_workspace ON campaigns(workspace_id);
CREATE INDEX idx_campaigns_status ON campaigns(workspace_id, status);

-- =====================================
-- 9. MOVES
-- =====================================
CREATE TABLE moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    goal TEXT DEFAULT 'leads' CHECK (goal IN ('leads', 'calls', 'sales', 'proof', 'distribution', 'activation')),
    channel TEXT DEFAULT 'email' CHECK (channel IN ('linkedin', 'email', 'instagram', 'whatsapp', 'cold_dms', 'partnerships', 'twitter')),
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'queued', 'active', 'completed', 'abandoned')),
    priority INTEGER DEFAULT 3 CHECK (priority >= 1 AND priority <= 5),
    icp_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,
    bcm_version INTEGER,
    duration_days INTEGER DEFAULT 7,
    start_date TIMESTAMPTZ,
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    hypothesis TEXT,
    action_steps TEXT[] DEFAULT '{}',
    execution_result JSONB DEFAULT '{}',
    tool_requirements JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_moves_workspace ON moves(workspace_id);
CREATE INDEX idx_moves_status ON moves(workspace_id, status);
CREATE INDEX idx_moves_campaign ON moves(campaign_id);

-- =====================================
-- 10. SUBSCRIPTION PLANS
-- =====================================
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    description TEXT,
    price_monthly INTEGER DEFAULT 0,
    price_annual INTEGER DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'INR',
    features JSONB DEFAULT '{}',
    limits JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 11. SUBSCRIPTIONS
-- =====================================
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES subscription_plans(id),
    plan_name TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'past_due', 'trialing')),
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);

-- =====================================
-- 12. AUDIT LOGS
-- =====================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    actor_id UUID,
    action TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    changes JSONB DEFAULT '{}',
    status TEXT DEFAULT 'success',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_audit_logs_workspace ON audit_logs(workspace_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- =====================================
-- 13. SEED DEFAULT SUBSCRIPTION PLANS
-- =====================================
INSERT INTO subscription_plans (name, slug, display_name, description, price_monthly, price_annual, features, limits, is_active, sort_order) VALUES
('Free', 'free', 'Free Plan', 'Get started with basic features', 0, 0, '{"campaigns": true, "moves": true, "muse": true, "foundation": true}', '{"campaigns_per_month": 5, "moves_per_month": 20, "muse_generations": 50}', true, 0),
('Starter', 'starter', 'Starter Plan', 'For growing businesses', 99900, 999000, '{"campaigns": true, "moves": true, "muse": true, "foundation": true, "analytics": true}', '{"campaigns_per_month": 20, "moves_per_month": 100, "muse_generations": 500}', true, 1),
('Growth', 'growth', 'Growth Plan', 'For scaling teams', 249900, 2499000, '{"campaigns": true, "moves": true, "muse": true, "foundation": true, "analytics": true, "advanced_ai": true}', '{"campaigns_per_month": 50, "moves_per_month": 500, "muse_generations": 2000}', true, 2),
('Enterprise', 'enterprise', 'Enterprise Plan', 'Custom solutions for large organizations', 0, 0, '{"campaigns": true, "moves": true, "muse": true, "foundation": true, "analytics": true, "advanced_ai": true, "custom_integrations": true}', '{"campaigns_per_month": -1, "moves_per_month": -1, "muse_generations": -1}', true, 3);

-- =====================================
-- 14. RLS POLICIES (permissive for reconstruction mode)
-- =====================================
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundations ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_context_manifests ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE moves ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS, so these policies are for anon/authenticated access
CREATE POLICY "Allow all for service role" ON workspaces FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON workspace_members FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON profiles FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON foundations FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON business_context_manifests FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON icp_profiles FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON campaigns FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON moves FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON subscription_plans FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON subscriptions FOR ALL USING (true);
CREATE POLICY "Allow all for service role" ON audit_logs FOR ALL USING (true);
