-- Workflow budget tracking for cost management
-- Enables persistence of token budgets across sessions

CREATE TABLE IF NOT EXISTS workflow_budgets (
    workflow_id VARCHAR(255) PRIMARY KEY,
    total_tokens INTEGER NOT NULL,
    used_tokens INTEGER NOT NULL DEFAULT 0,
    remaining_tokens INTEGER NOT NULL,
    checkpoints INTEGER[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for efficient lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS workflow_budgets_workflow_id_idx
ON workflow_budgets(workflow_id);

-- RLS Policy - users can only access their own workflow budgets
ALTER TABLE workflow_budgets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access their workflow budgets" ON workflow_budgets
    FOR ALL USING (
        workflow_id LIKE auth.uid()::text || '%'
        OR workflow_id LIKE 'system_%'
    );

-- Function to clean up old workflow budgets (older than 30 days)
CREATE OR REPLACE FUNCTION cleanup_old_workflow_budgets()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM workflow_budgets
    WHERE created_at < NOW() - INTERVAL '30 days'
    AND used_tokens >= total_tokens; -- Only delete completed workflows
END;
$$;

-- Create a scheduled job to run cleanup (would need pg_cron extension)
-- SELECT cron.schedule('cleanup-workflow-budgets', '0 2 * * *', 'SELECT cleanup_old_workflow_budgets();');


