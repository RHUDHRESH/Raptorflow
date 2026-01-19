-- ============================================================================
-- Migration: 071_proof_points_schema.sql
-- Purpose: Add proof points and truth sheet tables for onboarding
-- ============================================================================

-- Proof Points Table
-- Stores validated proof points for claims
CREATE TABLE IF NOT EXISTS onboarding_proof_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    
    -- Claim information
    claim_id TEXT NOT NULL,
    claim_text TEXT NOT NULL,
    claim_category TEXT DEFAULT 'general',
    
    -- Validation results
    verification_status TEXT DEFAULT 'unverified', -- verified, partially_verified, unverified, needs_evidence
    claim_strength TEXT DEFAULT 'moderate', -- strong, moderate, weak
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    
    -- Proof details
    proof_points JSONB DEFAULT '[]'::jsonb, -- Array of proof point objects
    recommendations JSONB DEFAULT '[]'::jsonb,
    improved_claim TEXT,
    risk_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Truth Sheet Entries Table
-- Stores extracted and user-edited truth sheet entries
CREATE TABLE IF NOT EXISTS onboarding_truth_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    
    -- Entry information
    category TEXT NOT NULL, -- company, product, market, customer, competition, financials, team
    field_name TEXT NOT NULL,
    field_value TEXT NOT NULL,
    
    -- Source tracking
    source TEXT DEFAULT 'auto-extracted',
    source_excerpt TEXT,
    
    -- Confidence and verification
    confidence_level TEXT DEFAULT 'medium', -- high, medium, low
    verified BOOLEAN DEFAULT FALSE,
    user_edited BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    extracted_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint per field per session
    UNIQUE(session_id, category, field_name)
);

-- Validation Summary Table
-- Stores overall validation results per session
CREATE TABLE IF NOT EXISTS onboarding_validation_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE UNIQUE,
    
    -- Summary metrics
    total_claims INTEGER DEFAULT 0,
    strong_claims INTEGER DEFAULT 0,
    moderate_claims INTEGER DEFAULT 0,
    weak_claims INTEGER DEFAULT 0,
    needs_evidence INTEGER DEFAULT 0,
    overall_score DECIMAL(3,2) DEFAULT 0.00,
    
    -- Truth sheet metrics
    truth_completeness DECIMAL(3,2) DEFAULT 0.00,
    truth_entries_count INTEGER DEFAULT 0,
    categories_covered JSONB DEFAULT '[]'::jsonb,
    missing_fields JSONB DEFAULT '[]'::jsonb,
    
    -- Recommendations
    recommendations JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    last_validated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_proof_points_session ON onboarding_proof_points(session_id);
CREATE INDEX IF NOT EXISTS idx_proof_points_workspace ON onboarding_proof_points(workspace_id);
CREATE INDEX IF NOT EXISTS idx_proof_points_claim_id ON onboarding_proof_points(claim_id);

CREATE INDEX IF NOT EXISTS idx_truth_entries_session ON onboarding_truth_entries(session_id);
CREATE INDEX IF NOT EXISTS idx_truth_entries_workspace ON onboarding_truth_entries(workspace_id);
CREATE INDEX IF NOT EXISTS idx_truth_entries_category ON onboarding_truth_entries(category);

CREATE INDEX IF NOT EXISTS idx_validation_summary_session ON onboarding_validation_summary(session_id);

-- Enable RLS
ALTER TABLE onboarding_proof_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_truth_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_validation_summary ENABLE ROW LEVEL SECURITY;

-- RLS Policies for proof_points
CREATE POLICY "Users can view own workspace proof points" 
    ON onboarding_proof_points FOR SELECT
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can insert proof points in own workspace"
    ON onboarding_proof_points FOR INSERT
    WITH CHECK (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can update proof points in own workspace"
    ON onboarding_proof_points FOR UPDATE
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

-- RLS Policies for truth_entries
CREATE POLICY "Users can view own workspace truth entries"
    ON onboarding_truth_entries FOR SELECT
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can insert truth entries in own workspace"
    ON onboarding_truth_entries FOR INSERT
    WITH CHECK (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can update truth entries in own workspace"
    ON onboarding_truth_entries FOR UPDATE
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

-- RLS Policies for validation_summary
CREATE POLICY "Users can view own workspace validation summary"
    ON onboarding_validation_summary FOR SELECT
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can manage validation summary in own workspace"
    ON onboarding_validation_summary FOR ALL
    USING (workspace_id IN (
        SELECT workspace_id FROM workspace_members WHERE user_id = auth.uid()
    ));

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_proof_points_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_proof_points_updated_at
    BEFORE UPDATE ON onboarding_proof_points
    FOR EACH ROW EXECUTE FUNCTION update_proof_points_updated_at();

CREATE TRIGGER trigger_truth_entries_updated_at
    BEFORE UPDATE ON onboarding_truth_entries
    FOR EACH ROW EXECUTE FUNCTION update_proof_points_updated_at();

CREATE TRIGGER trigger_validation_summary_updated_at
    BEFORE UPDATE ON onboarding_validation_summary
    FOR EACH ROW EXECUTE FUNCTION update_proof_points_updated_at();

-- ============================================================================
-- End of Migration
-- ============================================================================
