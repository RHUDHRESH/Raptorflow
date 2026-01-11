-- Research findings table
-- Migration: 20240117_research_findings.sql

CREATE TABLE IF NOT EXISTS public.research_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    research_type TEXT CHECK (research_type IN ('market', 'competitor', 'customer', 'trend')),
    query TEXT,
    sources JSONB DEFAULT '[]',
    findings JSONB DEFAULT '[]',
    summary TEXT,
    confidence_score INTEGER CHECK (confidence_score >= 0 AND confidence_score <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_research_findings_workspace_id ON public.research_findings(workspace_id);
CREATE INDEX IF NOT EXISTS idx_research_findings_research_type ON public.research_findings(research_type);
CREATE INDEX IF NOT EXISTS idx_research_findings_confidence_score ON public.research_findings(confidence_score);
CREATE INDEX IF NOT EXISTS idx_research_findings_created_at ON public.research_findings(created_at);

-- GIN index for JSONB columns
CREATE INDEX IF NOT EXISTS idx_research_findings_sources_gin ON public.research_findings USING GIN (sources);
CREATE INDEX IF NOT EXISTS idx_research_findings_findings_gin ON public.research_findings USING GIN (findings);

-- Enable RLS
ALTER TABLE public.research_findings ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "Users can view own research findings" ON public.research_findings
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own research findings" ON public.research_findings
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own research findings" ON public.research_findings
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete own research findings" ON public.research_findings
    FOR DELETE USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );
