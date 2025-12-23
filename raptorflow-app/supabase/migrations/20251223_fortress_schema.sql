-- RaptorFlow Fortress - State Management Schema
-- Extends base LangGraph schema with SOTA metadata tracking

-- High-level thread management (SOTA)
-- Links thread_ids to workspaces and users for strict isolation
CREATE TABLE IF NOT EXISTS graph_threads (
    thread_id TEXT PRIMARY KEY,
    workspace_id UUID NOT NULL,
    user_id UUID,
    status TEXT DEFAULT 'idle' CHECK (status IN ('idle', 'busy', 'interrupted', 'error', 'completed')),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Checkpoint Metadata (for better observability in UI)
CREATE TABLE IF NOT EXISTS checkpoint_metadata (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    step_name TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    latency_ms REAL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_id)
);

-- Index for workspace lookups
CREATE INDEX IF NOT EXISTS idx_graph_threads_workspace ON graph_threads(workspace_id);

-- --- VECTOR MEMORY (SOTA) ---

-- Entity Memory: Tracking people, brands, and competitors
CREATE TABLE IF NOT EXISTS entity_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- e.g., 'competitor', 'founder', 'influencer'
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(768), -- Optimized for Gemini text-embedding-004
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fact Store: Atomic pieces of evergreen knowledge
CREATE TABLE IF NOT EXISTS fact_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    content TEXT NOT NULL,
    category TEXT, -- e.g., 'tone', 'target_audience', 'pricing'
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(768),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW Indexes for SOTA Retrieval Speed
CREATE INDEX IF NOT EXISTS idx_entity_vector ON entity_embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_fact_vector ON fact_store USING hnsw (embedding vector_cosine_ops);
