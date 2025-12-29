-- Migration: Create Swarm Context table
CREATE TABLE IF NOT EXISTS swarm_context (
    workspace_id UUID PRIMARY KEY REFERENCES workspaces(id) ON DELETE CASCADE,
    context_data JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_swarm_context_workspace ON swarm_context(workspace_id);
