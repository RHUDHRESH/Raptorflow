-- Agent Executions table (product-specific)
-- Migration: 20240110_agent_executions.sql
-- Description: AI agent execution tracking and monitoring with workspace isolation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Agent Executions table
CREATE TABLE IF NOT EXISTS public.agent_executions (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Workspace isolation
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Execution metadata
    execution_name TEXT NOT NULL,
    description TEXT,
    agent_type TEXT NOT NULL, -- e.g., 'icp_architect', 'move_strategist', 'content_creator', 'market_researcher'
    agent_name TEXT NOT NULL, -- Specific agent instance name
    execution_type TEXT NOT NULL, -- e.g., 'analysis', 'generation', 'optimization', 'research'
    status TEXT DEFAULT 'pending', -- pending, running, completed, failed, cancelled, timeout

    -- Execution details
    task_description TEXT NOT NULL,
    input_data JSONB DEFAULT '{}', -- Input data provided to agent
    output_data JSONB DEFAULT '{}', -- Output data from agent
    parameters JSONB DEFAULT '{}', -- Execution parameters and configuration
    context JSONB DEFAULT '{}', -- Additional context for the execution

    -- Timing and performance
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER, -- Duration in milliseconds
    estimated_duration_ms INTEGER, -- Estimated duration
    timeout_ms INTEGER DEFAULT 300000, -- Timeout in milliseconds (5 minutes default)

    -- Resource usage
    tokens_used INTEGER DEFAULT 0, -- Tokens consumed
    cost_estimate DECIMAL(10,6) DEFAULT 0.000000, -- Estimated cost in USD
    memory_usage_mb DECIMAL(8,2) DEFAULT 0.00, -- Memory usage in MB
    cpu_usage_percent DECIMAL(5,2) DEFAULT 0.00, -- CPU usage percentage

    -- Quality and confidence
    confidence_score DECIMAL(3,2) DEFAULT 0.00, -- Agent's confidence in output (0.00 to 1.00)
    quality_score DECIMAL(3,2) DEFAULT 0.00, -- Quality assessment (0.00 to 1.00)
    accuracy_score DECIMAL(3,2) DEFAULT 0.00, -- Accuracy assessment (0.00 to 1.00)
    completeness_score DECIMAL(3,2) DEFAULT 0.00, -- Completeness assessment (0.00 to 1.00)

    -- Error handling
    error_message TEXT,
    error_type TEXT, -- e.g., 'timeout', 'rate_limit', 'invalid_input', 'api_error', 'internal_error'
    error_details JSONB DEFAULT '{}', -- Detailed error information
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Related entities
    foundation_id UUID REFERENCES foundations(id) ON DELETE SET NULL,
    icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    move_id UUID REFERENCES moves(id) ON DELETE SET NULL,
    move_task_id UUID REFERENCES move_tasks(id) ON DELETE SET NULL,
    blackbox_strategy_id UUID REFERENCES blackbox_strategies(id) ON DELETE SET NULL,
    muse_asset_id UUID REFERENCES muse_assets(id) ON DELETE SET NULL,

    -- User interaction
    initiated_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Feedback and ratings
    user_feedback TEXT,
    user_rating INTEGER, -- 1-5 rating from user
    user_comments TEXT,
    auto_feedback JSONB DEFAULT '{}', -- Automatic feedback from system

    -- Learning and improvement
    learnings JSONB DEFAULT '[]', -- Key learnings from execution
    improvements_suggested JSONB DEFAULT '[]', -- Suggested improvements
    performance_insights JSONB DEFAULT '{}', -- Performance insights

    -- Caching and optimization
    cache_key TEXT, -- Key for caching results
    cache_ttl INTEGER DEFAULT 3600, -- Cache TTL in seconds
    is_cached BOOLEAN DEFAULT FALSE,
    cache_hit BOOLEAN DEFAULT FALSE,

    -- Monitoring and analytics
    monitoring_data JSONB DEFAULT '{}', -- Detailed monitoring data
    metrics JSONB DEFAULT '{}', -- Performance metrics
    benchmarks JSONB DEFAULT '{}', -- Benchmark comparisons

    -- Metadata
    tags JSONB DEFAULT '[]', -- Array of tags for categorization
    keywords JSONB DEFAULT '[]', -- Search keywords
    attributes JSONB DEFAULT '{}', -- Custom attributes
    metadata JSONB DEFAULT '{}', -- Additional metadata

    -- Versioning
    version INTEGER DEFAULT 1,
    is_latest BOOLEAN DEFAULT TRUE,
    version_notes TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ,

    -- Constraints
    CHECK (execution_type IN ('analysis', 'generation', 'optimization', 'research', 'validation', 'planning')),
    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout')),
    CHECK (duration_ms >= 0),
    CHECK (estimated_duration_ms >= 0),
    CHECK (timeout_ms > 0),
    CHECK (tokens_used >= 0),
    CHECK (cost_estimate >= 0),
    CHECK (memory_usage_mb >= 0),
    CHECK (cpu_usage_percent >= 0 AND cpu_usage_percent <= 100),
    CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CHECK (quality_score >= 0 AND quality_score <= 1),
    CHECK (accuracy_score >= 0 AND accuracy_score <= 1),
    CHECK (completeness_score >= 0 AND completeness_score <= 1),
    CHECK (retry_count >= 0 AND retry_count <= max_retries),
    CHECK (max_retries >= 0),
    CHECK (user_rating >= 1 AND user_rating <= 5),
    CHECK (cache_ttl >= 0),
    CHECK (version >= 1)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_executions_workspace_id ON public.agent_executions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_type ON public.agent_executions(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent_name ON public.agent_executions(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_executions_execution_type ON public.agent_executions(execution_type);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON public.agent_executions(status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_started_at ON public.agent_executions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at ON public.agent_executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_initiated_by ON public.agent_executions(initiated_by);
CREATE INDEX IF NOT EXISTS idx_agent_executions_completed_at ON public.agent_executions(completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_duration_ms ON public.agent_executions(duration_ms);
CREATE INDEX IF NOT EXISTS idx_agent_executions_tokens_used ON public.agent_executions(tokens_used DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_cost_estimate ON public.agent_executions(cost_estimate DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_confidence_score ON public.agent_executions(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_quality_score ON public.agent_executions(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_accuracy_score ON public.agent_executions(accuracy_score DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_foundation_id ON public.agent_executions(foundation_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_icp_profile_id ON public.agent_executions(icp_profile_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_campaign_id ON public.agent_executions(campaign_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_move_id ON public.agent_executions(move_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_move_task_id ON public.agent_executions(move_task_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_blackbox_strategy_id ON public.agent_executions(blackbox_strategy_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_muse_asset_id ON public.agent_executions(muse_asset_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_cache_key ON public.agent_executions(cache_key);
CREATE INDEX IF NOT EXISTS idx_agent_executions_is_cached ON public.agent_executions(is_cached);
CREATE INDEX IF NOT EXISTS idx_agent_executions_user_rating ON public.agent_executions(user_rating DESC);
CREATE INDEX IF NOT EXISTS idx_agent_executions_is_latest ON public.agent_executions(is_latest);
CREATE INDEX IF NOT EXISTS idx_agent_executions_tags ON public.agent_executions USING GIN (tags) WITH (jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_agent_executions_keywords ON public.agent_executions USING GIN (keywords) WITH (jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_agent_executions_attributes ON public.agent_executions USING GIN (attributes) WITH (jsonb_path_ops);

-- Vector index for semantic search
CREATE INDEX IF NOT EXISTS idx_agent_executions_content_embedding
    ON public.agent_executions USING ivfflat (content_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Unique constraint on execution name per workspace
CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_executions_unique_name
    ON public.agent_executions(workspace_id, execution_name) WHERE status != 'draft';

-- Trigger for updated_at
CREATE TRIGGER agent_executions_updated_at
    BEFORE UPDATE ON public.agent_executions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE public.agent_executions ENABLE ROW LEVEL SECURITY;
