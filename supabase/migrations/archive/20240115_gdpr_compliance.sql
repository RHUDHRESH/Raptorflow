-- GDPR Compliance System
-- Migration: 20240115_gdpr_compliance.sql
--
-- This migration implements comprehensive GDPR compliance features including
-- data subject rights, consent management, data retention, and breach notification

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Data subject consent records
CREATE TABLE IF NOT EXISTS data_subject_consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Subject identification
    user_id UUID NOT NULL REFERENCES users(id),
    consent_type TEXT NOT NULL CHECK (
        consent_type IN ('data_processing', 'marketing', 'analytics', 'cookies', 'third_party_sharing', 'international_transfer')
    ),

    -- Consent details
    consent_given BOOLEAN NOT NULL,
    consent_version TEXT NOT NULL DEFAULT '1.0',
    consent_text TEXT NOT NULL,

    -- Legal basis
    legal_basis TEXT NOT NULL CHECK (
        legal_basis IN ('consent', 'contract', 'legal_obligation', 'vital_interests', 'public_task', 'legitimate_interests')
    ),
    legal_basis_details TEXT,

    -- Scope and purpose
    data_categories TEXT[] NOT NULL DEFAULT '{}', -- Types of data covered
    purposes TEXT[] NOT NULL DEFAULT '{}', -- Purposes for processing
    third_parties TEXT[] DEFAULT '{}', -- Third parties data may be shared with

    -- Validity period
    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    valid_until TIMESTAMPTZ,
    is_revocable BOOLEAN DEFAULT TRUE,

    -- Withdrawal
    withdrawn_at TIMESTAMPTZ,
    withdrawal_reason TEXT,
    withdrawal_method TEXT,

    -- Context
    ip_address INET,
    user_agent TEXT,
    consent_channel TEXT DEFAULT 'web', -- web, mobile, email, phone

    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, consent_type, consent_version)
);

-- Data subject requests (DSAR)
CREATE TABLE IF NOT EXISTS data_subject_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Request identification
    request_id TEXT UNIQUE NOT NULL DEFAULT (encode(gen_random_bytes(32), 'hex')),
    user_id UUID REFERENCES users(id),

    -- Request details
    request_type TEXT NOT NULL CHECK (
        request_type IN ('access', 'portability', 'rectification', 'erasure', 'restriction', 'objection')
    ),
    request_details TEXT,
    data_scope TEXT[] DEFAULT '{}', -- Specific data categories requested

    -- Status tracking
    status TEXT NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'processing', 'awaiting_verification', 'completed', 'denied', 'withdrawn')
    ),

    -- Processing
    assigned_to UUID REFERENCES users(id),
    started_processing_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    processing_days INTEGER,

    -- Response
    response_data JSONB, -- Response data for access/portability requests
    response_format TEXT CHECK (
        response_format IN ('json', 'csv', 'pdf', 'xml')
    ),
    response_method TEXT CHECK (
        response_method IN ('download', 'email', 'secure_link', 'postal')
    ),

    -- Verification
    verification_method TEXT CHECK (
        verification_method IN ('email', 'sms', 'id_document', 'video_call', 'in_person')
    ),
    verification_token TEXT,
    verified_at TIMESTAMPTZ,

    -- Context
    ip_address INET,
    user_agent TEXT,

    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data retention policies
CREATE TABLE IF NOT EXISTS data_retention_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Policy identification
    name TEXT NOT NULL,
    description TEXT,
    data_category TEXT NOT NULL,

    -- Retention rules
    retention_period INTERVAL NOT NULL,
    retention_reason TEXT NOT NULL,

    -- Legal basis for retention
    legal_basis TEXT NOT NULL CHECK (
        legal_basis IN ('consent', 'contract', 'legal_obligation', 'vital_interests', 'public_task', 'legitimate_interests')
    ),

    -- Actions after retention
    post_retention_action TEXT NOT NULL CHECK (
        post_retention_action IN ('delete', 'anonymize', 'archive', 'transfer')
    ),

    -- Exceptions
    exceptions JSONB DEFAULT '{}', -- Conditions under which retention may be extended

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE, -- System policies cannot be deleted

    -- Metadata
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(name, data_category)
);

