-- Brand Foundation & Positioning Schema

-- Ensure Foundation kit exists
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

-- Positioning Intelligence
CREATE TABLE IF NOT EXISTS brand_positioning_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_kit_id UUID REFERENCES foundation_brand_kit(id) ON DELETE CASCADE,
    uvp TEXT NOT NULL, -- Unique Value Proposition
    target_market_segments JSONB DEFAULT '[]'::jsonb,
    competitive_moat TEXT,
    brand_archetype TEXT,
    mission_statement TEXT,
    vision_statement TEXT,
    key_differentiators TEXT[],
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Brand Voice & Persona
CREATE TABLE IF NOT EXISTS brand_voice_persona (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_kit_id UUID REFERENCES foundation_brand_kit(id) ON DELETE CASCADE,
    persona_name TEXT NOT NULL,
    traits TEXT[],
    tone_guidelines JSONB DEFAULT '{}'::jsonb,
    prohibited_words TEXT[],
    sample_content JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE brand_positioning_intelligence ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_voice_persona ENABLE ROW LEVEL SECURITY;

-- Tenant Isolation (Basic)
CREATE POLICY tenant_isolation_positioning ON brand_positioning_intelligence
    USING (EXISTS (SELECT 1 FROM foundation_brand_kit WHERE id = brand_kit_id AND tenant_id = auth.uid()));

CREATE POLICY tenant_isolation_voice ON brand_voice_persona
    USING (EXISTS (SELECT 1 FROM foundation_brand_kit WHERE id = brand_kit_id AND tenant_id = auth.uid()));
