-- Two-Factor Authentication Database Schema
-- Migration: 20260116_two_factor_auth.sql
-- Implements TOTP support, backup codes, and recovery options

-- Create user_mfa table
CREATE TABLE IF NOT EXISTS public.user_mfa (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  totp_secret TEXT,
  totp_enabled BOOLEAN NOT NULL DEFAULT false,
  backup_codes TEXT[] DEFAULT ARRAY[]::TEXT[],
  backup_codes_used TEXT[] DEFAULT ARRAY[]::TEXT[],
  recovery_email TEXT NOT NULL,
  recovery_phone TEXT,
  last_used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE(user_id)
);

-- Create recovery_codes table
CREATE TABLE IF NOT EXISTS public.recovery_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  code TEXT NOT NULL,
  method TEXT NOT NULL CHECK (method IN ('email', 'sms')),
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create mfa_sessions table for tracking MFA verified sessions
CREATE TABLE IF NOT EXISTS public.mfa_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  session_token TEXT NOT NULL UNIQUE,
  verified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create mfa_attempts table for tracking failed attempts
CREATE TABLE IF NOT EXISTS public.mfa_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  ip_address INET,
  user_agent TEXT,
  method TEXT NOT NULL CHECK (method IN ('totp', 'backup_code', 'recovery')),
  success BOOLEAN NOT NULL DEFAULT false,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_mfa_user_id ON public.user_mfa(user_id);
CREATE INDEX IF NOT EXISTS idx_user_mfa_totp_enabled ON public.user_mfa(totp_enabled);
CREATE INDEX IF NOT EXISTS idx_user_mfa_recovery_email ON public.user_mfa(recovery_email);

CREATE INDEX IF NOT EXISTS idx_recovery_codes_user_id ON public.recovery_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_recovery_codes_code ON public.recovery_codes(code);
CREATE INDEX IF NOT EXISTS idx_recovery_codes_expires_at ON public.recovery_codes(expires_at);
CREATE INDEX IF NOT EXISTS idx_recovery_codes_method ON public.recovery_codes(method);

CREATE INDEX IF NOT EXISTS idx_mfa_sessions_user_id ON public.mfa_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_mfa_sessions_token ON public.mfa_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_mfa_sessions_expires_at ON public.mfa_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_mfa_attempts_user_id ON public.mfa_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_mfa_attempts_ip_address ON public.mfa_attempts(ip_address);
CREATE INDEX IF NOT EXISTS idx_mfa_attempts_created_at ON public.mfa_attempts(created_at);
CREATE INDEX IF NOT EXISTS idx_mfa_attempts_success ON public.mfa_attempts(success);

-- Enable RLS on all tables
ALTER TABLE public.user_mfa ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recovery_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mfa_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mfa_attempts ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_mfa
CREATE POLICY "user_mfa_select_own" ON public.user_mfa
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "user_mfa_insert_own" ON public.user_mfa
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "user_mfa_update_own" ON public.user_mfa
  FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "user_mfa_delete_own" ON public.user_mfa
  FOR DELETE
  USING (user_id = auth.uid());

-- RLS Policies for recovery_codes
CREATE POLICY "recovery_codes_select_own" ON public.recovery_codes
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "recovery_codes_insert_own" ON public.recovery_codes
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "recovery_codes_update_own" ON public.recovery_codes
  FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "recovery_codes_delete_own" ON public.recovery_codes
  FOR DELETE
  USING (user_id = auth.uid());

-- RLS Policies for mfa_sessions
CREATE POLICY "mfa_sessions_select_own" ON public.mfa_sessions
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "mfa_sessions_insert_own" ON public.mfa_sessions
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "mfa_sessions_update_own" ON public.mfa_sessions
  FOR UPDATE
  USING (user_id = auth.uid());

CREATE POLICY "mfa_sessions_delete_own" ON public.mfa_sessions
  FOR DELETE
  USING (user_id = auth.uid());

-- RLS Policies for mfa_attempts (allow inserts for logging)
CREATE POLICY "mfa_attempts_select_own" ON public.mfa_attempts
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "mfa_attempts_insert_authenticated" ON public.mfa_attempts
  FOR INSERT
  WITH CHECK (user_id = auth.uid() OR user_id IS NULL);