-- Data breach records
CREATE TABLE IF NOT EXISTS data_breach_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Breach identification
    breach_id TEXT UNIQUE NOT NULL DEFAULT (encode(gen_random_bytes(32), 'hex')),

    -- Classification
    severity TEXT NOT NULL CHECK (
        severity IN ('low', 'medium', 'high', 'critical')
    ),
    breach_type TEXT NOT NULL CHECK (
        breach_type IN ('unauthorized_access', 'data_loss', 'data_destruction', 'data_alteration', 'unauthorized_disclosure')
    ),

    -- Timeline
    detected_at TIMESTAMPTZ NOT NULL,
    occurred_at TIMESTAMPTZ,
    contained_at TIMESTAMPTZ,
    reported_at TIMESTAMPTZ,

    -- Affected data
    data_categories TEXT[] NOT NULL DEFAULT '{}',
    affected_records INTEGER DEFAULT 0,
    affected_users INTEGER DEFAULT 0,

    -- Impact assessment
    potential_consequences TEXT[] DEFAULT '{}',
    likelihood_of_risk TEXT CHECK (
        likelihood_of_risk IN ('unlikely', 'possible', 'likely', 'very_likely')
    ),
    severity_of_impact TEXT CHECK (
        severity_of_impact IN ('minimal', 'limited', 'significant', 'severe')
    ),

    -- Notification requirements
    requires_supervisor_notification BOOLEAN DEFAULT FALSE,
    requires_dpa_notification BOOLEAN DEFAULT FALSE,
    requires_subject_notification BOOLEAN DEFAULT FALSE,
    notification_deadline TIMESTAMPTZ,

    -- Response actions
    immediate_actions TEXT[] DEFAULT '{}',
    containment_measures TEXT[] DEFAULT '{}',
    recovery_measures TEXT[] DEFAULT '{}',

    -- Investigation
    investigating_team TEXT[] DEFAULT '{}',
    investigation_status TEXT NOT NULL DEFAULT 'ongoing' CHECK (
        investigation_status IN ('ongoing', 'completed', 'closed')
    ),
    root_cause TEXT,

    -- Context
    source_ip INET,
    attack_vector TEXT,
    vulnerabilities_exploited TEXT[] DEFAULT '{}',

    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data processing records
CREATE TABLE IF NOT EXISTS data_processing_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Record identification
    record_id TEXT UNIQUE NOT NULL DEFAULT (encode(gen_random_bytes(32), 'hex')),

    -- Processing details
    processing_activity TEXT NOT NULL,
    data_categories TEXT[] NOT NULL DEFAULT '{}',
    data_subjects TEXT[] NOT NULL DEFAULT '{}', -- Categories of data subjects

    -- Legal basis
    legal_basis TEXT NOT NULL CHECK (
        legal_basis IN ('consent', 'contract', 'legal_obligation', 'vital_interests', 'public_task', 'legitimate_interests')
    ),
    legal_basis_description TEXT,

    -- Purpose
    processing_purposes TEXT[] NOT NULL DEFAULT '{}',
    legitimate_interests TEXT[] DEFAULT '{}',

    -- Recipients
    recipients TEXT[] DEFAULT '{}', -- Categories of recipients
    international_transfers BOOLEAN DEFAULT FALSE,
    transfer_countries TEXT[] DEFAULT '{}',

    -- Retention
    retention_period INTERVAL,
    retention_schedule TEXT,

    -- Security measures
    security_measures TEXT[] DEFAULT '{}',

    -- Context
    processing_system TEXT,
    automated BOOLEAN DEFAULT TRUE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cookie consent records
