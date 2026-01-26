-- Migration: 20260118_council_sessions.sql
-- Store Expert Council deliberations and final reports

CREATE TABLE IF NOT EXISTS public.council_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    mission TEXT NOT NULL,

    -- Discussion state
    contributions JSONB DEFAULT '[]', -- List of CouncilContribution
    skills_loaded JSONB DEFAULT '{}',
    final_report TEXT,

    -- Metrics
    accuracy_score FLOAT DEFAULT 0.0,
    latency_ms INTEGER DEFAULT 0,
    consensus_reached BOOLEAN DEFAULT FALSE,

    -- Status & Escalation
    status TEXT DEFAULT 'deliberating', -- deliberating, finalized, escalated
    escalation_path TEXT DEFAULT 'lead', -- lead, escalation-team

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.council_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own council sessions" ON public.council_sessions
    FOR ALL USING (EXISTS (
        SELECT 1 FROM workspaces WHERE workspaces.id = council_sessions.workspace_id AND workspaces.user_id = auth.uid()
    ));

-- Trigger for updated_at
CREATE TRIGGER council_sessions_updated_at
    BEFORE UPDATE ON public.council_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
