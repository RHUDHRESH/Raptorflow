-- Optimize Memory Indexing for Industrial Intelligence Engine
-- Target: Vertex AI (768 dimensions)

-- 1. Update dimensions if they were incorrectly set to 1536 (OpenAI default)
-- Note: In a live DB with data, this would require more care, but for this build we ensure correctness.

ALTER TABLE agent_memory_semantic ALTER COLUMN embedding TYPE vector(768);
ALTER TABLE agent_memory_episodic ALTER COLUMN embedding TYPE vector(768);

-- 2. Add HNSW Indices for SOTA low-latency retrieval
-- We use vector_cosine_ops as it's the standard for agentic semantic search.

CREATE INDEX IF NOT EXISTS idx_semantic_memory_vector 
ON agent_memory_semantic 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_episodic_memory_vector 
ON agent_memory_episodic 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- 3. Add procedural memory table (Industrial requirement from Phase 15)
CREATE TABLE IF NOT EXISTS agent_memory_procedural (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    fact TEXT NOT NULL,
    metadata JSONB,
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE agent_memory_procedural ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_procedural_memory ON agent_memory_procedural USING (tenant_id = auth.uid());

CREATE INDEX IF NOT EXISTS idx_procedural_memory_vector 
ON agent_memory_procedural 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
