-- Users and Workspaces tables with RLS
-- Migration: 20240101_users_workspaces.sql

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,

    -- Subscription
    subscription_tier TEXT DEFAULT 'free' CHECK (
        subscription_tier IN ('free', 'starter', 'growth', 'enterprise')
    ),

    -- Budget
    budget_limit_monthly DECIMAL(10,4) DEFAULT 1.00,

    -- Onboarding
    onboarding_completed_at TIMESTAMPTZ,

    -- Preferences
    preferences JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workspaces table (multi-tenant isolation)
CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    slug TEXT UNIQUE,

    -- Settings
    settings JSONB DEFAULT '{
        "timezone": "Asia/Kolkata",
        "currency": "INR",
        "language": "en"
    }',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_workspaces_user ON workspaces(user_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON workspaces(slug);

-- Enable RLS on both tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER workspaces_updated_at
    BEFORE UPDATE ON public.workspaces
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Auto-create user profile on signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email)
    VALUES (NEW.id, NEW.email);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- CREATE TRIGGER on_auth_user_created
--    AFTER INSERT ON auth.users
--    FOR EACH ROW
--    EXECUTE FUNCTION handle_new_user();

-- Auto-create workspace for new user
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
        CONCAT(SPLIT_PART(NEW.email, '@', 1), '''s Workspace'),
        CONCAT('ws-', LEFT(workspace_uuid::TEXT, 8))
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_user_created_workspace
    AFTER INSERT ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user_workspace();
