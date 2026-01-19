-- Migration: Update onboarding to support 23 steps
-- Created: January 16, 2026
-- Purpose: Add new onboarding steps and supporting tables for enhanced AI agents

-- First, let's add the new onboarding steps to the existing structure
-- We'll update the onboarding_sessions table to support the new step flow

-- Add new columns for enhanced onboarding tracking
ALTER TABLE onboarding_sessions 
ADD COLUMN IF NOT EXISTS current_step_index INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS step_progress JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS ai_processing_status JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS evidence_classification JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS extracted_facts JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS contradictions_detected JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS reddit_research_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS perceptual_map_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS neuroscience_copy_data JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS channel_recommendations JSONB DEFAULT '{}';

-- Create evidence classifications table
CREATE TABLE IF NOT EXISTS evidence_classifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    evidence_id UUID,
    evidence_type VARCHAR(50) NOT NULL,
    confidence DECIMAL(3,2),
    reasoning TEXT,
    key_indicators JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create extracted facts table
CREATE TABLE IF NOT EXISTS extracted_facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    fact_id VARCHAR(20) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    label VARCHAR(200) NOT NULL,
    value TEXT NOT NULL,
    confidence DECIMAL(3,2),
    sources JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'pending',
    extraction_method VARCHAR(50),
    context TEXT,
    contradictions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create contradictions table
CREATE TABLE IF NOT EXISTS fact_contradictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    contradiction_id VARCHAR(20) UNIQUE NOT NULL,
    type VARCHAR(30) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    conflicting_facts JSONB DEFAULT '[]',
    confidence DECIMAL(3,2),
    explanation TEXT,
    suggested_resolution TEXT,
    auto_resolvable BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create reddit research table
CREATE TABLE IF NOT EXISTS reddit_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    search_query TEXT NOT NULL,
    posts_analyzed INTEGER DEFAULT 0,
    subreddits_analyzed JSONB DEFAULT '[]',
    pain_points JSONB DEFAULT '[]',
    market_insights JSONB DEFAULT '[]',
    competitor_mentions JSONB DEFAULT '[]',
    sentiment_analysis JSONB DEFAULT '{}',
    recommendations JSONB DEFAULT '[]',
    research_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create perceptual maps table
CREATE TABLE IF NOT EXISTS perceptual_maps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    primary_axis JSONB NOT NULL,
    secondary_axis JSONB NOT NULL,
    current_position JSONB NOT NULL,
    competitors JSONB DEFAULT '[]',
    positioning_options JSONB DEFAULT '[]',
    market_gaps JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    analysis_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create neuroscience copy variants table
CREATE TABLE IF NOT EXISTS neuroscience_copy_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    variant_id VARCHAR(20) UNIQUE NOT NULL,
    text TEXT NOT NULL,
    principle VARCHAR(30) NOT NULL,
    copy_type VARCHAR(30) NOT NULL,
    tone VARCHAR(20) NOT NULL,
    effectiveness_score DECIMAL(3,2),
    emotional_impact DECIMAL(3,2),
    clarity_score DECIMAL(3,2),
    persuasion_score DECIMAL(3,2),
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create channel strategy table
CREATE TABLE IF NOT EXISTS channel_strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    recommendations JSONB DEFAULT '[]',
    budget_allocation JSONB DEFAULT '{}',
    timeline JSONB DEFAULT '{}',
    resource_requirements JSONB DEFAULT '{}',
    synergy_opportunities JSONB DEFAULT '[]',
    risk_assessment JSONB DEFAULT '{}',
    expected_roi JSONB DEFAULT '{}',
    implementation_roadmap JSONB DEFAULT '[]',
    market_insights JSONB DEFAULT '[]',
    competitor_channels JSONB DEFAULT '[]',
    seasonal_trends JSONB DEFAULT '{}',
    recommendations_summary TEXT,
    next_steps JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create onboarding step definitions table for the 23-step process
CREATE TABLE IF NOT EXISTS onboarding_step_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    step_number INTEGER UNIQUE NOT NULL,
    step_key VARCHAR(50) UNIQUE NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    step_description TEXT,
    step_type VARCHAR(30) DEFAULT 'processing', -- 'user_input', 'processing', 'review'
    estimated_duration_minutes INTEGER DEFAULT 5,
    required_previous_steps JSONB DEFAULT '[]',
    ai_agent_required VARCHAR(50),
    data_schema JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert the 23 onboarding step definitions
