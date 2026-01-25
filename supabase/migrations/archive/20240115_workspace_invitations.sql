-- Role-Based Workspace Invitations System
-- Migration: 20240115_workspace_invitations.sql
-- 
-- This migration implements a comprehensive workspace invitation system
-- with role-based permissions and audit trails

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Workspace invitations table
CREATE TABLE IF NOT EXISTS workspace_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    invited_email TEXT NOT NULL,
    invited_by UUID NOT NULL REFERENCES users(id),
    
    -- Role and permissions
    role TEXT NOT NULL DEFAULT 'member' CHECK (
        role IN ('owner', 'admin', 'member', 'viewer', 'guest')
    ),
    permissions JSONB DEFAULT '[]', -- Additional permissions beyond role defaults
    
    -- Status tracking
    status TEXT NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'accepted', 'declined', 'expired', 'revoked')
    ),
    
    -- Timestamps
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '7 days'),
    accepted_at TIMESTAMPTZ,
    accepted_by UUID REFERENCES users(id),
    
    -- Security
    invitation_token TEXT UNIQUE NOT NULL DEFAULT (encode(gen_random_bytes(32), 'hex')),
    ip_address INET,
    user_agent TEXT,
    
    -- Metadata
    message TEXT, -- Personal invitation message
    metadata JSONB DEFAULT '{}', -- Additional invitation data
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workspace members table (replaces simple workspace-user relationship)
CREATE TABLE IF NOT EXISTS workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Role and permissions
    role TEXT NOT NULL DEFAULT 'member' CHECK (
        role IN ('owner', 'admin', 'member', 'viewer', 'guest')
    ),
    permissions JSONB DEFAULT '[]', -- Additional permissions beyond role defaults
    
    -- Invitation tracking
    invited_by UUID REFERENCES users(id),
    invitation_id UUID REFERENCES workspace_invitations(id),
    
    -- Status and activity
    status TEXT NOT NULL DEFAULT 'active' CHECK (
        status IN ('active', 'inactive', 'suspended', 'removed')
    ),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ,
    
    -- Security
    ip_address INET,
    user_agent TEXT,
    
    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(workspace_id, user_id)
);

-- Workspace role definitions
CREATE TABLE IF NOT EXISTS workspace_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    
    -- Permissions
    permissions JSONB NOT NULL DEFAULT '[]',
    is_system_role BOOLEAN DEFAULT FALSE, -- Built-in roles cannot be deleted
    
    -- Hierarchy
    level INTEGER NOT NULL DEFAULT 0, -- Higher number = more privileges
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(workspace_id, name)
);

-- Insert default workspace roles
INSERT INTO workspace_roles (workspace_id, name, display_name, description, permissions, is_system_role, level) VALUES
-- These will be inserted per workspace via trigger
SELECT 
    w.id,
    'owner',
    'Owner',
    'Full control over workspace',
    '["read:workspace", "write:workspace", "delete:workspace", "manage:members", "manage:billing", "manage:settings"]',
    TRUE,
    100
FROM workspaces w
WHERE NOT EXISTS (
    SELECT 1 FROM workspace_roles wr 
    WHERE wr.workspace_id = w.id AND wr.name = 'owner'
)

UNION ALL

SELECT 
    w.id,
    'admin',
    'Administrator',
    'Can manage workspace settings and members',
    '["read:workspace", "write:workspace", "manage:members", "manage:settings"]',
    TRUE,
    80
FROM workspaces w
WHERE NOT EXISTS (
    SELECT 1 FROM workspace_roles wr 
    WHERE wr.workspace_id = w.id AND wr.name = 'admin'
)

UNION ALL

SELECT 
    w.id,
    'member',
    'Member',
    'Can create and edit content',
    '["read:workspace", "write:workspace"]',
    TRUE,
    50
FROM workspaces w
WHERE NOT EXISTS (
    SELECT 1 FROM workspace_roles wr 
    WHERE wr.workspace_id = w.id AND wr.name = 'member'
)

UNION ALL

SELECT 
    w.id,
    'viewer',
    'Viewer',
    'Can only view content',
    '["read:workspace"]',
    TRUE,
    20
FROM workspaces w
WHERE NOT EXISTS (
    SELECT 1 FROM workspace_roles wr 
    WHERE wr.workspace_id = w.id AND wr.name = 'viewer'
)

