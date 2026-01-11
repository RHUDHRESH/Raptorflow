-- Graph relationships table for knowledge graph connections
-- Stores relationships between entities (e.g., company HAS_USP feature)

CREATE TABLE IF NOT EXISTS graph_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Relationship endpoints
    source_id UUID NOT NULL REFERENCES graph_entities(id) ON DELETE CASCADE,
    target_id UUID NOT NULL REFERENCES graph_entities(id) ON DELETE CASCADE,

    -- Relationship classification
    relation_type TEXT NOT NULL CHECK (relation_type IN (
        'HAS_ICP', 'COMPETES_WITH', 'USES_CHANNEL', 'SOLVES_PAIN',
        'HAS_USP', 'HAS_FEATURE', 'TARGETS', 'PART_OF',
        'CREATED_BY', 'MENTIONS', 'RELATES_TO', 'INFLUENCES'
    )),

    -- Relationship properties
    properties JSONB DEFAULT '{}',
    weight DECIMAL(3,2) DEFAULT 1.0 CHECK (weight >= 0.0 AND weight <= 10.0),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT no_self_relationship CHECK (source_id != target_id),
    CONSTRAINT unique_relationship UNIQUE (workspace_id, source_id, target_id, relation_type)
);

-- Indexes for performance
CREATE INDEX idx_graph_relationships_workspace_id ON graph_relationships(workspace_id);
CREATE INDEX idx_graph_relationships_source_id ON graph_relationships(source_id);
CREATE INDEX idx_graph_relationships_target_id ON graph_relationships(target_id);
CREATE INDEX idx_graph_relationships_type ON graph_relationships(relation_type);
CREATE INDEX idx_graph_relationships_weight ON graph_relationships(weight);
CREATE INDEX idx_graph_relationships_workspace_source ON graph_relationships(workspace_id, source_id);
CREATE INDEX idx_graph_relationships_workspace_target ON graph_relationships(workspace_id, target_id);
CREATE INDEX idx_graph_relationships_workspace_type ON graph_relationships(workspace_id, relation_type);

-- Composite index for common queries
CREATE INDEX idx_graph_relationships_lookup ON graph_relationships(workspace_id, source_id, relation_type);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_graph_relationships_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_graph_relationships_updated_at
    BEFORE UPDATE ON graph_relationships
    FOR EACH ROW
    EXECUTE FUNCTION update_graph_entities_updated_at();

-- Function to get all relationships for an entity
CREATE OR REPLACE FUNCTION get_entity_relationships(
    p_workspace_id UUID,
    p_entity_id UUID,
    p_direction TEXT DEFAULT 'both' -- 'incoming', 'outgoing', 'both'
)
RETURNS TABLE (
    relationship_id UUID,
    source_id UUID,
    target_id UUID,
    relation_type TEXT,
    properties JSONB,
    weight DECIMAL(3,2),
    created_at TIMESTAMPTZ,
    direction TEXT
) AS $$
BEGIN
    IF p_direction = 'outgoing' THEN
        RETURN QUERY
        SELECT
            r.id,
            r.source_id,
            r.target_id,
            r.relation_type,
            r.properties,
            r.weight,
            r.created_at,
            'outgoing'::TEXT
        FROM graph_relationships r
        WHERE r.workspace_id = p_workspace_id
        AND r.source_id = p_entity_id;
    ELSIF p_direction = 'incoming' THEN
        RETURN QUERY
        SELECT
            r.id,
            r.source_id,
            r.target_id,
            r.relation_type,
            r.properties,
            r.weight,
            r.created_at,
            'incoming'::TEXT
        FROM graph_relationships r
        WHERE r.workspace_id = p_workspace_id
        AND r.target_id = p_entity_id;
    ELSE
        RETURN QUERY
        SELECT
            r.id,
            r.source_id,
            r.target_id,
            r.relation_type,
            r.properties,
            r.weight,
            r.created_at,
            CASE
                WHEN r.source_id = p_entity_id THEN 'outgoing'::TEXT
                WHEN r.target_id = p_entity_id THEN 'incoming'::TEXT
            END as direction
        FROM graph_relationships r
        WHERE r.workspace_id = p_workspace_id
        AND (r.source_id = p_entity_id OR r.target_id = p_entity_id);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE graph_relationships IS 'Knowledge graph relationships connecting entities';
COMMENT ON COLUMN graph_relationships.source_id IS 'ID of the source entity in the relationship';
COMMENT ON COLUMN graph_relationships.target_id IS 'ID of the target entity in the relationship';
COMMENT ON COLUMN graph_relationships.relation_type IS 'Type of relationship (HAS_ICP, COMPETES_WITH, etc.)';
COMMENT ON COLUMN graph_relationships.properties IS 'Additional relationship attributes as JSON';
COMMENT ON COLUMN graph_relationships.weight IS 'Strength or importance of the relationship (0.0-10.0)';
COMMENT ON FUNCTION get_entity_relationships IS 'Get all relationships for an entity with direction';
