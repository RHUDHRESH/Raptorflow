-- RaptorFlow Complete Database Schema (v2.0) - Part 4: ICP & Radar Modules
-- Ideal Customer Profile and Market Intelligence

-- =====================================
-- 12. IDEAL CUSTOMER PROFILE (ICP)
-- =====================================

-- ICP Definitions
CREATE TABLE IF NOT EXISTS icp_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    
    name TEXT NOT NULL,
    priority TEXT DEFAULT 'secondary' CHECK (priority IN ('primary', 'secondary')),
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'deprecated')),
    confidence_score NUMERIC DEFAULT 0.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Performance tracking
    performance_data JSONB DEFAULT '{}',
    last_evaluated_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ICP Firmographics
CREATE TABLE IF NOT EXISTS icp_firmographics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    icp_id UUID NOT NULL REFERENCES icp_profiles(id) ON DELETE CASCADE,
    
    company_types TEXT[], -- 'saas', 'd2c', 'agency', 'service'
    company_size_min INTEGER,
    company_size_max INTEGER,
    geography TEXT[],
    acv_min NUMERIC,
    acv_max NUMERIC,
    sales_motions TEXT[], -- 'self-serve', 'demo-led', 'sales-assisted'
    budget_comfort TEXT[], -- 'low', 'medium', 'high', 'enterprise'
    decision_makers TEXT[], -- 'founder', 'marketing_manager', etc.
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ICP Pain Mapping
CREATE TABLE IF NOT EXISTS icp_pain_map (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    icp_id UUID NOT NULL REFERENCES icp_profiles(id) ON DELETE CASCADE,
    
    primary_pains TEXT[], -- Max 2
    secondary_pains TEXT[],
    trigger_events TEXT[],
    urgency_level TEXT DEFAULT 'someday' CHECK (urgency_level IN ('now', 'soon', 'someday')),
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ICP Psycholinguistics
CREATE TABLE IF NOT EXISTS icp_psycholinguistics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    icp_id UUID NOT NULL REFERENCES icp_profiles(id) ON DELETE CASCADE,
    
    mindset_traits TEXT[], -- 'skeptical', 'data-driven'
    emotional_triggers TEXT[],
    tone_preference TEXT[],
    words_to_use TEXT[],
    words_to_avoid TEXT[],
    proof_preference TEXT[], -- 'case-study', 'data', 'logos'
    cta_style TEXT[], -- 'soft', 'direct'
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ICP Disqualifiers
CREATE TABLE IF NOT EXISTS icp_disqualifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    icp_id UUID NOT NULL REFERENCES icp_profiles(id) ON DELETE CASCADE,
    
    excluded_company_types TEXT[],
    excluded_sizes TEXT[],
    excluded_geographies TEXT[],
    excluded_behaviors TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT now()
);

-- =====================================
-- 13. RADAR MODULE (Market Intelligence)
-- =====================================

-- Radar Signals
CREATE TABLE IF NOT EXISTS radar_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    
    title TEXT NOT NULL,
    why_it_matters TEXT,
    timestamp TIMESTAMPTZ DEFAULT now(),
    
    -- Source information
    source_name TEXT,
    source_type TEXT CHECK (source_type IN ('news', 'social', 'blog', 'competitor', 'regulation', 'video')),
    source_url TEXT,
    
    confidence TEXT DEFAULT 'medium' CHECK (confidence IN ('high', 'medium', 'low')),
    tags TEXT[],
    is_saved BOOLEAN DEFAULT FALSE,
    
    -- Processing metadata
    processed_at TIMESTAMPTZ,
    relevance_score NUMERIC CHECK (relevance_score >= 0 AND relevance_score <= 1),
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Radar Signal Angles (Content generation prompts)
CREATE TABLE IF NOT EXISTS radar_signal_angles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id UUID NOT NULL REFERENCES radar_signals(id) ON DELETE CASCADE,
    
    label TEXT NOT NULL,
    angle_type TEXT CHECK (angle_type IN ('contrarian', 'practical', 'story', 'meme', 'data', 'hot-take')),
    prompt TEXT, -- The prompt to send to Muse
    
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Radar Dossiers (Compiled intelligence reports)
CREATE TABLE IF NOT EXISTS radar_dossiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    
    title TEXT NOT NULL,
    date TIMESTAMPTZ DEFAULT now(),
    summary TEXT[],
    what_changed TEXT,
    
    -- Impact analysis
    impacts TEXT[],
    objections TEXT[],
    opportunities TEXT[],
    
    -- Market narrative
    believing TEXT,
    overhyped TEXT,
    underrated TEXT,
    
    -- Recommended actions
    recommended_move_name TEXT,
    recommended_move_target TEXT,
    recommended_move_action TEXT,
    
    -- Asset requirements
    asset_email BOOLEAN DEFAULT FALSE,
    asset_post BOOLEAN DEFAULT FALSE,
    asset_meme BOOLEAN DEFAULT FALSE,
    asset_landing BOOLEAN DEFAULT FALSE,
    
    -- Sources
    sources JSONB DEFAULT '[]',
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
