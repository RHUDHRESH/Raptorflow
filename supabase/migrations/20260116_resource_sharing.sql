-- Resource Sharing Database Schema
-- Migration: 20260116_resource_sharing.sql
-- Implements cross-workspace sharing, permission grants, and access logs

-- Create shared_resources table
CREATE TABLE IF NOT EXISTS public.shared_resources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_type TEXT NOT NULL,
  resource_id TEXT NOT NULL,
  resource_name TEXT NOT NULL,
  resource_data JSONB,
  owner_workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  owner_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  sharing_level TEXT NOT NULL DEFAULT 'private' CHECK (sharing_level IN ('private', 'workspace', 'public', 'custom')),
  sharing_settings JSONB NOT NULL DEFAULT '{
    "allow_copy": false,
    "allow_edit": false,
    "allow_download": false
  }'::JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE(resource_type, resource_id)
);

-- Create resource_shares table
CREATE TABLE IF NOT EXISTS public.resource_shares (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_id TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  from_workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  to_workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  shared_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  permissions TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  access_level TEXT NOT NULL DEFAULT 'view' CHECK (access_level IN ('view', 'edit', 'admin')),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'revoked', 'expired')),
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  UNIQUE(from_workspace_id, to_workspace_id, resource_type, resource_id)
);

-- Create share_links table
CREATE TABLE IF NOT EXISTS public.share_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_id TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  token TEXT NOT NULL UNIQUE,
  permissions TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  access_level TEXT NOT NULL DEFAULT 'view' CHECK (access_level IN ('view', 'edit')),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'revoked', 'expired')),
  expires_at TIMESTAMPTZ,
  access_count INTEGER NOT NULL DEFAULT 0,
  max_access INTEGER,
  password_protected BOOLEAN NOT NULL DEFAULT false,
  access_code TEXT,
  created_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create resource_access_logs table
