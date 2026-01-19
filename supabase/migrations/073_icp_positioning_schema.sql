-- ============================================================================
-- Migration: 073_icp_positioning_schema.sql
-- Purpose: Enhanced ICP and positioning tables for onboarding
-- ============================================================================

-- Enhanced ICP Profiles Table (extends existing icp_profiles)
CREATE TABLE IF NOT EXISTS onboarding_icp_deep (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    
    -- ICP basics
    icp_id TEXT NOT NULL,
    name TEXT NOT NULL,
    tier TEXT DEFAULT 'primary', -- primary, secondary, tertiary
    description TEXT,
    
    -- Firmographics
    firmographics JSONB DEFAULT '{}'::jsonb,
    
    -- Psychographics
    psychographics JSONB DEFAULT '{}'::jsonb,
    
    -- Pain points and triggers
    pain_points JSONB DEFAULT '[]'::jsonb,
    trigger_events JSONB DEFAULT '[]'::jsonb,
    disqualifiers JSONB DEFAULT '[]'::jsonb,
    
    -- Buyer info
    buyer_types JSONB DEFAULT '[]'::jsonb,
    key_stakeholders JSONB DEFAULT '[]'::jsonb,
    
    -- Messaging
    key_messages JSONB DEFAULT '[]'::jsonb,
    objections JSONB DEFAULT '[]'::jsonb,
    
    -- Sales metrics
    estimated_deal_size TEXT,
    sales_cycle_length TEXT,
    win_rate_estimate TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(session_id, icp_id)
);

-- Positioning Statements Table
CREATE TABLE IF NOT EXISTS onboarding_positioning_statements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    
    -- Statement info
    statement_id TEXT NOT NULL,
    statement_type TEXT NOT NULL, -- full, elevator, tagline, value_prop, category
    framework TEXT NOT NULL, -- classic, challenger, category_creator, benefit_focused, comparison
    
    -- Content
    statement TEXT NOT NULL,
    audience TEXT,
    key_elements JSONB DEFAULT '{}'::jsonb,
    
    -- Quality
    score DECIMAL(3,2) DEFAULT 0.50,
    is_primary BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_approved BOOLEAN DEFAULT FALSE,
    notes TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(session_id, statement_id)
);

-- Only We Claims Table
CREATE TABLE IF NOT EXISTS onboarding_only_we_claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    
    claim TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_source TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Positioning Matrix Table
CREATE TABLE IF NOT EXISTS onboarding_positioning_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE UNIQUE,
    
    axes JSONB DEFAULT '[]'::jsonb,
    your_position JSONB DEFAULT '{}'::jsonb,
    competitor_positions JSONB DEFAULT '{}'::jsonb,
    white_space TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_icp_deep_session ON onboarding_icp_deep(session_id);
CREATE INDEX IF NOT EXISTS idx_icp_deep_workspace ON onboarding_icp_deep(workspace_id);
CREATE INDEX IF NOT EXISTS idx_icp_deep_tier ON onboarding_icp_deep(tier);

CREATE INDEX IF NOT EXISTS idx_positioning_session ON onboarding_positioning_statements(session_id);
CREATE INDEX IF NOT EXISTS idx_positioning_workspace ON onboarding_positioning_statements(workspace_id);
CREATE INDEX IF NOT EXISTS idx_positioning_primary ON onboarding_positioning_statements(is_primary);

CREATE INDEX IF NOT EXISTS idx_only_we_session ON onboarding_only_we_claims(session_id);

-- Enable RLS
ALTER TABLE onboarding_icp_deep ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_positioning_statements ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_only_we_claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_positioning_matrix ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own workspace ICP deep"
    ON onboarding_icp_deep FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage ICP deep in own workspace"
    ON onboarding_icp_deep FOR ALL
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can view own workspace positioning"
    ON onboarding_positioning_statements FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage positioning in own workspace"
    ON onboarding_positioning_statements FOR ALL
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can view own workspace only we claims"
    ON onboarding_only_we_claims FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage only we claims in own workspace"
    ON onboarding_only_we_claims FOR ALL
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can view own workspace positioning matrix"
    ON onboarding_positioning_matrix FOR SELECT
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage positioning matrix in own workspace"
    ON onboarding_positioning_matrix FOR ALL
    USING (workspace_id IN (SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()));

-- Triggers
CREATE TRIGGER trigger_icp_deep_updated_at
    BEFORE UPDATE ON onboarding_icp_deep
    FOR EACH ROW EXECUTE FUNCTION update_proof_points_updated_at();

CREATE TRIGGER trigger_positioning_updated_at
    BEFORE UPDATE ON onboarding_positioning_statements
    FOR EACH ROW EXECUTE FUNCTION update_proof_points_updated_at();

CREATE TRIGGER trigger_matrix_updated_at
    BEFORE UPDATE ON onboarding_positioning_matrix
    FOR EACH ROW EXECUTE FUNCTION update_proof_points_updated_at();

-- ============================================================================
-- End of Migration
-- ============================================================================
