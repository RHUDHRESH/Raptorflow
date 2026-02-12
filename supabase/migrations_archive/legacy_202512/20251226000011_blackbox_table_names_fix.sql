-- RaptorFlow Database Schema Fix: Blackbox Table Names
-- Updates Blackbox table names to match existing codebase

-- =====================================
-- BLACKBOX TABLE NAME FIXES
-- =====================================

-- The application code uses "_industrial" suffix for Blackbox tables
-- We need to rename the tables to match the existing codebase

-- Rename Blackbox tables to match codebase
ALTER TABLE blackbox_telemetry RENAME TO blackbox_telemetry_industrial;
ALTER TABLE blackbox_outcomes RENAME TO blackbox_outcomes_industrial;
ALTER TABLE blackbox_learnings RENAME TO blackbox_learnings_industrial;

-- Update indexes to match new table names
DROP INDEX IF EXISTS idx_blackbox_telemetry_workspace_id;
DROP INDEX IF EXISTS idx_blackbox_telemetry_experiment_id;
DROP INDEX IF EXISTS idx_blackbox_telemetry_timestamp;

CREATE INDEX IF NOT EXISTS idx_blackbox_telemetry_industrial_tenant_id ON blackbox_telemetry_industrial(tenant_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_telemetry_industrial_experiment_id ON blackbox_telemetry_industrial(experiment_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_telemetry_industrial_timestamp ON blackbox_telemetry_industrial(timestamp DESC);

DROP INDEX IF EXISTS idx_blackbox_outcomes_workspace_id;
DROP INDEX IF EXISTS idx_blackbox_outcomes_timestamp;

CREATE INDEX IF NOT EXISTS idx_blackbox_outcomes_industrial_tenant_id ON blackbox_outcomes_industrial(tenant_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_outcomes_industrial_timestamp ON blackbox_outcomes_industrial(timestamp DESC);

DROP INDEX IF EXISTS idx_blackbox_learnings_embedding;
DROP INDEX IF EXISTS idx_blackbox_learnings_workspace_id;

CREATE INDEX IF NOT EXISTS idx_blackbox_learnings_industrial_embedding ON blackbox_learnings_industrial USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_blackbox_learnings_industrial_tenant_id ON blackbox_learnings_industrial(tenant_id);

-- Update RLS policies to match new table names
DROP POLICY IF EXISTS "Blackbox Telemetry: Workspace members can view" ON blackbox_telemetry;
DROP POLICY IF EXISTS "Blackbox Telemetry: Owners and admins can manage" ON blackbox_telemetry;

CREATE POLICY "Blackbox Telemetry: Workspace members can view" ON blackbox_telemetry_industrial
    FOR SELECT USING (
        tenant_id IN (
            SELECT tenant_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Blackbox Telemetry: Owners and admins can manage" ON blackbox_telemetry_industrial
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.tenant_id = blackbox_telemetry_industrial.tenant_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

DROP POLICY IF EXISTS "Blackbox Outcomes: Workspace members can view" ON blackbox_outcomes;
DROP POLICY IF EXISTS "Blackbox Outcomes: Owners and admins can manage" ON blackbox_outcomes;

CREATE POLICY "Blackbox Outcomes: Workspace members can view" ON blackbox_outcomes_industrial
    FOR SELECT USING (
        tenant_id IN (
            SELECT tenant_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Blackbox Outcomes: Owners and admins can manage" ON blackbox_outcomes_industrial
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.tenant_id = blackbox_outcomes_industrial.tenant_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

DROP POLICY IF EXISTS "Blackbox Learnings: Workspace members can view" ON blackbox_learnings;
DROP POLICY IF EXISTS "Blackbox Learnings: Owners and admins can manage" ON blackbox_learnings;

CREATE POLICY "Blackbox Learnings: Workspace members can view" ON blackbox_learnings_industrial
    FOR SELECT USING (
        tenant_id IN (
            SELECT tenant_id FROM workspace_members
            WHERE workspace_members.user_id = auth.uid()
        )
    );

CREATE POLICY "Blackbox Learnings: Owners and admins can manage" ON blackbox_learnings_industrial
    FOR ALL USING (
        auth.uid() IN (
            SELECT user_id FROM workspace_members
            WHERE workspace_members.tenant_id = blackbox_learnings_industrial.tenant_id
            AND workspace_members.role IN ('owner', 'admin')
        )
    );

-- Update functions to use new table names
DROP FUNCTION IF EXISTS find_similar_learnings(VECTOR(768), UUID, INTEGER);
CREATE OR REPLACE FUNCTION find_similar_learnings(query_embedding VECTOR(768), tenant_uuid UUID, limit_count INTEGER DEFAULT 5)
RETURNS TABLE (
    learning_id UUID,
    content TEXT,
    similarity_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        bli.id,
        bli.content,
        1 - (bli.embedding <=> query_embedding) as similarity
    FROM blackbox_learnings_industrial bli
    WHERE bli.tenant_id = tenant_uuid
    AND bli.embedding IS NOT NULL
    ORDER BY bli.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ language 'plpgsql';

-- Update triggers to match new table names
DROP TRIGGER IF EXISTS update_blackbox_telemetry_updated_at ON blackbox_telemetry;
DROP TRIGGER IF EXISTS update_blackbox_outcomes_updated_at ON blackbox_outcomes;
DROP TRIGGER IF EXISTS update_blackbox_learnings_updated_at ON blackbox_learnings;

CREATE TRIGGER update_blackbox_telemetry_industrial_updated_at BEFORE UPDATE ON blackbox_telemetry_industrial
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blackbox_outcomes_industrial_updated_at BEFORE UPDATE ON blackbox_outcomes_industrial
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blackbox_learnings_industrial_updated_at BEFORE UPDATE ON blackbox_learnings_industrial
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================
-- VALIDATION
-- =====================================

-- Create validation function to check Blackbox table consistency
CREATE OR REPLACE FUNCTION validate_blackbox_table_consistency()
RETURNS JSONB AS $$
DECLARE
    result JSONB;
    telemetry_exists BOOLEAN;
    outcomes_exists BOOLEAN;
    learnings_exists BOOLEAN;
BEGIN
    -- Check if industrial tables exist
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'blackbox_telemetry_industrial'
        AND table_schema = 'public'
    ) INTO telemetry_exists;

    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'blackbox_outcomes_industrial'
        AND table_schema = 'public'
    ) INTO outcomes_exists;

    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'blackbox_learnings_industrial'
        AND table_schema = 'public'
    ) INTO learnings_exists;

    result := jsonb_build_object(
        'validation_timestamp', now(),
        'blackbox_telemetry_industrial_exists', telemetry_exists,
        'blackbox_outcomes_industrial_exists', outcomes_exists,
        'blackbox_learnings_industrial_exists', learnings_exists,
        'status', CASE
            WHEN telemetry_exists AND outcomes_exists AND learnings_exists THEN 'consistent'
            ELSE 'inconsistent'
        END
    );

    RETURN result;
END;
$$ language 'plpgsql';

-- Run validation
SELECT validate_blackbox_table_consistency();
