-- Similarity search function for memory vectors
-- Migration: 20240201_similarity_search.sql
-- Description: Function for semantic similarity search in memory vectors

CREATE OR REPLACE FUNCTION search_memory_vectors(
    p_workspace_id UUID,
    p_query_embedding vector(384),
    p_memory_types TEXT[] DEFAULT NULL,
    p_limit INT DEFAULT 10,
    p_min_similarity FLOAT DEFAULT 0.5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    memory_type TEXT,
    similarity FLOAT,
    score FLOAT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        mv.id,
        mv.content,
        mv.metadata,
        mv.memory_type,
        1 - (mv.embedding <=> p_query_embedding) AS similarity,
        mv.score,
        mv.created_at
    FROM public.memory_vectors mv
    WHERE
        mv.workspace_id = p_workspace_id
        AND (p_memory_types IS NULL OR mv.memory_type = ANY(p_memory_types))
        AND (1 - (mv.embedding <=> p_query_embedding)) >= p_min_similarity
    ORDER BY similarity DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a simpler wrapper for text-based search
CREATE OR REPLACE FUNCTION search_memory_by_text(
    p_workspace_id UUID,
    p_query_text TEXT,
    p_memory_types TEXT[] DEFAULT NULL,
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    memory_type TEXT,
    similarity FLOAT,
    score FLOAT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        mv.id,
        mv.content,
        mv.metadata,
        mv.memory_type,
        1 - (mv.embedding <=> p_query_text::vector) AS similarity,
        mv.score,
        mv.created_at
    FROM public.memory_vectors mv
    WHERE
        mv.workspace_id = p_workspace_id
        AND (p_memory_types IS NULL OR mv.memory_type = ANY(p_memory_types))
        AND (1 - (mv.embedding <=> p_query_text::vector)) >= 0.5
    ORDER BY similarity DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION search_memory_vectors TO authenticated;
GRANT EXECUTE ON FUNCTION search_memory_by_text TO authenticated;
