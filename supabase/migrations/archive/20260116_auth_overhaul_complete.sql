-- ============================================================================
-- RAPTORFLOW AUTHENTICATION OVERHAUL - COMPLETE MIGRATION
-- Migration: 20260116_auth_overhaul_complete.sql
--
-- This migration:
-- 1. Updates subscription pricing to ₹5000/₹7000/₹10000
-- 2. Fixes RLS policies for proper workspace isolation
-- 3. Adds missing auth-related columns and constraints
-- 4. Creates proper rate limiting infrastructure
-- ============================================================================

-- ============================================================================
-- PART 1: UPDATE SUBSCRIPTION PRICING
-- Ascent: ₹5,000/month, Glide: ₹7,000/month, Soar: ₹10,000/month
-- ============================================================================

-- Update Ascent pricing
UPDATE subscription_plans SET
    price_monthly = 500000,    -- ₹5,000 in paise
    price_annual = 5000000,    -- ₹50,000 in paise (2 months free)
    description = 'For founders just getting started with systematic marketing.',
    features = '["Foundation setup (ICP + Positioning)", "Weekly Moves (3 per week)", "Basic Muse AI generation", "Matrix analytics dashboard", "3 Active Campaigns", "3 ICPs", "5GB Storage", "Email support"]'::jsonb,
    limits = '{"moves_per_week": 3, "campaigns": 3, "icps": 3, "team_seats": 1, "storage_gb": 5, "api_calls_per_hour": 100, "ai_generations_per_day": 10, "file_upload_mb": 50, "muse_ai_basic": true, "api_access": false, "priority_support": false}'::jsonb,
    updated_at = NOW()
WHERE slug = 'ascent';

-- Update Glide pricing
UPDATE subscription_plans SET
    price_monthly = 700000,    -- ₹7,000 in paise
    price_annual = 7000000,    -- ₹70,000 in paise (2 months free)
    description = 'For founders scaling their marketing engine.',
    features = '["Everything in Ascent", "Unlimited Moves", "Advanced Muse (voice training)", "Cohort segmentation", "Campaign planning tools", "Priority support", "Blackbox learnings vault", "10 ICPs", "25GB Storage", "5 Team Seats"]'::jsonb,
    limits = '{"moves_per_week": -1, "campaigns": -1, "icps": 10, "team_seats": 5, "storage_gb": 25, "api_calls_per_hour": 500, "ai_generations_per_day": 50, "file_upload_mb": 200, "muse_ai_advanced": true, "api_access": false, "priority_support": true}'::jsonb,
    updated_at = NOW()
WHERE slug = 'glide';

-- Update Soar pricing
UPDATE subscription_plans SET
    price_monthly = 1000000,   -- ₹10,000 in paise
    price_annual = 10000000,   -- ₹100,000 in paise (2 months free)
    description = 'For teams running multi-channel campaigns.',
    features = '["Everything in Glide", "Unlimited Team seats", "White-label exports", "Custom AI training", "Full API access", "Dedicated success manager", "Custom integrations", "Unlimited ICPs", "100GB Storage"]'::jsonb,
    limits = '{"moves_per_week": -1, "campaigns": -1, "icps": -1, "team_seats": -1, "storage_gb": 100, "api_calls_per_hour": 2000, "ai_generations_per_day": -1, "file_upload_mb": 500, "muse_ai_custom": true, "api_access": true, "white_label": true, "priority_support": true}'::jsonb,
    updated_at = NOW()
WHERE slug = 'soar';

-- ============================================================================
-- PART 2: ADD MISSING COLUMNS TO USERS TABLE
-- ============================================================================

-- Add auth_user_id if not exists (links to auth.users)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'users'
                   AND column_name = 'auth_user_id') THEN
        ALTER TABLE public.users ADD COLUMN auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
        -- Populate for existing users (where id = auth.users.id)
        UPDATE public.users SET auth_user_id = id WHERE auth_user_id IS NULL;
    END IF;
END $$;

-- Add role column for admin access
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'users'
                   AND column_name = 'role') THEN
        ALTER TABLE public.users ADD COLUMN role TEXT DEFAULT 'user'
            CHECK (role IN ('user', 'admin', 'super_admin'));
    END IF;
END $$;

-- Add account status columns
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'users'
                   AND column_name = 'is_active') THEN
        ALTER TABLE public.users ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'users'
                   AND column_name = 'is_banned') THEN
        ALTER TABLE public.users ADD COLUMN is_banned BOOLEAN DEFAULT false;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'users'
                   AND column_name = 'ban_reason') THEN
        ALTER TABLE public.users ADD COLUMN ban_reason TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'users'
                   AND column_name = 'banned_at') THEN
        ALTER TABLE public.users ADD COLUMN banned_at TIMESTAMPTZ;
    END IF;
