-- Blackbox Strategies table (product-specific)
-- Migration: 20240108_blackbox_strategies.sql
-- Description: Strategic blackbox approaches and tactics with workspace isolation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Blackbox Strategies table
CREATE TABLE IF NOT EXISTS public.blackbox_strategies (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Workspace isolation
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Strategy metadata
    name TEXT NOT NULL,
    description TEXT,
    strategy_type TEXT NOT NULL, -- e.g., 'growth_hack', 'marketing_psyop', 'sales_tactic', 'product_innovation'
    category TEXT NOT NULL, -- e.g., 'growth', 'marketing', 'sales', 'product', 'operations'
    status TEXT DEFAULT 'draft', -- draft, testing, active, paused, deprecated, archived
    priority INTEGER DEFAULT 3, -- 1=High, 2=Medium, 3=Low, 4=Background

    -- Strategy details
    objective TEXT NOT NULL,
    hypothesis TEXT, -- The core hypothesis being tested
    approach TEXT, -- How the strategy works
    expected_outcome TEXT,
    success_criteria JSONB DEFAULT '[]', -- Array of success criteria

    -- Blackbox methodology
    is_blackbox BOOLEAN DEFAULT TRUE, -- Whether this is a blackbox approach
    blackbox_level TEXT DEFAULT 'partial', -- partial, full, experimental
    uncertainty_level TEXT DEFAULT 'high', -- low, medium, high, extreme
    learning_approach TEXT, -- e.g., 'iterative', 'experimental', 'data_driven'

    -- Implementation details
    implementation_steps JSONB DEFAULT '[]', -- Array of implementation steps
    required_resources JSONB DEFAULT '[]', -- Resources needed
    time_investment INTEGER DEFAULT 0, -- Estimated hours
    budget_estimate DECIMAL(10,2) DEFAULT 0.00,

    -- Target context
    target_audience TEXT,
    target_market TEXT,
    target_icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,
    foundation_id UUID REFERENCES foundations(id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,

    -- Testing and validation
    test_design JSONB DEFAULT '{}', -- A/B test or experimental design
    test_duration_days INTEGER DEFAULT 30,
    control_group TEXT, -- Description of control group
    test_metrics JSONB DEFAULT '[]', -- Metrics to track

    -- Results and outcomes
    actual_results JSONB DEFAULT '{}', -- Actual test results
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    roi_measured DECIMAL(5,2) DEFAULT 0.00,
    conversion_improvement DECIMAL(5,2) DEFAULT 0.00,

    -- Learning and insights
    key_insights JSONB DEFAULT '[]', -- Key learnings from testing
    unexpected_outcomes JSONB DEFAULT '[]', -- Unexpected results
    refinements JSONB DEFAULT '[]', -- Strategy refinements made
    lessons_learned TEXT,

    -- AI-generated content
    ai_suggestion TEXT,
    ai_confidence DECIMAL(3,2) DEFAULT 0.00,
    ai_generated_at TIMESTAMPTZ,
    ai_optimization_score DECIMAL(3,2) DEFAULT 0.00,

    -- Risk assessment
    risk_level TEXT DEFAULT 'medium', -- low, medium, high, extreme
    risk_factors JSONB DEFAULT '[]', -- Array of risk factors
    mitigation_strategies JSONB DEFAULT '[]', -- Risk mitigation approaches
    compliance_check BOOLEAN DEFAULT FALSE,

    -- Documentation and sharing
    documentation TEXT,
    case_study TEXT,
    shareable_insights JSONB DEFAULT '[]', -- Insights that can be shared
    publication_status TEXT DEFAULT 'internal', -- internal, team, public, published

    -- Performance metrics
    views INTEGER DEFAULT 0,
    downloads INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    adoption_rate DECIMAL(5,2) DEFAULT 0.00,
    satisfaction_score DECIMAL(3,2) DEFAULT 0.00,

    -- Metadata
    tags JSONB DEFAULT '[]', -- Array of tags for categorization
    keywords JSONB DEFAULT '[]', -- SEO keywords
    attributes JSONB DEFAULT '{}', -- Custom attributes
    metadata JSONB DEFAULT '{}', -- Additional metadata

    -- Versioning
    version INTEGER DEFAULT 1,
    is_latest BOOLEAN DEFAULT TRUE,
    version_notes TEXT,

    -- Ownership and tracking
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    tested_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ,

    -- Constraints
    CHECK (priority >= 1 AND priority <= 4),
    CHECK (time_investment >= 0),
    CHECK (budget_estimate >= 0),
    CHECK (success_rate >= 0 AND success_rate <= 100),
    CHECK (roi_measured >= 0),
    CHECK (conversion_improvement >= 0 AND conversion_improvement <= 100),
    CHECK (adoption_rate >= 0 AND adoption_rate <= 100),
    CHECK (satisfaction_score >= 0 AND satisfaction_score <= 1),
    CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    CHECK (ai_optimization_score >= 0 AND ai_optimization_score <= 1),
    CHECK (version >= 1)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_workspace_id ON public.blackbox_strategies(workspace_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_strategy_type ON public.blackbox_strategies(strategy_type);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_category ON public.blackbox_strategies(category);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_status ON public.blackbox_strategies(status);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_priority ON public.blackbox_strategies(priority);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_blackbox_level ON public.blackbox_strategies(blackbox_level);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_uncertainty_level ON public.blackbox_strategies(uncertainty_level);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_is_blackbox ON public.blackbox_strategies(is_blackbox);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_created_at ON public.blackbox_strategies(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_created_by ON public.blackbox_strategies(created_by);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_tested_at ON public.blackbox_strategies(tested_at DESC);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_published_at ON public.blackbox_strategies(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_success_rate ON public.blackbox_strategies(success_rate DESC);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_roi_measured ON public.blackbox_strategies(roi_measured DESC);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_foundation_id ON public.blackbox_strategies(foundation_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_icp_profile_id ON public.blackbox_strategies(target_icp_profile_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_campaign_id ON public.blackbox_strategies(campaign_id);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_is_latest ON public.blackbox_strategies(is_latest);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_tags ON public.blackbox_strategies USING GIN (tags) WITH (jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_keywords ON public.blackbox_strategies USING GIN (keywords) WITH (jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_attributes ON public.blackbox_strategies USING GIN (attributes) WITH (jsonb_path_ops);

-- Vector index for semantic search
CREATE INDEX IF NOT EXISTS idx_blackbox_strategies_content_embedding
    ON public.blackbox_strategies USING ivfflat (content_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Unique constraint on strategy name per workspace
CREATE UNIQUE INDEX IF NOT EXISTS idx_blackbox_strategies_unique_name
    ON public.blackbox_strategies(workspace_id, name) WHERE status != 'draft';

-- Trigger for updated_at
CREATE TRIGGER blackbox_strategies_updated_at
    BEFORE UPDATE ON public.blackbox_strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE public.blackbox_strategies ENABLE ROW LEVEL SECURITY;
