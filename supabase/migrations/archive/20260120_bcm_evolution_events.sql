-- BCM Evolution Engine - Event Ledger
-- Migration: 20260120_bcm_evolution_events.sql

CREATE TABLE IF NOT EXISTS public.bcm_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL, -- e.g., 'STRATEGIC_SHIFT', 'MOVE_COMPLETED', 'USER_INTERACTION'
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    ucid TEXT, -- RaptorFlow UCID format RF-YYYY-XXXX
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for workspace-based state reconstruction
CREATE INDEX IF NOT EXISTS idx_bcm_events_workspace ON public.bcm_events(workspace_id);
-- Index for chronological replay
CREATE INDEX IF NOT EXISTS idx_bcm_events_created_at ON public.bcm_events(created_at);
-- Index for UCID tracking
CREATE INDEX IF NOT EXISTS idx_bcm_events_ucid ON public.bcm_events(ucid);

-- Enable Row Level Security
ALTER TABLE public.bcm_events ENABLE ROW LEVEL SECURITY;

-- RLS Policies
DROP POLICY IF EXISTS "bcm_events_select_isolation" ON public.bcm_events;
CREATE POLICY "bcm_events_select_isolation" ON public.bcm_events
    FOR SELECT USING (check_membership(workspace_id));

DROP POLICY IF EXISTS "bcm_events_insert_isolation" ON public.bcm_events;
CREATE POLICY "bcm_events_insert_isolation" ON public.bcm_events
    FOR INSERT WITH CHECK (check_membership(workspace_id));

-- Note: BCM Events are immutable by design (Event Sourcing), so no UPDATE or DELETE policies are provided.
