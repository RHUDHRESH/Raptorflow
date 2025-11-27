-- Migration: Create Cost Tracking System
-- Date: 2025-01-27
-- Description: Create cost_logs table to track estimated costs of all AI agent actions

CREATE TABLE IF NOT EXISTS cost_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    correlation_id UUID NOT NULL,
    agent_name TEXT NOT NULL,
    action_name TEXT NOT NULL,
    input_tokens INTEGER NOT NULL CHECK (input_tokens >= 0),
    output_tokens INTEGER NOT NULL CHECK (output_tokens >= 0),
    estimated_cost_usd NUMERIC(10, 6) NOT NULL CHECK (estimated_cost_usd >= 0),
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Create index on workspace_id for efficient filtering
CREATE INDEX IF NOT EXISTS idx_cost_logs_workspace_id ON cost_logs(workspace_id);

-- Create index on correlation_id for workflow tracking
CREATE INDEX IF NOT EXISTS idx_cost_logs_correlation_id ON cost_logs(correlation_id);

-- Create index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_cost_logs_created_at ON cost_logs(created_at);
