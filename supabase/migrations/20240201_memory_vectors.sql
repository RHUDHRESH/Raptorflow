-- Memory Vectors table for semantic search
-- Migration: 20240201_memory_vectors.sql
-- Description: Vector memory storage with workspace isolation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Memory Vectors table
CREATE TABLE IF NOT EXISTS public.memory_vectors (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Workspace isolation
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Memory classification
    memory_type TEXT NOT NULL CHECK (memory_type IN (
        'foundation',
        'icp',
        'move',
        'campaign',
        'research',
        'conversation',
        'feedback'
    )),

    -- Content and metadata
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',

    -- Vector embedding (384 dimensions for all-MiniLM-L6-v2)
    embedding vector(384) NOT NULL,

    -- Reference to source entity
    reference_id UUID,
    reference_table TEXT,

    -- Quality and scoring
    score FLOAT,
    confidence FLOAT DEFAULT 1.0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CHECK (score >= 0 AND score <= 1),
    CHECK (confidence >= 0 AND confidence <= 1)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_memory_vectors_workspace_id ON public.memory_vectors(workspace_id);
CREATE INDEX IF NOT EXISTS idx_memory_vectors_workspace_type ON public.memory_vectors(workspace_id, memory_type);
CREATE INDEX IF NOT EXISTS idx_memory_vectors_type ON public.memory_vectors(memory_type);
CREATE INDEX IF NOT EXISTS idx_memory_vectors_reference ON public.memory_vectors(reference_table, reference_id);
CREATE INDEX IF NOT EXISTS idx_memory_vectors_created_at ON public.memory_vectors(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_vectors_score ON public.memory_vectors(score DESC);

-- Vector index for similarity search
CREATE INDEX IF NOT EXISTS idx_memory_vectors_embedding
    ON public.memory_vectors USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Unique constraint to prevent duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_vectors_unique_content
    ON public.memory_vectors(workspace_id, memory_type, content) WHERE reference_id IS NULL;

-- Trigger for updated_at
CREATE TRIGGER memory_vectors_updated_at
    BEFORE UPDATE ON public.memory_vectors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE public.memory_vectors ENABLE ROW LEVEL SECURITY;
