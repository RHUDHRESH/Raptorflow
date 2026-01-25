-- ============================================================================
-- ONBOARDING ENHANCED SCHEMA
-- Migration for 23-step onboarding vision
-- Created: January 2026
-- ============================================================================

-- 1. Evidence Vault Enhanced Columns
ALTER TABLE IF EXISTS evidence_vault
ADD COLUMN IF NOT EXISTS document_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS classification_confidence FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS extracted_content JSONB DEFAULT '{}';

-- Create index for document type lookups
CREATE INDEX IF NOT EXISTS idx_evidence_vault_document_type
ON evidence_vault(document_type);

-- 2. Contradictions Table
CREATE TABLE IF NOT EXISTS onboarding_contradictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    workspace_id UUID NOT NULL,
    claim1 TEXT NOT NULL,
    claim1_source TEXT,
    claim2 TEXT NOT NULL,
    claim2_source TEXT,
    contradiction_type VARCHAR(50) DEFAULT 'semantic',
    severity VARCHAR(20) DEFAULT 'medium',
    confidence FLOAT DEFAULT 0.5,
    explanation TEXT,
    suggested_resolution TEXT,
    resolution TEXT,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID,
    auto_resolvable BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_contradictions_workspace FOREIGN KEY (workspace_id)
        REFERENCES workspaces(id) ON DELETE CASCADE
);

-- Indexes for contradictions
CREATE INDEX IF NOT EXISTS idx_contradictions_session ON onboarding_contradictions(session_id);
CREATE INDEX IF NOT EXISTS idx_contradictions_workspace ON onboarding_contradictions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_contradictions_severity ON onboarding_contradictions(severity);

-- 3. Market Insights Table (from Reddit/web research)
CREATE TABLE IF NOT EXISTS onboarding_market_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    workspace_id UUID NOT NULL,
    insight_type VARCHAR(50) NOT NULL, -- pain_point, desire, objection, opportunity
    category VARCHAR(50), -- technical, financial, process, ux, etc.
    description TEXT NOT NULL,
    quote TEXT, -- verbatim quote from source
    source_url TEXT,
    source_platform VARCHAR(50), -- reddit, twitter, forum, review_site
    source_subreddit VARCHAR(100),
    sentiment FLOAT DEFAULT 0.0, -- -1 to 1
    frequency VARCHAR(20) DEFAULT 'occasional', -- rare, occasional, common, very_common
    severity FLOAT DEFAULT 0.5,
    relevance_score FLOAT DEFAULT 0.5,
    suggested_solution TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_market_insights_workspace FOREIGN KEY (workspace_id)
        REFERENCES workspaces(id) ON DELETE CASCADE
);

-- Indexes for market insights
CREATE INDEX IF NOT EXISTS idx_market_insights_session ON onboarding_market_insights(session_id);
CREATE INDEX IF NOT EXISTS idx_market_insights_workspace ON onboarding_market_insights(workspace_id);
CREATE INDEX IF NOT EXISTS idx_market_insights_type ON onboarding_market_insights(insight_type);

-- 4. Auto-discovered Competitors Table
CREATE TABLE IF NOT EXISTS onboarding_competitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    workspace_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    website_url TEXT,
    competitor_type VARCHAR(50) DEFAULT 'direct', -- direct, indirect, status_quo
    core_claim TEXT,
    target_audience TEXT,
    pricing_model VARCHAR(50),
    pricing_range VARCHAR(100),
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    features JSONB DEFAULT '[]',
    market_position VARCHAR(50), -- leader, challenger, niche, follower
    sentiment_score FLOAT DEFAULT 0.0,
    mention_count INTEGER DEFAULT 0,
    discovered_by VARCHAR(50) DEFAULT 'ai', -- ai, manual (should be ai only per vision)
    discovery_source TEXT, -- reddit, web_scrape, user_mention
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_competitors_workspace FOREIGN KEY (workspace_id)
        REFERENCES workspaces(id) ON DELETE CASCADE
);

-- Indexes for competitors
CREATE INDEX IF NOT EXISTS idx_competitors_session ON onboarding_competitors(session_id);
CREATE INDEX IF NOT EXISTS idx_competitors_workspace ON onboarding_competitors(workspace_id);
CREATE INDEX IF NOT EXISTS idx_competitors_type ON onboarding_competitors(competitor_type);

