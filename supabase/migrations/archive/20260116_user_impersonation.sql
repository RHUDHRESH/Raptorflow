-- User Impersonation Database Schema
-- Migration: 20260116_user_impersonation.sql
-- Implements secure impersonation, audit logging, and access controls

-- Create impersonation_sessions table
CREATE TABLE IF NOT EXISTS public.impersonation_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  target_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  impersonation_token TEXT NOT NULL UNIQUE,
  original_session_token TEXT NOT NULL,
  ip_address INET NOT NULL,
  user_agent TEXT,
  reason TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_accessed TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  access_count INTEGER NOT NULL DEFAULT 1,
  is_active BOOLEAN NOT NULL DEFAULT true
);

-- Create impersonation_logs table
CREATE TABLE IF NOT EXISTS public.impersonation_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  impersonation_session_id UUID NOT NULL REFERENCES public.impersonation_sessions(id) ON DELETE CASCADE,
  admin_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  target_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  action TEXT NOT NULL CHECK (action IN ('start', 'access', 'end')),
  resource_accessed TEXT,
  ip_address INET,
  user_agent TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create impersonation_permissions table
CREATE TABLE IF NOT EXISTS public.impersonation_permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  can_impersonate BOOLEAN NOT NULL DEFAULT false,
  max_duration_hours INTEGER NOT NULL DEFAULT 2,
  allowed_user_ids TEXT[] DEFAULT ARRAY[]::TEXT[],
  allowed_roles TEXT[] DEFAULT ARRAY[]::TEXT[],
  requires_approval BOOLEAN NOT NULL DEFAULT false,
  audit_level TEXT NOT NULL DEFAULT 'detailed' CHECK (audit_level IN ('basic', 'detailed', 'comprehensive')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE(admin_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_impersonation_sessions_admin_id ON public.impersonation_sessions(admin_id);
CREATE INDEX IF NOT EXISTS idx_impersonation_sessions_target_user_id ON public.impersonation_sessions(target_user_id);
CREATE INDEX IF NOT EXISTS idx_impersonation_sessions_token ON public.impersonation_sessions(impersonation_token);
CREATE INDEX IF NOT EXISTS idx_impersonation_sessions_active ON public.impersonation_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_impersonation_sessions_expires_at ON public.impersonation_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_impersonation_sessions_created_at ON public.impersonation_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_impersonation_sessions_last_accessed ON public.impersonation_sessions(last_accessed);

CREATE INDEX IF NOT EXISTS idx_impersonation_logs_session_id ON public.impersonation_logs(impersonation_session_id);
CREATE INDEX IF NOT EXISTS idx_impersonation_logs_admin_id ON public.impersonation_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_impersonation_logs_target_user_id ON public.impersonation_logs(target_user_id);
CREATE INDEX IF NOT EXISTS idx_impersonation_logs_action ON public.impersonation_logs(action);
CREATE INDEX IF NOT EXISTS idx_impersonation_logs_created_at ON public.impersonation_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_impersonation_permissions_admin_id ON public.impersonation_permissions(admin_id);
CREATE INDEX IF NOT EXISTS idx_impersonation_permissions_can_impersonate ON public.impersonation_permissions(can_impersonate);

-- Enable RLS on all tables
ALTER TABLE public.impersonation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.impersonation_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.impersonation_permissions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for impersonation_sessions
CREATE POLICY "impersonation_sessions_select_admin" ON public.impersonation_sessions
  FOR SELECT
  USING (admin_id = auth.uid());

CREATE POLICY "impersonation_sessions_insert_admin" ON public.impersonation_sessions
  FOR INSERT
  WITH CHECK (admin_id = auth.uid());

CREATE POLICY "impersonation_sessions_update_admin" ON public.impersonation_sessions
  FOR UPDATE
  USING (admin_id = auth.uid());

CREATE POLICY "impersonation_sessions_delete_admin" ON public.impersonation_sessions
  FOR DELETE
  USING (admin_id = auth.uid());

-- RLS Policies for impersonation_logs
CREATE POLICY "impersonation_logs_select_admin" ON public.impersonation_logs
  FOR SELECT
  USING (admin_id = auth.uid());

CREATE POLICY "impersonation_logs_insert_authenticated" ON public.impersonation_logs
  FOR INSERT
  WITH CHECK (admin_id = auth.uid());

-- RLS Policies for impersonation_permissions
CREATE POLICY "impersonation_permissions_select_own" ON public.impersonation_permissions
  FOR SELECT
  USING (admin_id = auth.uid());

CREATE POLICY "impersonation_permissions_insert_admin" ON public.impersonation_permissions
  FOR INSERT
  WITH CHECK (admin_id = auth.uid());

CREATE POLICY "impersonation_permissions_update_own" ON public.impersonation_permissions
  FOR UPDATE
  USING (admin_id = auth.uid());

-- Create triggers for updated_at timestamps
CREATE TRIGGER impersonation_sessions_updated_at
    BEFORE UPDATE ON public.impersonation_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER impersonation_permissions_updated_at
    BEFORE UPDATE ON public.impersonation_permissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for incrementing access count
CREATE OR REPLACE FUNCTION increment_impersonation_access_count()
RETURNS TRIGGER AS $$
BEGIN
    NEW.access_count = OLD.access_count + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER increment_impersonation_access_count
    BEFORE UPDATE ON public.impersonation_sessions
    FOR EACH ROW
    WHEN (NEW.last_accessed > OLD.last_accessed)
    EXECUTE FUNCTION increment_impersonation_access_count();

-- Create function to check impersonation permissions
CREATE OR REPLACE FUNCTION can_impersonate_user(
    admin_uuid UUID,
    target_uuid UUID
)
RETURNS BOOLEAN AS $$
DECLARE
    can_impersonate BOOLEAN DEFAULT FALSE;
    max_hours INTEGER DEFAULT 2;
BEGIN
    -- Check if admin has impersonation permissions
    SELECT p.can_impersonate, p.max_duration_hours INTO can_impersonate, max_hours
    FROM public.impersonation_permissions p
    WHERE p.admin_id = admin_uuid;
    
    -- If no explicit permissions, check if admin is owner
    IF NOT FOUND THEN
        SELECT 1 INTO can_impersonate
        FROM public.workspace_members wm
        WHERE wm.user_id = admin_uuid
        AND wm.role = 'owner'
        LIMIT 1;
        
        max_hours := 2; -- Default for owners
    END IF;
    
    -- Check if target user is in allowed list (if specified)
    IF can_impersonate THEN
        SELECT 1 INTO can_impersonate
        FROM public.impersonation_permissions p
        WHERE p.admin_id = admin_uuid
        AND (cardinality(p.allowed_user_ids) = 0 OR target_uuid = ANY(p.allowed_user_ids))
        LIMIT 1;
    END IF;
    
    RETURN can_impersonate;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to validate impersonation token
CREATE OR REPLACE FUNCTION is_impersonation_token_valid(
    token_param TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    is_valid BOOLEAN DEFAULT FALSE;
BEGIN
    SELECT 1 INTO is_valid
    FROM public.impersonation_sessions
    WHERE impersonation_token = token_param
      AND is_active = true
      AND expires_at > NOW()
      AND last_accessed > NOW() - INTERVAL '1 hour'
      LIMIT 1;
    
    RETURN is_valid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get impersonation session details
CREATE OR REPLACE FUNCTION get_impersonation_session(
    token_param TEXT
)
RETURNS TABLE (
    session_id UUID,
    admin_id UUID,
    target_user_id UUID,
    original_session_token TEXT,
    ip_address INET,
    user_agent TEXT,
    reason TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ,
    last_accessed TIMESTAMPTZ,
    access_count INTEGER,
    is_active BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.admin_id,
        s.target_user_id,
        s.original_session_token,
        s.ip_address,
        s.user_agent,
        s.reason,
        s.expires_at,
        s.created_at,
        s.last_accessed,
        s.access_count,
        s.is_active
    FROM public.impersonation_sessions s
    WHERE s.impersonation_token = token_param
      AND s.is_active = true
      AND s.expires_at > NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to log impersonation action
CREATE OR REPLACE FUNCTION log_impersonation_action(
    session_id_param UUID,
    admin_uuid UUID,
    target_uuid UUID,
    action_param TEXT,
    ip_param INET DEFAULT NULL,
    user_agent_param TEXT DEFAULT NULL,
    metadata_param JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    log_id UUID;
BEGIN
    INSERT INTO public.impersonation_logs (
        impersonation_session_id,
        admin_id,
        target_user_id,
        action,
        ip_address,
        user_agent,
        metadata,
        created_at
    ) VALUES (
        session_id_param,
        admin_uuid,
        target_uuid,
        action_param,
        ip_param,
        user_agent_param,
        metadata_param,
        NOW()
    )
    RETURNING id INTO log_id;
    
    RETURN log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to end impersonation session
CREATE OR REPLACE FUNCTION end_impersonation_session(
    session_id_param UUID,
    reason_param TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    success BOOLEAN DEFAULT FALSE;
BEGIN
    UPDATE public.impersonation_sessions
    SET is_active = false,
        last_accessed = NOW()
    WHERE id = session_id_param
      AND is_active = true;
    
    GET DIAGNOSTICS (ROW_COUNT, success);
    
    -- Log the end action
    IF success THEN
        PERFORM log_impersonation_action(
            session_id_param,
            (SELECT admin_id FROM public.impersonation_sessions WHERE id = session_id_param),
            (SELECT target_user_id FROM public.impersonation_sessions WHERE id = session_id_param),
            'end',
            (SELECT ip_address FROM public.impersonation_sessions WHERE id = session_id_param),
            (SELECT user_agent FROM public.impersonation_sessions WHERE id = session_id_param),
            jsonb_build_object('reason', reason_param)
        );
    END IF;
    
    RETURN success;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check if user is being impersonated
CREATE OR REPLACE FUNCTION is_user_being_impersonated(
    user_uuid UUID
)
RETURNS BOOLEAN AS $$
DECLARE
    is_impersonated BOOLEAN DEFAULT FALSE;
BEGIN
    SELECT 1 INTO is_impersonated
    FROM public.impersonation_sessions
    WHERE target_user_id = user_uuid
      AND is_active = true
      AND expires_at > NOW()
      LIMIT 1;
    
    RETURN is_impersonated;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get current impersonation session for user
CREATE OR REPLACE FUNCTION get_current_impersonation(
    user_uuid UUID
)
RETURNS TABLE (
    session_id UUID,
    admin_id UUID,
    impersonation_token TEXT,
    reason TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.admin_id,
        s.impersonation_token,
        s.reason,
        s.expires_at,
        s.created_at
    FROM public.impersonation_sessions s
    WHERE s.target_user_id = user_uuid
      AND s.is_active = true
      AND s.expires_at > NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to clean up expired impersonation sessions
CREATE OR REPLACE FUNCTION cleanup_expired_impersonation_sessions()
RETURNS INTEGER AS $$
DECLARE
    cleaned_count INTEGER;
BEGIN
    UPDATE public.impersonation_sessions
    SET is_active = false,
        last_accessed = NOW()
    WHERE expires_at <= NOW()
      AND is_active = true;
    
    GET DIAGNOSTICS (ROW_COUNT, cleaned_count);
    RETURN cleaned_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT ON public.impersonation_sessions TO authenticated;
GRANT SELECT ON public.impersonation_logs TO authenticated;
GRANT SELECT ON public.impersonation_permissions TO authenticated;

GRANT EXECUTE ON FUNCTION can_impersonate_user TO authenticated;
GRANT EXECUTE ON FUNCTION is_impersonation_token_valid TO authenticated;
GRANT EXECUTE ON FUNCTION get_impersonation_session TO authenticated;
GRANT EXECUTE ON FUNCTION log_impersonation_action TO authenticated;
GRANT EXECUTE ON FUNCTION end_impersonation_session TO authenticated;
GRANT EXECUTE ON FUNCTION is_user_being_impersonated TO authenticated;
GRANT EXECUTE ON FUNCTION get_current_impersonation TO authenticated;
GRANT EXECUTE ON FUNCTION cleanup_expired_impersonation_sessions TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE public.impersonation_sessions IS 'Active impersonation sessions with audit trail';
COMMENT ON TABLE public.impersonation_logs IS 'Detailed audit log for all impersonation actions';
COMMENT ON TABLE public.impersonation_permissions IS 'Admin permissions and constraints for impersonation';

COMMENT ON FUNCTION can_impersonate_user IS 'Check if admin can impersonate target user';
COMMENT ON FUNCTION is_impersonation_token_valid IS 'Validate impersonation token and session';
COMMENT ON FUNCTION get_impersonation_session IS 'Get impersonation session details from token';
COMMENT ON FUNCTION log_impersonation_action IS 'Log impersonation action for audit trail';
COMMENT ON FUNCTION end_impersonation_session IS 'End impersonation session and log action';
COMMENT ON FUNCTION is_user_being_impersonated IS 'Check if user is currently being impersonated';
COMMENT ON FUNCTION get_current_impersonation IS 'Get current impersonation session for user';
COMMENT ON FUNCTION cleanup_expired_impersonation_sessions IS 'Clean up expired impersonation sessions';

-- Create function to increment access count
CREATE OR REPLACE FUNCTION increment_impersonation_access_count(
    session_id UUID
)
RETURNS VOID AS $$
BEGIN
    UPDATE public.impersonation_sessions
    SET access_count = access_count + 1,
        last_accessed = NOW()
    WHERE id = session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permission for increment function
GRANT EXECUTE ON FUNCTION increment_impersonation_access_count TO authenticated;

-- Add comments for documentation
COMMENT ON FUNCTION increment_impersonation_access_count IS 'Increment access count for impersonation session';
