-- Workspace Isolation Database Schema
-- Migration: 20260116_workspace_isolation.sql
-- Implements data segregation, permission boundaries, and resource allocation

-- Create workspace_members table if not exists
CREATE TABLE IF NOT EXISTS public.workspace_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
  permissions TEXT[] DEFAULT ARRAY[]::TEXT[],
  invited_by UUID REFERENCES auth.users(id),
  invited_at TIMESTAMPTZ DEFAULT NOW(),
  accepted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(user_id, workspace_id)
);

-- Create resource_permissions table
CREATE TABLE IF NOT EXISTS public.resource_permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  resource_type TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  permissions TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  granted_by UUID NOT NULL REFERENCES auth.users(id),
  granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(workspace_id, user_id, resource_type, resource_id)
);

-- Create resource_access_logs table
CREATE TABLE IF NOT EXISTS public.resource_access_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  resource_type TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  action TEXT NOT NULL,
  permissions TEXT[] DEFAULT ARRAY[]::TEXT[],
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create workspace_settings table
CREATE TABLE IF NOT EXISTS public.workspace_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  setting_key TEXT NOT NULL,
  setting_value JSONB NOT NULL,
  updated_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(workspace_id, setting_key)
);

-- Create workspace_invitations table
CREATE TABLE IF NOT EXISTS public.workspace_invitations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin', 'member', 'viewer')),
  permissions TEXT[] DEFAULT ARRAY[]::TEXT[],
  invited_by UUID NOT NULL REFERENCES auth.users(id),
  invitation_token TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'expired')),
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 days')),
  accepted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON public.workspace_members(user_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON public.workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_role ON public.workspace_members(role);
CREATE INDEX IF NOT EXISTS idx_workspace_members_invited_by ON public.workspace_members(invited_by);

CREATE INDEX IF NOT EXISTS idx_resource_permissions_workspace_id ON public.resource_permissions(workspace_id);
CREATE INDEX IF NOT EXISTS idx_resource_permissions_user_id ON public.resource_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_resource_permissions_resource ON public.resource_permissions(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_resource_permissions_granted_by ON public.resource_permissions(granted_by);

CREATE INDEX IF NOT EXISTS idx_resource_access_logs_workspace_id ON public.resource_access_logs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_resource_access_logs_user_id ON public.resource_access_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_resource_access_logs_resource ON public.resource_access_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_resource_access_logs_created_at ON public.resource_access_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_workspace_settings_workspace_id ON public.workspace_settings(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_settings_key ON public.workspace_settings(setting_key);

CREATE INDEX IF NOT EXISTS idx_workspace_invitations_workspace_id ON public.workspace_invitations(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_invitations_email ON public.workspace_invitations(email);
CREATE INDEX IF NOT EXISTS idx_workspace_invitations_token ON public.workspace_invitations(invitation_token);
CREATE INDEX IF NOT EXISTS idx_workspace_invitations_status ON public.workspace_invitations(status);

-- Enable RLS on all tables
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resource_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resource_access_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_invitations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for workspace_members
CREATE POLICY "workspace_members_select_own" ON public.workspace_members
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "workspace_members_insert_authenticated" ON public.workspace_members
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role = 'owner'
    )
  );

CREATE POLICY "workspace_members_update_own" ON public.workspace_members
  FOR UPDATE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role = 'owner'
    )
  );

CREATE POLICY "workspace_members_delete_own" ON public.workspace_members
  FOR DELETE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role = 'owner'
    )
  );

-- RLS Policies for resource_permissions
CREATE POLICY "resource_permissions_select_own" ON public.resource_permissions
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "resource_permissions_insert_authenticated" ON public.resource_permissions
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "resource_permissions_update_own" ON public.resource_permissions
  FOR UPDATE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "resource_permissions_delete_own" ON public.resource_permissions
  FOR DELETE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

-- RLS Policies for resource_access_logs
CREATE POLICY "resource_access_logs_select_own" ON public.resource_access_logs
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "resource_access_logs_insert_authenticated" ON public.resource_access_logs
  FOR INSERT
  WITH CHECK (
    user_id = auth.uid() AND
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

-- RLS Policies for workspace_settings
CREATE POLICY "workspace_settings_select_own" ON public.workspace_settings
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "workspace_settings_insert_authenticated" ON public.workspace_settings
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "workspace_settings_update_own" ON public.workspace_settings
  FOR UPDATE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "workspace_settings_delete_own" ON public.workspace_settings
  FOR DELETE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role = 'owner'
    )
  );

