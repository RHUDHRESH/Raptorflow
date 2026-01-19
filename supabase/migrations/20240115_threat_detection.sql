-- Advanced Threat Detection System
-- Migration: 20240115_threat_detection.sql
-- 
-- This migration implements comprehensive threat detection with machine learning,
-- behavioral analysis, and automated response capabilities

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Threat detection rules
CREATE TABLE IF NOT EXISTS threat_detection_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Rule identification
    name TEXT NOT NULL,
    description TEXT,
    rule_type TEXT NOT NULL CHECK (
        rule_type IN ('pattern', 'anomaly', 'signature', 'behavioral', 'reputation')
    ),
    category TEXT NOT NULL CHECK (
        category IN ('authentication', 'authorization', 'data_access', 'malware', 'network', 'social_engineering', 'insider_threat')
    ),
    
    -- Rule configuration
    conditions JSONB NOT NULL, -- Rule conditions in JSON format
    thresholds JSONB DEFAULT '{}', -- Thresholds for triggering
    
    -- Scoring
    severity_score INTEGER NOT NULL CHECK (severity_score >= 1 AND severity_score <= 100),
    confidence_threshold DECIMAL(3,2) DEFAULT 0.7 CHECK (confidence_threshold >= 0 AND confidence_threshold <= 1),
    
    -- Response configuration
    auto_response BOOLEAN DEFAULT FALSE,
    response_actions TEXT[] DEFAULT '{}', -- Actions to take when triggered
    escalation_rules JSONB DEFAULT '{}', -- When to escalate
    
    -- Machine learning
    ml_model_id TEXT, -- Reference to ML model
    ml_features TEXT[] DEFAULT '{}', -- Features used for ML
    training_data JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE, -- System rules cannot be deleted
    
    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(name)
);

-- Threat incidents
CREATE TABLE IF NOT EXISTS threat_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Incident identification
    incident_id TEXT UNIQUE NOT NULL DEFAULT (encode(gen_random_bytes(32), 'hex')),
    title TEXT NOT NULL,
    description TEXT,
    
    -- Classification
    threat_type TEXT NOT NULL CHECK (
        threat_type IN ('brute_force', 'credential_stuffing', 'sql_injection', 'xss', 'csrf', 'ddos', 'malware', 'phishing', 'social_engineering', 'insider_threat', 'data_exfiltration', 'account_takeover', 'unauthorized_access')
    ),
    severity TEXT NOT NULL CHECK (
        severity IN ('low', 'medium', 'high', 'critical')
    ),
    status TEXT NOT NULL DEFAULT 'open' CHECK (
        status IN ('open', 'investigating', 'contained', 'resolved', 'false_positive')
    ),
    
    -- Target information
    target_type TEXT NOT NULL CHECK (
        target_type IN ('user', 'workspace', 'system', 'data', 'network')
    ),
    target_id UUID,
    target_details JSONB DEFAULT '{}',
    
    -- Source information
    source_ip INET,
    source_user_id UUID REFERENCES users(id),
    source_device_fingerprint TEXT,
    source_location JSONB DEFAULT '{}',
    
    -- Detection details
    detection_rule_id UUID REFERENCES threat_detection_rules(id),
    detection_method TEXT NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    evidence JSONB DEFAULT '{}',
    
    -- Timeline
    first_detected_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    duration_minutes INTEGER,
    
    -- Impact assessment
    affected_users INTEGER DEFAULT 0,
    affected_systems TEXT[] DEFAULT '{}',
    data_exposed BOOLEAN DEFAULT FALSE,
    data_exfiltrated BOOLEAN DEFAULT FALSE,
    financial_impact DECIMAL(12,2) DEFAULT 0,
    
    -- Response
    response_actions TEXT[] DEFAULT '{}',
    auto_response_taken BOOLEAN DEFAULT FALSE,
    containment_measures TEXT[] DEFAULT '{}',
    
    -- Investigation
    assigned_to UUID REFERENCES users(id),
    investigation_notes TEXT,
    resolution_details TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Threat indicators
CREATE TABLE IF NOT EXISTS threat_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Indicator identification
    indicator_id TEXT UNIQUE NOT NULL DEFAULT (encode(gen_random_bytes(32), 'hex')),
    indicator_type TEXT NOT NULL CHECK (
        indicator_type IN ('ip', 'domain', 'url', 'hash', 'email', 'user_agent', 'pattern', 'signature')
    ),
    value TEXT NOT NULL,
    
    -- Classification
    category TEXT NOT NULL CHECK (
        category IN ('malicious', 'suspicious', 'benign', 'unknown')
    ),
    threat_types TEXT[] NOT NULL DEFAULT '{}',
    
    -- Source and confidence
    source TEXT NOT NULL, -- Source of the indicator
    confidence DECIMAL(3,2) DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    
    -- Context
    context JSONB DEFAULT '{}', -- Additional context
    tags TEXT[] DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    false_positive_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Behavioral baselines
CREATE TABLE IF NOT EXISTS behavioral_baselines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Entity identification
    entity_type TEXT NOT NULL CHECK (
        entity_type IN ('user', 'ip', 'device', 'session')
    ),
    entity_id TEXT NOT NULL,
    
    -- Baseline metrics
    metrics JSONB NOT NULL DEFAULT '{}', -- Behavioral metrics
    patterns JSONB DEFAULT '{}', -- Detected patterns
    
    -- Statistical data
    mean_values JSONB DEFAULT '{}',
    standard_deviations JSONB DEFAULT '{}',
    percentiles JSONB DEFAULT '{}',
    
    -- Training data
    sample_size INTEGER DEFAULT 0,
    training_period_days INTEGER DEFAULT 30,
    last_trained_at TIMESTAMPTZ,
    
    -- Model information
    model_version TEXT DEFAULT '1.0',
    model_accuracy DECIMAL(3,2),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(entity_type, entity_id)
);

-- Anomaly detections
CREATE TABLE IF NOT EXISTS anomaly_detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Detection identification
    detection_id TEXT UNIQUE NOT NULL DEFAULT (encode(gen_random_bytes(32), 'hex')),
    
    -- Entity information
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    baseline_id UUID REFERENCES behavioral_baselines(id),
    
    -- Anomaly details
    anomaly_type TEXT NOT NULL,
    anomaly_score DECIMAL(5,2) NOT NULL, -- 0-100
    confidence DECIMAL(3,2) NOT NULL,
    
    -- Anomaly metrics
    observed_values JSONB NOT NULL,
    expected_values JSONB NOT NULL,
    deviation_magnitude DECIMAL(5,2),
    
    -- Context
    context JSONB DEFAULT '{}',
    related_indicators TEXT[] DEFAULT '{}',
    
    -- Timeline
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    duration_minutes INTEGER,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'detected' CHECK (
        status IN ('detected', 'investigating', 'confirmed', 'false_positive', 'resolved')
    ),
    
    -- Incident linkage
    incident_id UUID REFERENCES threat_incidents(id),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Threat intelligence feeds
CREATE TABLE IF NOT EXISTS threat_intelligence_feeds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Feed identification
    feed_name TEXT UNIQUE NOT NULL,
    feed_type TEXT NOT NULL CHECK (
        feed_type IN ('ioc', 'reputation', 'malware', 'phishing', 'c2')
    ),
    feed_url TEXT,
    
    -- Feed configuration
    update_frequency_minutes INTEGER DEFAULT 60,
    format TEXT NOT NULL CHECK (
        format IN ('json', 'xml', 'csv', 'stix', 'taxii')
    ),
    
    -- Authentication
    api_key TEXT, -- Encrypted
    auth_type TEXT CHECK (
        auth_type IN ('none', 'api_key', 'oauth', 'certificate')
    ),
    
    -- Processing
    parser_config JSONB DEFAULT '{}',
    mapping_rules JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMPTZ,
    last_error TEXT,
    
    -- Statistics
    indicators_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ML models
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Model identification
    model_name TEXT UNIQUE NOT NULL,
    model_type TEXT NOT NULL CHECK (
        model_type IN ('classification', 'anomaly_detection', 'clustering', 'regression')
    ),
    model_version TEXT NOT NULL DEFAULT '1.0',
    
    -- Model configuration
    algorithm TEXT NOT NULL,
    hyperparameters JSONB DEFAULT '{}',
    feature_columns TEXT[] NOT NULL DEFAULT '{}',
    
    -- Training data
    training_dataset TEXT,
    training_samples INTEGER DEFAULT 0,
    validation_samples INTEGER DEFAULT 0,
    
    -- Performance metrics
    accuracy DECIMAL(3,2),
    precision DECIMAL(3,2),
    recall DECIMAL(3,2),
    f1_score DECIMAL(3,2),
    auc_score DECIMAL(3,2),
    
    -- Model files
    model_file_path TEXT,
    model_metadata JSONB DEFAULT '{}',
    
    -- Status
    is_active BOOLEAN DEFAULT FALSE,
    is_deployed BOOLEAN DEFAULT FALSE,
    
    -- Training
    trained_at TIMESTAMPTZ,
    trained_by UUID REFERENCES users(id),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_threat_detection_rules_type ON threat_detection_rules(rule_type);
CREATE INDEX idx_threat_detection_rules_category ON threat_detection_rules(category);
CREATE INDEX idx_threat_detection_rules_is_active ON threat_detection_rules(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_threat_incidents_type ON threat_incidents(threat_type);
CREATE INDEX idx_threat_incidents_severity ON threat_incidents(severity);
CREATE INDEX idx_threat_incidents_status ON threat_incidents(status);
CREATE INDEX idx_threat_incidents_detected_at ON threat_incidents(first_detected_at);
CREATE INDEX idx_threat_incidents_target ON threat_incidents(target_type, target_id);

CREATE INDEX idx_threat_indicators_type ON threat_indicators(indicator_type);
CREATE INDEX idx_threat_indicators_category ON threat_indicators(category);
CREATE INDEX idx_threat_indicators_value ON threat_indicators(value);
CREATE INDEX idx_threat_indicators_is_active ON threat_indicators(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_behavioral_baselines_entity ON behavioral_baselines(entity_type, entity_id);
CREATE INDEX idx_behavioral_baselines_is_active ON behavioral_baselines(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_anomaly_detections_entity ON anomaly_detections(entity_type, entity_id);
CREATE INDEX idx_anomaly_detections_score ON anomaly_detections(anomaly_score);
CREATE INDEX idx_anomaly_detections_detected_at ON anomaly_detections(detected_at);
CREATE INDEX idx_anomaly_detections_status ON anomaly_detections(status);

CREATE INDEX idx_threat_intelligence_feeds_is_active ON threat_intelligence_feeds(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_ml_models_is_active ON ml_models(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_ml_models_is_deployed ON ml_models(is_deployed) WHERE is_deployed = TRUE;

-- Create triggers for updated_at
CREATE TRIGGER update_threat_detection_rules_updated_at 
    BEFORE UPDATE ON threat_detection_rules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threat_incidents_updated_at 
    BEFORE UPDATE ON threat_incidents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threat_indicators_updated_at 
    BEFORE UPDATE ON threat_indicators 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_behavioral_baselines_updated_at 
    BEFORE UPDATE ON behavioral_baselines 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threat_intelligence_feeds_updated_at 
    BEFORE UPDATE ON threat_intelligence_feeds 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ml_models_updated_at 
    BEFORE UPDATE ON ml_models 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to detect threats
CREATE OR REPLACE FUNCTION detect_threats(
    p_entity_type TEXT,
    p_entity_id TEXT,
    p_event_data JSONB,
    p_context JSONB DEFAULT '{}'
) RETURNS TABLE(
    threat_detected BOOLEAN,
    threat_type TEXT,
    severity TEXT,
    confidence DECIMAL(3,2),
    rule_id UUID,
    rule_name TEXT,
    indicators JSONB,
    recommendations TEXT[]
) AS $$
DECLARE
    applicable_rules RECORD;
    baseline_record RECORD;
    threat_detected_val BOOLEAN := FALSE;
    threat_type_val TEXT;
    severity_val TEXT;
    confidence_val DECIMAL(3,2);
    rule_id_val UUID;
    rule_name_val TEXT;
    indicators_val JSONB;
    recommendations_val TEXT[];
BEGIN
    -- Get behavioral baseline
    SELECT * INTO baseline_record
    FROM behavioral_baselines
    WHERE entity_type = p_entity_type
    AND entity_id = p_entity_id
    AND is_active = TRUE
    LIMIT 1;
    
    -- Get applicable threat detection rules
    SELECT * INTO applicable_rules
    FROM threat_detection_rules
    WHERE is_active = TRUE
    AND (
        -- Simplified rule matching - in production, use proper rule engine
        rule_type = 'behavioral' OR
        rule_type = 'pattern' OR
        rule_type = 'anomaly'
    )
    ORDER BY severity_score DESC
    LIMIT 1;
    
    IF applicable_rules IS NOT NULL THEN
        -- Simplified threat detection logic
        -- In production, implement proper rule evaluation
        IF p_event_data ? 'failed_login_attempts' > 5 THEN
            threat_detected_val := TRUE;
            threat_type_val := 'brute_force';
            severity_val := 'high';
            confidence_val := 0.8;
            rule_id_val := applicable_rules.id;
            rule_name_val := applicable_rules.name;
            indicators_val := jsonb_build_object(
                'failed_attempts', p_event_data ? 'failed_login_attempts',
                'time_window', p_event_data ? 'time_window'
            );
            recommendations_val := ARRAY['Block IP', 'Require MFA', 'Notify user'];
        END IF;
    END IF;
    
    RETURN QUERY SELECT 
        threat_detected_val,
        threat_type_val,
        severity_val,
        confidence_val,
        rule_id_val,
        rule_name_val,
        indicators_val,
        recommendations_val;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create threat incident
CREATE OR REPLACE FUNCTION create_threat_incident(
    p_threat_type TEXT,
    p_severity TEXT,
    p_target_type TEXT,
    p_target_id UUID DEFAULT NULL,
    p_source_ip INET DEFAULT NULL,
    p_source_user_id UUID DEFAULT NULL,
    p_detection_rule_id UUID DEFAULT NULL,
    p_confidence DECIMAL(3,2),
    p_evidence JSONB DEFAULT '{}',
    p_title TEXT DEFAULT NULL,
    p_description TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    incident_id UUID;
    incident_id_val TEXT;
BEGIN
    -- Generate incident ID
    incident_id_val := format('INC_%s', encode(gen_random_bytes(16), 'hex'));
    
    -- Create incident
    INSERT INTO threat_incidents (
        incident_id,
        title,
        description,
        threat_type,
        severity,
        target_type,
        target_id,
        source_ip,
        source_user_id,
        detection_rule_id,
        confidence_score,
        evidence
    ) VALUES (
        incident_id_val,
        COALESCE(p_title, format('%s threat detected', p_threat_type)),
        p_description,
        p_threat_type,
        p_severity,
        p_target_type,
        p_target_id,
        p_source_ip,
        p_source_user_id,
        p_detection_rule_id,
        p_confidence,
        p_evidence
    ) RETURNING id INTO incident_id;
    
    -- Log the incident creation
    INSERT INTO audit_logs (
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        'THREAT_INCIDENT_CREATED',
        'security',
        format('Threat incident created: %s', incident_id_val),
        jsonb_build_object(
            'incident_id', incident_id,
            'threat_type', p_threat_type,
            'severity', p_severity,
            'confidence', p_confidence
        ),
        TRUE,
        NOW()
    );
    
    RETURN incident_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update behavioral baseline
CREATE OR REPLACE FUNCTION update_behavioral_baseline(
    p_entity_type TEXT,
    p_entity_id TEXT,
    p_metrics JSONB,
    p_patterns JSONB DEFAULT '{}'
) RETURNS BOOLEAN AS $$
DECLARE
    baseline_exists BOOLEAN;
    sample_size INTEGER;
BEGIN
    -- Check if baseline exists
    SELECT EXISTS(SELECT 1 FROM behavioral_baselines 
                   WHERE entity_type = p_entity_type 
                   AND entity_id = p_entity_id) 
    INTO baseline_exists;
    
    IF baseline_exists THEN
        -- Update existing baseline
        UPDATE behavioral_baselines
        SET 
            metrics = p_metrics,
            patterns = COALESCE(p_patterns, patterns),
            sample_size = sample_size + 1,
            updated_at = NOW()
        WHERE entity_type = p_entity_type
        AND entity_id = p_entity_id;
    ELSE
        -- Create new baseline
        INSERT INTO behavioral_baselines (
            entity_type,
            entity_id,
            metrics,
            patterns,
            sample_size
        ) VALUES (
            p_entity_type,
            p_entity_id,
            p_metrics,
            p_patterns,
            1
        );
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to add threat indicator
CREATE OR REPLACE FUNCTION add_threat_indicator(
    p_indicator_type TEXT,
    p_value TEXT,
    p_category TEXT,
    p_threat_types TEXT[],
    p_source TEXT,
    p_confidence DECIMAL(3,2) DEFAULT 0.5,
    p_context JSONB DEFAULT '{}',
    p_tags TEXT[] DEFAULT '{}'
) RETURNS UUID AS $$
DECLARE
    indicator_id UUID;
BEGIN
    INSERT INTO threat_indicators (
        indicator_type,
        value,
        category,
        threat_types,
        source,
        confidence,
        context,
        tags
    ) VALUES (
        p_indicator_type,
        p_value,
        p_category,
        p_threat_types,
        p_source,
        p_confidence,
        p_context,
        p_tags
    ) RETURNING id INTO indicator_id;
    
    RETURN indicator_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check threat indicators
CREATE OR REPLACE FUNCTION check_threat_indicators(
    p_indicator_type TEXT,
    p_value TEXT
) RETURNS TABLE(
    is_threat BOOLEAN,
    category TEXT,
    threat_types TEXT[],
    confidence DECIMAL(3,2),
    indicator_id UUID
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        TRUE,
        category,
        threat_types,
        confidence,
        id
    FROM threat_indicators
    WHERE indicator_type = p_indicator_type
    AND value = p_value
    AND is_active = TRUE
    AND category IN ('malicious', 'suspicious');
    
    -- If no threats found, return false
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, NULL, NULL, NULL, NULL LIMIT 1;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Enable RLS on threat detection tables
ALTER TABLE threat_detection_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE threat_incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE threat_indicators ENABLE ROW LEVEL SECURITY;
ALTER TABLE behavioral_baselines ENABLE ROW LEVEL SECURITY;
ALTER TABLE anomaly_detections ENABLE ROW LEVEL SECURITY;
ALTER TABLE threat_intelligence_feeds ENABLE ROW LEVEL SECURITY;
ALTER TABLE ml_models ENABLE ROW LEVEL SECURITY;

-- RLS policies for threat detection tables
CREATE POLICY "Admins can manage threat detection" ON threat_detection_rules
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth_user_id = auth.uid() 
            AND role IN ('admin', 'super_admin')
        )
    );

CREATE POLICY "Users can view own incidents" ON threat_incidents
    FOR SELECT USING (
        source_user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Admins can manage all incidents" ON threat_incidents
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth_user_id = auth.uid() 
            AND role IN ('admin', 'super_admin')
        )
    );

-- Grant permissions to authenticated users
GRANT EXECUTE ON FUNCTION detect_threats(TEXT, TEXT, JSONB, JSONB) TO authenticated;
GRANT EXECUTE ON FUNCTION create_threat_incident(TEXT, TEXT, TEXT, UUID, INET, UUID, UUID, DECIMAL(3,2), JSONB, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION update_behavioral_baseline(TEXT, TEXT, JSONB, JSONB) TO authenticated;
GRANT EXECUTE ON FUNCTION add_threat_indicator(TEXT, TEXT, TEXT, TEXT[], TEXT, DECIMAL(3,2), JSONB, TEXT[]) TO authenticated;
GRANT EXECUTE ON FUNCTION check_threat_indicators(TEXT, TEXT) TO authenticated;

-- Insert default threat detection rules
INSERT INTO threat_detection_rules (
    name,
    description,
    rule_type,
    category,
    conditions,
    thresholds,
    severity_score,
    auto_response,
    response_actions,
    is_system,
    is_active
) VALUES
-- Brute force detection
('Brute Force Attack Detection',
    'Detects brute force attacks on user accounts',
    'pattern',
    'authentication',
    jsonb_build_object(
        'failed_login_threshold', 5,
        'time_window_minutes', 15,
        'unique_ips_threshold', 3
    ),
    jsonb_build_object(
        'min_failed_attempts', 5,
        'max_time_window', 1800
    ),
    80,
    TRUE,
    ARRAY['block_ip', 'require_mfa', 'notify_admin'],
    TRUE,
    TRUE
),

-- Suspicious IP detection
('Suspicious IP Detection',
    'Detects access from known malicious or suspicious IPs',
    'reputation',
    'network',
    jsonb_build_object(
        'reputation_threshold', 0.3,
        'risk_level_threshold', 'high'
    ),
    jsonb_build_object(
        'min_reputation_score', 0.3,
        'risk_levels', ARRAY['high', 'critical']
    ),
    70,
    TRUE,
    ARRAY['challenge', 'log_access', 'notify_admin'],
    TRUE,
    TRUE
),

-- Anomaly detection
('Behavioral Anomaly Detection',
    'Detects unusual user behavior patterns',
    'behavioral',
    'insider_threat',
    jsonb_build_object(
        'deviation_threshold', 2.0,
        'confidence_threshold', 0.8
    ),
    jsonb_build_object(
        'min_deviation', 2.0,
        'min_confidence', 0.8
    ),
    60,
    FALSE,
    ARRAY['flag_for_review', 'notify_admin'],
    TRUE,
    TRUE
)

ON CONFLICT (name) DO NOTHING;

-- Add common threat indicators
INSERT INTO threat_indicators (
    indicator_type,
    value,
    category,
    threat_types,
    source,
    confidence,
    context
) VALUES
-- Known malicious IPs (examples)
('ip', '192.168.1.100', 'malicious', ARRAY['malware', 'botnet'], 'internal_threat_feed', 0.9, jsonb_build_object('source', 'internal_malware_analysis')),
('ip', '10.0.0.50', 'suspicious', ARRAY['scanner', 'reconnaissance'], 'internal_threat_feed', 0.7, jsonb_build_object('source', 'port_scan_detection')),

-- Suspicious domains
('domain', 'malicious-site.example.com', 'malicious', ARRAY['phishing', 'malware'], 'external_feed', 0.95, jsonb_build_object('feed', 'phish_tank')),
('domain', 'suspicious-domain.net', 'suspicious', ARRAY['phishing'], 'external_feed', 0.8, jsonb_build_object('feed', 'urlhaus'))

ON CONFLICT (indicator_type, value) DO NOTHING;

-- Log the threat detection system setup
INSERT INTO audit_logs (
    action,
    action_category,
    description,
    details,
    success,
    created_at
) VALUES (
    'THREAT_DETECTION_SYSTEM_SETUP',
    'security',
    'Advanced threat detection system implemented',
    jsonb_build_object(
        'migration', '20240115_threat_detection.sql',
        'tables_created', 7,
        'functions_created', 5,
        'default_rules', 3,
        'threat_indicators', 4
    ),
    TRUE,
    NOW()
);
