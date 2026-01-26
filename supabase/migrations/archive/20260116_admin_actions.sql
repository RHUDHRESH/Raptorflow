-- Admin Actions Database Schema
-- Migration: 20260116_admin_actions.sql
-- Implements user suspension, manual interventions, and bulk operations

-- Create admin_actions table
CREATE TABLE IF NOT EXISTS public.admin_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  action_type TEXT NOT NULL CHECK (action_type IN (
    'suspend_user', 'activate_user', 'reset_password', 'force_mfa_reset',
    'impersonate_user', 'bulk_suspend', 'bulk_activate', 'bulk_reset_password'
  )),
  target_user_ids TEXT[] DEFAULT ARRAY[]::TEXT[],
  target_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  reason TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::JSONB,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Create bulk_operations table
CREATE TABLE IF NOT EXISTS public.bulk_operations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  operation_type TEXT NOT NULL CHECK (operation_type IN (
    'suspend_users', 'activate_users', 'reset_passwords', 'force_mfa_reset'
  )),
  target_user_ids TEXT[] NOT NULL,
  reason TEXT NOT NULL,
  total_count INTEGER NOT NULL,
  completed_count INTEGER NOT NULL DEFAULT 0,
  failed_count INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
  results JSONB DEFAULT '[]'::JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Create user_suspensions table
CREATE TABLE IF NOT EXISTS public.user_suspensions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  suspended_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  reason TEXT NOT NULL,
  suspension_type TEXT NOT NULL CHECK (suspension_type IN ('temporary', 'permanent', 'security')),
  expires_at TIMESTAMPTZ,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  ended_by UUID REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Create manual_interventions table
CREATE TABLE IF NOT EXISTS public.manual_interventions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  intervention_type TEXT NOT NULL CHECK (intervention_type IN (
    'password_reset', 'mfa_reset', 'account_recovery', 'data_access', 'security_breach'
  )),
  target_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  reason TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::JSONB,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
  result JSONB,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Add is_suspended column to profiles table (if not exists)
DO $$
BEGIN
  ALTER TABLE public.profiles
  ADD COLUMN IF NOT EXISTS is_suspended BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS suspended_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS suspended_by UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  ADD COLUMN IF NOT EXISTS suspension_reason TEXT;
END $$;

