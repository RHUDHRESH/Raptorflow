-- Competitor profiles table
-- Migration: 20240118_competitor_profiles.sql

CREATE TABLE IF NOT EXISTS public.competitor_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    website TEXT,
    positioning TEXT,
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    content_strategy JSONB,
    last_analyzed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_workspace_id ON public.competitor_profiles(workspace_id);
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_name ON public.competitor_profiles(name);
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_last_analyzed_at ON public.competitor_profiles(last_analyzed_at);
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_created_at ON public.competitor_profiles(created_at);

-- GIN index for JSONB columns
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_strengths_gin ON public.competitor_profiles USING GIN (strengths);
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_weaknesses_gin ON public.competitor_profiles USING GIN (weaknesses);
CREATE INDEX IF NOT EXISTS idx_competitor_profiles_content_strategy_gin ON public.competitor_profiles USING GIN (content_strategy);

-- Enable RLS
ALTER TABLE public.competitor_profiles ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "Users can view own competitor profiles" ON public.competitor_profiles
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own competitor profiles" ON public.competitor_profiles
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own competitor profiles" ON public.competitor_profiles
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own competitor profiles" ON public.competitor_profiles
    FOR DELETE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION public.update_competitor_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER competitor_profiles_updated_at
    BEFORE UPDATE ON public.competitor_profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.update_competitor_profiles_updated_at();