INSERT INTO onboarding_step_definitions (step_number, step_key, step_name, step_description, step_type, ai_agent_required) VALUES
(1, 'evidence_vault', 'Evidence Vault Collection', 'Collect and organize all business evidence documents', 'user_input', NULL),
(2, 'auto_extraction', 'AI-Powered Extraction', 'Automatically extract facts and insights from evidence', 'processing', 'extraction_orchestrator'),
(3, 'contradiction_check', 'Contradiction Detection', 'Identify inconsistencies and contradictions in extracted data', 'processing', 'contradiction_detector'),
(4, 'reddit_research', 'Reddit Market Research', 'Analyze Reddit for pain points and market intelligence', 'processing', 'reddit_researcher'),
(5, 'competitor_analysis', 'Competitor Analysis', 'Analyze competitive landscape and positioning', 'user_input', NULL),
(6, 'category_paths', 'Category Strategy Paths', 'Define safe/clever/bold strategic positioning options', 'processing', 'perceptual_map_generator'),
(7, 'capability_rating', 'Capability Assessment', 'Rate capabilities (Only You/Unique/Competitive/Table Stakes)', 'user_input', NULL),
(8, 'perceptual_map', 'AI Perceptual Mapping', 'Generate 3 strategic positioning options with AI', 'processing', 'perceptual_map_generator'),
(9, 'neuroscience_copy', 'Neuroscience Copywriting', 'Create compelling copy using 6 neuroscience principles', 'processing', 'neuroscience_copywriter'),
(10, 'focus_sacrifice', 'Focus & Sacrifice', 'Define what to focus on and what to sacrifice', 'user_input', NULL),
(11, 'icp_generation', 'Deep ICP Generation', 'Generate detailed Ideal Customer Profiles', 'processing', 'icp_architect'),
(12, 'messaging_rules', 'Messaging Rules', 'Define core messaging principles and rules', 'user_input', NULL),
(13, 'soundbites_merge', 'Soundbites Integration', 'Merge and optimize key messaging soundbites', 'user_input', NULL),
(14, 'channel_strategy', 'Channel Strategy', 'AI-powered channel recommendations and strategy', 'processing', 'channel_recommender'),
(15, 'tam_sam_som', 'Market Sizing Visualization', 'Create TAM/SAM/SOM market size analysis', 'processing', 'market_analyzer'),
(16, 'brand_voice', 'Brand Voice Definition', 'Define brand personality and communication style', 'user_input', NULL),
(17, 'guardrails', 'Strategic Guardrails', 'Set boundaries and constraints for strategy', 'user_input', NULL),
(18, 'icp_cohorts', 'ICP Cohort Creation', 'Create detailed customer cohorts and segments', 'user_input', NULL),
(19, 'market_research', 'Market Research', 'Comprehensive market analysis and insights', 'user_input', NULL),
(20, 'differentiators', 'Differentiator Definition', 'Define and validate competitive differentiators', 'user_input', NULL),
(21, 'proof_points', 'Proof Points Collection', 'Gather evidence and proof for claims', 'user_input', NULL),
(22, 'muse_calibration', 'Muse Calibration', 'Calibrate AI assistant with brand knowledge', 'processing', 'muse_calibrator'),
(23, 'move_strategy', 'Move Strategy Planning', 'Plan strategic moves and initiatives', 'user_input', NULL),
(24, 'campaign_planning', 'Campaign Planning', 'Plan initial marketing campaigns', 'user_input', NULL),
(25, 'blackbox_activation', 'Blackbox Activation', 'Activate AI-powered growth engine', 'processing', 'blackbox'),
(26, 'launch', 'Launch Preparation', 'Final preparation for go-to-market', 'review', NULL)
ON CONFLICT (step_number) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_evidence_classifications_session_id ON evidence_classifications(session_id);
CREATE INDEX IF NOT EXISTS idx_evidence_classifications_evidence_type ON evidence_classifications(evidence_type);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_session_id ON extracted_facts(session_id);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_category ON extracted_facts(category);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_status ON extracted_facts(status);
CREATE INDEX IF NOT EXISTS idx_fact_contradictions_session_id ON fact_contradictions(session_id);
CREATE INDEX IF NOT EXISTS idx_fact_contradictions_severity ON fact_contradictions(severity);
CREATE INDEX IF NOT EXISTS idx_reddit_research_session_id ON reddit_research(session_id);
CREATE INDEX IF NOT EXISTS idx_perceptual_maps_session_id ON perceptual_maps(session_id);
CREATE INDEX IF NOT EXISTS idx_neuroscience_copy_variants_session_id ON neuroscience_copy_variants(session_id);
CREATE INDEX IF NOT EXISTS idx_neuroscience_copy_variants_principle ON neuroscience_copy_variants(principle);
CREATE INDEX IF NOT EXISTS idx_channel_strategies_session_id ON channel_strategies(session_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_step_definitions_active ON onboarding_step_definitions(is_active);

-- Add RLS policies for new tables
ALTER TABLE evidence_classifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE extracted_facts ENABLE ROW LEVEL SECURITY;
ALTER TABLE fact_contradictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE reddit_research ENABLE ROW LEVEL SECURITY;
ALTER TABLE perceptual_maps ENABLE ROW LEVEL SECURITY;
ALTER TABLE neuroscience_copy_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE channel_strategies ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own evidence classifications" ON evidence_classifications
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM onboarding_sessions 
            WHERE workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can insert their own evidence classifications" ON evidence_classifications
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT id FROM onboarding_sessions 
            WHERE workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can update their own evidence classifications" ON evidence_classifications
    FOR UPDATE USING (
        session_id IN (
            SELECT id FROM onboarding_sessions 
            WHERE workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        )
    );

-- Similar policies for other tables (abbreviated for brevity)
CREATE POLICY "Users can manage their own extracted facts" ON extracted_facts
    FOR ALL USING (
        session_id IN (
            SELECT id FROM onboarding_sessions 
            WHERE workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can manage their own contradictions" ON fact_contradictions
    FOR ALL USING (
        session_id IN (
            SELECT id FROM onboarding_sessions 
            WHERE workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can manage their own reddit research" ON reddit_research
    FOR ALL USING (
        session_id IN (
            SELECT id FROM onboarding_sessions 
            WHERE workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can manage their own perceptual maps" ON perceptual_maps
    FOR ALL USING (
        session_id IN (
            SELECT id FROM onboarding_sessions 
            WHERE workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can manage their own copy variants" ON neuroscience_copy_variants
    FOR ALL USING (
        session_id IN (
            SELECT id FROM onboarding_sessions 
            WHERE workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can manage their own channel strategies" ON channel_strategies
    FOR ALL USING (
        session_id IN (
            SELECT id FROM onboarding_sessions 
            WHERE workspace_id IN (
                SELECT id FROM workspaces WHERE user_id = auth.uid()
            )
        )
    );

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
CREATE TRIGGER update_evidence_classifications_updated_at BEFORE UPDATE ON evidence_classifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_extracted_facts_updated_at BEFORE UPDATE ON extracted_facts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_onboarding_step_definitions_updated_at BEFORE UPDATE ON onboarding_step_definitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a function to get current step definition
CREATE OR REPLACE FUNCTION get_current_step_definition(p_session_id UUID)
RETURNS TABLE(
    step_number INTEGER,
    step_key VARCHAR(50),
    step_name VARCHAR(100),
    step_description TEXT,
    step_type VARCHAR(30),
    ai_agent_required VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        osd.step_number,
        osd.step_key,
        osd.step_name,
        osd.step_description,
        osd.step_type,
        osd.ai_agent_required
    FROM onboarding_step_definitions osd
    JOIN onboarding_sessions os ON os.current_step_index + 1 = osd.step_number
    WHERE os.id = p_session_id AND osd.is_active = TRUE
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Create a function to advance to next step
CREATE OR REPLACE FUNCTION advance_onboarding_step(p_session_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    current_step_index INTEGER;
    max_step_index INTEGER;
BEGIN
    -- Get current step index
    SELECT COALESCE(current_step_index, -1) INTO current_step_index
    FROM onboarding_sessions
    WHERE id = p_session_id;
    
    -- Get max step index
    SELECT MAX(step_number) - 1 INTO max_step_index
    FROM onboarding_step_definitions
    WHERE is_active = TRUE;
    
    -- Advance if not at max
    IF current_step_index < max_step_index THEN
        UPDATE onboarding_sessions
        SET current_step_index = current_step_index + 1,
            updated_at = NOW()
        WHERE id = p_session_id;
        
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get step progress
CREATE OR REPLACE FUNCTION get_onboarding_progress(p_session_id UUID)
RETURNS JSONB AS $$
DECLARE
    total_steps INTEGER;
    completed_steps INTEGER;
    progress_percentage DECIMAL(5,2);
    result JSONB;
BEGIN
    -- Get total steps
    SELECT COUNT(*) INTO total_steps
    FROM onboarding_step_definitions
    WHERE is_active = TRUE;
    
    -- Get completed steps (based on current_step_index)
    SELECT COALESCE(current_step_index, 0) INTO completed_steps
    FROM onboarding_sessions
    WHERE id = p_session_id;
    
    -- Calculate percentage
    progress_percentage := (completed_steps::DECIMAL / total_steps::DECIMAL) * 100;
    
    -- Build result
    result := jsonb_build_object(
        'total_steps', total_steps,
        'completed_steps', completed_steps,
        'progress_percentage', progress_percentage,
        'current_step', completed_steps + 1,
        'is_complete', completed_steps >= total_steps
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE evidence_classifications IS 'Stores AI classifications of uploaded evidence documents';
COMMENT ON TABLE extracted_facts IS 'Stores facts extracted from evidence by AI';
COMMENT ON TABLE fact_contradictions IS 'Stores detected contradictions in extracted facts';
COMMENT ON TABLE reddit_research IS 'Stores Reddit market research results';
COMMENT ON TABLE perceptual_maps IS 'Stores AI-generated perceptual mapping results';
COMMENT ON TABLE neuroscience_copy_variants IS 'Stores neuroscience-based copywriting variants';
COMMENT ON TABLE channel_strategies IS 'Stores AI-powered channel strategy recommendations';
COMMENT ON TABLE onboarding_step_definitions IS 'Defines the 23-step onboarding process';

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON evidence_classifications TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON extracted_facts TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON fact_contradictions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON reddit_research TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON perceptual_maps TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON neuroscience_copy_variants TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON channel_strategies TO authenticated;
GRANT SELECT ON onboarding_step_definitions TO authenticated;
GRANT EXECUTE ON FUNCTION get_current_step_definition TO authenticated;
GRANT EXECUTE ON FUNCTION advance_onboarding_step TO authenticated;
GRANT EXECUTE ON FUNCTION get_onboarding_progress TO authenticated;
