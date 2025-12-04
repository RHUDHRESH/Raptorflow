-- Migration: 005_cohorts_radar.sql
-- Description: Adds cohorts table with interest tags for Radar feature
-- Tier limits: Ascent=3, Glide=5, Soar=10

-- =====================================================
-- COHORTS TABLE (replaces ICP concept)
-- =====================================================
CREATE TABLE IF NOT EXISTS cohorts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Basic info
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- active, archived
    
    -- 6D Profile Data
    firmographics JSONB DEFAULT '{}',
    /*
    {
        "age_range": "19-25",
        "gender": "male",
        "income_level": "middle",
        "education": "college",
        "occupation": "student",
        "company_size": null,
        "industries": ["education", "tech"],
        "locations": ["Chennai", "India"],
        "exclude": ["corporate professionals"]
    }
    */
    
    psychographics JSONB DEFAULT '{}',
    /*
    {
        "pain_points": [...],
        "motivations": [...],
        "values": [...],
        "lifestyle": [...],
        "internal_triggers": [...],
        "buying_constraints": [...]
    }
    */
    
    behavioral_triggers JSONB DEFAULT '[]',
    /*
    [
        {"signal": "...", "source": "...", "urgency_boost": 30}
    ]
    */
    
    buying_committee JSONB DEFAULT '[]',
    /*
    [
        {"role": "Decision Maker", "typical_title": "...", "concerns": [...], "success_criteria": [...]}
    ]
    */
    
    category_context JSONB DEFAULT '{}',
    /*
    {
        "market_position": "challenger",
        "current_solutions": [...],
        "switching_triggers": [...]
    }
    */
    
    -- Interest Tags (50 tags for Radar matching)
    interest_tags JSONB DEFAULT '[]',
    /*
    [
        {"tag": "cricket", "category": "interests", "weight": 85, "reasoning": "..."}
    ]
    */
    tags_count INTEGER DEFAULT 0,
    
    -- Scoring & Insights
    fit_score INTEGER DEFAULT 0,
    fit_reasoning TEXT,
    messaging_angle TEXT,
    qualification_questions JSONB DEFAULT '[]',
    
    -- Radar tracking
    last_radar_scan TIMESTAMPTZ,
    radar_opportunities_found INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_cohorts_user_id ON cohorts(user_id);
CREATE INDEX idx_cohorts_status ON cohorts(status);
CREATE INDEX idx_cohorts_interest_tags ON cohorts USING GIN(interest_tags);

-- RLS Policies
ALTER TABLE cohorts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own cohorts"
    ON cohorts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own cohorts"
    ON cohorts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own cohorts"
    ON cohorts FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own cohorts"
    ON cohorts FOR DELETE
    USING (auth.uid() = user_id);

-- =====================================================
-- RADAR OPPORTUNITIES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS radar_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    cohort_id UUID REFERENCES cohorts(id) ON DELETE CASCADE,
    
    -- Opportunity details
    title VARCHAR(500) NOT NULL,
    description TEXT,
    trend_type VARCHAR(50), -- breaking_news, viral_moment, cultural_event, etc.
    relevance_score INTEGER DEFAULT 0,
    urgency VARCHAR(50), -- post_now, within_hours, within_day, this_week
    
    -- Matching data
    matching_tags JSONB DEFAULT '[]',
    content_angles JSONB DEFAULT '[]',
    
    -- Risk assessment
    risk_level VARCHAR(50) DEFAULT 'safe',
    risk_notes TEXT,
    
    -- Sources
    sources JSONB DEFAULT '[]',
    
    -- Timing
    peak_window VARCHAR(255),
    decay_estimate VARCHAR(255),
    
    -- Status
    status VARCHAR(50) DEFAULT 'new', -- new, viewed, actioned, expired, dismissed
    actioned_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_radar_opportunities_user_id ON radar_opportunities(user_id);
