-- Session Security Database Schema
-- Migration: 20260116_session_security.sql
-- Implements concurrent session limits, device fingerprinting, and anomaly detection

-- Create device_fingerprints table
CREATE TABLE IF NOT EXISTS public.device_fingerprints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  fingerprint_hash TEXT NOT NULL,
  user_agent TEXT,
  ip_address INET,
  screen_resolution TEXT,
  timezone TEXT,
  language TEXT,
  platform TEXT,
  is_mobile BOOLEAN NOT NULL DEFAULT false,
  is_tablet BOOLEAN NOT NULL DEFAULT false,
  trusted BOOLEAN NOT NULL DEFAULT false,
  first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  access_count INTEGER NOT NULL DEFAULT 1,

  UNIQUE(user_id, fingerprint_hash)
);

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS public.user_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  session_token TEXT NOT NULL UNIQUE,
  device_fingerprint_id UUID NOT NULL REFERENCES public.device_fingerprints(id) ON DELETE CASCADE,
  ip_address INET,
  user_agent TEXT,
  is_active BOOLEAN NOT NULL DEFAULT true,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_accessed TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  access_count INTEGER NOT NULL DEFAULT 1,
  location JSONB DEFAULT '{
    "country": null,
    "city": null,
    "latitude": null,
    "longitude": null
  }'::JSONB
);

-- Create security_events table
CREATE TABLE IF NOT EXISTS public.security_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
  message TEXT NOT NULL,
  metadata JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_device_fingerprints_user_id ON public.device_fingerprints(user_id);