-- Add password_reset columns to profiles table (if not exists)
DO $$
BEGIN
  ALTER TABLE public.profiles
  ADD COLUMN IF NOT EXISTS password_hash TEXT,
  ADD COLUMN IF NOT EXISTS password_reset_required BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS password_reset_by UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  ADD COLUMN IF NOT EXISTS password_reset_reason TEXT,
  ADD COLUMN IF NOT EXISTS password_reset_at TIMESTAMPTZ;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_admin_actions_admin_id ON public.admin_actions(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_action_type ON public.admin_actions(action_type);
CREATE INDEX IF NOT EXISTS idx_admin_actions_status ON public.admin_actions(status);
CREATE INDEX IF NOT EXISTS idx_admin_actions_created_at ON public.admin_actions(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_actions_target_user_id ON public.admin_actions(target_user_id);

CREATE INDEX IF NOT EXISTS idx_bulk_operations_admin_id ON public.bulk_operations(admin_id);
CREATE INDEX IF NOT EXISTS idx_bulk_operations_operation_type ON public.bulk_operations(operation_type);
CREATE INDEX IF NOT EXISTS idx_bulk_operations_status ON public.bulk_operations(status);
CREATE INDEX IF NOT EXISTS idx_bulk_operations_created_at ON public.bulk_operations(created_at);
CREATE INDEX IF NOT EXISTS idx_bulk_operations_target_user_ids ON public.bulk_operations(target_user_ids);

CREATE INDEX IF NOT EXISTS idx_user_suspensions_user_id ON public.user_suspensions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_suspensions_suspended_by ON public.user_suspensions(suspended_by);
CREATE INDEX IF NOT EXISTS idx_user_suspensions_is_active ON public.user_suspensions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_suspensions_created_at ON public.user_suspensions(created_at);

CREATE INDEX IF NOT EXISTS idx_manual_interventions_admin_id ON public.manual_interventions(admin_id);
CREATE INDEX IF NOT EXISTS idx_manual_interventions_intervention_type ON public.manual_interventions(intervention_type);
CREATE INDEX IF NOT EXISTS idx_manual_interventions_target_user_id ON public.manual_interventions(target_user_id);
CREATE INDEX IF NOT EXISTS idx_manual_interventions_status ON public.manual_interventions(status);
CREATE INDEX IF NOT EXISTS idx_manual_interventions_created_at ON public.manual_interventions(created_at);

CREATE INDEX IF NOT EXISTS idx_profiles_is_suspended ON public.profiles(is_suspended);
CREATE INDEX IF NOT EXISTS idx_profiles_suspended_at ON public.profiles(suspended_at);
CREATE INDEX IF NOT EXISTS idx_profiles_suspended_by ON public.profiles(suspended_by);

-- Enable RLS on all tables
ALTER TABLE public.admin_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bulk_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_suspensions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.manual_interventions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for admin_actions
CREATE POLICY "admin_actions_select_admin" ON public.admin_actions
  FOR SELECT
  USING (admin_id = auth.uid());

CREATE POLICY "admin_actions_insert_admin" ON public.admin_actions
  FOR INSERT
  WITH CHECK (admin_id = auth.uid());

CREATE POLICY "admin_actions_update_admin" ON public.admin_actions
  FOR UPDATE
  USING (admin_id = auth.uid());

CREATE POLICY "admin_actions_delete_admin" ON public.admin_actions
  FOR DELETE
  USING (admin_id = auth.uid());

-- RLS Policies for bulk_operations
CREATE POLICY "bulk_operations_select_admin" ON public.bulk_operations
  FOR SELECT
  USING (admin_id = auth.uid());

CREATE POLICY "bulk_operations_insert_admin" ON public.bulk_operations
  FOR INSERT
  WITH CHECK (admin_id = auth.uid());

CREATE POLICY "bulk_operations_update_admin" ON public.bulk_operations
  FOR UPDATE
  USING (admin_id = auth.uid());

CREATE POLICY "bulk_operations_delete_admin" ON public.bulk_operations
  FOR DELETE
  USING (admin_id = auth.uid());

-- RLS Policies for user_suspensions
CREATE POLICY "user_suspensions_select_admin" ON public.user_suspensions
  FOR SELECT
  USING (suspended_by = auth.uid() OR target_user_id = auth.uid());

CREATE POLICY "user_suspensions_insert_admin" ON public.user_suspensions
  FOR INSERT
  WITH CHECK (suspended_by = auth.uid());

CREATE POLICY "user_suspensions_update_admin" ON public.user_suspensions
  FOR UPDATE
  USING (suspended_by = auth.uid() OR target_user_id = auth.uid());

CREATE POLICY "user_suspensions_delete_admin" ON public.user_suspensions
  FOR DELETE
  USING (suspended_by = auth.uid() OR target_user_id = auth.uid());

-- RLS Policies for manual_interventions
CREATE POLICY "manual_interventions_select_admin" ON public.manual_interventions
  FOR SELECT
  USING (admin_id = auth.uid());

CREATE POLICY "manual_interventions_insert_admin" ON public.manual_interventions
  FOR INSERT
  WITH CHECK (admin_id = auth.uid());

CREATE POLICY "manual_interventions_update_admin" ON public.manual_interventions
  FOR UPDATE
  USING (admin_id = auth.uid());

CREATE POLICY "manual_interventions_delete_admin" ON public.manual_interventions
  FOR DELETE
  USING (admin_id = auth.uid());

-- RLS Policies for profiles (for suspension-related columns)
CREATE POLICY "profiles_update_admin" ON public.profiles
  FOR UPDATE
  USING (auth.uid() OR id = auth.uid());

-- Create triggers for updated_at timestamps
CREATE TRIGGER admin_actions_updated_at
    BEFORE UPDATE ON public.admin_actions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER bulk_operations_updated_at
    BEFORE UPDATE ON public.bulk_operations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER user_suspensions_updated_at
    BEFORE UPDATE ON public.user_suspensions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER manual_interventions_updated_at
    BEFORE UPDATE ON public.manual_interventions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to check if user is suspended
CREATE OR REPLACE FUNCTION is_user_suspended(user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.user_suspensions
        WHERE user_id = user_uuid
        AND is_active = true
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check if admin can perform action
CREATE OR REPLACE FUNCTION can_perform_admin_action(
    admin_uuid UUID,
    action_type_param TEXT,
    target_user_uuid UUID DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    is_admin BOOLEAN DEFAULT FALSE;
BEGIN
    -- Check if admin is owner or admin
    SELECT 1 INTO is_admin
    FROM public.workspace_members wm
    WHERE wm.user_id = admin_uuid
    AND wm.role IN ('owner', 'admin')
    LIMIT 1;

    -- Additional checks for specific actions
    IF action_type_param = 'impersonate_user' AND target_user_uuid IS NOT NULL THEN
        -- Check if target user is not an admin
        SELECT 1 INTO is_admin
        FROM public.workspace_members wm
        WHERE wm.user_id = target_user_uuid
        AND wm.role IN ('owner', 'admin')
        LIMIT 1;

        RETURN is_admin AND NOT EXISTS (
            SELECT 1 FROM public.workspace_members wm
            WHERE wm.user_id = target_user_uuid
            AND wm.role IN ('owner', 'admin')
        );
    END IF;

    RETURN is_admin;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to log admin action
CREATE OR REPLACE FUNCTION log_admin_action(
    admin_uuid UUID,
    action_type_param TEXT,
    target_user_ids TEXT[],
    reason_param TEXT,
    metadata_param JSONB DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    action_id UUID;
BEGIN
    INSERT INTO public.admin_actions (
        admin_id: admin_uuid,
        action_type: action_type_param,
        target_user_ids: target_user_ids,
        target_user_id: target_user_uuid,
        reason: reason_param,
        metadata: metadata_param,
        status: 'completed',
        created_at: NOW(),
        updated_at: NOW(),
        completed_at: NOW()
    )
    RETURNING id INTO action_id;

    RETURN action_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get user suspension details
CREATE OR REPLACE FUNCTION get_user_suspension(
    user_uuid UUID
)
RETURNS TABLE (
    id UUID,
    user_id UUID,
    suspended_by UUID,
    reason TEXT,
    suspension_type TEXT,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    ended_by UUID
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.user_id,
        s.suspended_by,
        s.reason,
        s.suspension_type,
        s.expires_at,
        s.is_active,
        s.created_at,
        s.updated_at,
        s.ended_at,
        s.ended_by
    FROM public.user_suspensions s
    WHERE s.user_id = user_uuid
      AND s.is_active = true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to end user suspension
CREATE OR REPLACE FUNCTION end_user_suspension(
    suspension_id UUID,
    reason_param TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    success BOOLEAN DEFAULT FALSE;
BEGIN
    UPDATE public.user_suspensions
    SET is_active = false,
        ended_at = NOW(),
        ended_by = auth.uid(),
        updated_at = NOW()
    WHERE id = suspension_id
      AND is_active = true;

    GET DIAGNOSTICS (ROW_COUNT, success);
    RETURN success;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check bulk operation status
CREATE OR REPLACE FUNCTION get_bulk_operation_status(
    operation_id UUID
)
RETURNS TABLE (
    id UUID,
    admin_id UUID,
    operation_type TEXT,
    target_user_ids TEXT[],
    reason TEXT,
    total_count INTEGER,
    completed_count INTEGER,
    failed_count INTEGER,
    status TEXT,
    results JSONB,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        bo.id,
        bo.admin_id,
        bo.operation_type,
        bo.target_user_ids,
        bo.reason,
        bo.total_count,
        bo.completed_count,
        bo.failed_count,
        bo.status,
        bo.results,
        bo.created_at,
        bo.updated_at,
        bo.completed_at
    FROM public.bulk_operations bo
    WHERE bo.id = operation_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT ON public.admin_actions TO authenticated;
GRANT SELECT ON public.bulk_operations TO authenticated;
GRANT SELECT ON public.user_suspensions TO authenticated;
GRANT SELECT ON public.manual_interventions TO authenticated;
GRANT SELECT ON public.profiles TO authenticated;

GRANT EXECUTE ON FUNCTION is_user_suspended TO authenticated;
GRANT EXECUTE ON FUNCTION can_perform_admin_action TO authenticated;
GRANT EXECUTE FUNCTION log_admin_action TO authenticated;
GRANT EXECUTE FUNCTION get_user_suspension TO authenticated;
GRANT EXECUTE FUNCTION end_user_suspension TO authenticated;
GRANT EXECUTE FUNCTION get_bulk_operation_status TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE public.admin_actions IS 'Audit log of all admin actions performed';
COMMENT ON TABLE public.bulk_operations IS 'Bulk operations with detailed results and progress tracking';
COMMENT ON TABLE public.user_suspensions IS 'User suspension records with audit trail';
COMMENT ON TABLE public.manual_interventions IS 'Manual interventions requiring admin approval';

COMMENT ON FUNCTION is_user_suspended IS 'Check if user is currently suspended';
COMMENT ON FUNCTION can_perform_admin_action IS 'Check if admin can perform specific action';
COMMENT ON FUNCTION log_admin_action IS 'Log admin action for audit trail';
COMMENT ON FUNCTION get_user_suspension IS 'Get current suspension details for user';
COMMENT ON FUNCTION end_user_suspension IS 'End user suspension and log action';
COMMENT ON FUNCTION get_bulk_operation_status IS 'Get bulk operation status and results';

-- Create function to increment access count
CREATE OR REPLACE FUNCTION increment_access_count(
    table_name TEXT,
    record_id UUID
)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('UPDATE %I SET access_count = access_count + 1 WHERE id = $1', table_name, record_id);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permission for increment function
GRANT EXECUTE ON FUNCTION increment_access_count TO authenticated;

-- Add comments for documentation
COMMENT ON FUNCTION increment_access_count IS 'Increment access count for tracking';

-- Create function to get admin action statistics
CREATE OR REPLACE FUNCTION get_admin_action_stats(
    admin_uuid UUID DEFAULT NULL,
    days_param INTEGER DEFAULT 30
)
RETURNS TABLE (
    total_actions BIGINT,
    bulk_operations BIGINT,
    user_suspensions BIGINT,
    manual_interventions BIGINT,
    success_rate NUMERIC
    recent_activity BIGINT
) AS $$
DECLARE
    since TIMESTAMP;
BEGIN
    since := NOW() - (days_param || 30) * INTERVAL '1 day';

    RETURN QUERY
    SELECT
        COUNT(*) FILTER (admin_id = admin_uuid OR admin_uuid IS NULL) AS total_actions,
        COUNT(*) FILTER (operation_type IN ('bulk_suspend', 'bulk_activate', 'bulk_reset_password', 'bulk_force_mfa_reset')) FILTER (admin_id = admin_uuid OR admin_uuid IS NULL) AS bulk_operations,
        COUNT(*) FILTER (is_active = true) FILTER (admin_id = admin_uuid OR admin_uuid IS NULL) AS user_suspensions,
        COUNT(*) FILTER (admin_id = admin_uuid OR admin_uuid IS NULL) AS manual_interventions,
        (COUNT(*) FILTER (status = 'completed') * 100.0 / NULLIF(COUNT(*) FILTER (admin_id = admin_uuid OR admin_uuid IS NULL), 0)) FILTER (admin_id = admin_uuid OR admin_uuid IS NULL) AS success_rate,
        COUNT(*) FILTER (created_at >= since) FILTER (admin_id = admin_uuid OR admin_uuid IS NULL) AS recent_activity
    FROM public.admin_actions
    WHERE (admin_id = admin_uuid OR admin_uuid IS NULL)
      OR (admin_id IS NULL AND admin_id IS NULL);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permission for stats function
GRANT EXECUTE ON FUNCTION get_admin_action_stats TO authenticated;

-- Add comments for documentation
COMMENT ON FUNCTION get_admin_action_stats IS 'Get statistics for admin actions';
