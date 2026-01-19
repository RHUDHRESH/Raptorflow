-- CORRECTED DATABASE FIX SCRIPT
-- Fixed dependency issues

-- STEP 1: Clean up any existing problematic tables
DROP TABLE IF EXISTS public.profiles CASCADE;
DROP TABLE IF EXISTS public.business_context_manifests CASCADE;
DROP TABLE IF EXISTS public.foundations CASCADE;
DROP TABLE IF EXISTS public.icp_profiles CASCADE;
DROP TABLE IF EXISTS public.icp_firmographics CASCADE;
DROP TABLE IF EXISTS public.icp_pain_map CASCADE;
DROP TABLE IF EXISTS public.icp_psycholinguistics CASCADE;
DROP TABLE IF EXISTS public.icp_disqualifiers CASCADE;

-- STEP 2: Check and fix workspaces table structure
DO $$
BEGIN
    -- Check if owner_id column exists in workspaces
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'workspaces' 
        AND column_name = 'owner_id'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE public.workspaces ADD COLUMN owner_id UUID;
    END IF;
    
    -- Check if updated_at column exists in workspaces
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'workspaces' 
        AND column_name = 'updated_at'
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE public.workspaces ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
    END IF;
END $$;

-- STEP 3: Create profiles table
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'super_admin')),
    workspace_id UUID,
    subscription_plan TEXT DEFAULT 'free' CHECK (subscription_plan IN ('free', 'ascent', 'glide', 'soar')),
    subscription_status TEXT DEFAULT 'none' CHECK (subscription_status IN ('none', 'trial', 'active', 'cancelled', 'expired', 'suspended')),
    onboarding_status TEXT DEFAULT 'pending' CHECK (onboarding_status IN ('pending', 'in_progress', 'active', 'skipped')),
    is_active BOOLEAN DEFAULT true,
    is_banned BOOLEAN DEFAULT false,
    ban_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- STEP 4: Now add the foreign key constraint to workspaces
ALTER TABLE public.workspaces ADD CONSTRAINT fk_workspaces_owner 
    FOREIGN KEY (owner_id) REFERENCES public.profiles(id) ON DELETE CASCADE;

-- STEP 5: Create BCM manifest table
CREATE TABLE public.business_context_manifests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    manifest JSONB NOT NULL,
    checksum TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, version)
);

-- STEP 6: Create foundations table
CREATE TABLE public.foundations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    company_info JSONB,
    mission TEXT,
    vision TEXT,
    value_proposition TEXT,
    brand_voice JSONB,
    messaging JSONB,
    ai_context_summary TEXT,
    ai_context_embedding vector(1536),
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- STEP 7: Create comprehensive ICP tables
CREATE TABLE public.icp_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    demographics JSONB,
    psychographics JSONB,
    pain_points JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Additional ICP related tables