END $$;

-- Add onboarding status column
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'users'
                   AND column_name = 'onboarding_status') THEN
        ALTER TABLE public.users ADD COLUMN onboarding_status TEXT DEFAULT 'pending'
            CHECK (onboarding_status IN ('pending', 'in_progress', 'active', 'skipped'));
    END IF;
END $$;

-- Add workspace_id column for quick reference
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'users'
                   AND column_name = 'default_workspace_id') THEN
        ALTER TABLE public.users ADD COLUMN default_workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL;
    END IF;
END $$;

-- Add phone number for SMS MFA
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_schema = 'public'
                   AND table_name = 'users'
                   AND column_name = 'phone') THEN
        ALTER TABLE public.users ADD COLUMN phone TEXT;
    END IF;
END $$;

-- ============================================================================
-- PART 3: CREATE HELPER FUNCTION FOR WORKSPACE ACCESS
-- ============================================================================

-- Drop and recreate function to get user's workspace IDs
DROP FUNCTION IF EXISTS get_user_workspace_ids();
CREATE OR REPLACE FUNCTION get_user_workspace_ids()
RETURNS SETOF UUID AS $$
    SELECT id FROM workspaces WHERE user_id = auth.uid();
$$ LANGUAGE SQL SECURITY DEFINER STABLE;

-- Function to check if user owns a workspace
DROP FUNCTION IF EXISTS user_owns_workspace(UUID);
CREATE OR REPLACE FUNCTION user_owns_workspace(workspace_uuid UUID)
RETURNS BOOLEAN AS $$
    SELECT EXISTS (
        SELECT 1 FROM workspaces
        WHERE id = workspace_uuid AND user_id = auth.uid()
    );
$$ LANGUAGE SQL SECURITY DEFINER STABLE;

-- ============================================================================
-- PART 4: FIX RLS POLICIES - USERS TABLE
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "users_select_own" ON public.users;
DROP POLICY IF EXISTS "users_update_own" ON public.users;
DROP POLICY IF EXISTS "users_insert_own" ON public.users;

-- Enable RLS
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Users can view their own profile (using auth.uid() which returns auth.users.id)
CREATE POLICY "users_select_own" ON public.users
    FOR SELECT USING (id = auth.uid() OR auth_user_id = auth.uid());

-- Users can update their own profile
CREATE POLICY "users_update_own" ON public.users
    FOR UPDATE USING (id = auth.uid() OR auth_user_id = auth.uid());

-- Allow service role to insert (for triggers)
CREATE POLICY "users_service_insert" ON public.users
    FOR INSERT WITH CHECK (true);

-- ============================================================================
-- PART 5: FIX RLS POLICIES - WORKSPACES TABLE
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "workspace_select" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_select_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_update_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_insert_own" ON public.workspaces;
DROP POLICY IF EXISTS "workspaces_delete_own" ON public.workspaces;

-- Enable RLS
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

-- Users can view their own workspaces
CREATE POLICY "workspaces_select_own" ON public.workspaces
    FOR SELECT USING (user_id = auth.uid());

-- Users can update their own workspaces
CREATE POLICY "workspaces_update_own" ON public.workspaces
    FOR UPDATE USING (user_id = auth.uid());

-- Users can create workspaces for themselves
CREATE POLICY "workspaces_insert_own" ON public.workspaces
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- Users can delete their own workspaces
CREATE POLICY "workspaces_delete_own" ON public.workspaces
    FOR DELETE USING (user_id = auth.uid());

-- ============================================================================
-- PART 6: FIX RLS POLICIES - ALL WORKSPACE-SCOPED TABLES
-- ============================================================================

-- Helper macro for creating workspace-scoped policies
-- We'll apply to each table that has workspace_id

-- ICP Profiles
DROP POLICY IF EXISTS "icp_workspace_isolation" ON public.icp_profiles;
DROP POLICY IF EXISTS "icp_profiles_select" ON public.icp_profiles;
DROP POLICY IF EXISTS "icp_profiles_insert" ON public.icp_profiles;
DROP POLICY IF EXISTS "icp_profiles_update" ON public.icp_profiles;
DROP POLICY IF EXISTS "icp_profiles_delete" ON public.icp_profiles;

DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'icp_profiles') THEN
        ALTER TABLE public.icp_profiles ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "icp_profiles_select" ON public.icp_profiles
            FOR SELECT USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "icp_profiles_insert" ON public.icp_profiles
            FOR INSERT WITH CHECK (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "icp_profiles_update" ON public.icp_profiles
            FOR UPDATE USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "icp_profiles_delete" ON public.icp_profiles
            FOR DELETE USING (workspace_id IN (SELECT get_user_workspace_ids()));
    END IF;
END $$;

-- Campaigns
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'campaigns') THEN
        DROP POLICY IF EXISTS "campaigns_select" ON public.campaigns;
        DROP POLICY IF EXISTS "campaigns_insert" ON public.campaigns;
        DROP POLICY IF EXISTS "campaigns_update" ON public.campaigns;
        DROP POLICY IF EXISTS "campaigns_delete" ON public.campaigns;

        ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "campaigns_select" ON public.campaigns
            FOR SELECT USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "campaigns_insert" ON public.campaigns
            FOR INSERT WITH CHECK (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "campaigns_update" ON public.campaigns
            FOR UPDATE USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "campaigns_delete" ON public.campaigns
            FOR DELETE USING (workspace_id IN (SELECT get_user_workspace_ids()));
    END IF;
END $$;

-- Moves
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'moves') THEN
        DROP POLICY IF EXISTS "moves_select" ON public.moves;
        DROP POLICY IF EXISTS "moves_insert" ON public.moves;
        DROP POLICY IF EXISTS "moves_update" ON public.moves;
        DROP POLICY IF EXISTS "moves_delete" ON public.moves;

        ALTER TABLE public.moves ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "moves_select" ON public.moves
            FOR SELECT USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "moves_insert" ON public.moves
            FOR INSERT WITH CHECK (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "moves_update" ON public.moves
            FOR UPDATE USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "moves_delete" ON public.moves
            FOR DELETE USING (workspace_id IN (SELECT get_user_workspace_ids()));
    END IF;
END $$;

-- Muse Assets
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'muse_assets') THEN
        DROP POLICY IF EXISTS "muse_assets_select" ON public.muse_assets;
        DROP POLICY IF EXISTS "muse_assets_insert" ON public.muse_assets;
        DROP POLICY IF EXISTS "muse_assets_update" ON public.muse_assets;
        DROP POLICY IF EXISTS "muse_assets_delete" ON public.muse_assets;

        ALTER TABLE public.muse_assets ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "muse_assets_select" ON public.muse_assets
            FOR SELECT USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "muse_assets_insert" ON public.muse_assets
            FOR INSERT WITH CHECK (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "muse_assets_update" ON public.muse_assets
            FOR UPDATE USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "muse_assets_delete" ON public.muse_assets
            FOR DELETE USING (workspace_id IN (SELECT get_user_workspace_ids()));
    END IF;
END $$;

-- Blackbox Strategies
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'blackbox_strategies') THEN
        DROP POLICY IF EXISTS "blackbox_strategies_select" ON public.blackbox_strategies;
        DROP POLICY IF EXISTS "blackbox_strategies_insert" ON public.blackbox_strategies;
        DROP POLICY IF EXISTS "blackbox_strategies_update" ON public.blackbox_strategies;
        DROP POLICY IF EXISTS "blackbox_strategies_delete" ON public.blackbox_strategies;

        ALTER TABLE public.blackbox_strategies ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "blackbox_strategies_select" ON public.blackbox_strategies
            FOR SELECT USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "blackbox_strategies_insert" ON public.blackbox_strategies
            FOR INSERT WITH CHECK (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "blackbox_strategies_update" ON public.blackbox_strategies
            FOR UPDATE USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "blackbox_strategies_delete" ON public.blackbox_strategies
            FOR DELETE USING (workspace_id IN (SELECT get_user_workspace_ids()));
    END IF;
END $$;

-- Foundations
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'foundations') THEN
        DROP POLICY IF EXISTS "foundations_select" ON public.foundations;
        DROP POLICY IF EXISTS "foundations_insert" ON public.foundations;
        DROP POLICY IF EXISTS "foundations_update" ON public.foundations;
        DROP POLICY IF EXISTS "foundations_delete" ON public.foundations;

        ALTER TABLE public.foundations ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "foundations_select" ON public.foundations
            FOR SELECT USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "foundations_insert" ON public.foundations
            FOR INSERT WITH CHECK (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "foundations_update" ON public.foundations
            FOR UPDATE USING (workspace_id IN (SELECT get_user_workspace_ids()));
        CREATE POLICY "foundations_delete" ON public.foundations
            FOR DELETE USING (workspace_id IN (SELECT get_user_workspace_ids()));
    END IF;
END $$;

-- ============================================================================
-- PART 7: CREATE RATE LIMITING TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Rate limit tracking
    endpoint TEXT NOT NULL,
    request_count INTEGER DEFAULT 1,
    window_start TIMESTAMPTZ DEFAULT NOW(),
    window_duration_seconds INTEGER DEFAULT 3600, -- 1 hour default

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, endpoint, window_start)
);

