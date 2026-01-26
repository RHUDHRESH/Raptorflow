-- =============================================================================
-- RAPTORFLOW CONSOLIDATED AUTH SCHEMA
-- Migration: 20240125_consolidated_auth_schema.sql
-- Purpose: Ensure all auth-related tables are consistent and complete
-- =============================================================================

-- =============================================================================
-- 1. PLANS TABLE (Pricing Tiers)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,

    -- Pricing (in paise for INR)
    monthly_price INTEGER NOT NULL DEFAULT 0,
    yearly_price INTEGER NOT NULL DEFAULT 0,

    -- Limits
    max_icp_profiles INTEGER DEFAULT 3,
    max_campaigns INTEGER DEFAULT 5,
    max_team_members INTEGER DEFAULT 1,
    max_devices INTEGER DEFAULT 2,

    -- Features (JSON for flexibility)
    features JSONB DEFAULT '{}',

    -- Metadata
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default plans if not exists
INSERT INTO public.plans (name, slug, description, monthly_price, yearly_price, max_icp_profiles, max_campaigns, max_team_members, max_devices, features, sort_order)
VALUES
    ('Soar', 'soar', 'Perfect for solo founders getting started', 249900, 2499000, 3, 5, 1, 2,
     '{"ai_muse": true, "basic_analytics": true, "email_support": true}', 1),
    ('Glide', 'glide', 'For growing teams with scaling needs', 699900, 6999000, 10, 20, 5, 5,
     '{"ai_muse": true, "advanced_analytics": true, "priority_support": true, "team_collaboration": true}', 2),
    ('Ascent', 'ascent', 'Enterprise-grade for serious operations', 2499900, 24999000, 999, 999, 25, 10,
     '{"ai_muse": true, "enterprise_analytics": true, "dedicated_support": true, "team_collaboration": true, "custom_integrations": true, "sla": true}', 3)
ON CONFLICT (slug) DO NOTHING;

-- =============================================================================
-- 2. USER SESSIONS TABLE (Multi-device tracking)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE SET NULL,

    -- Session info
    session_token TEXT UNIQUE NOT NULL,
    refresh_token TEXT,

    -- Device info
    device_name TEXT,
    device_type TEXT, -- 'desktop', 'mobile', 'tablet'
    ip_address INET,
    user_agent TEXT,

    -- Location (optional)
    country TEXT,
    city TEXT,

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(user_id, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);

-- RLS
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own sessions" ON user_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- =============================================================================
-- 3. SUBSCRIPTIONS TABLE (Enhanced if not exists)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,

    -- Plan info
    plan TEXT NOT NULL CHECK (plan IN ('trial', 'soar', 'glide', 'ascent')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'trial', 'active', 'cancelled', 'expired', 'past_due')),

    -- Billing
    amount INTEGER DEFAULT 0, -- in paise
    billing_interval TEXT DEFAULT 'monthly' CHECK (billing_interval IN ('monthly', 'yearly')),

    -- Trial
    is_trial BOOLEAN DEFAULT false,
    trial_ends_at TIMESTAMPTZ,

    -- Period
    current_period_start TIMESTAMPTZ DEFAULT NOW(),
    current_period_end TIMESTAMPTZ,

    -- Payment info
    payment_method TEXT,
    last_payment_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, workspace_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_workspace ON subscriptions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

-- RLS
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own subscriptions" ON subscriptions
    FOR SELECT USING (auth.uid() = user_id);

-- =============================================================================
-- 4. ADD MISSING COLUMNS TO USERS TABLE
-- =============================================================================
DO $$
BEGIN
    -- Add auth_id if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'auth_id') THEN
        ALTER TABLE public.users ADD COLUMN auth_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;

    -- Add subscription tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'subscription_plan') THEN
        ALTER TABLE public.users ADD COLUMN subscription_plan TEXT DEFAULT 'trial';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'subscription_status') THEN
        ALTER TABLE public.users ADD COLUMN subscription_status TEXT DEFAULT 'none';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'trial_expires_at') THEN
        ALTER TABLE public.users ADD COLUMN trial_expires_at TIMESTAMPTZ;
    END IF;

    -- Add onboarding tracking
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'has_completed_onboarding') THEN
        ALTER TABLE public.users ADD COLUMN has_completed_onboarding BOOLEAN DEFAULT false;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'onboarding_step') THEN
        ALTER TABLE public.users ADD COLUMN onboarding_step TEXT DEFAULT 'welcome';
    END IF;

    -- Add last login
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'last_login_at') THEN
        ALTER TABLE public.users ADD COLUMN last_login_at TIMESTAMPTZ;
    END IF;

    -- Add metadata
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'metadata') THEN
        ALTER TABLE public.users ADD COLUMN metadata JSONB DEFAULT '{}';
    END IF;
END
$$;

-- =============================================================================
-- 5. ADD WORKSPACE MEMBERS TABLE (if not exists)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,

    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),

    invited_by UUID REFERENCES public.users(id),
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(workspace_id, user_id)
);

-- RLS
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view workspace members" ON workspace_members
    FOR SELECT USING (
        user_id = (SELECT id FROM public.users WHERE auth_id = auth.uid())
        OR workspace_id IN (
            SELECT workspace_id FROM workspace_members
            WHERE user_id = (SELECT id FROM public.users WHERE auth_id = auth.uid())
        )
    );

-- =============================================================================
-- 6. UPDATE TRIGGERS
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to plans
DROP TRIGGER IF EXISTS plans_updated_at ON public.plans;
CREATE TRIGGER plans_updated_at
    BEFORE UPDATE ON public.plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply to subscriptions
DROP TRIGGER IF EXISTS subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 7. CLEANUP FUNCTION FOR EXPIRED SESSIONS
-- =============================================================================
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.user_sessions
    WHERE expires_at < NOW() OR (is_active = false AND last_activity_at < NOW() - INTERVAL '7 days');

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 8. FUNCTION TO GET USER ACTIVE SESSIONS COUNT
-- =============================================================================
CREATE OR REPLACE FUNCTION get_user_active_sessions_count(p_user_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)::INTEGER
        FROM public.user_sessions
        WHERE user_id = p_user_id
        AND is_active = true
        AND expires_at > NOW()
    );
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 9. FUNCTION TO GET USER'S MAX ALLOWED DEVICES
-- =============================================================================
CREATE OR REPLACE FUNCTION get_user_max_devices(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    user_plan TEXT;
    max_devices INTEGER;
BEGIN
    -- Get user's current plan
    SELECT subscription_plan INTO user_plan
    FROM public.users
    WHERE id = p_user_id OR auth_id = p_user_id;

    -- Get plan's max devices
    SELECT p.max_devices INTO max_devices
    FROM public.plans p
    WHERE p.slug = user_plan;

    -- Default to 2 if not found
    RETURN COALESCE(max_devices, 2);
END;
$$ LANGUAGE plpgsql;
