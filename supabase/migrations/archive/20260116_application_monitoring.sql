-- Application Monitoring Database Schema
-- Migration: 20260116_application_monitoring.sql
-- Implements error tracking, performance metrics, and uptime monitoring

-- Create error_logs table
CREATE TABLE IF NOT EXISTS public.error_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  error_type TEXT NOT NULL,
  error_message TEXT NOT NULL,
  stack_trace TEXT,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  session_id TEXT,
  ip_address INET,
  user_agent TEXT,
  url TEXT,
  method TEXT,
  headers JSONB DEFAULT '{}'::JSONB,
  body JSONB,
  severity TEXT NOT NULL DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'closed')),
  assigned_to UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  resolution TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  resolved_at TIMESTAMPTZ
);

-- Create performance_metrics table
CREATE TABLE IF NOT EXISTS public.performance_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_type TEXT NOT NULL CHECK (metric_type IN (
    'response_time', 'throughput', 'error_rate', 'cpu_usage', 'memory_usage', 'database_connections'
  )),
  metric_name TEXT NOT NULL,
  value NUMERIC NOT NULL,
  unit TEXT NOT NULL,
  tags JSONB DEFAULT '{}'::JSONB,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  environment TEXT NOT NULL DEFAULT 'production' CHECK (environment IN ('development', 'staging', 'production')),
  service TEXT NOT NULL DEFAULT 'raptorflow',
  host TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create uptime_checks table
CREATE TABLE IF NOT EXISTS public.uptime_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  check_name TEXT NOT NULL,
  url TEXT NOT NULL,
  method TEXT NOT NULL DEFAULT 'GET',
  expected_status INTEGER NOT NULL DEFAULT 200,
  timeout_ms INTEGER NOT NULL DEFAULT 30000,
  interval_seconds INTEGER NOT NULL DEFAULT 60,
  is_active BOOLEAN NOT NULL DEFAULT true,
  last_checked TIMESTAMPTZ,
  last_status TEXT NOT NULL DEFAULT 'unknown' CHECK (last_status IN ('up', 'down', 'unknown')),
  last_response_time INTEGER,
  consecutive_failures INTEGER NOT NULL DEFAULT 0,
  total_checks INTEGER NOT NULL DEFAULT 0,
  successful_checks INTEGER NOT NULL DEFAULT 0,
  failed_checks INTEGER NOT NULL DEFAULT 0,
  uptime_percentage NUMERIC NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create health_checks table
CREATE TABLE IF NOT EXISTS public.health_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'healthy' CHECK (status IN ('healthy', 'unhealthy', 'degraded')),
  check_type TEXT NOT NULL CHECK (check_type IN ('database', 'redis', 'external_api', 'disk_space', 'memory')),
  response_time INTEGER,
  error_message TEXT,
  metadata JSONB DEFAULT '{}'::JSONB,
  last_checked TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create alerts table
CREATE TABLE IF NOT EXISTS public.alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_type TEXT NOT NULL CHECK (alert_type IN ('error', 'performance', 'uptime', 'security')),
  severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
  title TEXT NOT NULL,
  message TEXT NOT NULL,
  source TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::JSONB,
  is_active BOOLEAN NOT NULL DEFAULT true,
  acknowledged_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  acknowledged_at TIMESTAMPTZ,
  resolved_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  resolved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_error_logs_error_type ON public.error_logs(error_type);
CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON public.error_logs(severity);
CREATE INDEX IF NOT EXISTS idx_error_logs_status ON public.error_logs(status);
CREATE INDEX IF NOT EXISTS idx_error_logs_user_id ON public.error_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_created_at ON public.error_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_error_logs_ip_address ON public.error_logs(ip_address);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON public.performance_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON public.performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON public.performance_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_service ON public.performance_metrics(service);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_environment ON public.performance_metrics(environment);

CREATE INDEX IF NOT EXISTS idx_uptime_checks_active ON public.uptime_checks(is_active);
CREATE INDEX IF NOT EXISTS idx_uptime_checks_last_status ON public.uptime_checks(last_status);
CREATE INDEX IF NOT EXISTS idx_uptime_checks_last_checked ON public.uptime_checks(last_checked);
CREATE INDEX IF NOT EXISTS idx_uptime_checks_consecutive_failures ON public.uptime_checks(consecutive_failures);

CREATE INDEX IF NOT EXISTS idx_health_checks_service ON public.health_checks(service_name);
CREATE INDEX IF NOT EXISTS idx_health_checks_status ON public.health_checks(status);
CREATE INDEX IF NOT EXISTS idx_health_checks_type ON public.health_checks(check_type);
CREATE INDEX IF NOT EXISTS idx_health_checks_last_checked ON public.health_checks(last_checked);

