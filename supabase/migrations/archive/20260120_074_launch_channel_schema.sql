-- ============================================================================
-- Migration: 074_launch_channel_schema.sql
-- Purpose: Add launch readiness and channel strategy tables
-- ============================================================================

-- Launch Readiness Checklist Table
CREATE TABLE IF NOT EXISTS onboarding_launch_readiness (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE UNIQUE,

    -- Overall metrics
    overall_score DECIMAL(5,2) DEFAULT 0.00,
    ready_count INTEGER DEFAULT 0,
    total_items INTEGER DEFAULT 0,
    blockers_count INTEGER DEFAULT 0,
    launch_ready BOOLEAN DEFAULT FALSE,

    -- Recommendations
    launch_date_recommendation TEXT,
    next_steps JSONB DEFAULT '[]'::jsonb,

    -- Category breakdown
    by_category JSONB DEFAULT '{}'::jsonb,

    -- Detailed items
    checklist_items JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    checked_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Channel Strategy Table
CREATE TABLE IF NOT EXISTS onboarding_channel_strategy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE UNIQUE,

    -- Channel recommendations
    primary_channels JSONB DEFAULT '[]'::jsonb,
    secondary_channels JSONB DEFAULT '[]'::jsonb,
    future_channels JSONB DEFAULT '[]'::jsonb,

    -- Budget and timeline
    budget_allocation JSONB DEFAULT '{}'::jsonb,
    timeline JSONB DEFAULT '{}'::jsonb,
    budget_tier TEXT DEFAULT 'growth',

    -- Metrics
    total_score DECIMAL(5,2) DEFAULT 0.00,

    -- Recommendations
    recommendations JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Channel Performance Tracking (future use)
CREATE TABLE IF NOT EXISTS onboarding_channel_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,

    channel_type TEXT NOT NULL,
    channel_name TEXT NOT NULL,

    -- Performance metrics
    spend DECIMAL(12,2) DEFAULT 0.00,
    leads INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue DECIMAL(12,2) DEFAULT 0.00,

    -- Calculated metrics
    cpl DECIMAL(10,2), -- Cost per lead
    cac DECIMAL(10,2), -- Customer acquisition cost
    roas DECIMAL(6,2), -- Return on ad spend

    -- Period
    period_start DATE,
    period_end DATE,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_launch_readiness_session ON onboarding_launch_readiness(session_id);
CREATE INDEX IF NOT EXISTS idx_launch_readiness_workspace ON onboarding_launch_readiness(workspace_id);

CREATE INDEX IF NOT EXISTS idx_channel_strategy_session ON onboarding_channel_strategy(session_id);
CREATE INDEX IF NOT EXISTS idx_channel_strategy_workspace ON onboarding_channel_strategy(workspace_id);

CREATE INDEX IF NOT EXISTS idx_channel_performance_session ON onboarding_channel_performance(session_id);
CREATE INDEX IF NOT EXISTS idx_channel_performance_type ON onboarding_channel_performance(channel_type);

-- Enable RLS
ALTER TABLE onboarding_launch_readiness ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_channel_strategy ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_channel_performance ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own workspace launch readiness"
    ON onboarding_launch_readiness FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage launch readiness in own workspace"
    ON onboarding_launch_readiness FOR ALL
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can view own workspace channel strategy"
    ON onboarding_channel_strategy FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage channel strategy in own workspace"
    ON onboarding_channel_strategy FOR ALL
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can view own workspace channel performance"
    ON onboarding_channel_performance FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage channel performance in own workspace"
    ON onboarding_channel_performance FOR ALL
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

-- Triggers
CREATE TRIGGER trigger_launch_readiness_updated_at
    BEFORE UPDATE ON onboarding_launch_readiness
    FOR EACH ROW EXECUTE FUNCTION update_proof_points_updated_at();

CREATE TRIGGER trigger_channel_strategy_updated_at
    BEFORE UPDATE ON onboarding_channel_strategy
    FOR EACH ROW EXECUTE FUNCTION update_proof_points_updated_at();

-- ============================================================================
-- End of Migration
-- ============================================================================
