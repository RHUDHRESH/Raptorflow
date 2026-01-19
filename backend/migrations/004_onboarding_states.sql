-- Migration: Create onboarding_states table
-- Description: Centralized state management for onboarding workflow

CREATE TABLE IF NOT EXISTS onboarding_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    current_step TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    lock_expires_at TIMESTAMP WITH TIME ZONE,
    lock_owner TEXT,
    
    -- JSON fields for step states and metadata
    steps JSONB NOT NULL DEFAULT '{}',
    
    -- Indexes for performance
    UNIQUE(workspace_id),
    INDEX idx_onboarding_states_workspace_id (workspace_id),
    INDEX idx_onboarding_states_updated_at (updated_at),
    INDEX idx_onboarding_states_lock_expires (lock_expires_at),
    
    -- RLS policies
    POLICY "Users can view their own onboarding states" ON onboarding_states
        FOR SELECT USING (
            workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        ),
    
    POLICY "Users can update their own onboarding states" ON onboarding_states
        FOR UPDATE USING (
            workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        ),
    
    POLICY "Users can insert their own onboarding states" ON onboarding_states
        FOR INSERT WITH CHECK (
            workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        )
);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_onboarding_states_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER onboarding_states_updated_at
    BEFORE UPDATE ON onboarding_states
    FOR EACH ROW
    EXECUTE FUNCTION update_onboarding_states_updated_at();

-- Add comments
COMMENT ON TABLE onboarding_states IS 'Centralized state management for onboarding workflow';
COMMENT ON COLUMN onboarding_states.workspace_id IS 'Reference to workspace';
COMMENT ON COLUMN onboarding_states.current_step IS 'Currently executing step';
COMMENT ON COLUMN onboarding_states.steps IS 'JSON object containing all step states';
COMMENT ON COLUMN onboarding_states.lock_expires_at IS 'Timestamp when lock expires';
COMMENT ON COLUMN onboarding_states.lock_owner IS 'Identifier of lock owner';
