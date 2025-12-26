-- RaptorFlow Database Schema Fix: Experiments Table Name
-- Updates experiments table name to match existing codebase

-- =====================================
-- EXPERIMENTS TABLE NAME FIX
-- =====================================

-- The application code uses 'experiments' table name, not 'blackbox_experiments'
-- We need to rename the table to match the existing codebase

-- Rename experiments table to match codebase
ALTER TABLE blackbox_experiments RENAME TO experiments;

-- Update indexes to match new table name
DROP INDEX IF EXISTS idx_blackbox_experiments_tenant_id;
DROP INDEX IF EXISTS idx_blackbox_experiments_status;
DROP INDEX IF EXISTS idx_blackbox_experiments_goal;
DROP INDEX IF EXISTS idx_blackbox_experiments_channel;
DROP INDEX IF EXISTS idx_blackbox_experiments_created_at;
DROP INDEX IF EXISTS idx_blackbox_experiments_checkin_due;
DROP INDEX IF EXISTS idx_experiments_tenant_status_created;

CREATE INDEX IF NOT EXISTS idx_experiments_tenant_id ON experiments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_experiments_goal ON experiments(goal);
CREATE INDEX IF NOT EXISTS idx_experiments_channel ON experiments(channel);
CREATE INDEX IF NOT EXISTS idx_experiments_created_at ON experiments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_experiments_checkin_due ON experiments(checkin_due_at);
CREATE INDEX IF NOT EXISTS idx_experiments_tenant_status_created ON experiments(tenant_id, status, created_at DESC);

-- Update RLS policies to match new table name
DROP POLICY IF EXISTS "Blackbox Experiments: Workspace members can view" ON blackbox_experiments;
DROP POLICY IF EXISTS "Blackbox Experiments: Owners and admins can manage" ON blackbox_experiments;

CREATE POLICY "Experiments: Workspace members can view" ON experiments
    FOR SELECT USING (
        tenant_id IN (
            SELECT tenant_id FROM workspace_members 
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Experiments: Owners and admins can manage" ON experiments
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members 
            WHERE workspace_members.tenant_id = experiments.tenant_id 
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Update triggers to match new table name
DROP TRIGGER IF EXISTS update_blackbox_experiments_updated_at ON blackbox_experiments;

CREATE TRIGGER update_experiments_updated_at BEFORE UPDATE ON experiments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update functions that reference experiments table
DROP FUNCTION IF EXISTS launch_experiment(UUID);
CREATE OR REPLACE FUNCTION launch_experiment(experiment_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Update experiment status and set checkin dates
    UPDATE experiments 
    SET 
        status = 'launched',
        launched_at = now(),
        checkin_due_at = (now() + (duration_days || ' days')::INTERVAL),
        checkin_remind_at = (now() + (duration_days || ' days')::INTERVAL - INTERVAL '24 hours'),
        checkin_expire_at = (now() + (duration_days || ' days')::INTERVAL + INTERVAL '7 days')
    WHERE id = experiment_uuid;
    
    RETURN FOUND;
END;
$$ language 'plpgsql';

-- Update archive completed campaigns function to reference experiments
DROP FUNCTION IF EXISTS archive_completed_campaigns(UUID);
CREATE OR REPLACE FUNCTION archive_completed_campaigns(tenant_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE campaigns 
    SET status = 'archived'
    WHERE tenant_id = tenant_uuid
    AND status = 'wrapup'
    AND updated_at < now() - INTERVAL '30 days';
    
    GET DIAGNOSTICS archived_count = ROW_COUNT;
    RETURN archived_count;
END;
$$ language 'plpgsql';

-- =====================================
-- VALIDATION
-- =====================================

-- Create validation function to check experiments table consistency
CREATE OR REPLACE FUNCTION validate_experiments_table_consistency()
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    experiments_exists BOOLEAN;
    blackbox_experiments_exists BOOLEAN;
BEGIN
    -- Check if experiments table exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'experiments' 
        AND table_schema = 'public'
    ) INTO experiments_exists;
    
    -- Check if blackbox_experiments table still exists (should not)
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'blackbox_experiments' 
        AND table_schema = 'public'
    ) INTO blackbox_experiments_exists;
    
    result := jsonb_build_object(
        'validation_timestamp', now(),
        'experiments_table_exists', experiments_exists,
        'blackbox_experiments_table_exists', blackbox_experiments_exists,
        'status', CASE 
            WHEN experiments_exists AND NOT blackbox_experiments_exists THEN 'consistent'
            ELSE 'inconsistent'
        END
    );
    
    RETURN result;
END;
$$ language 'plpgsql';

-- Run validation
SELECT validate_experiments_table_consistency();
