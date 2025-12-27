-- Migration: Council Rejections Tracking
-- Created: 2025-12-27

CREATE TABLE IF NOT EXISTS council_rejections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    reasoning_chain_id UUID REFERENCES reasoning_chains(id) ON DELETE CASCADE,
    discarded_path TEXT NOT NULL,
    rejection_reason TEXT,
    rejected_by_agent_id TEXT, -- Optional: which agent was the primary critic
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    metadata JSONB DEFAULT '{}'
);

-- Index for lookup
CREATE INDEX IF NOT EXISTS idx_council_rejections_chain_id ON council_rejections(reasoning_chain_id);
CREATE INDEX IF NOT EXISTS idx_council_rejections_workspace_id ON council_rejections(workspace_id);

-- RLS Policies
ALTER TABLE council_rejections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view rejections for their workspace"
    ON council_rejections FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Agents can insert rejections"
    ON council_rejections FOR INSERT
    WITH CHECK (true);
