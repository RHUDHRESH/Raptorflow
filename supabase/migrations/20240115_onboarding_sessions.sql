-- Onboarding sessions table
-- Migration: 20240115_onboarding_sessions.sql

CREATE TABLE IF NOT EXISTS public.onboarding_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE UNIQUE,
    current_step INTEGER DEFAULT 1,
    completed_steps JSONB DEFAULT '[]',
    step_data JSONB DEFAULT '{}',
    evidence_items JSONB DEFAULT '[]',
    extracted_facts JSONB DEFAULT '[]',
    status TEXT DEFAULT 'in_progress',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_workspace_id ON public.onboarding_sessions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_status ON public.onboarding_sessions(status);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_started_at ON public.onboarding_sessions(started_at);

-- Enable RLS
ALTER TABLE public.onboarding_sessions ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "Users can view own onboarding sessions" ON public.onboarding_sessions
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own onboarding sessions" ON public.onboarding_sessions
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own onboarding sessions" ON public.onboarding_sessions
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own onboarding sessions" ON public.onboarding_sessions
    FOR DELETE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );
