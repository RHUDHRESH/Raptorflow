-- RaptorFlow Onboarding Backend - Initial Schema
-- Phase 1: Foundation Services Database Schema
-- Created: January 15, 2026

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable timestamp extension
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- =============================================
-- CORE SESSION MANAGEMENT TABLES
-- =============================================

-- Onboarding sessions table
CREATE TABLE IF NOT EXISTS onboarding_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL,
    user_id UUID NOT NULL,
    current_step INTEGER DEFAULT 1 NOT NULL,
    total_steps INTEGER DEFAULT 25 NOT NULL,
    status VARCHAR(50) DEFAULT 'in_progress' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1 NOT NULL,
    
    -- Constraints
    CONSTRAINT onboarding_sessions_status_check 
        CHECK (status IN ('in_progress', 'completed', 'abandoned', 'error', 'paused')),
    CONSTRAINT onboarding_sessions_step_check 
        CHECK (current_step >= 1 AND current_step <= total_steps)
);

-- Indexes for sessions
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_workspace_id ON onboarding_sessions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_user_id ON onboarding_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_status ON onboarding_sessions(status);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_created_at ON onboarding_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_updated_at ON onboarding_sessions(updated_at);

-- Step data table
CREATE TABLE IF NOT EXISTS onboarding_step_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    step_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'not_started' NOT NULL,
    data JSONB DEFAULT '{}' NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    version INTEGER DEFAULT 1 NOT NULL,
    validation_errors TEXT[],
    processing_time REAL,
    
    -- Constraints
    CONSTRAINT onboarding_step_data_status_check 
        CHECK (status IN ('not_started', 'in_progress', 'completed', 'skipped', 'error')),
    CONSTRAINT onboarding_step_data_unique_step 
        UNIQUE (session_id, step_id)
);

-- Indexes for step data
CREATE INDEX IF NOT EXISTS idx_onboarding_step_data_session_id ON onboarding_step_data(session_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_step_data_step_id ON onboarding_step_data(step_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_step_data_status ON onboarding_step_data(status);

-- Session snapshots for versioning
CREATE TABLE IF NOT EXISTS session_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    snapshot_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_by UUID NOT NULL,
    description TEXT,
    
    -- Constraints
    CONSTRAINT session_snapshots_unique_version 
        UNIQUE (session_id, version)
);

-- Indexes for snapshots
CREATE INDEX IF NOT EXISTS idx_session_snapshots_session_id ON session_snapshots(session_id);
CREATE INDEX IF NOT EXISTS idx_session_snapshots_created_at ON session_snapshots(created_at);

-- =============================================
-- DOCUMENT MANAGEMENT TABLES
-- =============================================

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    gcs_key VARCHAR(500) NOT NULL,
    content_type VARCHAR(100),
    size BIGINT,
    checksum VARCHAR(64),
    workspace_id UUID NOT NULL,
    user_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT documents_filename_length CHECK (length(filename) <= 255),
    CONSTRAINT documents_size_positive CHECK (size >= 0)
);

-- Indexes for documents
CREATE INDEX IF NOT EXISTS idx_documents_session_id ON documents(session_id);
CREATE INDEX IF NOT EXISTS idx_documents_workspace_id ON documents(workspace_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_content_type ON documents(content_type);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_documents_checksum ON documents(checksum);

-- OCR results table
CREATE TABLE IF NOT EXISTS ocr_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    extracted_text TEXT NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    structured_data JSONB,
    processing_time REAL NOT NULL,
    provider_used VARCHAR(50) NOT NULL,
    page_count INTEGER DEFAULT 1,
    language VARCHAR(10) DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Constraints
    CONSTRAINT ocr_results_confidence_range CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CONSTRAINT ocr_results_page_count_positive CHECK (page_count > 0)
);

-- Indexes for OCR results
CREATE INDEX IF NOT EXISTS idx_ocr_results_document_id ON ocr_results(document_id);
CREATE INDEX IF NOT EXISTS idx_ocr_results_provider ON ocr_results(provider_used);
CREATE INDEX IF NOT EXISTS idx_ocr_results_confidence ON ocr_results(confidence_score);

-- Document analysis results table
CREATE TABLE IF NOT EXISTS document_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    entities JSONB DEFAULT '[]',
    key_phrases JSONB DEFAULT '[]',
    sentiment JSONB,
    language VARCHAR(10),
    word_count INTEGER,
    readability_score DECIMAL(5,2),
    processing_time REAL NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Constraints
    CONSTRAINT document_analysis_confidence_range CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CONSTRAINT document_analysis_category_check 
        CHECK (category IN ('business', 'technical', 'marketing', 'legal', 'financial', 'strategic', 'operational', 'unknown'))
);

