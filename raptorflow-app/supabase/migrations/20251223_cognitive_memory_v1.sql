-- Update Agent Memory Tables for Vertex AI (text-embedding-004 uses 768 dimensions)

-- Episodic Memory
ALTER TABLE agent_memory_episodic 
ALTER COLUMN embedding TYPE vector(768);

-- Semantic Memory
ALTER TABLE agent_memory_semantic
ALTER COLUMN embedding TYPE vector(768);

-- ML Feature Store
ALTER TABLE ml_feature_store
ALTER COLUMN embedding TYPE vector(768);

-- Add Search Functions for RAG

-- Match Episodic
CREATE OR REPLACE FUNCTION match_episodic_memory (
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  p_thread_id text
)
RETURNS TABLE (
  id uuid,
  observation text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    ame.id,
    ame.observation,
    1 - (ame.embedding <=> query_embedding) AS similarity
  FROM agent_memory_episodic ame
  WHERE ame.thread_id = p_thread_id
    AND 1 - (ame.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;

-- Match Semantic
CREATE OR REPLACE FUNCTION match_semantic_memory (
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  p_tenant_id uuid
)
RETURNS TABLE (
  id uuid,
  fact text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    ams.id,
    ams.fact,
    ams.metadata,
    1 - (ams.embedding <=> query_embedding) AS similarity
  FROM agent_memory_semantic ams
  WHERE ams.tenant_id = p_tenant_id
    AND 1 - (ams.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
