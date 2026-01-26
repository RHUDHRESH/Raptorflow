-- Enhanced Audit Logging System
-- Migration: 20240115_enhanced_audit_logging.sql
--
-- This migration implements comprehensive audit logging with GDPR compliance
-- and detailed security event tracking

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enhanced audit logs table (replaces existing audit_logs)
CREATE TABLE IF NOT EXISTS audit_logs_v2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Actor information
    actor_id UUID REFERENCES users(id),
    actor_role TEXT,
    actor_ip INET,
    actor_user_agent TEXT,
    actor_session_id TEXT,

    -- Action details
    action_category TEXT NOT NULL CHECK (
        action_category IN ('read', 'write', 'delete', 'admin', 'auth', 'security', 'billing', 'workspace')
    ),
    action_type TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id UUID,

    -- Workspace context
    workspace_id UUID REFERENCES workspaces(id),

    -- Change details
    old_values JSONB,
    new_values JSONB,
    sensitive_fields TEXT[], -- Fields containing PII

    -- Request context
    request_id TEXT,
    request_path TEXT,
    request_method TEXT,

    -- Result
    success BOOLEAN NOT NULL,
    error_code TEXT,
    error_message TEXT,

    -- Compliance
    gdpr_relevant BOOLEAN DEFAULT FALSE,
    data_subject_id UUID REFERENCES users(id), -- For GDPR data subject requests
    legal_basis TEXT, -- Legal basis for processing

    -- Performance
    duration_ms INTEGER, -- Request processing time

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Data access tracking (GDPR Article 15)
CREATE TABLE IF NOT EXISTS data_access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_subject_id UUID NOT NULL REFERENCES users(id),
    accessor_id UUID NOT NULL REFERENCES users(id),
    accessor_role TEXT,
    accessed_data JSONB NOT NULL, -- What data was accessed
    purpose TEXT NOT NULL, -- Purpose of access
    legal_basis TEXT NOT NULL, -- Legal basis for access
    ip_address INET,
    user_agent TEXT,
    session_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Security events table (enhanced)
CREATE TABLE IF NOT EXISTS security_events_v2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Event classification
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (
        severity IN ('info', 'warning', 'high', 'critical')
    ),
    category TEXT NOT NULL CHECK (
        category IN ('authentication', 'authorization', 'data_access', 'system', 'network', 'malware', 'fraud')
    ),

    -- User information
    user_id UUID REFERENCES users(id),
    user_email TEXT,
    user_role TEXT,

    -- Event details
    description TEXT,
    details JSONB,
    indicators JSONB, -- Threat indicators

    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id TEXT,
    workspace_id UUID REFERENCES workspaces(id),

    -- Response
    action_taken TEXT CHECK (
        action_taken IN ('blocked', 'flagged', 'logged', 'notified', 'investigated', 'resolved')
    ),
    auto_response BOOLEAN DEFAULT FALSE,

    -- Investigation
    investigated BOOLEAN DEFAULT FALSE,
    investigated_by UUID REFERENCES users(id),
    investigation_notes TEXT,
    investigation_priority TEXT DEFAULT 'medium' CHECK (
        investigation_priority IN ('low', 'medium', 'high', 'critical')
    ),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- User behavior baselines for anomaly detection
CREATE TABLE IF NOT EXISTS user_behavior_baselines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),

    -- Access patterns
    typical_ip_ranges INET[],
    typical_devices JSONB,
    typical_working_hours_start TIME,
    typical_working_hours_end TIME,
    typical_days_of_week INTEGER[], -- 0-6 (Sunday-Saturday)

    -- Usage patterns
    avg_session_duration INTEGER, -- minutes
    typical_actions_per_session INTEGER,
    typical_data_access_patterns JSONB,

    -- Metadata
    baseline_period_start TIMESTAMPTZ,
    baseline_period_end TIMESTAMPTZ,
    sample_size INTEGER DEFAULT 0, -- Number of data points used
    confidence_score DECIMAL(3,2) DEFAULT 0.5, -- 0-1

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id)
);

