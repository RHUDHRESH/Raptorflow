-- Migration: Agent Memory System
-- Description: Add vector-based memory storage for agent learning and context retention
-- Date: 2025-01-22
-- Dependencies: pgvector extension

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create agent_memories table for storing agent execution memories
CREATE TABLE IF NOT EXISTS agent_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    agent_name TEXT NOT NULL,
    memory_type TEXT NOT NULL CHECK (memory_type IN ('success', 'failure', 'preference', 'insight')),
    context JSONB NOT NULL,
    result JSONB NOT NULL,
    embedding VECTOR(768), -- textembedding-gecko dimension
    success_score FLOAT NOT NULL DEFAULT 0.5 CHECK (success_score >= 0.0 AND success_score <= 1.0),
    feedback JSONB,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_agent_memories_workspace_agent
    ON agent_memories(workspace_id, agent_name);

CREATE INDEX IF NOT EXISTS idx_agent_memories_type
    ON agent_memories(memory_type);

CREATE INDEX IF NOT EXISTS idx_agent_memories_score
    ON agent_memories(success_score DESC);

CREATE INDEX IF NOT EXISTS idx_agent_memories_tags
    ON agent_memories USING GIN(tags);

CREATE INDEX IF NOT EXISTS idx_agent_memories_created
    ON agent_memories(created_at DESC);

-- Vector similarity search index (IVFFlat for cosine similarity)
-- Note: This index should be created AFTER data is loaded for optimal performance
-- For initial migration, we create it immediately
CREATE INDEX IF NOT EXISTS idx_agent_memories_embedding
    ON agent_memories USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
-- Lists = 100 is suitable for ~10K memories. Adjust based on expected data size:
-- - 10K memories: lists = 100
-- - 100K memories: lists = 1000
-- - 1M memories: lists = 10000

-- Row-level security for multi-tenancy
ALTER TABLE agent_memories ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access memories from their workspaces
CREATE POLICY agent_memories_workspace_isolation ON agent_memories
    FOR ALL
    USING (
        workspace_id IN (
            SELECT workspace_id
            FROM user_workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Policy: Service role can access all memories (for backend operations)
CREATE POLICY agent_memories_service_role ON agent_memories
    FOR ALL
    TO service_role
    USING (true);

-- Function: Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_agent_memory_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_agent_memory_timestamp
    BEFORE UPDATE ON agent_memories
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_memory_timestamp();

-- Function: Search agent memories by vector similarity
CREATE OR REPLACE FUNCTION search_agent_memories(
    query_embedding VECTOR(768),
    filter_workspace_id UUID,
    filter_agent_name TEXT,
    filter_memory_types TEXT[] DEFAULT NULL,
    filter_tags TEXT[] DEFAULT NULL,
    min_score FLOAT DEFAULT 0.0,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    agent_name TEXT,
    memory_type TEXT,
    context JSONB,
    result JSONB,
    success_score FLOAT,
    feedback JSONB,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.agent_name,
        m.memory_type,
        m.context,
        m.result,
        m.success_score,
        m.feedback,
        m.tags,
        m.created_at,
        1 - (m.embedding <=> query_embedding) AS similarity
    FROM agent_memories m
    WHERE m.workspace_id = filter_workspace_id
        AND m.agent_name = filter_agent_name
        AND (filter_memory_types IS NULL OR m.memory_type = ANY(filter_memory_types))
        AND (filter_tags IS NULL OR m.tags && filter_tags) -- Overlaps operator
        AND m.success_score >= min_score
        AND m.embedding IS NOT NULL
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: Get memory statistics for an agent in a workspace
CREATE OR REPLACE FUNCTION get_agent_memory_stats(
    filter_workspace_id UUID,
    filter_agent_name TEXT
)
RETURNS TABLE (
    total_memories BIGINT,
    success_count BIGINT,
    failure_count BIGINT,
    avg_success_score FLOAT,
    earliest_memory TIMESTAMP WITH TIME ZONE,
    latest_memory TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT AS total_memories,
        COUNT(*) FILTER (WHERE memory_type = 'success')::BIGINT AS success_count,
        COUNT(*) FILTER (WHERE memory_type = 'failure')::BIGINT AS failure_count,
        AVG(success_score)::FLOAT AS avg_success_score,
        MIN(created_at) AS earliest_memory,
        MAX(created_at) AS latest_memory
    FROM agent_memories
    WHERE workspace_id = filter_workspace_id
        AND agent_name = filter_agent_name;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: Clean up old low-quality memories (for periodic maintenance)
CREATE OR REPLACE FUNCTION cleanup_low_quality_memories(
    score_threshold FLOAT DEFAULT 0.3,
    age_days INT DEFAULT 90
)
RETURNS BIGINT AS $$
DECLARE
    deleted_count BIGINT;
BEGIN
    WITH deleted AS (
        DELETE FROM agent_memories
        WHERE memory_type = 'failure'
            AND success_score < score_threshold
            AND created_at < NOW() - (age_days || ' days')::INTERVAL
        RETURNING *
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Sample data for testing (optional - remove in production)
-- This is useful for local development and testing

-- COMMENT ON TABLE agent_memories IS 'Stores agent execution memories with vector embeddings for semantic search and learning';
-- COMMENT ON COLUMN agent_memories.embedding IS 'Vector embedding (768-dim) from textembedding-gecko@003';
-- COMMENT ON COLUMN agent_memories.success_score IS 'Quality score (0.0-1.0) for this execution';
-- COMMENT ON COLUMN agent_memories.memory_type IS 'Type: success (high-performing), failure (to avoid), preference (user settings), insight (learned pattern)';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON agent_memories TO service_role;
GRANT SELECT ON agent_memories TO authenticated;

-- Performance optimization notes:
--
-- 1. Vector Index Tuning:
--    - IVFFlat index 'lists' parameter should be sqrt(total_rows) for optimal performance
--    - Rebuild index periodically as data grows: REINDEX INDEX idx_agent_memories_embedding;
--
-- 2. Vacuuming:
--    - Run VACUUM ANALYZE agent_memories regularly to maintain query performance
--
-- 3. Monitoring:
--    - Track index usage: SELECT * FROM pg_stat_user_indexes WHERE indexrelname LIKE 'idx_agent_memories%';
--    - Monitor table size: SELECT pg_size_pretty(pg_total_relation_size('agent_memories'));
--
-- 4. Cleanup Strategy:
--    - Run cleanup_low_quality_memories() monthly to remove old failures
--    - Archive high-value memories to separate table for long-term retention

-- Rollback instructions:
-- DROP FUNCTION IF EXISTS cleanup_low_quality_memories(FLOAT, INT);
-- DROP FUNCTION IF EXISTS get_agent_memory_stats(UUID, TEXT);
-- DROP FUNCTION IF EXISTS search_agent_memories(VECTOR, UUID, TEXT, TEXT[], TEXT[], FLOAT, INT);
-- DROP TRIGGER IF EXISTS trigger_update_agent_memory_timestamp ON agent_memories;
-- DROP FUNCTION IF EXISTS update_agent_memory_timestamp();
-- DROP POLICY IF EXISTS agent_memories_service_role ON agent_memories;
-- DROP POLICY IF EXISTS agent_memories_workspace_isolation ON agent_memories;
-- DROP TABLE IF EXISTS agent_memories CASCADE;
