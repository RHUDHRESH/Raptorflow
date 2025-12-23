-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Foundation Tables
CREATE TABLE IF NOT EXISTS foundation_brand_kit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name TEXT NOT NULL,
    logo_url TEXT,
    primary_color TEXT,
    secondary_color TEXT,
    accent_color TEXT,
    typography_config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS foundation_positioning (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_kit_id UUID REFERENCES foundation_brand_kit(id),
    uvp TEXT NOT NULL,
    target_market TEXT NOT NULL,
    competitive_advantage TEXT,
    elevator_pitch TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS foundation_voice_tone (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_kit_id UUID REFERENCES foundation_brand_kit(id),
    tone_name TEXT NOT NULL,
    description TEXT,
    keywords TEXT[],
    examples JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Campaigns & Moves
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    title TEXT NOT NULL,
    objective TEXT,
    status TEXT DEFAULT 'draft', -- draft, active, completed, archived
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending', -- pending, in_progress, approved, rejected, executed
    agent_id TEXT,
    thread_id TEXT,
    execution_result JSONB,
    approval_comment TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS move_approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    move_id UUID REFERENCES moves(id),
    user_id UUID NOT NULL,
    status TEXT NOT NULL,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Blackbox & Telemetry
CREATE TABLE IF NOT EXISTS blackbox_telemetry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    entity_type TEXT NOT NULL, -- move, campaign, agent
    entity_id UUID NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS blackbox_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    move_id UUID REFERENCES moves(id),
    metric_name TEXT NOT NULL,
    metric_value NUMERIC NOT NULL,
    attributed_at TIMESTAMPTZ DEFAULT now()
);

-- ML & Feature Store
CREATE TABLE IF NOT EXISTS ml_feature_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_id UUID NOT NULL,
    feature_name TEXT NOT NULL,
    feature_value NUMERIC NOT NULL,
    vector_value vector(1536), -- Assuming OpenAI embeddings
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Agent Memory
CREATE TABLE IF NOT EXISTS agent_memory_episodic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id TEXT NOT NULL,
    observation TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_memory_semantic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    fact TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Skill Registry
CREATE TABLE IF NOT EXISTS skill_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    input_schema JSONB,
    output_schema JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);