CREATE TABLE IF NOT EXISTS cookie_consent_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identification
    consent_id TEXT UNIQUE NOT NULL DEFAULT (encode(gen_random_bytes(32), 'hex')),
    user_id UUID REFERENCES users(id),
    session_id TEXT,

    -- Consent details
    consent_given BOOLEAN NOT NULL,
    consent_version TEXT NOT NULL DEFAULT '1.0',

    -- Cookie categories
    necessary_cookies BOOLEAN DEFAULT TRUE,
    functional_cookies BOOLEAN DEFAULT FALSE,
    analytics_cookies BOOLEAN DEFAULT FALSE,
    marketing_cookies BOOLEAN DEFAULT FALSE,
    third_party_cookies BOOLEAN DEFAULT FALSE,

    -- Context
    ip_address INET,
    user_agent TEXT,
    consent_method TEXT DEFAULT 'click', -- click, scroll, form_submit

    -- Validity
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    withdrawn_at TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Anonymization mappings (for GDPR right to be forgotten)
CREATE TABLE IF NOT EXISTS anonymization_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Original and anonymized IDs
    original_id UUID NOT NULL,
    anonymized_id UUID NOT NULL DEFAULT gen_random_uuid(),

    -- Entity type
    entity_type TEXT NOT NULL CHECK (
        entity_type IN ('user', 'workspace', 'icp_profile', 'campaign', 'session')
    ),

    -- Data to preserve
    preserved_data JSONB DEFAULT '{}', -- Data that can be retained after anonymization

    -- Context
    anonymization_reason TEXT NOT NULL,
    anonymized_at TIMESTAMPTZ DEFAULT NOW(),
    anonymized_by UUID REFERENCES users(id),

    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_data_subject_consents_user_id ON data_subject_consents(user_id);
CREATE INDEX idx_data_subject_consents_type ON data_subject_consents(consent_type);
CREATE INDEX idx_data_subject_consents_legal_basis ON data_subject_consents(legal_basis);
CREATE INDEX idx_data_subject_consents_valid_from ON data_subject_consents(valid_from);
CREATE INDEX idx_data_subject_consents_withdrawn_at ON data_subject_consents(withdrawn_at);

CREATE INDEX idx_data_subject_requests_user_id ON data_subject_requests(user_id);
CREATE INDEX idx_data_subject_requests_type ON data_subject_requests(request_type);
CREATE INDEX idx_data_subject_requests_status ON data_subject_requests(status);
CREATE INDEX idx_data_subject_requests_created_at ON data_subject_requests(created_at);

CREATE INDEX idx_data_retention_policies_category ON data_retention_policies(data_category);
CREATE INDEX idx_data_retention_policies_is_active ON data_retention_policies(is_active) WHERE is_active = TRUE;

CREATE INDEX idx_data_breach_records_severity ON data_breach_records(severity);
CREATE INDEX idx_data_breach_records_detected_at ON data_breach_records(detected_at);
CREATE INDEX idx_data_breach_records_status ON data_breach_records(investigation_status);

CREATE INDEX idx_data_processing_records_activity ON data_processing_records(processing_activity);
CREATE INDEX idx_data_processing_records_legal_basis ON data_processing_records(legal_basis);
CREATE INDEX idx_data_processing_records_created_at ON data_processing_records(created_at);

CREATE INDEX idx_cookie_consent_records_user_id ON cookie_consent_records(user_id);
CREATE INDEX idx_cookie_consent_records_session_id ON cookie_consent_records(session_id);
CREATE INDEX idx_cookie_consent_records_granted_at ON cookie_consent_records(granted_at);

CREATE INDEX idx_anonymization_mappings_original_id ON anonymization_mappings(original_id);
CREATE INDEX idx_anonymization_mappings_entity_type ON anonymization_mappings(entity_type);
CREATE INDEX idx_anonymization_mappings_anonymized_at ON anonymization_mappings(anonymized_at);

-- Create triggers for updated_at
CREATE TRIGGER update_data_subject_consents_updated_at
    BEFORE UPDATE ON data_subject_consents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_subject_requests_updated_at
    BEFORE UPDATE ON data_subject_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_retention_policies_updated_at
    BEFORE UPDATE ON data_retention_policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_breach_records_updated_at
    BEFORE UPDATE ON data_breach_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_processing_records_updated_at
    BEFORE UPDATE ON data_processing_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to record consent
