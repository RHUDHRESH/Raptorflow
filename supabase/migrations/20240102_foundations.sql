-- Foundations table with workspace isolation
-- Migration: 20240102_foundations.sql

-- Foundations table (business context from onboarding)
CREATE TABLE IF NOT EXISTS public.foundations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Company Info
    company_name TEXT,
    industry TEXT,
    company_stage TEXT CHECK (
        company_stage IN ('idea', 'mvp', 'growth', 'scale', 'enterprise')
    ),
    website_url TEXT,

    -- Truth Sheet (extracted facts)
    truth_sheet JSONB DEFAULT '{}',

    -- Market Research Results
    market_research JSONB DEFAULT '{
        "customer_insights": [],
        "competitor_analysis": [],
        "market_trends": []
    }',

    -- Competitors
    competitors JSONB DEFAULT '[]',

    -- Positioning
    positioning JSONB DEFAULT '{
        "category": null,
        "positioning_statement": null,
        "usps": [],
        "differentiators": []
    }',

    -- Brand Voice
    brand_voice TEXT DEFAULT 'professional',
    brand_voice_examples JSONB DEFAULT '[]',

    -- Messaging
    messaging_guardrails JSONB DEFAULT '[]',
    soundbite_library JSONB DEFAULT '{}',
    message_hierarchy JSONB DEFAULT '{}',

    -- AI Context (compressed summary for agents)
    summary TEXT,
    summary_embedding vector(384),  -- For semantic search

    -- Status
    onboarding_completed BOOLEAN DEFAULT FALSE,
    last_updated_by TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(workspace_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_foundations_workspace ON foundations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_foundations_embedding ON foundations
    USING ivfflat (summary_embedding vector_cosine_ops) WITH (lists = 100);

-- Enable RLS
ALTER TABLE public.foundations ENABLE ROW LEVEL SECURITY;

-- Trigger for updated_at
CREATE TRIGGER foundations_updated_at
    BEFORE UPDATE ON public.foundations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