CREATE TABLE IF NOT EXISTS public.resource_access_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  resource_id TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  workspace_id UUID REFERENCES public.workspaces(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  action TEXT NOT NULL CHECK (action IN ('view', 'edit', 'download', 'copy', 'share', 'revoke')),
  ip_address INET,
  user_agent TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_shared_resources_owner_workspace ON public.shared_resources(owner_workspace_id);
CREATE INDEX IF NOT EXISTS idx_shared_resources_owner_user ON public.shared_resources(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_shared_resources_type_id ON public.shared_resources(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_shared_resources_sharing_level ON public.shared_resources(sharing_level);

CREATE INDEX IF NOT EXISTS idx_resource_shares_from_workspace ON public.resource_shares(from_workspace_id);
CREATE INDEX IF NOT EXISTS idx_resource_shares_to_workspace ON public.resource_shares(to_workspace_id);
CREATE INDEX IF NOT EXISTS idx_resource_shares_resource ON public.resource_shares(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_resource_shares_shared_by ON public.resource_shares(shared_by);
CREATE INDEX IF NOT EXISTS idx_resource_shares_status ON public.resource_shares(status);
CREATE INDEX IF NOT EXISTS idx_resource_shares_expires_at ON public.resource_shares(expires_at);

CREATE INDEX IF NOT EXISTS idx_share_links_workspace ON public.share_links(workspace_id);
CREATE INDEX IF NOT EXISTS idx_share_links_token ON public.share_links(token);
CREATE INDEX IF NOT EXISTS idx_share_links_resource ON public.share_links(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_share_links_status ON public.share_links(status);
CREATE INDEX IF NOT EXISTS idx_share_links_expires_at ON public.share_links(expires_at);
CREATE INDEX IF NOT EXISTS idx_share_links_created_by ON public.share_links(created_by);

CREATE INDEX IF NOT EXISTS idx_resource_access_logs_workspace ON public.resource_access_logs(workspace_id);
CREATE INDEX IF NOT EXISTS idx_resource_access_logs_user ON public.resource_access_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_resource_access_logs_resource ON public.resource_access_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_resource_access_logs_action ON public.resource_access_logs(action);
CREATE INDEX IF NOT EXISTS idx_resource_access_logs_created_at ON public.resource_access_logs(created_at);

-- Enable RLS on all tables
ALTER TABLE public.shared_resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resource_shares ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.share_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resource_access_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for shared_resources
CREATE POLICY "shared_resources_select_own" ON public.shared_resources
  FOR SELECT
  USING (
    owner_workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "shared_resources_insert_authenticated" ON public.shared_resources
  FOR INSERT
  WITH CHECK (
    owner_workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
    AND owner_user_id = auth.uid()
  );

CREATE POLICY "shared_resources_update_own" ON public.shared_resources
  FOR UPDATE
  USING (
    owner_workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "shared_resources_delete_own" ON public.shared_resources
  FOR DELETE
  USING (
    owner_workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role = 'owner'
    )
  );

-- RLS Policies for resource_shares
CREATE POLICY "resource_shares_select_own" ON public.resource_shares
  FOR SELECT
  USING (
    from_workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
    OR to_workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "resource_shares_insert_authenticated" ON public.resource_shares
  FOR INSERT
  WITH CHECK (
    from_workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
    AND shared_by = auth.uid()
  );

CREATE POLICY "resource_shares_update_own" ON public.resource_shares
  FOR UPDATE
  USING (
    from_workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "resource_shares_delete_own" ON public.resource_shares
  FOR DELETE
  USING (
    from_workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

-- RLS Policies for share_links
CREATE POLICY "share_links_select_own" ON public.share_links
  FOR SELECT
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "share_links_insert_authenticated" ON public.share_links
  FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
    AND created_by = auth.uid()
  );

CREATE POLICY "share_links_update_own" ON public.share_links
  FOR UPDATE
  USING (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );

CREATE POLICY "share_links_delete_own" ON public.share_links
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
    OR user_id = auth.uid()
  );

CREATE POLICY "resource_access_logs_insert_authenticated" ON public.resource_access_logs
  FOR INSERT
  WITH CHECK (
    (workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid()
    ) OR workspace_id IS NULL)
    AND (user_id = auth.uid() OR user_id IS NULL)
  );

-- Create triggers for updated_at timestamps
CREATE TRIGGER shared_resources_updated_at
    BEFORE UPDATE ON public.shared_resources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER resource_shares_updated_at
    BEFORE UPDATE ON public.resource_shares
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER share_links_updated_at
    BEFORE UPDATE ON public.share_links
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to check resource sharing permissions
CREATE OR REPLACE FUNCTION can_share_resource(workspace_uuid UUID, user_uuid UUID, resource_type TEXT, resource_id TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if user owns the resource
    IF EXISTS (
        SELECT 1 FROM public.shared_resources
        WHERE resource_type = resource_type
        AND resource_id = resource_id
        AND owner_workspace_id = workspace_uuid
        AND owner_user_id = user_uuid
    ) THEN
        RETURN TRUE;
    END IF;
    
    -- Check if user has sharing permission in workspace
    RETURN EXISTS (
        SELECT 1 FROM public.workspace_members
        WHERE workspace_id = workspace_uuid
        AND user_id = user_uuid
        AND permissions @> ARRAY['resources.share']
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to check resource access via sharing
CREATE OR REPLACE FUNCTION can_access_shared_resource(workspace_uuid UUID, user_uuid UUID, resource_type TEXT, resource_id TEXT, permission TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if user owns the resource
    IF EXISTS (
        SELECT 1 FROM public.shared_resources
        WHERE resource_type = resource_type
        AND resource_id = resource_id
        AND owner_workspace_id = workspace_uuid
        AND owner_user_id = user_uuid
    ) THEN
        RETURN TRUE;
    END IF;
    
    -- Check if resource is shared with user's workspace
    IF EXISTS (
        SELECT 1 FROM public.resource_shares
        WHERE resource_type = resource_type
        AND resource_id = resource_id
        AND to_workspace_id = workspace_uuid
        AND status = 'active'
        AND (expires_at IS NULL OR expires_at > NOW())
        AND permissions @> ARRAY[permission]
    ) THEN
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to log resource access
CREATE OR REPLACE FUNCTION log_resource_access(
    resource_id_param TEXT,
    resource_type_param TEXT,
    workspace_uuid UUID,
    user_uuid UUID,
    action_param TEXT,
    ip_param INET DEFAULT NULL,
    user_agent_param TEXT DEFAULT NULL,
    metadata_param JSONB DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO public.resource_access_logs (
        resource_id,
        resource_type,
        workspace_id,
        user_id,
        action,
        ip_address,
        user_agent,
        metadata
    ) VALUES (
        resource_id_param,
        resource_type_param,
        workspace_uuid,
        user_uuid,
        action_param,
        ip_param,
        user_agent_param,
        metadata_param
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions
GRANT SELECT ON public.shared_resources TO authenticated;
GRANT SELECT ON public.resource_shares TO authenticated;
GRANT SELECT ON public.share_links TO authenticated;
GRANT SELECT ON public.resource_access_logs TO authenticated;

GRANT EXECUTE ON FUNCTION can_share_resource TO authenticated;
GRANT EXECUTE ON FUNCTION can_access_shared_resource TO authenticated;
GRANT EXECUTE ON FUNCTION log_resource_access TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE public.shared_resources IS 'Resources that can be shared across workspaces';
COMMENT ON TABLE public.resource_shares IS 'Sharing relationships between workspaces for specific resources';
COMMENT ON TABLE public.share_links IS 'Public share links for resources with access control';
COMMENT ON TABLE public.resource_access_logs IS 'Audit log for all resource access and sharing actions';

COMMENT ON FUNCTION can_share_resource IS 'Check if user can share a specific resource';
COMMENT ON FUNCTION can_access_shared_resource IS 'Check if user can access a shared resource';
COMMENT ON FUNCTION log_resource_access IS 'Log resource access for auditing';