CREATE INDEX IF NOT EXISTS idx_alerts_type ON public.alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON public.alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_active ON public.alerts(is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_source ON public.alerts(source);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON public.alerts(created_at);

-- Enable RLS on all tables
ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uptime_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.health_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;

-- RLS Policies for error_logs
CREATE POLICY "error_logs_select_admin" ON public.error_logs
  FOR SELECT
  USING (auth.jwt() ->> 'role' IN ('admin', 'owner'));

CREATE POLICY "error_logs_insert_authenticated" ON public.error_logs
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "error_logs_update_admin" ON public.error_logs
  FOR UPDATE
  USING (auth.jwt() ->> 'role' IN ('admin', 'owner'));

-- RLS Policies for performance_metrics
CREATE POLICY "performance_metrics_select_all" ON public.performance_metrics
  FOR SELECT
  USING (true);

CREATE POLICY "performance_metrics_insert_authenticated" ON public.performance_metrics
  FOR INSERT
  WITH CHECK (true);

-- RLS Policies for uptime_checks
CREATE POLICY "uptime_checks_select_admin" ON public.uptime_checks
  FOR SELECT
  USING (auth.jwt() ->> 'role' IN ('admin', 'owner'));

CREATE POLICY "uptime_checks_insert_admin" ON public.uptime_checks
  FOR INSERT
  WITH CHECK (auth.jwt() ->> 'role' IN ('admin', 'owner'));

CREATE POLICY "uptime_checks_update_admin" ON public.uptime_checks
  FOR UPDATE
  USING (auth.jwt() ->> 'role' IN ('admin', 'owner'));

-- RLS Policies for health_checks
CREATE POLICY "health_checks_select_all" ON public.health_checks
  FOR SELECT
  USING (true);

CREATE POLICY "health_checks_insert_authenticated" ON public.health_checks
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "health_checks_update_authenticated" ON public.health_checks
  FOR UPDATE
  USING (true);

-- RLS Policies for alerts
CREATE POLICY "alerts_select_admin" ON public.alerts
  FOR SELECT
  USING (auth.jwt() ->> 'role' IN ('admin', 'owner'));

CREATE POLICY "alerts_insert_authenticated" ON public.alerts
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "alerts_update_admin" ON public.alerts
  FOR UPDATE
  USING (auth.jwt() ->> 'role' IN ('admin', 'owner'));

-- Create triggers for updated_at timestamps
CREATE TRIGGER error_logs_updated_at
    BEFORE UPDATE ON public.error_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER uptime_checks_updated_at
    BEFORE UPDATE ON public.uptime_checks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER health_checks_updated_at
    BEFORE UPDATE ON public.health_checks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER alerts_updated_at
    BEFORE UPDATE ON public.alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to log application error
CREATE OR REPLACE FUNCTION log_application_error(
    error_type_param TEXT,
    error_message_param TEXT,
    stack_trace_param TEXT DEFAULT NULL,
    user_uuid UUID DEFAULT NULL,
    session_id_param TEXT DEFAULT NULL,
    ip_param INET DEFAULT NULL,
    user_agent_param TEXT DEFAULT NULL,
    url_param TEXT DEFAULT NULL,
    method_param TEXT DEFAULT NULL,
    headers_param JSONB DEFAULT NULL,
    body_param JSONB DEFAULT NULL,
    severity_param TEXT DEFAULT 'medium'
)
RETURNS UUID AS $$
DECLARE
    error_id UUID;
BEGIN
    INSERT INTO public.error_logs (
        error_type: error_type_param,
        error_message: error_message_param,
        stack_trace: stack_trace_param,
        user_id: user_uuid,
        session_id: session_id_param,
        ip_address: ip_param,
        user_agent: user_agent_param,
        url: url_param,
        method: method_param,
        headers: headers_param,
        body: body_param,
        severity: severity_param,
        created_at: NOW(),
        updated_at: NOW()
    )
    RETURNING id INTO error_id;

    RETURN error_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to record performance metric
CREATE OR REPLACE FUNCTION record_performance_metric(
    metric_type_param TEXT,
    metric_name_param TEXT,
    value_param NUMERIC,
    unit_param TEXT,
    tags_param JSONB DEFAULT NULL,
    environment_param TEXT DEFAULT 'production',
    service_param TEXT DEFAULT 'raptorflow',
    host_param TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    metric_id UUID;
BEGIN
    INSERT INTO public.performance_metrics (
        metric_type: metric_type_param,
        metric_name: metric_name_param,
        value: value_param,
        unit: unit_param,
        tags: tags_param,
        timestamp: NOW(),
        environment: environment_param,
        service: service_param,
        host: host_param,
        created_at: NOW()
    )
    RETURNING id INTO metric_id;

    RETURN metric_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to create alert
CREATE OR REPLACE FUNCTION create_alert(
    alert_type_param TEXT,
    severity_param TEXT,
    title_param TEXT,
    message_param TEXT,
    source_param TEXT,
    metadata_param JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    alert_id UUID;
BEGIN
    INSERT INTO public.alerts (
        alert_type: alert_type_param,
        severity: severity_param,
        title: title_param,
        message: message_param,
        source: source_param,
        metadata: metadata_param,
        is_active: true,
        created_at: NOW(),
        updated_at: NOW()
    )
    RETURNING id INTO alert_id;

    RETURN alert_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to acknowledge alert
CREATE OR REPLACE FUNCTION acknowledge_alert(
    alert_id_param UUID,
    user_uuid UUID
)
RETURNS BOOLEAN AS $$
DECLARE
    success BOOLEAN DEFAULT FALSE;
BEGIN
    UPDATE public.alerts
    SET acknowledged_by = user_uuid,
        acknowledged_at = NOW(),
        updated_at = NOW()
    WHERE id = alert_id_param
      AND is_active = true;

    GET DIAGNOSTICS (ROW_COUNT, success);
    RETURN success;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to resolve alert
CREATE OR REPLACE FUNCTION resolve_alert(
    alert_id_param UUID,
    user_uuid UUID,
    resolution_param TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    success BOOLEAN DEFAULT FALSE;
BEGIN
    UPDATE public.alerts
    SET is_active = false,
        resolved_by = user_uuid,
        resolved_at = NOW(),
        resolution: resolution_param,
        updated_at = NOW()
    WHERE id = alert_id_param
      AND is_active = true;

    GET DIAGNOSTICS (ROW_COUNT, success);
    RETURN success;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get monitoring statistics
CREATE OR REPLACE FUNCTION get_monitoring_stats(
    days_param INTEGER DEFAULT 30
)
RETURNS TABLE (
    total_errors BIGINT,
    critical_errors BIGINT,
    resolved_errors BIGINT,
    avg_response_time NUMERIC,
    uptime_percentage NUMERIC,
    active_alerts BIGINT,
    health_status JSONB
) AS $$
DECLARE
    since TIMESTAMP;
BEGIN
    since := NOW() - (days_param || 30) * INTERVAL '1 day';

    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM public.error_logs WHERE created_at >= since) AS total_errors,
        (SELECT COUNT(*) FROM public.error_logs WHERE severity = 'critical' AND created_at >= since) AS critical_errors,
        (SELECT COUNT(*) FROM public.error_logs WHERE status = 'resolved' AND created_at >= since) AS resolved_errors,
        COALESCE(AVG(value), 0) FILTER (metric_type = 'response_time' AND timestamp >= since) AS avg_response_time,
        COALESCE(AVG(uptime_percentage), 100) AS uptime_percentage,
        (SELECT COUNT(*) FROM public.alerts WHERE is_active = true) AS active_alerts,
        jsonb_build_object(
            'database': (SELECT status FROM public.health_checks WHERE check_type = 'database' ORDER BY last_checked DESC LIMIT 1),
            'redis': (SELECT status FROM public.health_checks WHERE check_type = 'redis' ORDER BY last_checked DESC LIMIT 1),
            'external_api': (SELECT status FROM public.health_checks WHERE check_type = 'external_api' ORDER BY last_checked DESC LIMIT 1),
            'disk_space': (SELECT status FROM public.health_checks WHERE check_type = 'disk_space' ORDER BY last_checked DESC LIMIT 1),
            'memory': (SELECT status FROM public.health_checks WHERE check_type = 'memory' ORDER BY last_checked DESC LIMIT 1)
        ) AS health_status
    FROM public.error_logs
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to clean up old monitoring data
CREATE OR REPLACE FUNCTION cleanup_old_monitoring_data(
    days_old INTEGER DEFAULT 90
)
RETURNS TABLE (
    error_logs_deleted BIGINT,
    performance_metrics_deleted BIGINT,
    alerts_deleted BIGINT
) AS $$
DECLARE
    cutoff_date TIMESTAMP;
    error_count BIGINT;
    metric_count BIGINT;
    alert_count BIGINT;
BEGIN
    cutoff_date := NOW() - (days_old || 90) * INTERVAL '1 day';

    -- Delete old error logs
    DELETE FROM public.error_logs
    WHERE created_at < cutoff_date;
    GET DIAGNOSTICS (ROW_COUNT, error_count);

    -- Delete old performance metrics
    DELETE FROM public.performance_metrics
    WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS (ROW_COUNT, metric_count);

    -- Delete old resolved alerts
    DELETE FROM public.alerts
    WHERE created_at < cutoff_date
      AND is_active = false;
    GET DIAGNOSTICS (ROW_COUNT, alert_count);

    RETURN QUERY
    SELECT error_count, metric_count, alert_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT ON public.error_logs TO authenticated;
GRANT SELECT ON public.performance_metrics TO authenticated;
GRANT SELECT ON public.uptime_checks TO authenticated;
GRANT SELECT ON public.health_checks TO authenticated;
GRANT SELECT ON public.alerts TO authenticated;

GRANT EXECUTE ON FUNCTION log_application_error TO authenticated;
GRANT EXECUTE ON FUNCTION record_performance_metric TO authenticated;
GRANT EXECUTE ON FUNCTION create_alert TO authenticated;
GRANT EXECUTE ON FUNCTION acknowledge_alert TO authenticated;
GRANT EXECUTE ON FUNCTION resolve_alert TO authenticated;
GRANT EXECUTE ON FUNCTION get_monitoring_stats TO authenticated;
GRANT EXECUTE ON FUNCTION cleanup_old_monitoring_data TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE public.error_logs IS 'Application error logs with detailed context and tracking';
COMMENT ON TABLE public.performance_metrics IS 'Performance metrics for monitoring system health';
COMMENT ON TABLE public.uptime_checks IS 'Uptime monitoring for external services and endpoints';
COMMENT ON TABLE public.health_checks IS 'Health checks for internal services and dependencies';
COMMENT ON TABLE public.alerts IS 'Alerts for monitoring events and incidents';

COMMENT ON FUNCTION log_application_error IS 'Log application error with context';
COMMENT ON FUNCTION record_performance_metric IS 'Record performance metric for monitoring';
COMMENT ON FUNCTION create_alert IS 'Create alert for monitoring events';
COMMENT ON FUNCTION acknowledge_alert IS 'Acknowledge alert for tracking';
COMMENT ON FUNCTION resolve_alert IS 'Resolve alert and record resolution';
COMMENT ON FUNCTION get_monitoring_stats IS 'Get comprehensive monitoring statistics';
COMMENT ON FUNCTION cleanup_old_monitoring_data IS 'Clean up old monitoring data to manage storage';

-- Create function to update uptime check statistics
CREATE OR REPLACE FUNCTION update_uptime_check_stats(
    check_id_param UUID,
    status_param TEXT,
    response_time_param INTEGER DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    current_check RECORD;
    new_total_checks INTEGER;
    new_successful_checks INTEGER;
    new_failed_checks INTEGER;
    new_consecutive_failures INTEGER;
    new_uptime_percentage NUMERIC;
BEGIN
    -- Get current check data
    SELECT * INTO current_check
    FROM public.uptime_checks
    WHERE id = check_id_param;

    -- Calculate new statistics
    new_total_checks := current_check.total_checks + 1;

    IF status_param = 'up' THEN
        new_successful_checks := current_check.successful_checks + 1;
        new_failed_checks := current_check.failed_checks;
        new_consecutive_failures := 0;
    ELSE
        new_successful_checks := current_check.successful_checks;
        new_failed_checks := current_check.failed_checks + 1;
        new_consecutive_failures := current_check.consecutive_failures + 1;
    END IF;

    new_uptime_percentage := (new_successful_checks::NUMERIC / new_total_checks::NUMERIC) * 100;

    -- Update check
    UPDATE public.uptime_checks
    SET last_checked = NOW(),
        last_status = status_param,
        last_response_time = response_time_param,
        consecutive_failures = new_consecutive_failures,
        total_checks = new_total_checks,
        successful_checks = new_successful_checks,
        failed_checks = new_failed_checks,
        uptime_percentage = new_uptime_percentage,
        updated_at = NOW()
    WHERE id = check_id_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permission for update function
GRANT EXECUTE ON FUNCTION update_uptime_check_stats TO authenticated;

-- Add comments for documentation
COMMENT ON FUNCTION update_uptime_check_stats IS 'Update uptime check statistics after check';