-- Audit log retention policies
CREATE TABLE IF NOT EXISTS audit_retention_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name TEXT NOT NULL,
    retention_period INTERVAL NOT NULL,
    archival_method TEXT DEFAULT 'delete' CHECK (
        archival_method IN ('delete', 'archive', 'anonymize')
    ),
    gdpr_category TEXT, -- For GDPR-specific retention
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default retention policies
INSERT INTO audit_retention_policies (table_name, retention_period, archival_method, gdpr_category) VALUES
('audit_logs_v2', INTERVAL '2 years', 'archive', 'general'),
('data_access_logs', INTERVAL '3 years', 'archive', 'data_access'),
('security_events_v2', INTERVAL '1 year', 'delete', 'security'),
('user_behavior_baselines', INTERVAL '5 years', 'delete', 'behavioral')
ON CONFLICT (table_name) DO NOTHING;

-- Create indexes for performance
CREATE INDEX idx_audit_logs_v2_actor_id ON audit_logs_v2(actor_id);
CREATE INDEX idx_audit_logs_v2_workspace_id ON audit_logs_v2(workspace_id);
CREATE INDEX idx_audit_logs_v2_action_category ON audit_logs_v2(action_category);
CREATE INDEX idx_audit_logs_v2_resource_type ON audit_logs_v2(resource_type);
CREATE INDEX idx_audit_logs_v2_created_at ON audit_logs_v2(created_at);
CREATE INDEX idx_audit_logs_v2_gdpr_relevant ON audit_logs_v2(gdpr_relevant) WHERE gdpr_relevant = TRUE;
CREATE INDEX idx_audit_logs_v2_request_id ON audit_logs_v2(request_id);

CREATE INDEX idx_data_access_logs_subject_id ON data_access_logs(data_subject_id);
CREATE INDEX idx_data_access_logs_accessor_id ON data_access_logs(accessor_id);
CREATE INDEX idx_data_access_logs_created_at ON data_access_logs(created_at);

CREATE INDEX idx_security_events_v2_user_id ON security_events_v2(user_id);
CREATE INDEX idx_security_events_v2_severity ON security_events_v2(severity);
CREATE INDEX idx_security_events_v2_category ON security_events_v2(category);
CREATE INDEX idx_security_events_v2_event_type ON security_events_v2(event_type);
CREATE INDEX idx_security_events_v2_created_at ON security_events_v2(created_at);
CREATE INDEX idx_security_events_v2_investigated ON security_events_v2(investigated) WHERE investigated = FALSE;

CREATE INDEX idx_user_behavior_baselines_user_id ON user_behavior_baselines(user_id);
CREATE INDEX idx_user_behavior_baselines_updated_at ON user_behavior_baselines(updated_at);

-- Create triggers for updated_at
CREATE TRIGGER update_user_behavior_baselines_updated_at
    BEFORE UPDATE ON user_behavior_baselines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audit_retention_policies_updated_at
    BEFORE UPDATE ON audit_retention_policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to log audit events