UNION ALL

SELECT 
    w.id,
    'guest',
    'Guest',
    'Limited access to specific resources',
    '[]',
    TRUE,
    10
FROM workspaces w
WHERE NOT EXISTS (
    SELECT 1 FROM workspace_roles wr 
    WHERE wr.workspace_id = w.id AND wr.name = 'guest'
);

-- Create indexes
CREATE INDEX idx_workspace_invitations_workspace_id ON workspace_invitations(workspace_id);
CREATE INDEX idx_workspace_invitations_email ON workspace_invitations(invited_email);
CREATE INDEX idx_workspace_invitations_status ON workspace_invitations(status);
CREATE INDEX idx_workspace_invitations_token ON workspace_invitations(invitation_token);
CREATE INDEX idx_workspace_invitations_expires_at ON workspace_invitations(expires_at);

CREATE INDEX idx_workspace_members_workspace_id ON workspace_members(workspace_id);
CREATE INDEX idx_workspace_members_user_id ON workspace_members(user_id);
CREATE INDEX idx_workspace_members_role ON workspace_members(role);
CREATE INDEX idx_workspace_members_status ON workspace_members(status);
CREATE INDEX idx_workspace_members_joined_at ON workspace_members(joined_at);

CREATE INDEX idx_workspace_roles_workspace_id ON workspace_roles(workspace_id);
CREATE INDEX idx_workspace_roles_name ON workspace_roles(name);
CREATE INDEX idx_workspace_roles_level ON workspace_roles(level);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_workspace_invitations_updated_at 
    BEFORE UPDATE ON workspace_invitations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspace_members_updated_at 
    BEFORE UPDATE ON workspace_members 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspace_roles_updated_at 
    BEFORE UPDATE ON workspace_roles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to create workspace invitation
CREATE OR REPLACE FUNCTION create_workspace_invitation(
    p_workspace_id UUID,
    p_invited_email TEXT,
    p_role TEXT DEFAULT 'member',
    p_permissions JSONB DEFAULT '[]',
    p_message TEXT DEFAULT NULL,
    p_expires_days INTEGER DEFAULT 7
) RETURNS UUID AS $$
DECLARE
    invitation_id UUID;
    inviter_id UUID;
    workspace_owner_id UUID;
BEGIN
    -- Get current user as inviter
    SELECT id INTO inviter_id
    FROM users
    WHERE auth_user_id = auth.uid();
    
    IF inviter_id IS NULL THEN
        RAISE EXCEPTION 'User not authenticated';
    END IF;
    
    -- Check if inviter has permission to invite members
    IF NOT EXISTS (
        SELECT 1 FROM workspace_members wm
        WHERE wm.workspace_id = p_workspace_id
        AND wm.user_id = inviter_id
        AND wm.status = 'active'
        AND wm.role IN ('owner', 'admin')
    ) THEN
        RAISE EXCEPTION 'User does not have permission to invite members';
    END IF;
    
    -- Check if invitation already exists and is pending
    IF EXISTS (
        SELECT 1 FROM workspace_invitations wi
        WHERE wi.workspace_id = p_workspace_id
        AND wi.invited_email = p_invited_email
        AND wi.status = 'pending'
        AND wi.expires_at > NOW()
    ) THEN
        RAISE EXCEPTION 'Invitation already exists for this email';
    END IF;
    
    -- Create invitation
    INSERT INTO workspace_invitations (
        workspace_id,
        invited_email,
        invited_by,
        role,
        permissions,
        message,
        expires_at
    ) VALUES (
        p_workspace_id,
        p_invited_email,
        inviter_id,
        p_role,
        p_permissions,
        p_message,
        NOW() + (p_expires_days || ' days')::INTERVAL
    ) RETURNING id INTO invitation_id;
    
    -- Log the invitation
    INSERT INTO audit_logs (
        actor_id,
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        inviter_id,
        'WORKSPACE_INVITATION_CREATED',
        'workspace',
        format('Invitation sent to %s for workspace %s', p_invited_email, p_workspace_id),
        jsonb_build_object(
            'invitation_id', invitation_id,
            'workspace_id', p_workspace_id,
            'invited_email', p_invited_email,
            'role', p_role,
            'expires_days', p_expires_days
        ),
        TRUE,
        NOW()
    );
    
    RETURN invitation_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to accept workspace invitation