CREATE INDEX IF NOT EXISTS idx_device_fingerprints_hash ON public.device_fingerprints(fingerprint_hash);
CREATE INDEX IF NOT EXISTS idx_device_fingerprints_trusted ON public.device_fingerprints(trusted);
CREATE INDEX IF NOT EXISTS idx_device_fingerprints_last_seen ON public.device_fingerprints(last_seen);
CREATE INDEX IF NOT EXISTS idx_device_fingerprints_access_count ON public.device_fingerprints(access_count);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON public.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_device ON public.user_sessions(device_fingerprint_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON public.user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON public.user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_accessed ON public.user_sessions(last_accessed);

CREATE INDEX IF NOT EXISTS idx_security_events_user_id ON public.security_events(user_id);
CREATE INDEX IF NOT EXISTS idx_security_events_type ON public.security_events(event_type);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON public.security_events(severity);
CREATE INDEX IF NOT EXISTS idx_security_events_created_at ON public.security_events(created_at);

-- Enable RLS on all tables
ALTER TABLE public.device_fingerprints ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_events ENABLE ROW LEVEL SECURITY;

-- RLS Policies for device_fingerprints
CREATE POLICY "device_fingerprints_select_own" ON public.device_fingerprints
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "device_fingerprints_insert_own" ON public.device_fingerprints
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "device_fingerprints_update_own" ON public.device_fingerprints
  FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "device_fingerprints_delete_own" ON public.device_fingerprints
  FOR DELETE
  USING (user_id = auth.uid());

-- RLS Policies for user_sessions
CREATE POLICY "user_sessions_select_own" ON public.user_sessions
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "user_sessions_insert_own" ON public.user_sessions
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "user_sessions_update_own" ON public.user_sessions
  FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "user_sessions_delete_own" ON public.user_sessions
  FOR DELETE
  USING (user_id = auth.uid());

-- RLS Policies for security_events
CREATE POLICY "security_events_select_own" ON public.security_events
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "security_events_insert_authenticated" ON public.security_events
  FOR INSERT
  WITH CHECK (user_id = auth.uid() OR user_id IS NULL);

-- Create triggers for updated_at timestamps
CREATE TRIGGER device_fingerprints_updated_at
    BEFORE UPDATE ON public.device_fingerprints
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER user_sessions_updated_at
    BEFORE UPDATE ON public.user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for incrementing access count
CREATE OR REPLACE FUNCTION increment_access_count()
RETURNS TRIGGER AS $$
BEGIN
    NEW.access_count = OLD.access_count + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER increment_session_access_count
    BEFORE UPDATE ON public.user_sessions
    FOR EACH ROW
    WHEN (NEW.last_accessed > OLD.last_accessed)
    EXECUTE FUNCTION increment_access_count();

-- Create function to check session validity
CREATE OR REPLACE FUNCTION is_session_valid(session_token TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.user_sessions
        WHERE session_token = session_token
        AND is_active = true
        AND expires_at > NOW()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check device trust
CREATE OR REPLACE FUNCTION is_device_trusted(user_uuid UUID, device_hash TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.device_fingerprints
        WHERE user_id = user_uuid
        AND fingerprint_hash = device_hash
        AND trusted = true
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check concurrent session limit
CREATE OR REPLACE FUNCTION check_concurrent_session_limit(
    user_uuid UUID,
    max_sessions INTEGER DEFAULT 3
)
RETURNS BOOLEAN AS $$
DECLARE
    current_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO current_count
    FROM public.user_sessions
    WHERE user_id = user_uuid
    AND is_active = true
    AND expires_at > NOW();

    RETURN current_count < max_sessions;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check device session limit
CREATE OR REPLACE FUNCTION check_device_session_limit(
    user_uuid UUID,
    device_fingerprint_id UUID,
    max_per_device INTEGER DEFAULT 1
)
RETURNS BOOLEAN AS $$
DECLARE
    current_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO current_count
    FROM public.user_sessions
    WHERE user_id = user_uuid
    AND device_fingerprint_id = device_fingerprint_id
    AND is_active = true
    AND expires_at > NOW();

    RETURN current_count < max_per_device;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get user's device fingerprint
CREATE OR REPLACE FUNCTION get_device_fingerprint(
    user_uuid UUID,
    device_hash TEXT
)
RETURNS UUID AS $$
DECLARE
    device_id UUID;
BEGIN
    SELECT id INTO device_id
    FROM public.device_fingerprints
    WHERE user_id = user_uuid
    AND fingerprint_hash = device_hash;

    RETURN device_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to log security event
CREATE OR REPLACE FUNCTION log_security_event(
    user_uuid UUID,
    event_type_param TEXT,
    severity_param TEXT,
    message_param TEXT,
    metadata_param JSONB DEFAULT NULL,
    ip_param INET DEFAULT NULL,
    user_agent_param TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    event_id UUID;
BEGIN
    INSERT INTO public.security_events (
        user_id,
        event_type,
        severity,
        message,
        metadata,
        ip_address,
        user_agent
    ) VALUES (
        user_uuid,
        event_type_param,
        severity_param,
        message_param,
        metadata_param,
        ip_param,
        user_agent_param
    )
    RETURNING id INTO event_id;

    RETURN event_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    UPDATE public.user_sessions
    SET is_active = false,
        last_accessed = NOW()
    WHERE expires_at <= NOW()
    AND is_active = true;

    GET DIAGNOSTICS (ROW_COUNT, deleted_count);
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to clean up inactive devices
CREATE OR REPLACE FUNCTION cleanup_inactive_devices(
    days_inactive INTEGER DEFAULT 30
)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.device_fingerprints
    WHERE last_seen < NOW() - (days_inactive || 30) * INTERVAL '1 day'
    AND id NOT IN (
        SELECT DISTINCT device_fingerprint_id
        FROM public.user_sessions
        WHERE is_active = true
    );

    GET DIAGNOSTICS (ROW_COUNT, deleted_count);
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to increment session access count
CREATE OR REPLACE FUNCTION increment_session_access_count(session_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE public.user_sessions
    SET access_count = access_count + 1,
        last_accessed = NOW()
    WHERE id = session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT ON public.device_fingerprints TO authenticated;
GRANT SELECT ON public.user_sessions TO authenticated;
GRANT SELECT ON public.security_events TO authenticated;

GRANT EXECUTE ON FUNCTION is_session_valid TO authenticated;
GRANT EXECUTE ON FUNCTION is_device_trusted TO authenticated;
GRANT EXECUTE ON FUNCTION check_concurrent_session_limit TO authenticated;
GRANT EXECUTE ON FUNCTION check_device_session_limit TO authenticated;
GRANT EXECUTE ON FUNCTION get_device_fingerprint TO authenticated;
GRANT EXECUTE ON FUNCTION log_security_event TO authenticated;
GRANT EXECUTE ON FUNCTION cleanup_expired_sessions TO authenticated;
GRANT EXECUTE FUNCTION cleanup_inactive_devices TO authenticated;
GRANT EXECUTE ON FUNCTION increment_session_access_count TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE public.device_fingerprints IS 'Device fingerprints for session security and anomaly detection';
COMMENT ON TABLE public.user_sessions IS 'User sessions with device tracking and security controls';
COMMENT ON TABLE public.security_events IS 'Security event log for monitoring suspicious activities';

COMMENT ON FUNCTION is_session_valid IS 'Check if a session token is still valid';
COMMENT ON FUNCTION is_device_trusted IS 'Check if a device fingerprint is trusted';
COMMENT ON FUNCTION check_concurrent_session_limit IS 'Check if user has exceeded concurrent session limit';
COMMENT ON FUNCTION check_device_session_limit IS 'Check if user has exceeded device session limit';
COMMENT ON FUNCTION get_device_fingerprint IS 'Get device fingerprint ID from hash';
COMMENT ON FUNCTION log_security_event IS 'Log security event for monitoring';
COMMENT ON FUNCTION cleanup_expired_sessions IS 'Clean up expired sessions';
COMMENT ON FUNCTION cleanup_inactive_devices IS 'Clean up inactive device fingerprints';