-- Indexes for document analysis
CREATE INDEX IF NOT EXISTS idx_document_analysis_document_id ON document_analysis(document_id);
CREATE INDEX IF NOT EXISTS idx_document_analysis_category ON document_analysis(category);
CREATE INDEX IF NOT EXISTS idx_document_analysis_confidence ON document_analysis(confidence_score);

-- =============================================
-- FACT EXTRACTION TABLES
-- =============================================

-- Extracted facts table
CREATE TABLE IF NOT EXISTS extracted_facts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    statement TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    fact_type VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    source_citation TEXT,
    page_number INTEGER,
    position JSONB,
    metadata JSONB DEFAULT '{}',
    validation JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Constraints
    CONSTRAINT extracted_facts_confidence_range CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CONSTRAINT extracted_facts_category_check 
        CHECK (category IN ('business_metrics', 'strategic_info', 'operational_details', 'market_info', 'financial_info', 'customer_info', 'product_info', 'competitive_info')),
    CONSTRAINT extracted_facts_type_check 
        CHECK (fact_type IN ('quantitative', 'qualitative', 'temporal', 'causal', 'comparative'))
);

-- Indexes for extracted facts
CREATE INDEX IF NOT EXISTS idx_extracted_facts_document_id ON extracted_facts(document_id);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_category ON extracted_facts(category);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_type ON extracted_facts(fact_type);
CREATE INDEX IF NOT EXISTS idx_extracted_facts_confidence ON extracted_facts(confidence_score);

-- Fact validation results table
CREATE TABLE IF NOT EXISTS fact_validation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fact_id UUID NOT NULL REFERENCES extracted_facts(id) ON DELETE CASCADE,
    is_valid BOOLEAN NOT NULL,
    confidence_adjustment DECIMAL(3,2) NOT NULL,
    issues TEXT[] DEFAULT '{}',
    suggestions TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Constraints
    CONSTRAINT fact_validation_confidence_range CHECK (confidence_adjustment >= -1 AND confidence_adjustment <= 1)
);

-- Indexes for fact validation
CREATE INDEX IF NOT EXISTS idx_fact_validation_fact_id ON fact_validation(fact_id);
CREATE INDEX IF NOT EXISTS idx_fact_validation_is_valid ON fact_validation(is_valid);

-- =============================================
-- LLM USAGE TRACKING
-- =============================================

-- LLM usage tracking table
CREATE TABLE IF NOT EXISTS llm_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES onboarding_sessions(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    cost DECIMAL(10,6) NOT NULL,
    processing_time REAL NOT NULL,
    request_type VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Constraints
    CONSTRAINT llm_usage_tokens_positive CHECK (prompt_tokens >= 0 AND completion_tokens >= 0 AND total_tokens >= 0),
    CONSTRAINT llm_usage_cost_positive CHECK (cost >= 0)
);

-- Indexes for LLM usage
CREATE INDEX IF NOT EXISTS idx_llm_usage_session_id ON llm_usage(session_id);
CREATE INDEX IF NOT EXISTS idx_llm_usage_provider ON llm_usage(provider);
CREATE INDEX IF NOT EXISTS idx_llm_usage_model ON llm_usage(model);
CREATE INDEX IF NOT EXISTS idx_llm_usage_created_at ON llm_usage(created_at);

-- =============================================
-- TRIGGERS AND FUNCTIONS
-- =============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_onboarding_sessions_updated_at 
    BEFORE UPDATE ON onboarding_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_onboarding_step_data_updated_at 
    BEFORE UPDATE ON onboarding_step_data 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to validate step progression
CREATE OR REPLACE FUNCTION validate_step_progression()
RETURNS TRIGGER AS $$
BEGIN
    -- Ensure current_step doesn't exceed total_steps
    IF NEW.current_step > NEW.total_steps THEN
        NEW.current_step = NEW.total_steps;
    END IF;
    
    -- Ensure current_step is at least 1
    IF NEW.current_step < 1 THEN
        NEW.current_step = 1;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER validate_step_progression_trigger 
    BEFORE INSERT OR UPDATE ON onboarding_sessions 
    FOR EACH ROW EXECUTE FUNCTION validate_step_progression();

-- =============================================
-- VIEWS FOR COMMON QUERIES
-- =============================================

-- Session progress view
CREATE OR REPLACE VIEW session_progress AS
SELECT 
    s.id,
    s.workspace_id,
    s.user_id,
    s.current_step,
    s.total_steps,
    ROUND((s.current_step::DECIMAL / s.total_steps::DECIMAL) * 100, 2) as completion_percentage,
    s.status,
    s.created_at,
    s.updated_at,
    s.completed_at,
    COUNT(CASE WHEN sd.status = 'completed' THEN 1 END) as completed_steps,
    COUNT(CASE WHEN sd.status IN ('in_progress', 'error') THEN 1 END) as active_steps
