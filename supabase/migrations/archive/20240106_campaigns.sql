-- Campaigns table (product-specific)
-- Migration: 20240106_campaigns.sql
-- Description: Marketing campaigns with workspace isolation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Campaigns table
CREATE TABLE IF NOT EXISTS public.campaigns (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Workspace isolation
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Campaign metadata
    name TEXT NOT NULL,
    description TEXT,
    campaign_type TEXT NOT NULL, -- e.g., 'email', 'social', 'content', 'advertising', 'event'
    status TEXT DEFAULT 'draft', -- draft, scheduled, active, paused, completed, cancelled
    priority INTEGER DEFAULT 3, -- 1=High, 2=Medium, 3=Low, 4=Background

    -- Campaign objectives
    primary_goal TEXT NOT NULL, -- e.g., 'lead_generation', 'brand_awareness', 'sales', 'engagement'
    secondary_goals JSONB DEFAULT '[]', -- Array of secondary goals
    target_audience TEXT,
    target_icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,

    -- Timeline and scheduling
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    duration_days INTEGER,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern TEXT, -- e.g., 'weekly', 'monthly', 'quarterly'
    next_run_date TIMESTAMPTZ,

    -- Budget and resources
    budget_total DECIMAL(10,2) DEFAULT 0.00,
    budget_spent DECIMAL(10,2) DEFAULT 0.00,
    budget_currency TEXT DEFAULT 'USD',
    cost_per_lead DECIMAL(10,2) DEFAULT 0.00,
    expected_roi DECIMAL(5,2) DEFAULT 0.00,

    -- Content and messaging
    headline TEXT,
    tagline TEXT,
    body_content TEXT,
    call_to_action TEXT,
    value_proposition TEXT,
    key_messages JSONB DEFAULT '[]', -- Array of key messages

    -- Creative assets
    assets JSONB DEFAULT '[]', -- Array of asset references (images, videos, documents)
    brand_guidelines JSONB DEFAULT '{}', -- Brand guidelines and constraints
    creative_brief TEXT,

    -- Channels and distribution
    channels JSONB DEFAULT '[]', -- Array of channels (email, social, web, etc.)
    distribution_list JSONB DEFAULT '[]', -- Target distribution lists
    platform_configs JSONB DEFAULT '{}', -- Platform-specific configurations

    -- Performance tracking
    target_metrics JSONB DEFAULT '[]', -- Array of target KPIs
    current_metrics JSONB DEFAULT '{}', -- Current performance metrics
    conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    engagement_rate DECIMAL(5,2) DEFAULT 0.00,
    click_through_rate DECIMAL(5,2) DEFAULT 0.00,

    -- AI-generated content
    ai_suggestions JSONB DEFAULT '{}', -- AI-generated suggestions for optimization
    ai_confidence DECIMAL(3,2) DEFAULT 0.00,
    ai_generated_at TIMESTAMPTZ,
    ai_optimization_score DECIMAL(3,2) DEFAULT 0.00,

    -- Quality and compliance
    quality_score DECIMAL(3,2) DEFAULT 0.00, -- 0.00 to 1.00
    compliance_status TEXT DEFAULT 'pending', -- pending, approved, rejected
    compliance_notes TEXT,
    legal_review BOOLEAN DEFAULT FALSE,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMPTZ,

    -- Analytics and reporting
    analytics_data JSONB DEFAULT '{}', -- Detailed analytics data
    a_b_test_results JSONB DEFAULT '{}', -- A/B test results
    performance_summary TEXT,
    lessons_learned TEXT,

    -- Metadata
    tags JSONB DEFAULT '[]', -- Array of tags for categorization
    category TEXT,
    industry TEXT,
    campaign_season TEXT, -- e.g., 'Q1_2026', 'summer_2026', 'holiday_2026'

    -- Ownership and tracking
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    campaign_manager UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    archived_at TIMESTAMPTZ,

    -- Constraints
    CHECK (priority >= 1 AND priority <= 4),
    CHECK (duration_days > 0),
    CHECK (budget_total >= 0),
    CHECK (budget_spent >= 0),
    CHECK (budget_spent <= budget_total),
    CHECK (cost_per_lead >= 0),
    CHECK (expected_roi >= 0),
    CHECK (conversion_rate >= 0 AND conversion_rate <= 100),
    CHECK (engagement_rate >= 0 AND engagement_rate <= 100),
    CHECK (click_through_rate >= 0 AND click_through_rate <= 100),
    CHECK (quality_score >= 0 AND quality_score <= 1),
    CHECK (ai_confidence >= 0 AND ai_confidence <= 1),
    CHECK (ai_optimization_score >= 0 AND ai_optimization_score <= 1)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_campaigns_workspace_id ON public.campaigns(workspace_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_campaign_type ON public.campaigns(campaign_type);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON public.campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_priority ON public.campaigns(priority);
CREATE INDEX IF NOT EXISTS idx_campaigns_start_date ON public.campaigns(start_date);
CREATE INDEX IF NOT EXISTS idx_campaigns_end_date ON public.campaigns(end_date);
CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON public.campaigns(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaigns_created_by ON public.campaigns(created_by);
CREATE INDEX IF NOT EXISTS idx_campaigns_campaign_manager ON public.campaigns(campaign_manager);
CREATE INDEX IF NOT EXISTS idx_campaigns_target_icp_profile_id ON public.campaigns(target_icp_profile_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_next_run_date ON public.campaigns(next_run_date);
CREATE INDEX IF NOT EXISTS idx_campaigns_tags ON public.campaigns USING GIN (tags) WITH (jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_campaigns_channels ON public.campaigns USING GIN (channels) WITH (jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_campaigns_target_metrics ON public.campaigns USING GIN (target_metrics) WITH (jsonb_path_ops);

-- Vector index for semantic search
CREATE INDEX IF NOT EXISTS idx_campaigns_content_embedding
    ON public.campaigns USING ivfflat (content_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Unique constraint on campaign name per workspace
CREATE UNIQUE INDEX IF NOT EXISTS idx_campaigns_unique_name
    ON public.campaigns(workspace_id, name) WHERE status != 'draft';

-- Trigger for updated_at
CREATE TRIGGER campaigns_updated_at
    BEFORE UPDATE ON public.campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE public.campaigns ENABLE ROW LEVEL SECURITY;
