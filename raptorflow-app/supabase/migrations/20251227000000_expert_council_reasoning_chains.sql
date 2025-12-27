-- Migration: Expert Council Reasoning Chains
-- Created: 2025-12-27

CREATE TABLE IF NOT EXISTS reasoning_chains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    debate_history JSONB NOT NULL DEFAULT '[]',
    final_synthesis TEXT,
    metrics JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    metadata JSONB DEFAULT '{}'
);

-- Index for workspace lookups
CREATE INDEX IF NOT EXISTS idx_reasoning_chains_workspace_id ON reasoning_chains(workspace_id);

-- RLS Policies
ALTER TABLE reasoning_chains ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view reasoning chains for their workspace"
    ON reasoning_chains FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Agents can insert reasoning chains"
    ON reasoning_chains FOR INSERT
    WITH CHECK (true); -- In a real prod, this might be restricted to service roles or specific IDs