FROM onboarding_sessions s
LEFT JOIN onboarding_step_data sd ON s.id = sd.session_id
GROUP BY s.id, s.workspace_id, s.user_id, s.current_step, s.total_steps, s.status, s.created_at, s.updated_at, s.completed_at;

-- Document processing status view
CREATE OR REPLACE VIEW document_processing_status AS
SELECT 
    d.id,
    d.filename,
    d.content_type,
    d.size,
    d.created_at as uploaded_at,
    o.processed_at as ocr_completed_at,
    da.created_at as analysis_completed_at,
    CASE 
        WHEN o.id IS NOT NULL AND da.id IS NOT NULL THEN 'completed'
        WHEN o.id IS NOT NULL THEN 'ocr_completed'
        WHEN da.id IS NOT NULL THEN 'analysis_completed'
        ELSE 'uploaded'
    END as processing_status,
    COALESCE(o.confidence_score, 0) as ocr_confidence,
    COALESCE(da.confidence_score, 0) as analysis_confidence
FROM documents d
LEFT JOIN ocr_results o ON d.id = o.document_id
LEFT JOIN document_analysis da ON d.id = da.document_id;

-- Fact extraction summary view
CREATE OR REPLACE VIEW fact_extraction_summary AS
SELECT 
    d.id as document_id,
    d.filename,
    COUNT(ef.id) as total_facts,
    COUNT(CASE WHEN ef.category = 'business_metrics' THEN 1 END) as business_metrics_facts,
    COUNT(CASE WHEN ef.category = 'strategic_info' THEN 1 END) as strategic_facts,
    COUNT(CASE WHEN ef.category = 'financial_info' THEN 1 END) as financial_facts,
    COUNT(CASE WHEN ef.category = 'market_info' THEN 1 END) as market_facts,
    AVG(ef.confidence_score) as avg_confidence,
    MAX(ef.confidence_score) as max_confidence,
    MIN(ef.confidence_score) as min_confidence
FROM documents d
LEFT JOIN extracted_facts ef ON d.id = ef.document_id
GROUP BY d.id, d.filename;

-- =============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================

-- Enable RLS on all tables
ALTER TABLE onboarding_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE onboarding_step_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE ocr_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE extracted_facts ENABLE ROW LEVEL SECURITY;
ALTER TABLE llm_usage ENABLE ROW LEVEL SECURITY;

-- RLS policy for sessions (users can only access their own sessions)
CREATE POLICY "Users can view own sessions" ON onboarding_sessions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own sessions" ON onboarding_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own sessions" ON onboarding_sessions
    FOR UPDATE USING (auth.uid() = user_id);

-- RLS policy for step data
CREATE POLICY "Users can view own step data" ON onboarding_step_data
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM onboarding_sessions 
            WHERE id = session_id AND auth.uid() = user_id
        )
    );

-- RLS policy for documents
CREATE POLICY "Users can view own documents" ON documents
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM onboarding_sessions 
            WHERE id = session_id AND auth.uid() = user_id
        )
    );

-- RLS policy for OCR results
CREATE POLICY "Users can view own OCR results" ON ocr_results
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM documents d
            JOIN onboarding_sessions s ON d.session_id = s.id
            WHERE d.id = document_id AND auth.uid() = s.user_id
        )
    );

-- =============================================
-- COMMENTS AND DOCUMENTATION
-- =============================================

COMMENT ON TABLE onboarding_sessions IS 'Main onboarding session tracking table';
COMMENT ON TABLE onboarding_step_data IS 'Individual step data for onboarding sessions';
COMMENT ON TABLE session_snapshots IS 'Versioned snapshots of session state for recovery';
COMMENT ON TABLE documents IS 'Uploaded documents metadata and storage references';
COMMENT ON TABLE ocr_results IS 'OCR extraction results with confidence scores';
COMMENT ON TABLE document_analysis IS 'Document analysis results including entities and sentiment';
COMMENT ON TABLE extracted_facts IS 'Business facts extracted from documents';
COMMENT ON TABLE fact_validation IS 'Validation results for extracted facts';
COMMENT ON TABLE llm_usage IS 'LLM API usage tracking for cost management';

COMMENT ON VIEW session_progress IS 'Session progress with completion percentages';
COMMENT ON VIEW document_processing_status IS 'Document processing pipeline status';
COMMENT ON VIEW fact_extraction_summary IS 'Summary statistics for fact extraction';

-- =============================================
-- SAMPLE DATA (for development)
-- =============================================

-- This section would be populated in a separate migration file
-- INSERT INTO sample_data ...