CREATE INDEX idx_radar_opportunities_cohort_id ON radar_opportunities(cohort_id);
CREATE INDEX idx_radar_opportunities_status ON radar_opportunities(status);
CREATE INDEX idx_radar_opportunities_urgency ON radar_opportunities(urgency);

-- RLS Policies
ALTER TABLE radar_opportunities ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own radar opportunities"
    ON radar_opportunities FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own radar opportunities"
    ON radar_opportunities FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own radar opportunities"
    ON radar_opportunities FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own radar opportunities"
    ON radar_opportunities FOR DELETE
    USING (auth.uid() = user_id);

-- =====================================================
-- CONTENT IDEAS TABLE (generated from opportunities)
-- =====================================================
CREATE TABLE IF NOT EXISTS content_ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    opportunity_id UUID REFERENCES radar_opportunities(id) ON DELETE SET NULL,
    cohort_id UUID REFERENCES cohorts(id) ON DELETE SET NULL,
    
    -- Content brief
    headline VARCHAR(500),
    subheadline VARCHAR(500),
    body_copy TEXT,
    call_to_action VARCHAR(255),
    hashtags JSONB DEFAULT '[]',
    
    -- Visual direction
    visual_concept TEXT,
    visual_style VARCHAR(50),
    color_suggestions JSONB DEFAULT '[]',
    
    -- Variations for A/B testing
    variations JSONB DEFAULT '[]',
    
    -- Platform & format
    format VARCHAR(50), -- image_post, video, carousel, story, reel, thread, blog, email
    platform VARCHAR(100),
    
    -- Execution details
    estimated_time VARCHAR(50),
    difficulty VARCHAR(50),
    resources_needed JSONB DEFAULT '[]',
    
    -- Predictions
    engagement_estimate VARCHAR(50),
    best_posting_time VARCHAR(100),
    expected_reach_multiplier DECIMAL(3,1),
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, approved, scheduled, published
    published_at TIMESTAMPTZ,
    
    -- Performance (after publishing)
    actual_engagement JSONB DEFAULT '{}',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_content_ideas_user_id ON content_ideas(user_id);
CREATE INDEX idx_content_ideas_cohort_id ON content_ideas(cohort_id);
CREATE INDEX idx_content_ideas_status ON content_ideas(status);
CREATE INDEX idx_content_ideas_platform ON content_ideas(platform);

-- RLS Policies
ALTER TABLE content_ideas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own content ideas"
    ON content_ideas FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own content ideas"
    ON content_ideas FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own content ideas"
    ON content_ideas FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own content ideas"
    ON content_ideas FOR DELETE
    USING (auth.uid() = user_id);

-- =====================================================
-- UPDATED_AT TRIGGERS
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_cohorts_updated_at
    BEFORE UPDATE ON cohorts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_ideas_updated_at
    BEFORE UPDATE ON content_ideas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- FUNCTION TO CHECK COHORT LIMITS
-- =====================================================
CREATE OR REPLACE FUNCTION check_cohort_limit()
RETURNS TRIGGER AS $$
DECLARE
    user_plan VARCHAR(50);
    cohort_count INTEGER;
    plan_limit INTEGER;
BEGIN
    -- Get user's plan
    SELECT plan INTO user_plan FROM profiles WHERE id = NEW.user_id;
    
    -- Set limits based on plan
    plan_limit := CASE user_plan
        WHEN 'soar' THEN 10
        WHEN 'glide' THEN 5
        WHEN 'ascent' THEN 3
        ELSE 1 -- free tier
    END;
    
    -- Count existing cohorts
    SELECT COUNT(*) INTO cohort_count FROM cohorts WHERE user_id = NEW.user_id;
    
    -- Check if limit exceeded
    IF cohort_count >= plan_limit THEN
        RAISE EXCEPTION 'Cohort limit reached. Your % plan allows % cohorts.', COALESCE(user_plan, 'free'), plan_limit;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_cohort_limit
    BEFORE INSERT ON cohorts
    FOR EACH ROW
    EXECUTE FUNCTION check_cohort_limit();