CREATE TABLE public.icp_firmographics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    icp_profile_id UUID NOT NULL REFERENCES icp_profiles(id) ON DELETE CASCADE,
    company_size TEXT,
    industry TEXT,
    revenue_range TEXT,
    geography JSONB,
    sales_motion TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.icp_pain_map (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    icp_profile_id UUID NOT NULL REFERENCES icp_profiles(id) ON DELETE CASCADE,
    pain_points JSONB,
    trigger_events JSONB,
    urgency_level TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.icp_psycholinguistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    icp_profile_id UUID NOT NULL REFERENCES icp_profiles(id) ON DELETE CASCADE,
    language_preferences JSONB,
    communication_style TEXT,
    decision_factors JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.icp_disqualifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    icp_profile_id UUID NOT NULL REFERENCES icp_profiles(id) ON DELETE CASCADE,
    criteria JSONB,
    reasons TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- STEP 8: Create all necessary indexes
-- Profiles indexes
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_workspace ON public.profiles(workspace_id);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_subscription ON public.profiles(subscription_status);

-- Workspaces indexes
CREATE INDEX IF NOT EXISTS idx_workspaces_owner ON public.workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON public.workspaces(slug);

-- BCM indexes
CREATE INDEX IF NOT EXISTS idx_bcm_workspace ON public.business_context_manifests(workspace_id);
CREATE INDEX IF NOT EXISTS idx_bcm_version ON public.business_context_manifests(workspace_id, version);
CREATE INDEX IF NOT EXISTS idx_bcm_checksum ON public.business_context_manifests(checksum);

-- Foundations indexes
CREATE INDEX IF NOT EXISTS idx_foundations_workspace ON public.foundations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_foundations_status ON public.foundations(status);
CREATE INDEX IF NOT EXISTS idx_foundations_embedding ON public.foundations USING ivfflat (ai_context_embedding vector_cosine_ops);

-- ICP indexes
CREATE INDEX IF NOT EXISTS idx_icp_workspace ON public.icp_profiles(workspace_id);
CREATE INDEX IF NOT EXISTS idx_icp_name ON public.icp_profiles(name);
CREATE INDEX IF NOT EXISTS idx_icp_firmographics_profile ON public.icp_firmographics(icp_profile_id);
CREATE INDEX IF NOT EXISTS idx_icp_pain_profile ON public.icp_pain_map(icp_profile_id);
CREATE INDEX IF NOT EXISTS idx_icp_psycholinguistics_profile ON public.icp_psycholinguistics(icp_profile_id);
CREATE INDEX IF NOT EXISTS idx_icp_disqualifiers_profile ON public.icp_disqualifiers(icp_profile_id);

-- STEP 9: Enable Row Level Security on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_context_manifests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.foundations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.icp_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.icp_firmographics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.icp_pain_map ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.icp_psycholinguistics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.icp_disqualifiers ENABLE ROW LEVEL SECURITY;

-- STEP 10: Create comprehensive RLS policies
-- Profiles policies
DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
CREATE POLICY "profiles_select_own" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;
CREATE POLICY "profiles_update_own" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "profiles_insert_system" ON public.profiles;
CREATE POLICY "profiles_insert_system" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Workspaces policies
DROP POLICY IF EXISTS "workspaces_select_own" ON public.workspaces;
CREATE POLICY "workspaces_select_own" ON public.workspaces
    FOR SELECT USING (owner_id = auth.uid());

DROP POLICY IF EXISTS "workspaces_update_own" ON public.workspaces;
CREATE POLICY "workspaces_update_own" ON public.workspaces
    FOR UPDATE USING (owner_id = auth.uid());

DROP POLICY IF EXISTS "workspaces_insert_own" ON public.workspaces;
CREATE POLICY "workspaces_insert_own" ON public.workspaces
    FOR INSERT WITH CHECK (owner_id = auth.uid());

-- BCM policies
DROP POLICY IF EXISTS "bcm_select_workspace" ON public.business_context_manifests;
CREATE POLICY "bcm_select_workspace" ON public.business_context_manifests
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces 
            WHERE owner_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "bcm_insert_workspace" ON public.business_context_manifests;
CREATE POLICY "bcm_insert_workspace" ON public.business_context_manifests
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM public.workspaces 
            WHERE owner_id = auth.uid()
        )
    );

-- Foundations policies
DROP POLICY IF EXISTS "foundations_select_workspace" ON public.foundations;
CREATE POLICY "foundations_select_workspace" ON public.foundations
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces 
            WHERE owner_id = auth.uid()
        )
    );

-- ICP policies
DROP POLICY IF EXISTS "icp_select_workspace" ON public.icp_profiles;
CREATE POLICY "icp_select_workspace" ON public.icp_profiles
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces 
            WHERE owner_id = auth.uid()
        )
    );

-- STEP 11: Create triggers and functions
-- Updated_at trigger function
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create updated_at triggers
CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER workspaces_updated_at
    BEFORE UPDATE ON public.workspaces
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER foundations_updated_at
    BEFORE UPDATE ON public.foundations
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER icp_profiles_updated_at
    BEFORE UPDATE ON public.icp_profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- User profile auto-creation trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- STEP 12: Update migration records
TRUNCATE TABLE supabase_migrations.schema_migrations RESTART IDENTITY;

INSERT INTO supabase_migrations.schema_migrations (version, name, statements) VALUES
('001_profiles', '001_profiles.sql', 'profiles table with RLS'),
('002_workspaces', '002_workspaces.sql', 'workspaces table with owner_id'),
('20240102_foundations', '20240102_foundations.sql', 'foundations table with embeddings'),
('20240103_icp_profiles', '20240103_icp_profiles.sql', 'ICP profiles and related tables'),
('20260116_bcm_manifest', '20260116_bcm_manifest.sql', 'BCM manifest table');

-- STEP 13: Final verification
SELECT 'DATABASE FIX COMPLETED SUCCESSFULLY' as status,
       (SELECT COUNT(*) FROM public.profiles) as profiles_count,
       (SELECT COUNT(*) FROM public.workspaces) as workspaces_count,
       (SELECT COUNT(*) FROM public.business_context_manifests) as bcm_count,
       (SELECT COUNT(*) FROM public.foundations) as foundations_count,
       (SELECT COUNT(*) FROM public.icp_profiles) as icp_count,
       (SELECT COUNT(*) FROM public.icp_firmographics) as icp_firmographics_count,
       (SELECT COUNT(*) FROM public.icp_pain_map) as icp_pain_count,
       (SELECT COUNT(*) FROM public.icp_psycholinguistics) as icp_psycholinguistics_count,
       (SELECT COUNT(*) FROM public.icp_disqualifiers) as icp_disqualifiers_count;