CREATE OR REPLACE FUNCTION log_audit_event(
    p_actor_id UUID,
    p_action_category TEXT,
    p_action_type TEXT,
    p_resource_type TEXT,
    p_resource_id UUID DEFAULT NULL,
    p_workspace_id UUID DEFAULT NULL,
    p_old_values JSONB DEFAULT NULL,
    p_new_values JSONB DEFAULT NULL,
    p_sensitive_fields TEXT[] DEFAULT NULL,
    p_request_id TEXT DEFAULT NULL,
    p_request_path TEXT DEFAULT NULL,
    p_request_method TEXT DEFAULT NULL,
    p_success BOOLEAN DEFAULT TRUE,
    p_error_code TEXT DEFAULT NULL,
    p_error_message TEXT DEFAULT NULL,
    p_gdpr_relevant BOOLEAN DEFAULT FALSE,
    p_data_subject_id UUID DEFAULT NULL,
    p_legal_basis TEXT DEFAULT NULL,
    p_duration_ms INTEGER DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    audit_id UUID;
    current_user_id UUID;
BEGIN
    -- Get current user if not provided
    current_user_id := COALESCE(p_actor_id, (SELECT id FROM users WHERE auth_user_id = auth.uid()));

    -- Insert audit record
    INSERT INTO audit_logs_v2 (
        actor_id,
        action_category,
        action_type,
        resource_type,
        resource_id,
        workspace_id,
        old_values,
        new_values,
        sensitive_fields,
        request_id,
        request_path,
        request_method,
        success,
        error_code,
        error_message,
        gdpr_relevant,
        data_subject_id,
        legal_basis,
        duration_ms,
        actor_ip,
        actor_user_agent,
        actor_session_id,
        actor_role
    ) VALUES (
        current_user_id,
        p_action_category,
        p_action_type,
        p_resource_type,
        p_resource_id,
        p_workspace_id,
        p_old_values,
        p_new_values,
        p_sensitive_fields,
        p_request_id,
        p_request_path,
        p_request_method,
        p_success,
        p_error_code,
        p_error_message,
        p_gdpr_relevant,
        p_data_subject_id,
        p_legal_basis,
        p_duration_ms,
        inet_client_addr(),
        current_setting('request.headers')::json->>'user-agent',
        current_setting('request.headers')::json->>'x-session-id',
        (SELECT role FROM users WHERE id = current_user_id)
    ) RETURNING id INTO audit_id;

    RETURN audit_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log data access (GDPR compliance)
CREATE OR REPLACE FUNCTION log_data_access(
    p_data_subject_id UUID,
    p_purpose TEXT,
    p_legal_basis TEXT,
    p_accessed_data JSONB,
    p_accessor_id UUID DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    access_id UUID;
    current_accessor_id UUID;
BEGIN
    -- Get current user if not provided
    current_accessor_id := COALESCE(p_accessor_id, (SELECT id FROM users WHERE auth_user_id = auth.uid()));

    -- Insert data access record
    INSERT INTO data_access_logs (
        data_subject_id,
        accessor_id,
        accessor_role,
        accessed_data,
        purpose,
        legal_basis,
        ip_address,
        user_agent,
        session_id
    ) VALUES (
        p_data_subject_id,
        current_accessor_id,
        (SELECT role FROM users WHERE id = current_accessor_id),
        p_accessed_data,
        p_purpose,
        p_legal_basis,
        inet_client_addr(),
        current_setting('request.headers')::json->>'user-agent',
        current_setting('request.headers')::json->>'x-session-id'
    ) RETURNING id INTO access_id;

    RETURN access_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log security events
CREATE OR REPLACE FUNCTION log_security_event(
    p_event_type TEXT,
    p_severity TEXT,
    p_category TEXT,
    p_description TEXT DEFAULT NULL,
    p_details JSONB DEFAULT NULL,
    p_indicators JSONB DEFAULT NULL,
    p_user_id UUID DEFAULT NULL,
    p_workspace_id UUID DEFAULT NULL,
    p_action_taken TEXT DEFAULT 'logged',
    p_auto_response BOOLEAN DEFAULT FALSE,
    p_investigation_priority TEXT DEFAULT 'medium'
) RETURNS UUID AS $$
DECLARE
    event_id UUID;
    current_user_id UUID;
BEGIN
    -- Get current user if not provided
    current_user_id := COALESCE(p_user_id, (SELECT id FROM users WHERE auth_user_id = auth.uid()));

    -- Insert security event
    INSERT INTO security_events_v2 (
        event_type,
        severity,
        category,
        description,
        details,
        indicators,
        user_id,
        user_email,
        user_role,
        ip_address,
        user_agent,
        session_id,
        workspace_id,
        action_taken,
        auto_response,
        investigation_priority
    ) VALUES (
        p_event_type,
        p_severity,
        p_category,
        p_description,
        p_details,
        p_indicators,
        current_user_id,
        (SELECT email FROM users WHERE id = current_user_id),
        (SELECT role FROM users WHERE id = current_user_id),
        inet_client_addr(),
        current_setting('request.headers')::json->>'user-agent',
        current_setting('request.headers')::json->>'x-session-id',
        p_workspace_id,
        p_action_taken,
        p_auto_response,
        p_investigation_priority
    ) RETURNING id INTO event_id;

    RETURN event_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update user behavior baseline
CREATE OR REPLACE FUNCTION update_user_behavior_baseline(
    p_user_id UUID,
    p_session_duration INTEGER DEFAULT NULL,
    p_actions_count INTEGER DEFAULT NULL,
    p_data_access_pattern JSONB DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    baseline_exists BOOLEAN;
BEGIN
    -- Check if baseline exists
    SELECT EXISTS(SELECT 1 FROM user_behavior_baselines WHERE user_id = p_user_id)
    INTO baseline_exists;

    IF baseline_exists THEN
        -- Update existing baseline
        UPDATE user_behavior_baselines SET
            avg_session_duration = COALESCE(
                (avg_session_duration + p_session_duration) / 2,
                avg_session_duration
            ),
            typical_actions_per_session = COALESCE(
                (typical_actions_per_session + p_actions_count) / 2,
                typical_actions_per_session
            ),
            typical_data_access_patterns = COALESCE(p_data_access_pattern, typical_data_access_patterns),
            sample_size = sample_size + 1,
            updated_at = NOW()
        WHERE user_id = p_user_id;
    ELSE
        -- Create new baseline
        INSERT INTO user_behavior_baselines (
            user_id,
            avg_session_duration,
            typical_actions_per_session,
            typical_data_access_patterns,
            baseline_period_start,
            baseline_period_end,
            sample_size
        ) VALUES (
            p_user_id,
            p_session_duration,
            p_actions_count,
            p_data_access_pattern,
            NOW() - INTERVAL '30 days',
            NOW(),
            1
        );
    END IF;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to detect anomalous behavior
CREATE OR REPLACE FUNCTION detect_anomalous_behavior(
    p_user_id UUID,
    p_current_ip INET DEFAULT NULL,
    p_current_device JSONB DEFAULT NULL,
    p_current_time TIMESTAMPTZ DEFAULT NOW(),
    p_session_duration INTEGER DEFAULT NULL,
    p_actions_count INTEGER DEFAULT NULL
) RETURNS TABLE(
    anomaly_type TEXT,
    severity TEXT,
    confidence DECIMAL(3,2),
    details JSONB
) AS $$
DECLARE
    baseline RECORD;
    anomalies JSONB := '[]'::jsonb;
BEGIN
    -- Get user baseline
    SELECT * INTO baseline
    FROM user_behavior_baselines
    WHERE user_id = p_user_id;

    IF NOT FOUND THEN
        -- No baseline available, create one
        PERFORM update_user_behavior_baseline(p_user_id, p_session_duration, p_actions_count);
        RETURN;
    END IF;

    -- Check for IP anomalies
    IF p_current_ip IS NOT NULL AND baseline.typical_ip_ranges IS NOT NULL THEN
        IF NOT (p_current_ip = ANY(baseline.typical_ip_ranges)) THEN
            anomalies := anomalies || jsonb_build_object(
                'type', 'unusual_ip',
                'severity', 'medium',
                'confidence', 0.7,
                'details', jsonb_build_object(
                    'current_ip', p_current_ip::text,
                    'typical_ips', baseline.typical_ip_ranges
                )
            );
        END IF;
    END IF;

    -- Check for time anomalies
    IF EXTRACT(HOUR FROM p_current_time) < EXTRACT(HOUR FROM baseline.typical_working_hours_start) OR
       EXTRACT(HOUR FROM p_current_time) > EXTRACT(HOUR FROM baseline.typical_working_hours_end) THEN
        anomalies := anomalies || jsonb_build_object(
            'type', 'unusual_time',
            'severity', 'low',
            'confidence', 0.6,
            'details', jsonb_build_object(
                'current_time', p_current_time,
                'typical_hours', jsonb_build_object(
                    'start', baseline.typical_working_hours_start,
                    'end', baseline.typical_working_hours_end
                )
            )
        );
    END IF;

    -- Check for session duration anomalies
    IF p_session_duration IS NOT NULL AND baseline.avg_session_duration IS NOT NULL THEN
        IF p_session_duration > baseline.avg_session_duration * 3 THEN
            anomalies := anomalies || jsonb_build_object(
                'type', 'unusual_session_duration',
                'severity', 'medium',
                'confidence', 0.8,
                'details', jsonb_build_object(
                    'current_duration', p_session_duration,
                    'typical_duration', baseline.avg_session_duration,
                    'ratio', p_session_duration::decimal / baseline.avg_session_duration
                )
            );
        END IF;
    END IF;

    -- Return detected anomalies
    RETURN QUERY
    SELECT
        anomaly->>'type' as anomaly_type,
        anomaly->>'severity' as severity,
        (anomaly->>'confidence')::decimal(3,2) as confidence,
        anomaly->'details' as details
    FROM jsonb_array_elements(anomalies) as anomaly;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to cleanup old audit logs
CREATE OR REPLACE FUNCTION cleanup_audit_logs() RETURNS TABLE(
    table_name TEXT,
    records_deleted INTEGER,
    retention_period INTERVAL
) AS $$
DECLARE
    policy_record RECORD;
    deleted_count INTEGER;
BEGIN
    FOR policy_record IN
        SELECT table_name, retention_period
        FROM audit_retention_policies
        WHERE is_active = TRUE
    LOOP
        -- Dynamic cleanup based on retention policies
        EXECUTE format('WITH deleted AS (
            DELETE FROM %I
            WHERE created_at < NOW() - %L
            RETURNING 1
        ) SELECT COUNT(*) FROM deleted',
            policy_record.table_name,
            policy_record.retention_period
        ) INTO deleted_count;

        RETURN QUERY SELECT
            policy_record.table_name,
            deleted_count,
            policy_record.retention_period;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Enable RLS on audit tables
ALTER TABLE audit_logs_v2 ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_access_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_events_v2 ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_behavior_baselines ENABLE ROW LEVEL SECURITY;

-- RLS policies for audit logs
CREATE POLICY "Users can read own audit logs" ON audit_logs_v2
    FOR SELECT USING (
        actor_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Admins can read all audit logs" ON audit_logs_v2
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- RLS policies for data access logs
CREATE POLICY "Users can read own data access logs" ON data_access_logs
    FOR SELECT USING (
        data_subject_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Admins can read all data access logs" ON data_access_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- RLS policies for security events
CREATE POLICY "Users can read own security events" ON security_events_v2
    FOR SELECT USING (
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Admins can read all security events" ON security_events_v2
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_user_id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- Grant permissions to authenticated users
GRANT EXECUTE ON FUNCTION log_audit_event(
    UUID, TEXT, TEXT, TEXT, UUID, UUID, JSONB, JSONB, TEXT[], TEXT, TEXT, TEXT, BOOLEAN, TEXT, TEXT, BOOLEAN, UUID, TEXT, INTEGER
) TO authenticated;

GRANT EXECUTE ON FUNCTION log_data_access(UUID, TEXT, TEXT, JSONB, UUID) TO authenticated;

GRANT EXECUTE ON FUNCTION log_security_event(
    TEXT, TEXT, TEXT, TEXT, JSONB, JSONB, UUID, UUID, TEXT, BOOLEAN, TEXT
) TO authenticated;

GRANT EXECUTE ON FUNCTION update_user_behavior_baseline(UUID, INTEGER, INTEGER, JSONB) TO authenticated;

GRANT EXECUTE ON FUNCTION detect_anomalous_behavior(UUID, INET, JSONB, TIMESTAMPTZ, INTEGER, INTEGER) TO authenticated;

GRANT EXECUTE ON FUNCTION cleanup_audit_logs() TO authenticated;

-- Log the enhanced audit logging setup
INSERT INTO audit_logs (
    actor_id,
    action,
    action_category,
    description,
    details,
    success,
    created_at
) VALUES (
    (SELECT id FROM users WHERE auth_user_id = auth.uid()),
    'ENHANCED_AUDIT_LOGGING_SETUP',
    'security',
    'Enhanced audit logging system implemented',
    jsonb_build_object(
        'migration', '20240115_enhanced_audit_logging.sql',
        'tables_created', 4,
        'functions_created', 6,
        'gdpr_compliant', TRUE
    ),
    TRUE,
    NOW()
);
