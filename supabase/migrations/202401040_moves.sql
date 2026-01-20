-- Moves table (product-specific)
-- Migration: 20240104_moves.sql
-- Description: Strategic moves and actions for business growth

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Moves table
CREATE TABLE IF NOT EXISTS public.moves (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Workspace isolation
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Move metadata
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL, -- e.g., 'marketing', 'sales', 'product', 'operations'
    priority INTEGER DEFAULT 3, -- 1=High, 2=Medium, 3=Low, 4=Background
    status TEXT DEFAULT 'draft', -- draft, planned, in_progress, completed, paused, cancelled

    -- Move details
    objective TEXT NOT NULL,
    target_audience TEXT,
    success_metrics JSONB DEFAULT '[]', -- Array of success metrics
    timeline_days INTEGER DEFAULT 30,
    budget_estimate DECIMAL(10,2) DEFAULT 0.00,

    -- Content and assets
    content TEXT,
    assets JSONB DEFAULT '[]', -- Array of asset references (images, documents, etc.)
    tags JSONB DEFAULT '[]', -- Array of tags for categorization

    -- Foundation and ICP references
    foundation_id UUID REFERENCES foundations(id) ON DELETE SET NULL,
    icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,

    -- Execution tracking
    progress_percentage INTEGER DEFAULT 0,
    start_date TIMESTAMPTZ,
    target_date TIMESTAMPTZ,
    completion_date TIMESTAMPTZ,

    -- AI-generated content
    ai_suggestion TEXT,
    ai_confidence DECIMAL(3,2) DEFAULT 0.00,
    ai_generated_at TIMESTAMPTZ,
    content_embedding vector(384), -- For semantic search

    -- Performance tracking
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue_impact DECIMAL(10,2) DEFAULT 0.00,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Constraints
    CHECK (priority >= 1 AND priority <= 4),
    CHECK (timeline_days > 0),
    CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    CHECK (budget_estimate >= 0)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_moves_workspace_id ON public.moves(workspace_id);
CREATE INDEX IF NOT EXISTS idx_moves_status ON public.moves(status);
CREATE INDEX IF NOT EXISTS idx_moves_tags ON public.moves USING GIN (tags jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_moves_created_at ON public.moves(created_at);

-- Vector index for semantic search
CREATE INDEX IF NOT EXISTS idx_moves_content_embedding
    ON public.moves USING ivfflat (content_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Unique constraint on move title per workspace
CREATE UNIQUE INDEX IF NOT EXISTS idx_moves_unique_title
    ON public.moves(workspace_id, title) WHERE status != 'draft';

-- Trigger for updated_at
CREATE TRIGGER moves_updated_at
    BEFORE UPDATE ON public.moves
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE public.moves ENABLE ROW LEVEL SECURITY;
