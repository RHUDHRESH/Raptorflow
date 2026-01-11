-- Row Level Security (RLS) policies for graph tables
-- Ensures workspace isolation for all graph operations

-- Enable RLS on graph tables
ALTER TABLE graph_entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE graph_relationships ENABLE ROW LEVEL SECURITY;

-- Policy for graph_entities: Users can only access entities in their workspaces
CREATE POLICY "Workspace isolation for graph entities" ON graph_entities
    FOR ALL USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );

-- Policy for graph_relationships: Users can only access relationships in their workspaces
CREATE POLICY "Workspace isolation for graph relationships" ON graph_relationships
    FOR ALL USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );

-- Additional policies for specific operations

-- Graph entities policies
CREATE POLICY "Users can insert graph entities in their workspaces" ON graph_entities
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update graph entities in their workspaces" ON graph_entities
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete graph entities in their workspaces" ON graph_entities
    FOR DELETE USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );

-- Graph relationships policies
CREATE POLICY "Users can insert graph relationships in their workspaces" ON graph_relationships
    FOR INSERT WITH CHECK (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update graph relationships in their workspaces" ON graph_relationships
    FOR UPDATE USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete graph relationships in their workspaces" ON graph_relationships
    FOR DELETE USING (
        workspace_id IN (
            SELECT id FROM workspaces WHERE user_id = auth.uid()
        )
    );

-- Function to validate workspace access for graph operations
CREATE OR REPLACE FUNCTION validate_graph_workspace_access(p_workspace_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM workspaces
        WHERE id = p_workspace_id AND user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if entities belong to the same workspace
CREATE OR REPLACE FUNCTION validate_same_workspace_relationship(
    p_source_id UUID,
    p_target_id UUID,
    p_workspace_id UUID
)
RETURNS BOOLEAN AS $$
DECLARE
    source_workspace UUID;
    target_workspace UUID;
BEGIN
    -- Get workspace IDs for both entities
    SELECT workspace_id INTO source_workspace
    FROM graph_entities
    WHERE id = p_source_id;

    SELECT workspace_id INTO target_workspace
    FROM graph_entities
    WHERE id = p_target_id;

    -- Validate both entities exist and belong to the same workspace
    RETURN source_workspace IS NOT NULL
           AND target_workspace IS NOT NULL
           AND source_workspace = target_workspace
           AND source_workspace = p_workspace_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically enforce workspace consistency for relationships
CREATE OR REPLACE FUNCTION enforce_relationship_workspace_consistency()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure both entities belong to the same workspace
    IF NOT EXISTS (
        SELECT 1 FROM graph_entities e1, graph_entities e2
        WHERE e1.id = NEW.source_id
        AND e2.id = NEW.target_id
        AND e1.workspace_id = e2.workspace_id
        AND e1.workspace_id = NEW.workspace_id
    ) THEN
        RAISE EXCEPTION 'Source and target entities must belong to the same workspace';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_enforce_relationship_workspace_consistency
    BEFORE INSERT OR UPDATE ON graph_relationships
    FOR EACH ROW
    EXECUTE FUNCTION enforce_relationship_workspace_consistency();

-- Comments for documentation
COMMENT ON POLICY "Workspace isolation for graph entities" IS 'Ensures users can only access graph entities in their own workspaces';
COMMENT ON POLICY "Workspace isolation for graph relationships" IS 'Ensures users can only access graph relationships in their own workspaces';
COMMENT ON FUNCTION validate_graph_workspace_access IS 'Validates that a user has access to a workspace for graph operations';
COMMENT ON FUNCTION validate_same_workspace_relationship IS 'Validates that relationship entities belong to the same workspace';
COMMENT ON TRIGGER trigger_enforce_relationship_workspace_consistency IS 'Ensures relationships are only created between entities in the same workspace';
