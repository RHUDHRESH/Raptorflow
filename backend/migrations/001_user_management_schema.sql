-- RaptorFlow User Management Schema
-- Complete authentication, workspace, and subscription system

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- USERS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Auth fields (linked to Supabase auth.users)
    auth_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    
    -- Profile information
    full_name VARCHAR(255),
    avatar_url TEXT,
    
    -- Subscription information
    subscription_plan VARCHAR(50) DEFAULT 'none' CHECK (subscription_plan IN ('none', 'trial', 'soar', 'glide', 'ascent')),
    subscription_status VARCHAR(50) DEFAULT 'none' CHECK (subscription_status IN ('none', 'trial', 'active', 'cancelled', 'expired')),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    trial_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Onboarding status
    has_completed_onboarding BOOLEAN DEFAULT FALSE,
    onboarding_step VARCHAR(50) DEFAULT 'welcome',
    
    -- Account status
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- ==========================================
-- WORKSPACES TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Workspace information
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    
    -- Owner
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Subscription limits based on plan
    max_icp_profiles INTEGER DEFAULT 3,
    max_campaigns INTEGER DEFAULT 5,
    max_team_members INTEGER DEFAULT 1,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_trial BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- WORKSPACE MEMBERS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS workspace_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Relations
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Member details
    role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    permissions JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    invited_at TIMESTAMP WITH TIME ZONE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(workspace_id, user_id)
);

-- ==========================================
-- SUBSCRIPTIONS TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Relations
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    
    -- Subscription details
    plan VARCHAR(50) NOT NULL CHECK (plan IN ('trial', 'soar', 'glide', 'ascent')),
    status VARCHAR(50) NOT NULL DEFAULT 'trial' CHECK (status IN ('trial', 'active', 'cancelled', 'expired')),
    
    -- Billing
    amount INTEGER NOT NULL, -- in cents
    currency VARCHAR(3) DEFAULT 'USD',
    billing_interval VARCHAR(20) DEFAULT 'month' CHECK (billing_interval IN ('month', 'year')),
    
    -- Payment provider
    provider VARCHAR(50) DEFAULT 'stripe', -- stripe, phonepe, etc.
    provider_subscription_id VARCHAR(255),
    provider_customer_id VARCHAR(255),
    
    -- Trial information
    is_trial BOOLEAN DEFAULT TRUE,
    trial_ends_at TIMESTAMP WITH TIME ZONE,
    
    -- Subscription period
    current_period_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    current_period_end TIMESTAMP WITH TIME ZONE,
    
    -- Cancellation
    cancels_at TIMESTAMP WITH TIME ZONE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, workspace_id)
);

-- ==========================================
-- PLANS CONFIGURATION TABLE
-- ==========================================
CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Plan details
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    
    -- Pricing
    monthly_price INTEGER NOT NULL, -- in cents
    yearly_price INTEGER NOT NULL, -- in cents
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Features and limits
    max_icp_profiles INTEGER NOT NULL,
    max_campaigns INTEGER NOT NULL,
    max_team_members INTEGER NOT NULL,
    features JSONB DEFAULT '{}',
    
    -- Plan metadata
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- INDEXES
-- ==========================================
CREATE INDEX IF NOT EXISTS idx_users_auth_id ON users(auth_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON users(subscription_status);
CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON workspaces(slug);
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON workspace_members(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_workspace_id ON subscriptions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

-- ==========================================
-- TRIGGERS FOR UPDATED_AT
-- ==========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspace_members_updated_at BEFORE UPDATE ON workspace_members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plans_updated_at BEFORE UPDATE ON plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- INSERT DEFAULT PLANS
-- ==========================================
INSERT INTO plans (name, slug, description, monthly_price, yearly_price, max_icp_profiles, max_campaigns, max_team_members, features, sort_order) VALUES
('Trial', 'trial', 'Free trial with basic features', 0, 0, 3, 5, 1, '{"icp_generation": true, "basic_analytics": true, "email_support": false}', 0),
('Soar', 'soar', 'Perfect for getting started', 2900, 29000, 5, 10, 3, '{"icp_generation": true, "advanced_analytics": true, "email_support": true, "priority_support": false}', 1),
('Glide', 'glide', 'For growing businesses', 9900, 99000, 15, 25, 10, '{"icp_generation": true, "advanced_analytics": true, "email_support": true, "priority_support": true, "api_access": false}', 2),
('Ascent', 'ascent', 'Maximum power for enterprises', 29900, 299000, -1, -1, -1, '{"icp_generation": true, "advanced_analytics": true, "email_support": true, "priority_support": true, "api_access": true, "dedicated_support": true}', 3)
ON CONFLICT (slug) DO NOTHING;

-- ==========================================
-- RLS (ROW LEVEL SECURITY) POLICIES
-- ==========================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth_id = auth.uid());
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth_id = auth.uid());

-- Workspace members can view workspaces they belong to
CREATE POLICY "Workspace members can view workspace" ON workspaces FOR SELECT USING (
    id IN (
        SELECT workspace_id FROM workspace_members 
        WHERE user_id = (SELECT id FROM users WHERE auth_id = auth.uid())
    )
);

-- Users can view their workspace memberships
CREATE POLICY "Users can view own memberships" ON workspace_members FOR SELECT USING (
    user_id = (SELECT id FROM users WHERE auth_id = auth.uid())
);

-- Users can view their subscriptions
CREATE POLICY "Users can view own subscriptions" ON subscriptions FOR SELECT USING (
    user_id = (SELECT id FROM users WHERE auth_id = auth.uid())
);
