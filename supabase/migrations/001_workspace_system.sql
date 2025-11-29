-- =====================================================
-- RaptorFlow Workspace System Migration
-- =====================================================
-- Version: 001
-- Description: Creates workspace tables and RLS policies
-- Dependencies: Supabase Auth (auth.users)
--
-- This migration creates:
-- 1. profiles table - Extended user information
-- 2. workspace_role enum - Role types for workspace members
-- 3. workspaces table - Workspace/organization details
-- 4. workspace_members table - Workspace membership with roles
-- 5. workspace_invites table - Pending workspace invitations
-- 6. RLS policies for secure data access
-- 7. Triggers for auto-creation and cleanup
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. CREATE PROFILES TABLE
-- =====================================================
-- Extends Supabase auth.users with additional profile data

CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    avatar_url TEXT,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    onboarding_skipped BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- =====================================================
-- 2. CREATE WORKSPACE_ROLE ENUM
-- =====================================================
-- Defines roles for workspace members

DO $$ BEGIN
    CREATE TYPE workspace_role AS ENUM ('owner', 'admin', 'member', 'viewer');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- =====================================================
-- 3. CREATE WORKSPACES TABLE
-- =====================================================
-- Main workspace/organization table

CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan TEXT DEFAULT 'starter',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON public.workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON public.workspaces(slug);
CREATE INDEX IF NOT EXISTS idx_workspaces_created_at ON public.workspaces(created_at DESC);

-- Enable RLS
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

-- RLS Policies for workspaces
CREATE POLICY "Users can view workspaces they are members of"
    ON public.workspaces FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members
            WHERE workspace_members.workspace_id = workspaces.id
            AND workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert workspaces"
    ON public.workspaces FOR INSERT
    WITH CHECK (auth.uid() = owner_id);

CREATE POLICY "Owners can update their workspaces"
    ON public.workspaces FOR UPDATE
    USING (auth.uid() = owner_id);

CREATE POLICY "Owners can delete their workspaces"
    ON public.workspaces FOR DELETE
    USING (auth.uid() = owner_id);

-- =====================================================
-- 4. CREATE WORKSPACE_MEMBERS TABLE
-- =====================================================
-- Tracks workspace membership and roles

CREATE TABLE IF NOT EXISTS public.workspace_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role workspace_role NOT NULL DEFAULT 'member',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON public.workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON public.workspace_members(user_id);

-- Enable RLS
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;

-- RLS Policies for workspace_members
CREATE POLICY "Users can view members of their workspaces"
    ON public.workspace_members FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members AS wm
            WHERE wm.workspace_id = workspace_members.workspace_id
            AND wm.user_id = auth.uid()
        )
    );

CREATE POLICY "Owners and admins can insert members"
    ON public.workspace_members FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workspace_members AS wm
            WHERE wm.workspace_id = workspace_members.workspace_id
            AND wm.user_id = auth.uid()
            AND wm.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Owners and admins can update members"
    ON public.workspace_members FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members AS wm
            WHERE wm.workspace_id = workspace_members.workspace_id
            AND wm.user_id = auth.uid()
            AND wm.role IN ('owner', 'admin')
        )
    );

CREATE POLICY "Owners and admins can delete members"
    ON public.workspace_members FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members AS wm
            WHERE wm.workspace_id = workspace_members.workspace_id
            AND wm.user_id = auth.uid()
            AND wm.role IN ('owner', 'admin')
        )
    );

-- =====================================================
-- 5. CREATE WORKSPACE_INVITES TABLE
-- =====================================================
-- Pending workspace invitations

CREATE TABLE IF NOT EXISTS public.workspace_invites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role workspace_role NOT NULL DEFAULT 'member',
    invited_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_workspace_invites_workspace_id ON public.workspace_invites(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_invites_email ON public.workspace_invites(email);
CREATE INDEX IF NOT EXISTS idx_workspace_invites_token ON public.workspace_invites(token);

-- Enable RLS
ALTER TABLE public.workspace_invites ENABLE ROW LEVEL SECURITY;

-- RLS Policies for workspace_invites
CREATE POLICY "Users can view invites for their workspaces"
    ON public.workspace_invites FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.workspace_members
            WHERE workspace_members.workspace_id = workspace_invites.workspace_id
            AND workspace_members.user_id = auth.uid()
            AND workspace_members.role IN ('owner', 'admin')
        )
        OR workspace_invites.email = (SELECT email FROM auth.users WHERE id = auth.uid())
    );

-- =====================================================
-- 6. TRIGGERS
-- =====================================================

-- Function to auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user profile creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
DROP TRIGGER IF EXISTS set_updated_at_profiles ON public.profiles;
CREATE TRIGGER set_updated_at_profiles
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

DROP TRIGGER IF EXISTS set_updated_at_workspaces ON public.workspaces;
CREATE TRIGGER set_updated_at_workspaces
    BEFORE UPDATE ON public.workspaces
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- =====================================================
-- 7. GRANTS
-- =====================================================
-- Grant access to authenticated users

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- Next steps:
-- 1. Verify tables created: SELECT * FROM public.profiles;
-- 2. Test workspace creation via frontend
-- 3. Verify RLS policies work correctly
-- =====================================================
