-- ============================================================================
-- Migration: 072_messaging_schema.sql
-- Purpose: Add messaging rules and soundbites tables
-- ============================================================================

-- Messaging Rules Table
CREATE TABLE IF NOT EXISTS onboarding_messaging_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    
    -- Rule information
    rule_id TEXT NOT NULL,
    category TEXT NOT NULL, -- tone, language, claims, competitors, pricing, legal, brand
    name TEXT NOT NULL,
    description TEXT,
    
    -- Rule configuration
    pattern TEXT, -- Regex pattern
    examples_good JSONB DEFAULT '[]'::jsonb,
    examples_bad JSONB DEFAULT '[]'::jsonb,
    severity TEXT DEFAULT 'warning', -- error, warning, suggestion
    status TEXT DEFAULT 'active', -- active, inactive, draft
    
    -- Metadata
    auto_generated BOOLEAN DEFAULT TRUE,
    rationale TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(session_id, rule_id)
);

-- Soundbites Library Table
CREATE TABLE IF NOT EXISTS onboarding_soundbites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    
    -- Soundbite information
    soundbite_id TEXT NOT NULL,
    soundbite_type TEXT NOT NULL, -- tagline, value_prop, headline, cta, elevator_pitch, etc.
    content TEXT NOT NULL,
    
    -- Context
    audience TEXT DEFAULT 'general', -- decision_maker, technical, end_user, general
    tone TEXT DEFAULT 'confident', -- confident, urgent, aspirational, empathetic, provocative
    
    -- Metrics
    character_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    quality_score DECIMAL(3,2) DEFAULT 0.50,
    
    -- Related data
    use_cases JSONB DEFAULT '[]'::jsonb,
    variations JSONB DEFAULT '[]'::jsonb,
    notes TEXT,
    
    -- Status
    is_favorite BOOLEAN DEFAULT FALSE,
    is_approved BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(session_id, soundbite_id)
);

-- Content Check Results Table
CREATE TABLE IF NOT EXISTS onboarding_content_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    
    -- Content being checked
    content_snippet TEXT NOT NULL,
    content_type TEXT DEFAULT 'general', -- email, landing_page, ad, social, etc.
    
    -- Check results
    violations JSONB DEFAULT '[]'::jsonb,
    passed BOOLEAN DEFAULT FALSE,
    score INTEGER DEFAULT 0, -- 0-100
    
    -- Metadata
    checked_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_messaging_rules_session ON onboarding_messaging_rules(session_id);
CREATE INDEX IF NOT EXISTS idx_messaging_rules_workspace ON onboarding_messaging_rules(workspace_id);
CREATE INDEX IF NOT EXISTS idx_messaging_rules_category ON onboarding_messaging_rules(category);

CREATE INDEX IF NOT EXISTS idx_soundbites_session ON onboarding_soundbites(session_id);
CREATE INDEX IF NOT EXISTS idx_soundbites_workspace ON onboarding_soundbites(workspace_id);
CREATE INDEX IF NOT EXISTS idx_soundbites_type ON onboarding_soundbites(soundbite_type);

CREATE INDEX IF NOT EXISTS idx_content_checks_session ON onboarding_content_checks(session_id);

-- Enable RLS
ALTER TABLE onboarding_messaging_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_soundbites ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_content_checks ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own workspace messaging rules"
    ON onboarding_messaging_rules FOR SELECT
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can manage messaging rules in own workspace"
    ON onboarding_messaging_rules FOR ALL
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own workspace soundbites"
    ON onboarding_soundbites FOR SELECT
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can manage soundbites in own workspace"
    ON onboarding_soundbites FOR ALL
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view own workspace content checks"
    ON onboarding_content_checks FOR SELECT
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can manage content checks in own workspace"
    ON onboarding_content_checks FOR ALL
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

-- Triggers for updated_at
CREATE TRIGGER trigger_messaging_rules_updated_at
    BEFORE UPDATE ON onboarding_messaging_rules
    FOR EACH ROW EXECUTE FUNCTION update_proof_points_updated_at();

CREATE TRIGGER trigger_soundbites_updated_at
    BEFORE UPDATE ON onboarding_soundbites
    FOR EACH ROW EXECUTE FUNCTION update_proof_points_updated_at();

-- ============================================================================
-- End of Migration
-- ============================================================================
