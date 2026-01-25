-- ICP Profiles table with primary ICP constraint
-- Migration: 20240103_icp_profiles.sql

-- ICP Profiles (Ideal Customer Profiles)
CREATE TABLE IF NOT EXISTS public.icp_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,

    -- Basic Info
    name TEXT NOT NULL,  -- "Scaling SaaS Founder at $1M-$5M ARR"
    tagline TEXT,
    code TEXT,  -- "ICP-001"

    -- Status
    is_primary BOOLEAN DEFAULT FALSE,
    is_secondary BOOLEAN DEFAULT FALSE,

    -- Demographics
    demographics JSONB DEFAULT '{
        "age_range": null,
        "income_range": null,
        "location": [],
        "role": null,
        "company_size": null,
        "industry": []
    }',

    -- Psychographics
    psychographics JSONB DEFAULT '{
        "beliefs": [],
        "identity": null,
        "becoming": null,
        "fears": [],
        "values": []
    }',

    -- Behaviors
    behaviors JSONB DEFAULT '{
        "hangouts": [],
        "consumption": [],
        "follows": [],
        "language_patterns": [],
        "buying_triggers": [],
        "objections": []
    }',

    -- Market Sophistication (Eugene Schwartz stages)
    market_sophistication JSONB DEFAULT '{
        "stage": 3,
        "stage_name": "Solution Aware",
        "reasoning": null
    }',

    -- Fit Scores (0-100)
    scores JSONB DEFAULT '{
        "pain_intensity": 0,
        "willingness_to_pay": 0,
        "accessibility": 0,
        "product_fit": 0
    }',

    -- AI Context
    summary TEXT,
    summary_embedding vector(384),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_icp_profiles_workspace ON icp_profiles(workspace_id);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_primary ON icp_profiles(workspace_id, is_primary);
CREATE INDEX IF NOT EXISTS idx_icp_profiles_embedding ON icp_profiles
    USING ivfflat (summary_embedding vector_cosine_ops) WITH (lists = 100);

-- Ensure only one primary ICP per workspace
CREATE UNIQUE INDEX IF NOT EXISTS idx_icp_profiles_unique_primary
    ON icp_profiles(workspace_id) WHERE is_primary = TRUE;

-- Enable RLS
ALTER TABLE public.icp_profiles ENABLE ROW LEVEL SECURITY;

-- Trigger for updated_at
CREATE TRIGGER icp_profiles_updated_at
    BEFORE UPDATE ON public.icp_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