CREATE OR REPLACE FUNCTION record_consent(
    p_user_id UUID,
    p_consent_type TEXT,
    p_consent_given BOOLEAN,
    p_consent_text TEXT,
    p_legal_basis TEXT,
    p_legal_basis_details TEXT DEFAULT NULL,
    p_data_categories TEXT[] DEFAULT '{}',
    p_purposes TEXT[] DEFAULT '{}',
    p_third_parties TEXT[] DEFAULT '{}',
    p_valid_until TIMESTAMPTZ DEFAULT NULL,
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    consent_id UUID;
BEGIN
    INSERT INTO data_subject_consents (
        user_id,
        consent_type,
        consent_given,
        consent_text,
        legal_basis,
        legal_basis_details,
        data_categories,
        purposes,
        third_parties,
        valid_until,
        ip_address,
        user_agent
    ) VALUES (
        p_user_id,
        p_consent_type,
        p_consent_given,
        p_consent_text,
        p_legal_basis,
        p_legal_basis_details,
        p_data_categories,
        p_purposes,
        p_third_parties,
        p_valid_until,
        p_ip_address,
        p_user_agent
    ) RETURNING id INTO consent_id;

    -- Log consent recording
    INSERT INTO audit_logs (
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        'CONSENT_RECORDED',
        'gdpr',
        format('Consent recorded for user %s: %s', p_user_id, p_consent_type),
        jsonb_build_object(
            'consent_id', consent_id,
            'consent_given', p_consent_given,
            'legal_basis', p_legal_basis,
            'data_categories', p_data_categories
        ),
        TRUE,
        NOW()
    );

    RETURN consent_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to withdraw consent
CREATE OR REPLACE FUNCTION withdraw_consent(
    p_user_id UUID,
    p_consent_type TEXT,
    p_withdrawal_reason TEXT DEFAULT NULL,
    p_withdrawal_method TEXT DEFAULT 'web'
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE data_subject_consents
    SET
        consent_given = FALSE,
        withdrawn_at = NOW(),
        withdrawal_reason = p_withdrawal_reason,
        withdrawal_method = p_withdrawal_method,
        updated_at = NOW()
    WHERE user_id = p_user_id
    AND consent_type = p_consent_type
    AND consent_given = TRUE;

    -- Log consent withdrawal
    INSERT INTO audit_logs (
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        'CONSENT_WITHDRAWN',
        'gdpr',
        format('Consent withdrawn for user %s: %s', p_user_id, p_consent_type),
        jsonb_build_object(
            'withdrawal_reason', p_withdrawal_reason,
            'withdrawal_method', p_withdrawal_method
        ),
        TRUE,
        NOW()
    );

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create data subject request
CREATE OR REPLACE FUNCTION create_dsar(
    p_user_id UUID,
    p_request_type TEXT,
    p_request_details TEXT DEFAULT NULL,
    p_data_scope TEXT[] DEFAULT '{}',
    p_response_format TEXT DEFAULT 'json',
    p_response_method TEXT DEFAULT 'download'
) RETURNS TEXT AS $$
DECLARE
    request_id_val TEXT;
BEGIN
    INSERT INTO data_subject_requests (
        user_id,
        request_type,
        request_details,
        data_scope,
        response_format,
        response_method
    ) VALUES (
        p_user_id,
        p_request_type,
        p_request_details,
        p_data_scope,
        p_response_format,
        p_response_method
    ) RETURNING request_id INTO request_id_val;

    -- Log DSAR creation
    INSERT INTO audit_logs (
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        'DSAR_CREATED',
        'gdpr',
        format('Data subject request created for user %s: %s', p_user_id, p_request_type),
        jsonb_build_object(
            'request_id', request_id_val,
            'request_type', p_request_type,
            'data_scope', p_data_scope
        ),
        TRUE,
        NOW()
    );

    RETURN request_id_val;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to anonymize user data
CREATE OR REPLACE FUNCTION anonymize_user_data(
    p_user_id UUID,
    p_anonymization_reason TEXT,
    p_preserve_data JSONB DEFAULT '{}'
) RETURNS UUID AS $$
DECLARE
    mapping_id UUID;
    anonymized_id UUID;
BEGIN
    -- Generate anonymized ID
    anonymized_id := gen_random_uuid();

    -- Create anonymization mapping
    INSERT INTO anonymization_mappings (
        original_id,
        anonymized_id,
        entity_type,
        preserved_data,
        anonymization_reason
    ) VALUES (
        p_user_id,
        anonymized_id,
        'user',
        p_preserve_data,
        p_anonymization_reason
    ) RETURNING id INTO mapping_id;

    -- Anonymize user record
    UPDATE users
    SET
        email = format('anonymized_%s@anonymized.com', anonymized_id),
        full_name = 'Anonymized User',
        phone = NULL,
        avatar_url = NULL,
        notes = jsonb_set(
            COALESCE(notes, '{}'),
            '{anonymized}',
            'true',
            '{anonymized_at}',
            NOW(),
            '{anonymized_reason}',
            p_anonymization_reason
        )
    WHERE id = p_user_id;

    -- Anonymize related records (simplified)
    UPDATE workspaces
    SET
        name = format('Anonymized Workspace %s', anonymized_id),
        slug = format('anonymized-%s', anonymized_id)
    WHERE user_id = p_user_id;

    -- Log anonymization
    INSERT INTO audit_logs (
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        'USER_DATA_ANONYMIZED',
        'gdpr',
        format('User data anonymized: %s', p_user_id),
        jsonb_build_object(
            'mapping_id', mapping_id,
            'anonymized_id', anonymized_id,
            'anonymization_reason', p_anonymization_reason
        ),
        TRUE,
        NOW()
    );

    RETURN mapping_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check consent
CREATE OR REPLACE FUNCTION check_consent(
    p_user_id UUID,
    p_consent_type TEXT,
    p_data_categories TEXT[] DEFAULT NULL,
    p_purposes TEXT[] DEFAULT NULL
) RETURNS TABLE(
    has_consent BOOLEAN,
    consent_version TEXT,
    legal_basis TEXT,
    valid_until TIMESTAMPTZ,
    is_expired BOOLEAN
) AS $$
DECLARE
    consent_record RECORD;
    current_time TIMESTAMPTZ := NOW();
BEGIN
    -- Get most recent consent record
    SELECT * INTO consent_record
    FROM data_subject_consents
    WHERE user_id = p_user_id
    AND consent_type = p_consent_type
    AND consent_given = TRUE
    AND valid_from <= current_time
    AND (valid_until IS NULL OR valid_until > current_time)
    ORDER BY valid_from DESC
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, NULL, NULL, NULL, TRUE;
    END IF;

    -- Check if consent covers requested data categories and purposes
    IF p_data_categories IS NOT NULL THEN
        IF NOT (p_data_categories <@ consent_record.data_categories) THEN
            RETURN QUERY SELECT FALSE, NULL, NULL, NULL, FALSE;
        END IF;
    END IF;

    IF p_purposes IS NOT NULL THEN
        IF NOT (p_purposes <@ consent_record.purposes) THEN
            RETURN QUERY SELECT FALSE, NULL, NULL, NULL, FALSE;
        END IF;
    END IF;

    RETURN QUERY SELECT
        TRUE,
        consent_record.consent_version,
        consent_record.legal_basis,
        consent_record.valid_until,
        FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to record data breach
CREATE OR REPLACE FUNCTION record_data_breach(
    p_severity TEXT,
    p_breach_type TEXT,
    p_detected_at TIMESTAMPTZ,
    p_occurred_at TIMESTAMPTZ,
    p_data_categories TEXT[],
    p_affected_records INTEGER DEFAULT 0,
    p_affected_users INTEGER DEFAULT 0,
    p_description TEXT DEFAULT NULL,
    p_potential_consequences TEXT[] DEFAULT '{}',
    p_likelihood_of_risk TEXT DEFAULT 'possible',
    p_severity_of_impact TEXT DEFAULT 'limited',
    p_source_ip INET DEFAULT NULL,
    p_attack_vector TEXT DEFAULT NULL
) RETURNS TEXT AS $$
DECLARE
    breach_id_val TEXT;
    notification_deadline TIMESTAMPTZ;
BEGIN
    -- Calculate notification deadline based on severity
    CASE p_severity
        WHEN 'critical' THEN
            notification_deadline := p_detected_at + INTERVAL '72 hours';
        WHEN 'high' THEN
            notification_deadline := p_detected_at + INTERVAL '72 hours';
        WHEN 'medium' THEN
            notification_deadline := p_detected_at + INTERVAL '30 days';
        ELSE
            notification_deadline := p_detected_at + INTERVAL '30 days';
    END CASE;

    INSERT INTO data_breach_records (
        severity,
        breach_type,
        detected_at,
        occurred_at,
        data_categories,
        affected_records,
        affected_users,
        potential_consequences,
        likelihood_of_risk,
        severity_of_impact,
        notification_deadline,
        source_ip,
        attack_vector,
        metadata
    ) VALUES (
        p_severity,
        p_breach_type,
        p_detected_at,
        p_occurred_at,
        p_data_categories,
        p_affected_records,
        p_affected_users,
        p_potential_consequences,
        p_likelihood_of_risk,
        p_severity_of_impact,
        notification_deadline,
        p_source_ip,
        p_attack_vector,
        jsonb_build_object('description', p_description)
    ) RETURNING breach_id INTO breach_id_val;

    -- Log breach recording
    INSERT INTO audit_logs (
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        'DATA_BREACH_RECORDED',
        'gdpr',
        format('Data breach recorded: %s', breach_id_val),
        jsonb_build_object(
            'breach_id', breach_id_val,
            'severity', p_severity,
            'breach_type', p_breach_type,
            'affected_users', p_affected_users
        ),
        TRUE,
        NOW()
    );

    RETURN breach_id_val;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Enable RLS on GDPR tables
ALTER TABLE data_subject_consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_subject_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_retention_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_breach_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_processing_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE cookie_consent_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE anonymization_mappings ENABLE ROW LEVEL SECURITY;

-- RLS policies for GDPR tables
CREATE POLICY "Users can manage own consents" ON data_subject_consents
    FOR ALL USING (
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Admins can manage all consents" ON data_subject_consents
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

CREATE POLICY "Users can manage own DSARs" ON data_subject_requests
    FOR ALL USING (
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Admins can manage all DSARs" ON data_subject_requests
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- Grant permissions to authenticated users
GRANT EXECUTE ON FUNCTION record_consent(UUID, TEXT, BOOLEAN, TEXT, TEXT, TEXT, TEXT[], TEXT[], TEXT[], TIMESTAMPTZ, INET, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION withdraw_consent(UUID, TEXT, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION create_dsar(UUID, TEXT, TEXT, TEXT[], TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION anonymize_user_data(UUID, TEXT, JSONB) TO authenticated;
GRANT EXECUTE ON FUNCTION check_consent(UUID, TEXT, TEXT[], TEXT[]) TO authenticated;
GRANT EXECUTE ON FUNCTION record_data_breach(TEXT, TEXT, TIMESTAMPTZ, TIMESTAMPTZ, TEXT[], INTEGER, INTEGER, TEXT, TEXT[], TEXT, TEXT, INET, TEXT) TO authenticated;

-- Insert default data retention policies
INSERT INTO data_retention_policies (
    name,
    description,
    data_category,
    retention_period,
    retention_reason,
    legal_basis,
    post_retention_action,
    is_system,
    is_active
) VALUES
-- User data retention
('User Account Data',
 'Basic user account information and profile data',
'user_profile',
    INTERVAL '7 years',
    'Legal obligation for accounting and compliance',
    'legal_obligation',
    'anonymize',
    TRUE,
    TRUE
),

-- Analytics data retention
('Analytics Data',
 'User behavior analytics and usage statistics',
'analytics',
    INTERVAL '2 years',
    'Legitimate interests for service improvement',
    'legitimate_interests',
    'delete',
    TRUE,
    TRUE
),

-- Security logs retention
('Security Logs',
    'Security event logs and audit trails',
'security_logs',
    INTERVAL '1 year',
    'Legal obligation for security monitoring',
    'legal_obligation',
    'delete',
    TRUE,
    TRUE
),

-- Consent records retention
('Consent Records',
'GDPR consent records and withdrawal history',
'consent_records',
    INTERVAL '7 years',
    'Legal obligation for consent management',
    'legal_obligation',
    'delete',
    TRUE,
    TRUE
)

ON CONFLICT (name, data_category) DO NOTHING;

-- Log the GDPR compliance system setup
INSERT INTO audit_logs (
    action,
    action_category,
    description,
    details,
    success,
    created_at
) VALUES (
    'GDPR_COMPLIANCE_SYSTEM_SETUP',
    'gdpr',
    'GDPR compliance system implemented',
    jsonb_build_object(
        'migration', '20240115_gdpr_compliance.sql',
        'tables_created', 7,
        'functions_created', 6,
        'retention_policies', 4
    ),
    TRUE,
    NOW()
);