-- RLS Policies for workspace_invitations
CREATE POLICY "workspace_invitations_select_own" ON public.workspace_invitations
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "workspace_invitations_insert_authenticated" ON public.workspace_invitations
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "workspace_invitations_update_own" ON public.workspace_invitations
  FOR UPDATE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "workspace_invitations_delete_own" ON public.workspace_invitations
  FOR DELETE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role = 'owner'
    )
  );

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER workspace_members_updated_at
    BEFORE UPDATE ON public.workspace_members
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER resource_permissions_updated_at
    BEFORE UPDATE ON public.resource_permissions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER workspace_settings_updated_at
    BEFORE UPDATE ON public.workspace_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER workspace_invitations_updated_at
    BEFORE UPDATE ON public.workspace_invitations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to check workspace membership
CREATE OR REPLACE FUNCTION is_workspace_member(workspace_uuid UUID, user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.workspace_members
        WHERE workspace_id = workspace_uuid
        AND user_id = user_uuid
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get user role in workspace
CREATE OR REPLACE FUNCTION get_workspace_role(workspace_uuid UUID, user_uuid UUID)
RETURNS TEXT AS $$
BEGIN
    RETURN (
        SELECT role FROM public.workspace_members
        WHERE workspace_id = workspace_uuid
        AND user_id = user_uuid
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check workspace permission
CREATE OR REPLACE FUNCTION has_workspace_permission(workspace_uuid UUID, user_uuid UUID, permission TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Owners have all permissions
    IF EXISTS (
        SELECT 1 FROM public.workspace_members
        WHERE workspace_id = workspace_uuid
        AND user_id = user_uuid
        AND role = 'owner'
    ) THEN
        RETURN TRUE;
    END IF;

    -- Check explicit permissions
    RETURN EXISTS (
        SELECT 1 FROM public.workspace_members
        WHERE workspace_id = workspace_uuid
        AND user_id = user_uuid
        AND permissions @> ARRAY[permission]
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check resource permission
CREATE OR REPLACE FUNCTION has_resource_permission(workspace_uuid UUID, user_uuid UUID, resource_type TEXT, resource_id TEXT, permission TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- First check workspace-level permissions
    IF has_workspace_permission(workspace_uuid, user_uuid, 'resources.all') THEN
        RETURN TRUE;
    END IF;

    -- Check specific resource permissions
    RETURN EXISTS (
        SELECT 1 FROM public.resource_permissions
        WHERE workspace_id = workspace_uuid
        AND user_id = user_uuid
        AND resource_type = resource_type
        AND resource_id = resource_id
        AND permissions @> ARRAY[permission]
        AND (expires_at IS NULL OR expires_at > NOW())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT ON public.workspace_members TO authenticated;
GRANT SELECT ON public.resource_permissions TO authenticated;
GRANT SELECT ON public.resource_access_logs TO authenticated;
GRANT SELECT ON public.workspace_settings TO authenticated;
GRANT SELECT ON public.workspace_invitations TO authenticated;

GRANT EXECUTE ON FUNCTION is_workspace_member TO authenticated;
GRANT EXECUTE ON FUNCTION get_workspace_role TO authenticated;
GRANT EXECUTE ON FUNCTION has_workspace_permission TO authenticated;
GRANT EXECUTE ON FUNCTION has_resource_permission TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE public.workspace_members IS 'Members of workspaces with roles and permissions';
COMMENT ON TABLE public.resource_permissions IS 'Granular permissions for resources within workspaces';
COMMENT ON TABLE public.resource_access_logs IS 'Audit log for resource access';
COMMENT ON TABLE public.workspace_settings IS 'Workspace-specific settings and configuration';
COMMENT ON TABLE public.workspace_invitations IS 'Invitations to join workspaces';

COMMENT ON FUNCTION is_workspace_member IS 'Check if user is a member of a workspace';
COMMENT ON FUNCTION get_workspace_role IS 'Get user role in a workspace';
COMMENT ON FUNCTION has_workspace_permission IS 'Check if user has specific permission in workspace';
COMMENT ON FUNCTION has_resource_permission IS 'Check if user has permission for specific resource';
