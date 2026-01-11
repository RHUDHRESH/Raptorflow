-- Daily Wins table (product-specific)
-- Migration: 20240109_daily_wins.sql
-- Description: Daily achievements and wins tracking with workspace isolation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Daily Wins table
CREATE TABLE IF NOT EXISTS public.daily_wins (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Workspace isolation
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Win metadata
    title TEXT NOT NULL,
    description TEXT,
    win_type TEXT NOT NULL, -- e.g., 'milestone', 'achievement', 'breakthrough', 'learning', 'revenue'
    category TEXT NOT NULL, -- e.g., 'business', 'personal', 'team', 'product', 'marketing', 'sales'
    significance_level TEXT DEFAULT 'medium', -- low, medium, high, critical

    -- Achievement details
    achievement_date DATE NOT NULL,
    achievement_context TEXT, -- Context of the achievement
    challenge_overcome TEXT, -- What challenge was overcome
    approach_taken TEXT, -- How the win was achieved

    -- Impact metrics
    impact_description TEXT,
    quantitative_impact JSONB DEFAULT '{}', -- Quantitative impact metrics
    qualitative_impact JSONB DEFAULT '{}', -- Qualitative impact descriptions
    business_value DECIMAL(10,2) DEFAULT 0.00, -- Estimated business value
    time_saved_hours DECIMAL(5,2) DEFAULT 0.00, -- Time saved in hours
    cost_saved DECIMAL(10,2) DEFAULT 0.00, -- Money saved

    -- Team and collaboration
    team_members JSONB DEFAULT '[]', -- Array of team members involved
    collaboration_level TEXT DEFAULT 'individual', -- individual, team, cross_team, external
    recognition_given JSONB DEFAULT '[]', -- Recognition given to team members

    -- Related entities
    foundation_id UUID REFERENCES foundations(id) ON DELETE SET NULL,
    icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    move_id UUID REFERENCES moves(id) ON DELETE SET NULL,
    move_task_id UUID REFERENCES move_tasks(id) ON DELETE SET NULL,
    blackbox_strategy_id UUID REFERENCES blackbox_strategies(id) ON DELETE SET NULL,

    -- Learning and insights
    key_learnings JSONB DEFAULT '[]', -- Key learnings from the win
    skills_gained JSONB DEFAULT '[]', -- Skills gained or improved
    insights_discovered JSONB DEFAULT '[]', -- Insights discovered
    best_practices JSONB DEFAULT '[]', -- Best practices identified

    -- Future implications
    next_steps JSONB DEFAULT '[]', -- Next steps following the win
    opportunities_created JSONB DEFAULT '[]', -- Opportunities created
    repeatability_score DECIMAL(3,2) DEFAULT 0.00, -- How repeatable this win is (0.00 to 1.00)
    scalability_potential TEXT, -- Potential for scaling this win

    -- Emotional and motivational aspects
    satisfaction_level INTEGER DEFAULT 5, -- 1-10 satisfaction level
    motivation_boost INTEGER DEFAULT 5, -- 1-10 motivation boost
    confidence_gain INTEGER DEFAULT 5, -- 1-10 confidence gain
    celebration_notes TEXT, -- How the win was celebrated

    -- Documentation and sharing
    documentation TEXT,
    case_study TEXT,
    shareable_story TEXT, -- Story that can be shared
    publication_status TEXT DEFAULT 'internal', -- internal, team, public, published

    -- AI-generated content
    ai_suggestion TEXT,
    ai_confidence DECIMAL(3,2) DEFAULT 0.00,
    ai_generated_at TIMESTAMPTZ,
    ai_insights JSONB DEFAULT '{}', -- AI-generated insights

    -- Tracking and analytics
    views INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    inspiration_score DECIMAL(3,2) DEFAULT 0.00, -- How inspiring this win is to others

    -- Metadata
    tags JSONB DEFAULT '[]', -- Array of tags for categorization
    keywords JSONB DEFAULT '[]', -- SEO keywords
    attributes JSONB DEFAULT '{}', -- Custom attributes
    metadata JSONB DEFAULT '{}', -- Additional metadata

    -- Ownership and tracking
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    celebrated_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    archived_at TIMESTAMPTZ,

    -- Constraints
    CHECK (significance_level IN ('low', 'medium', 'high', 'critical')),
    CHECK (collaboration_level IN ('individual', 'team', 'cross_team', 'external')),
    CHECK (business_value >= 0),
    CHECK (time_saved_hours >= 0),
    CHECK (cost_saved >= 0),
    CHECK (repeatability_score >= 0 AND repeatability_score <= 1),
    CHECK (satisfaction_level >= 1 AND satisfaction_level <= 10),
    CHECK (motivation_boost >= 1 AND motivation_boost <= 10),
    CHECK (confidence_gain >= 1 AND confidence_gain <= 10),
    CHECK (inspiration_score >= 0 AND inspiration_score <= 1),
    CHECK (ai_confidence >= 0 AND ai_confidence <= 1)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_daily_wins_workspace_id ON public.daily_wins(workspace_id);
CREATE INDEX IF NOT EXISTS idx_daily_wins_win_type ON public.daily_wins(win_type);
CREATE INDEX IF NOT EXISTS idx_daily_wins_category ON public.daily_wins(category);
CREATE INDEX IF NOT EXISTS idx_daily_wins_significance_level ON public.daily_wins(significance_level);
CREATE INDEX IF NOT EXISTS idx_daily_wins_achievement_date ON public.daily_wins(achievement_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_created_at ON public.daily_wins(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_created_by ON public.daily_wins(created_by);
CREATE INDEX IF NOT EXISTS idx_daily_wins_celebrated_at ON public.daily_wins(celebrated_at DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_published_at ON public.daily_wins(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_business_value ON public.daily_wins(business_value DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_satisfaction_level ON public.daily_wins(satisfaction_level DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_motivation_boost ON public.daily_wins(motivation_boost DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_confidence_gain ON public.daily_wins(confidence_gain DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_foundation_id ON public.daily_wins(foundation_id);
CREATE INDEX IF NOT EXISTS idx_daily_wins_icp_profile_id ON public.daily_wins(icp_profile_id);
CREATE INDEX IF NOT EXISTS idx_daily_wins_campaign_id ON public.daily_wins(campaign_id);
CREATE INDEX IF NOT EXISTS idx_daily_wins_move_id ON public.daily_wins(move_id);
CREATE INDEX IF NOT EXISTS idx_daily_wins_move_task_id ON public.daily_wins(move_task_id);
CREATE INDEX IF NOT EXISTS idx_daily_wins_blackbox_strategy_id ON public.daily_wins(blackbox_strategy_id);
CREATE INDEX IF NOT EXISTS idx_daily_wins_collaboration_level ON public.daily_wins(collaboration_level);
CREATE INDEX IF NOT EXISTS idx_daily_wins_views ON public.daily_wins(views DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_inspiration_score ON public.daily_wins(inspiration_score DESC);
CREATE INDEX IF NOT EXISTS idx_daily_wins_tags ON public.daily_wins USING GIN (tags) WITH (jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_daily_wins_keywords ON public.daily_wins USING GIN (keywords) WITH (jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_daily_wins_attributes ON public.daily_wins USING GIN (attributes) WITH (jsonb_path_ops);

-- Vector index for semantic search
CREATE INDEX IF NOT EXISTS idx_daily_wins_content_embedding
    ON public.daily_wins USING ivfflat (content_embedding vector_cosine_ops)
    WITH (lists = 100);

-- Unique constraint on title per achievement date per workspace
CREATE UNIQUE INDEX IF NOT EXISTS idx_daily_wins_unique_title_date
    ON public.daily_wins(workspace_id, title, achievement_date);

-- Trigger for updated_at
CREATE TRIGGER daily_wins_updated_at
    BEFORE UPDATE ON public.daily_wins
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Enable Row Level Security
ALTER TABLE public.daily_wins ENABLE ROW LEVEL SECURITY;
