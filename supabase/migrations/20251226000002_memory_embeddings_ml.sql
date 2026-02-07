-- RaptorFlow Complete Database Schema (v2.0) - Part 3: Memory & AI Infrastructure
-- Agent memory, embeddings, and ML components

-- =====================================
-- 8. AGENT MEMORY SYSTEMS
-- =====================================

-- Episodic Memory (Thread-specific observations)
CREATE TABLE IF NOT EXISTS agent_memory_episodic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    thread_id TEXT NOT NULL,
    observation TEXT NOT NULL,
    context JSONB DEFAULT '{}',

    -- Vector embedding for similarity search
    embedding VECTOR(768),

    importance_score NUMERIC DEFAULT 1.0,
    is_expired BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT now()
);

-- Semantic Memory (Facts and knowledge)
CREATE TABLE IF NOT EXISTS agent_memory_semantic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    fact TEXT NOT NULL,
    category TEXT,
    confidence NUMERIC DEFAULT 1.0,

    metadata JSONB DEFAULT '{}',
    source_ids UUID[] DEFAULT '{}',

    -- Vector embedding for similarity search
    embedding VECTOR(768),

    is_validated BOOLEAN DEFAULT FALSE,
    validation_count INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Procedural Memory (How-to knowledge)
CREATE TABLE IF NOT EXISTS agent_memory_procedural (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    procedure TEXT NOT NULL,
    steps JSONB DEFAULT '{}',
    category TEXT,

    metadata JSONB DEFAULT '{}',
    success_rate NUMERIC DEFAULT 0.0,

    -- Vector embedding for similarity search
    embedding VECTOR(768),

    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 9. KNOWLEDGE GRAPH & EMBEDDINGS
-- =====================================

-- Knowledge Concepts (Graph nodes)
CREATE TABLE IF NOT EXISTS knowledge_concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    name TEXT NOT NULL,
    description TEXT,
    concept_type TEXT, -- entity, idea, principle, metric

    metadata JSONB DEFAULT '{}',

    -- Vector embedding
    embedding VECTOR(768),

    -- Graph metrics
    connection_count INTEGER DEFAULT 0,
    importance_score NUMERIC DEFAULT 1.0,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE(workspace_id, name)
);

-- Knowledge Links (Graph relationships)
CREATE TABLE IF NOT EXISTS knowledge_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    source_id UUID REFERENCES knowledge_concepts(id) ON DELETE CASCADE,
    target_id UUID REFERENCES knowledge_concepts(id) ON DELETE CASCADE,

    relation TEXT NOT NULL, -- related_to, causes, enables, requires, etc.
    weight FLOAT DEFAULT 1.0,
    confidence NUMERIC DEFAULT 1.0,

    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE(source_id, target_id, relation)
);

-- Entity Embeddings (General entity embeddings)
CREATE TABLE IF NOT EXISTS entity_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- campaign, move, asset, user, etc.
    description TEXT,

    metadata JSONB DEFAULT '{}',

    -- Vector embedding
    embedding VECTOR(768),

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Fact Store (Structured facts)
CREATE TABLE IF NOT EXISTS fact_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    content TEXT NOT NULL,
    category TEXT,
    source TEXT,

    metadata JSONB DEFAULT '{}',

    -- Vector embedding for search
    embedding VECTOR(768),

    is_verified BOOLEAN DEFAULT FALSE,
    verification_count INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 10. ML FEATURE STORE
-- =====================================

-- ML Feature Store (Machine learning features)
CREATE TABLE IF NOT EXISTS ml_feature_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    entity_id UUID NOT NULL,
    entity_type TEXT NOT NULL,

    feature_name TEXT NOT NULL,
    feature_value NUMERIC NOT NULL,
    vector_value VECTOR(768),

    -- Feature metadata
    feature_group TEXT,
    importance NUMERIC DEFAULT 1.0,

    created_at TIMESTAMPTZ DEFAULT now()
);

-- Model Lineage (ML model tracking)
CREATE TABLE IF NOT EXISTS model_lineage (
    model_id TEXT PRIMARY KEY,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    dataset_uri TEXT NOT NULL,
    artifact_uri TEXT NOT NULL,

    model_type TEXT,
    version TEXT,

    metadata JSONB DEFAULT '{}',

    performance_metrics JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 11. LANGGRAPH CHECKPOINTING
-- =====================================

-- Graph Threads (LangGraph thread management)
CREATE TABLE IF NOT EXISTS graph_threads (
    thread_id TEXT PRIMARY KEY,
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    user_id UUID REFERENCES auth.users(id),
    status TEXT DEFAULT 'idle' CHECK (status IN ('idle', 'busy', 'interrupted', 'error', 'completed')),

    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Checkpoints (LangGraph checkpointing)
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,

    parent_checkpoint_id TEXT,
    type TEXT,

    checkpoint BYTEA,
    metadata BYTEA,

    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

-- Checkpoint Blobs (Binary data for checkpoints)
CREATE TABLE IF NOT EXISTS checkpoint_blobs (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,

    type TEXT,
    blob BYTEA,

    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

-- Checkpoint Writes (Write-ahead logging)
CREATE TABLE IF NOT EXISTS checkpoint_writes (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    idx INTEGER NOT NULL,

    channel TEXT NOT NULL,
    type TEXT,
    blob BYTEA,

    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

-- Checkpoint Metadata (Performance tracking)
CREATE TABLE IF NOT EXISTS checkpoint_metadata (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,

    step_name TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    latency_ms REAL DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT now(),

    PRIMARY KEY (thread_id, checkpoint_id)
);