-- Create triggers for updated_at timestamps
CREATE TRIGGER user_mfa_updated_at
    BEFORE UPDATE ON public.user_mfa
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to check if user has MFA enabled
CREATE OR REPLACE FUNCTION has_mfa_enabled(user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.user_mfa
        WHERE user_id = user_uuid
        AND totp_enabled = true
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check if MFA session is valid
CREATE OR REPLACE FUNCTION is_mfa_session_valid(session_token TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.mfa_sessions
        WHERE session_token = session_token
        AND expires_at > NOW()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to log MFA attempt
CREATE OR REPLACE FUNCTION log_mfa_attempt(
    user_uuid UUID,
    ip_param INET DEFAULT NULL,
    user_agent_param TEXT DEFAULT NULL,
    method_param TEXT,
    success_param BOOLEAN DEFAULT false,
    error_message_param TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO public.mfa_attempts (
        user_id,
        ip_address,
        user_agent,
        method,
        success,
        error_message
    ) VALUES (
        user_uuid,
        ip_param,
        user_agent_param,
        method_param,
        success_param,
        error_message_param
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to create MFA session
CREATE OR REPLACE FUNCTION create_mfa_session(
    user_uuid UUID,
    session_token_param TEXT,
    ip_param INET DEFAULT NULL,
    user_agent_param TEXT DEFAULT NULL,
    expires_in_minutes INTEGER DEFAULT 30
)
RETURNS UUID AS $$
DECLARE
    session_id UUID;
BEGIN
    INSERT INTO public.mfa_sessions (
        user_id,
        session_token,
        expires_at,
        ip_address,
        user_agent
    ) VALUES (
        user_uuid,
        session_token_param,
        NOW() + (expires_in_minutes || 30) * INTERVAL '1 minute',
        ip_param,
        user_agent_param
    )
    RETURNING id INTO session_id;
    
    RETURN session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to clean up expired MFA sessions
CREATE OR REPLACE FUNCTION cleanup_expired_mfa_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.mfa_sessions
    WHERE expires_at <= NOW();
    
    GET DIAGNOSTICS (ROW_COUNT, deleted_count);
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to clean up expired recovery codes
CREATE OR REPLACE FUNCTION cleanup_expired_recovery_codes()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.recovery_codes
    WHERE expires_at <= NOW();
    
    GET DIAGNOSTICS (ROW_COUNT, deleted_count);
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check rate limiting for MFA attempts
CREATE OR REPLACE FUNCTION check_mfa_rate_limit(
    user_uuid UUID,
    ip_param INET,
    time_window_minutes INTEGER DEFAULT 5,
    max_attempts INTEGER DEFAULT 5
)
RETURNS BOOLEAN AS $$
DECLARE
    attempt_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO attempt_count
    FROM public.mfa_attempts
    WHERE (user_id = user_uuid OR user_id IS NULL)
      AND (ip_address = ip_param OR ip_address IS NULL)
      AND created_at > NOW() - (time_window_minutes || 5) * INTERVAL '1 minute'
      AND success = false;
    
    RETURN attempt_count < max_attempts;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT ON public.user_mfa TO authenticated;
GRANT SELECT ON public.recovery_codes TO authenticated;
GRANT SELECT ON public.mfa_sessions TO authenticated;
GRANT SELECT ON public.mfa_attempts TO authenticated;

GRANT EXECUTE ON FUNCTION has_mfa_enabled TO authenticated;
GRANT EXECUTE ON FUNCTION is_mfa_session_valid TO authenticated;
GRANT EXECUTE ON FUNCTION log_mfa_attempt TO authenticated;
GRANT EXECUTE ON FUNCTION create_mfa_session TO authenticated;
GRANT EXECUTE ON FUNCTION cleanup_expired_mfa_sessions TO authenticated;
GRANT EXECUTE ON FUNCTION cleanup_expired_recovery_codes TO authenticated;
GRANT EXECUTE ON FUNCTION check_mfa_rate_limit TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE public.user_mfa IS 'User MFA settings including TOTP secrets and backup codes';
COMMENT ON TABLE public.recovery_codes IS 'Temporary recovery codes for MFA reset';
COMMENT ON TABLE public.mfa_sessions IS 'Sessions that have passed MFA verification';
COMMENT ON TABLE public.mfa_attempts IS 'Log of MFA verification attempts for security monitoring';

COMMENT ON FUNCTION has_mfa_enabled IS 'Check if user has MFA enabled';
COMMENT ON FUNCTION is_mfa_session_valid IS 'Check if MFA session token is still valid';
COMMENT ON FUNCTION log_mfa_attempt IS 'Log MFA verification attempt for security monitoring';
COMMENT ON FUNCTION create_mfa_session IS 'Create a new MFA-verified session';
COMMENT ON FUNCTION cleanup_expired_mfa_sessions IS 'Clean up expired MFA sessions';
COMMENT ON FUNCTION cleanup_expired_recovery_codes IS 'Clean up expired recovery codes';
COMMENT ON FUNCTION check_mfa_rate_limit IS 'Check rate limiting for MFA attempts';