CREATE OR REPLACE FUNCTION accept_workspace_invitation(
    p_invitation_token TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    invitation_record RECORD;
    user_id UUID;
    workspace_id UUID;
BEGIN
    -- Get invitation
    SELECT * INTO invitation_record
    FROM workspace_invitations
    WHERE invitation_token = p_invitation_token
    AND status = 'pending'
    AND expires_at > NOW();
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid or expired invitation';
    END IF;
    
    -- Get current user
    SELECT id INTO user_id
    FROM users
    WHERE auth_user_id = auth.uid();
    
    IF user_id IS NULL THEN
        RAISE EXCEPTION 'User not authenticated';
    END IF;
    
    -- Check if user is already a member
    IF EXISTS (
        SELECT 1 FROM workspace_members
        WHERE workspace_id = invitation_record.workspace_id
        AND user_id = user_id
        AND status = 'active'
    ) THEN
        RAISE EXCEPTION 'User is already a member of this workspace';
    END IF;
    
    -- Add user to workspace
    INSERT INTO workspace_members (
        workspace_id,
        user_id,
        role,
        permissions,
        invited_by,
        invitation_id,
        ip_address,
        user_agent
    ) VALUES (
        invitation_record.workspace_id,
        user_id,
        invitation_record.role,
        invitation_record.permissions,
        invitation_record.invited_by,
        invitation_record.id,
        inet_client_addr(),
        current_setting('request.headers')::json->>'user-agent'
    );
    
    -- Update invitation status
    UPDATE workspace_invitations
    SET 
        status = 'accepted',
        accepted_at = NOW(),
        accepted_by = user_id
    WHERE id = invitation_record.id;
    
    -- Log the acceptance
    INSERT INTO audit_logs (
        actor_id,
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        user_id,
        'WORKSPACE_INVITATION_ACCEPTED',
        'workspace',
        format('Invitation accepted for workspace %s', invitation_record.workspace_id),
        jsonb_build_object(
            'invitation_id', invitation_record.id,
            'workspace_id', invitation_record.workspace_id,
            'role', invitation_record.role
        ),
        TRUE,
        NOW()
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to decline workspace invitation
CREATE OR REPLACE FUNCTION decline_workspace_invitation(
    p_invitation_token TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    invitation_record RECORD;
    user_id UUID;
BEGIN
    -- Get invitation
    SELECT * INTO invitation_record
    FROM workspace_invitations
    WHERE invitation_token = p_invitation_token
    AND status = 'pending'
    AND expires_at > NOW();
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid or expired invitation';
    END IF;
    
    -- Get current user
    SELECT id INTO user_id
    FROM users
    WHERE auth_user_id = auth.uid();
    
    IF user_id IS NULL THEN
        RAISE EXCEPTION 'User not authenticated';
    END IF;
    
    -- Update invitation status
    UPDATE workspace_invitations
    SET 
        status = 'declined',
        accepted_at = NOW(),
        accepted_by = user_id
    WHERE id = invitation_record.id;
    
    -- Log the decline
    INSERT INTO audit_logs (
        actor_id,
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        user_id,
        'WORKSPACE_INVITATION_DECLINED',
        'workspace',
        format('Invitation declined for workspace %s', invitation_record.workspace_id),
        jsonb_build_object(
            'invitation_id', invitation_record.id,
            'workspace_id', invitation_record.workspace_id
        ),
        TRUE,
        NOW()
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to remove workspace member
CREATE OR REPLACE FUNCTION remove_workspace_member(
    p_workspace_id UUID,
    p_user_id UUID,
    p_reason TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    remover_id UUID;
    member_role TEXT;
BEGIN
    -- Get current user as remover
    SELECT id INTO remover_id
    FROM users
    WHERE auth_user_id = auth.uid();
    
    IF remover_id IS NULL THEN
        RAISE EXCEPTION 'User not authenticated';
    END IF;
    
    -- Get member role
    SELECT role INTO member_role
    FROM workspace_members
    WHERE workspace_id = p_workspace_id
    AND user_id = p_user_id
    AND status = 'active';
    
    IF member_role IS NULL THEN
        RAISE EXCEPTION 'User is not an active member of this workspace';
    END IF;
    
    -- Check permissions (can remove self or if admin/owner)
    IF remover_id != p_user_id AND NOT EXISTS (
        SELECT 1 FROM workspace_members wm
        WHERE wm.workspace_id = p_workspace_id
        AND wm.user_id = remover_id
        AND wm.status = 'active'
        AND wm.role IN ('owner', 'admin')
    ) THEN
        RAISE EXCEPTION 'User does not have permission to remove members';
    END IF;
    
    -- Cannot remove owner unless they are removing themselves
    IF member_role = 'owner' AND remover_id != p_user_id THEN
        RAISE EXCEPTION 'Cannot remove workspace owner';
    END IF;
    
    -- Remove member
    UPDATE workspace_members
    SET 
        status = 'removed',
        updated_at = NOW()
    WHERE workspace_id = p_workspace_id
    AND user_id = p_user_id;
    
    -- Log the removal
    INSERT INTO audit_logs (
        actor_id,
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        remover_id,
        'WORKSPACE_MEMBER_REMOVED',
        'workspace',
        format('Member %s removed from workspace %s', p_user_id, p_workspace_id),
        jsonb_build_object(
            'workspace_id', p_workspace_id,
            'removed_user_id', p_user_id,
            'previous_role', member_role,
            'reason', p_reason
        ),
        TRUE,
        NOW()
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get workspace members
CREATE OR REPLACE FUNCTION get_workspace_members(p_workspace_id UUID)
RETURNS TABLE(
    user_id UUID,
    email TEXT,
    full_name TEXT,
    role TEXT,
    permissions JSONB,
    status TEXT,
    joined_at TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ,
    invited_by_email TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        wm.user_id,
        u.email,
        u.full_name,
        wm.role,
        wm.permissions,
        wm.status,
        wm.joined_at,
        wm.last_accessed_at,
        inviter.email as invited_by_email
    FROM workspace_members wm
    JOIN users u ON wm.user_id = u.id
    LEFT JOIN users inviter ON wm.invited_by = inviter.id
    WHERE wm.workspace_id = p_workspace_id
    ORDER BY wm.joined_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Enable RLS on invitation tables
ALTER TABLE workspace_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_roles ENABLE ROW LEVEL SECURITY;

-- RLS policies for workspace invitations
CREATE POLICY "Users can view invitations for their workspaces" ON workspace_invitations
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members 
            WHERE user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
            AND status = 'active'
        )
    );

CREATE POLICY "Workspace admins can manage invitations" ON workspace_invitations
    FOR ALL USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members 
            WHERE user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
            AND status = 'active'
            AND role IN ('owner', 'admin')
        )
    );

-- RLS policies for workspace members
CREATE POLICY "Users can view members of their workspaces" ON workspace_members
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members 
            WHERE user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
            AND status = 'active'
        )
    );

CREATE POLICY "Workspace admins can manage members" ON workspace_members
    FOR ALL USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members 
            WHERE user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
            AND status = 'active'
            AND role IN ('owner', 'admin')
        )
    );

-- RLS policies for workspace roles
CREATE POLICY "Users can view roles for their workspaces" ON workspace_roles
    FOR SELECT USING (
        workspace_id IN (
            SELECT workspace_id FROM workspace_members 
            WHERE user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
            AND status = 'active'
        )
    );

-- Grant permissions to authenticated users
GRANT EXECUTE ON FUNCTION create_workspace_invitation(UUID, TEXT, TEXT, JSONB, TEXT, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION accept_workspace_invitation(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION decline_workspace_invitation(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION remove_workspace_member(UUID, UUID, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_workspace_members(UUID) TO authenticated;

-- Log the workspace invitations system setup
INSERT INTO audit_logs (
    action,
    action_category,
    description,
    details,
    success,
    created_at
) VALUES (
    'WORKSPACE_INVITATIONS_SYSTEM_SETUP',
    'workspace',
    'Role-based workspace invitations system implemented',
    jsonb_build_object(
        'migration', '20240115_workspace_invitations.sql',
        'tables_created', 3,
        'functions_created', 5
    ),
    TRUE,
    NOW()
);
