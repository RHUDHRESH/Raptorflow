-- Audit logs table for compliance and security
-- Migration: 20240122_audit_logs.sql

CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id UUID,
    details JSONB DEFAULT '{}',
    ip_address TEXT,
    user_agent TEXT,
    session_id TEXT,
    api_key_id UUID REFERENCES api_keys(id) ON DELETE SET NULL,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance and querying
CREATE INDEX IF NOT EXISTS idx_audit_logs_workspace_id ON public.audit_logs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON public.audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id ON public.audit_logs(resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_session_id ON public.audit_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_api_key_id ON public.audit_logs(api_key_id);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_workspace_created ON public.audit_logs(workspace_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action ON public.audit_logs(user_id, action, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_action ON public.audit_logs(resource_type, resource_id, action, created_at DESC);

-- GIN index for JSONB details
CREATE INDEX IF NOT EXISTS idx_audit_logs_details_gin ON public.audit_logs USING GIN (details);

-- Enable RLS
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies - Users can view audit logs for their own workspaces
CREATE POLICY "Users can view own workspace audit logs" ON public.audit_logs
    FOR SELECT USING (
        workspace_id IN (
            SELECT id FROM public.workspaces
            WHERE user_id = auth.uid()
        )
    );

-- Only system can insert audit logs (for security)
CREATE POLICY "System can insert audit logs" ON public.audit_logs
    FOR INSERT WITH CHECK (true);

-- Function to log audit events
CREATE OR REPLACE FUNCTION log_audit_event(
    p_workspace_id UUID,
    p_action TEXT,
    p_resource_type TEXT,
    p_resource_id UUID DEFAULT NULL,
    p_details JSONB DEFAULT '{}',
    p_user_id UUID DEFAULT NULL,
    p_ip_address TEXT DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_session_id TEXT DEFAULT NULL,
    p_api_key_id UUID DEFAULT NULL,
    p_success BOOLEAN DEFAULT true,
    p_error_message TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    audit_log_id UUID;
BEGIN
    -- Validate required parameters
    IF p_workspace_id IS NULL OR p_action IS NULL OR p_resource_type IS NULL THEN
        RAISE EXCEPTION 'workspace_id, action, and resource_type are required';
    END IF;

    -- Insert audit log
    INSERT INTO public.audit_logs (
        workspace_id,
        user_id,
        action,
        resource_type,
        resource_id,
        details,
        ip_address,
        user_agent,
        session_id,
        api_key_id,
        success,
        error_message
    ) VALUES (
        p_workspace_id,
        p_user_id,
        p_action,
        p_resource_type,
        p_resource_id,
        p_details,
        p_ip_address,
        p_user_agent,
        p_session_id,
        p_api_key_id,
        p_success,
        p_error_message
    ) RETURNING id INTO audit_log_id;

    RETURN audit_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log API access
CREATE OR REPLACE FUNCTION log_api_access(
    p_workspace_id UUID,
    p_method TEXT,
    p_endpoint TEXT,
    p_user_id UUID DEFAULT NULL,
    p_api_key_id UUID DEFAULT NULL,
    p_ip_address TEXT DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_response_status INTEGER DEFAULT NULL,
    p_response_time_ms INTEGER DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    audit_log_id UUID;
    details JSONB;
BEGIN
    -- Build details JSON
    details := jsonb_build_object(
        'method', p_method,
        'endpoint', p_endpoint,
        'response_status', p_response_status,
        'response_time_ms', p_response_time_ms
    );

    -- Determine success based on response status
    RETURN log_audit_event(
        p_workspace_id := p_workspace_id,
        p_action := 'api_access',
        p_resource_type := 'api_endpoint',
        p_resource_id := NULL,
        p_details := details,
        p_user_id := p_user_id,
        p_ip_address := p_ip_address,
        p_user_agent := p_user_agent,
        p_api_key_id := p_api_key_id,
        p_success := (p_response_status IS NULL OR p_response_status < 400),
        p_error_message := CASE WHEN p_response_status >= 400 THEN
            'HTTP ' || p_response_status ELSE NULL END
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log data changes
CREATE OR REPLACE FUNCTION log_data_change(
    p_workspace_id UUID,
    p_table_name TEXT,
    p_operation TEXT, -- 'INSERT', 'UPDATE', 'DELETE'
    p_record_id UUID,
    p_old_values JSONB DEFAULT NULL,
    p_new_values JSONB DEFAULT NULL,
    p_user_id UUID DEFAULT NULL,
    p_changed_fields TEXT[] DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    audit_log_id UUID;
    details JSONB;
BEGIN
    -- Validate operation
    IF p_operation NOT IN ('INSERT', 'UPDATE', 'DELETE') THEN
        RAISE EXCEPTION 'Invalid operation: %', p_operation;
    END IF;

    -- Build details JSON
    details := jsonb_build_object(
        'table', p_table_name,
        'operation', p_operation,
        'record_id', p_record_id,
        'old_values', p_old_values,
        'new_values', p_new_values,
        'changed_fields', p_changed_fields
    );

    RETURN log_audit_event(
        p_workspace_id := p_workspace_id,
        p_action := 'data_change',
        p_resource_type := p_table_name,
        p_resource_id := p_record_id,
        p_details := details,
        p_user_id := p_user_id,
        p_success := true
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log authentication events
CREATE OR REPLACE FUNCTION log_auth_event(
    p_user_id UUID,
    p_action TEXT, -- 'login', 'logout', 'signup', 'password_reset'
    p_success BOOLEAN DEFAULT true,
    p_error_message TEXT DEFAULT NULL,
    p_ip_address TEXT DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_session_id TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    workspace_id UUID;
    details JSONB;
BEGIN
    -- Get user's default workspace
    SELECT id INTO workspace_id
    FROM public.workspaces
    WHERE user_id = p_user_id
    LIMIT 1;

    -- Build details JSON
    details := jsonb_build_object(
        'auth_action', p_action,
        'success', p_success,
        'error_message', p_error_message
    );

    RETURN log_audit_event(
        p_workspace_id := workspace_id,
        p_action := 'authentication',
        p_resource_type := 'user_session',
        p_resource_id := p_user_id,
        p_details := details,
        p_user_id := p_user_id,
        p_ip_address := p_ip_address,
        p_user_agent := p_user_agent,
        p_session_id := p_session_id,
        p_success := p_success,
        p_error_message := p_error_message
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger function to automatically log data changes
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    workspace_id UUID;
    user_id UUID;
    old_values JSONB;
    new_values JSONB;
    changed_fields TEXT[];
    audit_log_id UUID;
BEGIN
    -- Try to get workspace_id from the record
    IF TG_OP = 'DELETE' THEN
        workspace_id := OLD.workspace_id;
        user_id := OLD.user_id;
        old_values := to_jsonb(OLD);
        new_values := NULL;
    ELSIF TG_OP = 'UPDATE' THEN
        workspace_id := NEW.workspace_id;
        user_id := NEW.user_id;
        old_values := to_jsonb(OLD);
        new_values := to_jsonb(NEW);

        -- Calculate changed fields
        changed_fields := ARRAY(
            SELECT key
            FROM jsonb_each_text(old_values) old(kv)
            JOIN jsonb_each_text(new_values) new(kv) ON old.key = new.key
            WHERE old.value != new.value
        );
    ELSE -- INSERT
        workspace_id := NEW.workspace_id;
        user_id := NEW.user_id;
        old_values := NULL;
        new_values := to_jsonb(NEW);
    END IF;

    -- Log the change if we have a workspace_id
    IF workspace_id IS NOT NULL THEN
        audit_log_id := log_data_change(
            p_workspace_id := workspace_id,
            p_table_name := TG_TABLE_NAME,
            p_operation := TG_OP,
            p_record_id := COALESCE(NEW.id, OLD.id),
            p_old_values := old_values,
            p_new_values := new_values,
            p_user_id := user_id,
            p_changed_fields := changed_fields
        );
    END IF;

    -- Return the appropriate record
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Views for common audit queries
CREATE OR REPLACE VIEW audit_summary AS
SELECT
    workspace_id,
    DATE_TRUNC('day', created_at) as audit_date,
    action,
    resource_type,
    COUNT(*) as event_count,
    COUNT(*) FILTER (WHERE NOT success) as error_count,
    MIN(created_at) as first_event,
    MAX(created_at) as last_event
FROM public.audit_logs
GROUP BY workspace_id, DATE_TRUNC('day', created_at), action, resource_type;

CREATE OR REPLACE VIEW user_activity_summary AS
SELECT
    user_id,
    workspace_id,
    DATE_TRUNC('day', created_at) as activity_date,
    COUNT(*) as total_actions,
    COUNT(DISTINCT action) as unique_actions,
    COUNT(DISTINCT resource_type) as resource_types_accessed,
    MIN(created_at) as first_activity,
    MAX(created_at) as last_activity
FROM public.audit_logs
WHERE user_id IS NOT NULL
GROUP BY user_id, workspace_id, DATE_TRUNC('day', created_at);

-- Function to cleanup old audit logs
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs(
    p_days_to_keep INTEGER DEFAULT 365
)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.audit_logs
    WHERE created_at < NOW() - INTERVAL '1 day' * p_days_to_keep;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT ON public.audit_logs TO authenticated;
GRANT SELECT ON audit_summary TO authenticated;
GRANT SELECT ON user_activity_summary TO authenticated;
GRANT EXECUTE ON FUNCTION log_audit_event(UUID, TEXT, TEXT, UUID, JSONB, UUID, TEXT, TEXT, TEXT, UUID, BOOLEAN, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION log_api_access(UUID, TEXT, TEXT, UUID, UUID, TEXT, TEXT, INTEGER, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION log_data_change(UUID, TEXT, TEXT, UUID, JSONB, JSONB, UUID, TEXT[]) TO authenticated;
GRANT EXECUTE ON FUNCTION log_auth_event(UUID, TEXT, BOOLEAN, TEXT, TEXT, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION cleanup_old_audit_logs(INTEGER) TO authenticated;