CREATE INDEX IF NOT EXISTS idx_rate_limits_user_endpoint ON public.rate_limits(user_id, endpoint);
CREATE INDEX IF NOT EXISTS idx_rate_limits_window ON public.rate_limits(window_start);

ALTER TABLE public.rate_limits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "rate_limits_select_own" ON public.rate_limits
    FOR SELECT USING (user_id = auth.uid());

-- Function to check rate limit
CREATE OR REPLACE FUNCTION check_rate_limit(
    p_user_id UUID,
    p_endpoint TEXT,
    p_limit INTEGER,
    p_window_seconds INTEGER DEFAULT 3600
) RETURNS BOOLEAN AS $$
DECLARE
    current_count INTEGER;
    window_start_time TIMESTAMPTZ;
BEGIN
    -- Calculate window start (truncate to window boundary)
    window_start_time := date_trunc('hour', NOW());

    -- Get or create rate limit record
    INSERT INTO rate_limits (user_id, endpoint, request_count, window_start, window_duration_seconds)
    VALUES (p_user_id, p_endpoint, 1, window_start_time, p_window_seconds)
    ON CONFLICT (user_id, endpoint, window_start)
    DO UPDATE SET
        request_count = rate_limits.request_count + 1,
        updated_at = NOW()
    RETURNING request_count INTO current_count;

    -- Check if within limit
    RETURN current_count <= p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- PART 8: CREATE USER SESSIONS TABLE FOR SECURITY TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Session details
    session_token TEXT UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    device_fingerprint TEXT,

    -- Status
    is_active BOOLEAN DEFAULT true,
    last_active_at TIMESTAMPTZ DEFAULT NOW(),

    -- Expiration
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,

    -- Revocation
    revoked_at TIMESTAMPTZ,
    revoked_reason TEXT CHECK (revoked_reason IN ('manual_logout', 'security_concern', 'password_changed', 'admin_action', 'expired', 'revoke_all'))
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON public.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON public.user_sessions(is_active) WHERE is_active = true;

ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_sessions_select_own" ON public.user_sessions
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "user_sessions_insert_own" ON public.user_sessions
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "user_sessions_update_own" ON public.user_sessions
    FOR UPDATE USING (user_id = auth.uid());

-- ============================================================================
-- PART 9: UPDATE TRIGGERS FOR USER CREATION
-- ============================================================================

-- Update the handle_new_user function to set auth_user_id
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, auth_user_id, email, full_name, role, is_active, onboarding_status)
    VALUES (
        NEW.id,
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', SPLIT_PART(NEW.email, '@', 1)),
        'user',
        true,
        'pending'
    )
    ON CONFLICT (id) DO UPDATE SET
        email = EXCLUDED.email,
        auth_user_id = EXCLUDED.auth_user_id,
        updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Update workspace creation to link to user
CREATE OR REPLACE FUNCTION handle_new_user_workspace()
RETURNS TRIGGER AS $$
DECLARE
    workspace_uuid UUID;
BEGIN
    workspace_uuid := gen_random_uuid();

    INSERT INTO public.workspaces (id, user_id, name, slug)
    VALUES (
        workspace_uuid,
        NEW.id,
        CONCAT(COALESCE(NEW.full_name, SPLIT_PART(NEW.email, '@', 1)), '''s Workspace'),
        CONCAT('ws-', LEFT(workspace_uuid::TEXT, 8))
    );

    -- Update user's default workspace
    UPDATE public.users
    SET default_workspace_id = workspace_uuid
    WHERE id = NEW.id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- PART 10: AUDIT LOG ENTRY
-- ============================================================================

INSERT INTO audit_logs (
    action,
    action_category,
    description,
    details,
    success,
    created_at
) VALUES (
    'AUTH_OVERHAUL_MIGRATION',
    'security',
    'Complete authentication system overhaul applied',
    jsonb_build_object(
        'migration', '20260116_auth_overhaul_complete.sql',
        'pricing_updated', true,
        'rls_policies_fixed', true,
        'new_tables', ARRAY['rate_limits', 'user_sessions'],
        'ascent_price', 5000,
        'glide_price', 7000,
        'soar_price', 10000
    ),
    true,
    NOW()
);

-- ============================================================================
-- VERIFICATION QUERIES (Run manually to verify)
-- ============================================================================

-- Verify pricing
-- SELECT name, price_monthly/100 as price_inr FROM subscription_plans;

-- Verify RLS is enabled
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('users', 'workspaces', 'icp_profiles', 'campaigns');

-- Verify policies exist
-- SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public';
