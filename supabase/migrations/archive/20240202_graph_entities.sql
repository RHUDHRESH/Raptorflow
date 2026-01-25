-- Graph entities table for knowledge graph storage
-- Stores entities like companies, ICPs, competitors, channels, etc.

CREATE TABLE IF NOT EXISTS graph_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Entity classification
    entity_type TEXT NOT NULL CHECK (entity_type IN (
        'company', 'icp', 'competitor', 'channel', 'pain_point',
        'usp', 'feature', 'move', 'campaign', 'content'
    )),

    -- Entity identity
    name TEXT NOT NULL,
    properties JSONB DEFAULT '{}',

    -- Vector embedding for semantic search
    embedding vector(384),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT unique_entity_per_workspace UNIQUE (workspace_id, entity_type, name)
);

-- Indexes for performance
CREATE INDEX idx_graph_entities_workspace_id ON graph_entities(workspace_id);
CREATE INDEX idx_graph_entities_type ON graph_entities(entity_type);
CREATE INDEX idx_graph_entities_workspace_type ON graph_entities(workspace_id, entity_type);
CREATE INDEX idx_graph_entities_name ON graph_entities(name);
CREATE INDEX idx_graph_entities_workspace_name ON graph_entities(workspace_id, name);

-- Vector index for semantic search (ivfflat for approximate nearest neighbor)
CREATE INDEX idx_graph_entities_embedding ON graph_entities
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_graph_entities_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_graph_entities_updated_at
    BEFORE UPDATE ON graph_entities
    FOR EACH ROW
    EXECUTE FUNCTION update_graph_entities_updated_at();

-- Comments for documentation
COMMENT ON TABLE graph_entities IS 'Knowledge graph entities for storing business concepts and their relationships';
COMMENT ON COLUMN graph_entities.entity_type IS 'Type of entity (company, icp, competitor, etc.)';
COMMENT ON COLUMN graph_entities.name IS 'Human-readable name of the entity';
COMMENT ON COLUMN graph_entities.properties IS 'Additional entity attributes as JSON';
COMMENT ON COLUMN graph_entities.embedding IS 'Vector embedding for semantic similarity search';