-- 5. Positioning Table
CREATE TABLE IF NOT EXISTS onboarding_positioning (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    workspace_id UUID NOT NULL,

    -- Perceptual Map Data
    perceptual_map_option INTEGER DEFAULT 1, -- 1, 2, or 3
    primary_axis_name VARCHAR(100),
    primary_axis_low VARCHAR(100),
    primary_axis_high VARCHAR(100),
    secondary_axis_name VARCHAR(100),
    secondary_axis_low VARCHAR(100),
    secondary_axis_high VARCHAR(100),
    position_x FLOAT DEFAULT 0.5,
    position_y FLOAT DEFAULT 0.5,

    -- Category Path
    category_path VARCHAR(50), -- safe, clever, bold
    category_rationale TEXT,

    -- Position Grid
    market_served VARCHAR(50), -- smb, mid_market, enterprise, startups
    category_name VARCHAR(255),
    tribe VARCHAR(100), -- growth_teams, founders, marketing_leaders
    story_type VARCHAR(100), -- david_vs_goliath, built_by_practitioners, opinionated

    -- Strategy
    positioning_strategy VARCHAR(50), -- cost_leader, differentiator, niche, quality, innovation, service
    competitive_angle TEXT,
    target_audience TEXT,

    -- Confidence
    confidence_score FLOAT DEFAULT 0.5,
    ai_rationale TEXT,

    -- Metadata
    is_selected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_positioning_workspace FOREIGN KEY (workspace_id)
        REFERENCES workspaces(id) ON DELETE CASCADE
);

-- Indexes for positioning
CREATE INDEX IF NOT EXISTS idx_positioning_session ON onboarding_positioning(session_id);
CREATE INDEX IF NOT EXISTS idx_positioning_workspace ON onboarding_positioning(workspace_id);
CREATE INDEX IF NOT EXISTS idx_positioning_selected ON onboarding_positioning(is_selected);

-- 6. Extracted Facts Table (for step 2-3)
CREATE TABLE IF NOT EXISTS onboarding_extracted_facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    workspace_id UUID NOT NULL,
    fact_code VARCHAR(50) NOT NULL, -- F-COM-001, F-POS-002, etc.
    category VARCHAR(50) NOT NULL, -- company, positioning, audience, market, product, revenue, team, metrics, competitors
    label VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.5,
    status VARCHAR(20) DEFAULT 'pending', -- pending, verified, rejected, needs_review
    extraction_method VARCHAR(50), -- pattern_matching, keyword_extraction, semantic_analysis, ai_insight
    source_type VARCHAR(50), -- file, url
    source_name TEXT,
    source_id UUID,
    context TEXT,
    verified_by UUID,
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_facts_workspace FOREIGN KEY (workspace_id)
        REFERENCES workspaces(id) ON DELETE CASCADE
);

-- Indexes for extracted facts
CREATE INDEX IF NOT EXISTS idx_facts_session ON onboarding_extracted_facts(session_id);
CREATE INDEX IF NOT EXISTS idx_facts_workspace ON onboarding_extracted_facts(workspace_id);
CREATE INDEX IF NOT EXISTS idx_facts_category ON onboarding_extracted_facts(category);
CREATE INDEX IF NOT EXISTS idx_facts_status ON onboarding_extracted_facts(status);

-- Enable RLS on all new tables
ALTER TABLE onboarding_contradictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_market_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_positioning ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_extracted_facts ENABLE ROW LEVEL SECURITY;

-- RLS Policies for workspace isolation
CREATE POLICY "workspace_isolation_contradictions" ON onboarding_contradictions
    FOR ALL USING (workspace_id IN (
        SELECT workspace_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "workspace_isolation_market_insights" ON onboarding_market_insights
    FOR ALL USING (workspace_id IN (
        SELECT workspace_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "workspace_isolation_competitors" ON onboarding_competitors
    FOR ALL USING (workspace_id IN (
        SELECT workspace_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "workspace_isolation_positioning" ON onboarding_positioning
    FOR ALL USING (workspace_id IN (
        SELECT workspace_id FROM profiles WHERE id = auth.uid()
    ));

CREATE POLICY "workspace_isolation_facts" ON onboarding_extracted_facts
    FOR ALL USING (workspace_id IN (
        SELECT workspace_id FROM profiles WHERE id = auth.uid()
    ));

-- Update trigger for all tables
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_contradictions_updated_at BEFORE UPDATE ON onboarding_contradictions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_market_insights_updated_at BEFORE UPDATE ON onboarding_market_insights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitors_updated_at BEFORE UPDATE ON onboarding_competitors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positioning_updated_at BEFORE UPDATE ON onboarding_positioning
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_facts_updated_at BEFORE UPDATE ON onboarding_extracted_facts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
