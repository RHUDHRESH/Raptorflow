-- Move Tasks table (product-specific)
-- Migration: 20240105_move_tasks.sql
-- Description: Task management for moves with workspace isolation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Move Tasks table
CREATE TABLE IF NOT EXISTS public.move_tasks (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Workspace isolation
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Move relationship
    move_id UUID NOT NULL REFERENCES moves(id) ON DELETE CASCADE,

    -- Task metadata
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL, -- e.g., 'research', 'content', 'outreach', 'analysis'
    priority INTEGER DEFAULT 3, -- 1=High, 2=Medium, 3=Low, 4=Background
    status TEXT DEFAULT 'todo', -- todo, in_progress, review, completed, blocked, cancelled

    -- Task details
    objective TEXT NOT NULL,
    requirements JSONB DEFAULT '[]', -- Array of task requirements
    deliverables JSONB DEFAULT '[]', -- Array of expected deliverables
    estimated_hours DECIMAL(5,2) DEFAULT 0.00,

    -- Dependencies
    dependencies JSONB DEFAULT '[]', -- Array of task IDs that must be completed first
    blocking_tasks JSONB DEFAULT '[]', -- Array of task IDs that depend on this task

    -- Assignment and ownership
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,

    -- Timeline
    start_date TIMESTAMPTZ,
    due_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Progress tracking
    progress_percentage INTEGER DEFAULT 0,
    actual_hours DECIMAL(5,2) DEFAULT 0.00,
    completion_notes TEXT,

    -- AI-generated content
    content_embedding vector(384), -- For semantic search
    ai_suggestion TEXT,
    ai_confidence DECIMAL(3,2) DEFAULT 0.00,
    ai_generated_at TIMESTAMPTZ,

    -- Content and assets
    content TEXT,
    assets JSONB DEFAULT '[]', -- Array of asset references
    tags JSONB DEFAULT '[]', -- Array of tags for categorization

    -- Quality and review
    quality_score DECIMAL(3,2) DEFAULT 0.00, -- 0.00 to 1.00
    review_status TEXT DEFAULT 'pending', -- pending, approved, rejected, needs_revision
    review_notes TEXT,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,

    -- Performance metrics
    completion_rate DECIMAL(3,2) DEFAULT 0.00,
    quality_rating DECIMAL(3,2) DEFAULT 0.00,
    satisfaction_score DECIMAL(3,2) DEFAULT 0.00,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CHECK (priority >= 1 AND priority <= 4),
    CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    CHECK (estimated_hours >= 0),
    CHECK (actual_hours >= 0),
    CHECK (quality_score >= 0 AND quality_score <= 1),
    CHECK (completion_rate >= 0 AND completion_rate <= 1),
    CHECK (quality_rating >= 0 AND quality_rating <= 1),
    CHECK (satisfaction_score >= 0 AND satisfaction_score <= 1)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_move_tasks_workspace_id ON public.move_tasks(workspace_id);
CREATE INDEX IF NOT EXISTS idx_move_tasks_move_id ON public.move_tasks(move_id);
CREATE INDEX IF NOT EXISTS idx_move_tasks_category ON public.move_tasks(category);
CREATE INDEX IF NOT EXISTS idx_move_tasks_status ON public.move_tasks(status);
CREATE INDEX IF NOT EXISTS idx_move_tasks_priority ON public.move_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_move_tasks_assigned_to ON public.move_tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_move_tasks_due_date ON public.move_tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_move_tasks_created_at ON public.move_tasks(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_move_tasks_created_by ON public.move_tasks(created_by);
-- Tags index
CREATE INDEX IF NOT EXISTS idx_move_tasks_tags ON public.move_tasks USING GIN (tags jsonb_path_ops);
-- Dependencies index
CREATE INDEX IF NOT EXISTS idx_move_tasks_dependencies ON public.move_tasks USING GIN (dependencies jsonb_path_ops);
-- Blocking tasks index
CREATE INDEX IF NOT EXISTS idx_move_tasks_blocking_tasks ON public.move_tasks USING GIN (blocking_tasks jsonb_path_ops);

-- Vector index for semantic search
CREATE INDEX IF NOT EXISTS idx_move_tasks_content_embedding
    ON public.move_tasks USING ivfflat (content_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Unique constraint on task title per move
CREATE UNIQUE INDEX IF NOT EXISTS idx_move_tasks_unique_title
    ON public.move_tasks(move_id, title) WHERE status != 'draft';

-- Trigger for updated_at
CREATE TRIGGER move_tasks_updated_at
    BEFORE UPDATE ON public.move_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE public.move_tasks ENABLE ROW LEVEL SECURITY;
