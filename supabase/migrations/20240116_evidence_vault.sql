-- Evidence vault table
-- Migration: 20240116_evidence_vault.sql

CREATE TABLE IF NOT EXISTS public.evidence_vault (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    source_type TEXT CHECK (source_type IN ('file', 'url')),
    source_name TEXT NOT NULL,
    file_path TEXT,
    url TEXT,
    content TEXT,
    content_type TEXT,
    word_count INTEGER,
    key_topics JSONB DEFAULT '[]',
    processing_status TEXT DEFAULT 'pending',
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_evidence_vault_workspace_id ON public.evidence_vault(workspace_id);
CREATE INDEX IF NOT EXISTS idx_evidence_vault_session_id ON public.evidence_vault(session_id);
CREATE INDEX IF NOT EXISTS idx_evidence_vault_processing_status ON public.evidence_vault(processing_status);
CREATE INDEX IF NOT EXISTS idx_evidence_vault_source_type ON public.evidence_vault(source_type);
CREATE INDEX IF NOT EXISTS idx_evidence_vault_created_at ON public.evidence_vault(created_at);

-- GIN index for JSONB columns
CREATE INDEX IF NOT EXISTS idx_evidence_vault_key_topics_gin ON public.evidence_vault USING GIN (key_topics);

-- Enable RLS
ALTER TABLE public.evidence_vault ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "Users can view own evidence" ON public.evidence_vault
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own evidence" ON public.evidence_vault
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own evidence" ON public.evidence_vault
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own evidence" ON public.evidence_vault
    FOR DELETE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );
