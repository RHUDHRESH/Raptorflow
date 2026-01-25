-- Database-Driven Permissions System
-- Migration: 20240115_permissions_system.sql
-- 
-- This migration implements a comprehensive, database-driven permissions system
-- that replaces hardcoded role permissions with dynamic, auditable permissions

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    resource TEXT NOT NULL,
    action TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'general',
    is_system BOOLEAN DEFAULT FALSE, -- System permissions cannot be deleted
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Role permissions mapping
CREATE TABLE IF NOT EXISTS role_permissions (
    role TEXT NOT NULL,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    granted_reason TEXT,
    PRIMARY KEY (role, permission_id)
);

-- User-specific permissions (overrides role permissions)
CREATE TABLE IF NOT EXISTS user_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    granted BOOLEAN NOT NULL DEFAULT TRUE, -- Can be used to deny specific permissions
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID REFERENCES users(id),
    granted_reason TEXT,
    expires_at TIMESTAMPTZ, -- Temporary permissions
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, permission_id)
);

-- Permission groups for easier management
CREATE TABLE IF NOT EXISTS permission_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Permission group mappings
CREATE TABLE IF NOT EXISTS permission_group_memberships (
    group_id UUID NOT NULL REFERENCES permission_groups(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (group_id, permission_id)
);

-- Role group assignments
CREATE TABLE IF NOT EXISTS role_permission_groups (
    role TEXT NOT NULL,
    group_id UUID NOT NULL REFERENCES permission_groups(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (role, group_id)
);

-- Insert default permissions
INSERT INTO permissions (name, resource, action, description, category, is_system) VALUES
-- User management
('read:own_profile', 'user', 'read', 'Read own user profile', 'user', TRUE),
('write:own_profile', 'user', 'write', 'Update own user profile', 'user', TRUE),
('delete:own_account', 'user', 'delete', 'Delete own account', 'user', TRUE),

-- Workspace management
('read:own_workspace', 'workspace', 'read', 'Read own workspace data', 'workspace', TRUE),
('write:own_workspace', 'workspace', 'write', 'Create and update workspace data', 'workspace', TRUE),
('delete:own_workspace', 'workspace', 'delete', 'Delete own workspace', 'workspace', TRUE),
('invite:workspace_members', 'workspace', 'invite', 'Invite members to workspace', 'workspace', TRUE),
('manage:workspace_members', 'workspace', 'manage', 'Manage workspace member roles', 'workspace', TRUE),

-- ICP Profiles
('read:icp_profiles', 'icp', 'read', 'Read ICP profiles in workspace', 'icp', TRUE),
('write:icp_profiles', 'icp', 'write', 'Create and update ICP profiles', 'icp', TRUE),
('delete:icp_profiles', 'icp', 'delete', 'Delete ICP profiles', 'icp', TRUE),

-- Campaigns
('read:campaigns', 'campaign', 'read', 'Read campaigns in workspace', 'campaign', TRUE),
('write:campaigns', 'campaign', 'write', 'Create and update campaigns', 'campaign', TRUE),
('delete:campaigns', 'campaign', 'delete', 'Delete campaigns', 'campaign', TRUE),

-- Analytics
('read:analytics', 'analytics', 'read', 'Access analytics data', 'analytics', TRUE),
('export:analytics', 'analytics', 'export', 'Export analytics data', 'analytics', TRUE),

-- Admin permissions
('admin:read_users', 'admin', 'read', 'Read all user accounts', 'admin', TRUE),
('admin:write_users', 'admin', 'write', 'Manage user accounts', 'admin', TRUE),
('admin:delete_users', 'admin', 'delete', 'Delete user accounts', 'admin', TRUE),
('admin:read_workspaces', 'admin', 'read', 'Read all workspaces', 'admin', TRUE),
('admin:manage_subscriptions', 'admin', 'manage', 'Manage user subscriptions', 'admin', TRUE),
('admin:read_audit_logs', 'admin', 'read', 'Read audit logs', 'admin', TRUE),
('admin:manage_permissions', 'admin', 'manage', 'Manage permissions and roles', 'admin', TRUE),
('admin:system_monitoring', 'admin', 'monitor', 'Access system monitoring tools', 'admin', TRUE),

-- Billing admin permissions
('billing:read_subscriptions', 'billing', 'read', 'Read subscription information', 'billing', TRUE),
('billing:write_subscriptions', 'billing', 'write', 'Manage subscriptions', 'billing', TRUE),
('billing:process_refunds', 'billing', 'refund', 'Process refunds', 'billing', TRUE),
('billing:read_transactions', 'billing', 'read', 'Read payment transactions', 'billing', TRUE),

-- Support permissions
('support:read_users', 'support', 'read', 'Read user information for support', 'support', TRUE),
('support:read_workspaces', 'support', 'read', 'Read workspace information for support', 'support', TRUE),
('support:manage_tickets', 'support', 'manage', 'Manage support tickets', 'support', TRUE)

ON CONFLICT (name) DO NOTHING;

-- Create permission groups
INSERT INTO permission_groups (name, description, is_system) VALUES
('Basic User', 'Basic permissions for all users', TRUE),
('Workspace Admin', 'Full workspace management permissions', TRUE),
('System Admin', 'Complete system administration', TRUE),
('Billing Manager', 'Billing and subscription management', TRUE),
('Support Agent', 'Customer support permissions', TRUE)
ON CONFLICT (name) DO NOTHING;

-- Assign permissions to groups
INSERT INTO permission_group_memberships (group_id, permission_id)
SELECT 
    pg.id,
    p.id
FROM permission_groups pg
CROSS JOIN permissions p
WHERE pg.name = 'Basic User'
AND p.name IN (
    'read:own_profile', 'write:own_profile', 'delete:own_account',
    'read:own_workspace', 'write:own_workspace', 'delete:own_workspace',
    'read:icp_profiles', 'write:icp_profiles', 'delete:icp_profiles',
    'read:campaigns', 'write:campaigns', 'delete:campaigns',
    'read:analytics', 'export:analytics'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

INSERT INTO permission_group_memberships (group_id, permission_id)
SELECT 
    pg.id,
    p.id
FROM permission_groups pg
CROSS JOIN permissions p
WHERE pg.name = 'Workspace Admin'
AND p.name IN (
    'read:own_profile', 'write:own_profile', 'delete:own_account',
    'read:own_workspace', 'write:own_workspace', 'delete:own_workspace',
    'invite:workspace_members', 'manage:workspace_members',
    'read:icp_profiles', 'write:icp_profiles', 'delete:icp_profiles',
    'read:campaigns', 'write:campaigns', 'delete:campaigns',
    'read:analytics', 'export:analytics'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

INSERT INTO permission_group_memberships (group_id, permission_id)
SELECT 
    pg.id,
    p.id
FROM permission_groups pg
CROSS JOIN permissions p
WHERE pg.name = 'System Admin'
AND p.name IN (
    'admin:read_users', 'admin:write_users', 'admin:delete_users',
    'admin:read_workspaces', 'admin:manage_subscriptions',
    'admin:read_audit_logs', 'admin:manage_permissions',
    'admin:system_monitoring'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

INSERT INTO permission_group_memberships (group_id, permission_id)
SELECT 
    pg.id,
    p.id
FROM permission_groups pg
CROSS JOIN permissions p
WHERE pg.name = 'Billing Manager'
AND p.name IN (
    'billing:read_subscriptions', 'billing:write_subscriptions',
    'billing:process_refunds', 'billing:read_transactions'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

INSERT INTO permission_group_memberships (group_id, permission_id)
SELECT 
    pg.id,
    p.id
FROM permission_groups pg
CROSS JOIN permissions p
WHERE pg.name = 'Support Agent'
AND p.name IN (
    'support:read_users', 'support:read_workspaces', 'support:manage_tickets'
)
ON CONFLICT (group_id, permission_id) DO NOTHING;

-- Assign groups to roles
INSERT INTO role_permission_groups (role, group_id)
SELECT 
    'user',
    pg.id
FROM permission_groups pg
WHERE pg.name = 'Basic User'
ON CONFLICT (role, group_id) DO NOTHING;

INSERT INTO role_permission_groups (role, group_id)
SELECT 
    'admin',
    pg.id
FROM permission_groups pg
WHERE pg.name IN ('Basic User', 'Workspace Admin', 'System Admin')
ON CONFLICT (role, group_id) DO NOTHING;

INSERT INTO role_permission_groups (role, group_id)
SELECT 
    'super_admin',
    pg.id
FROM permission_groups pg
WHERE pg.name IN ('Basic User', 'Workspace Admin', 'System Admin', 'Billing Manager', 'Support Agent')
ON CONFLICT (role, group_id) DO NOTHING;

INSERT INTO role_permission_groups (role, group_id)
SELECT 
    'billing_admin',
    pg.id
FROM permission_groups pg
WHERE pg.name IN ('Basic User', 'Billing Manager')
ON CONFLICT (role, group_id) DO NOTHING;

INSERT INTO role_permission_groups (role, group_id)
SELECT 
    'support',
    pg.id
FROM permission_groups pg
WHERE pg.name IN ('Basic User', 'Support Agent')
ON CONFLICT (role, group_id) DO NOTHING;

-- Create helper functions for permission checking

-- Function to check if a user has a specific permission
CREATE OR REPLACE FUNCTION user_has_permission(
    p_user_id UUID,
    p_permission_name TEXT,
    p_workspace_id UUID DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    has_user_permission BOOLEAN := FALSE;
    has_role_permission BOOLEAN := FALSE;
    user_role TEXT;
BEGIN
    -- Check user-specific permissions first (they override role permissions)
    SELECT granted INTO has_user_permission
    FROM user_permissions up
    JOIN permissions p ON up.permission_id = p.id
    WHERE up.user_id = p_user_id
    AND p.name = p_permission_name
    AND up.is_active = TRUE
    AND (up.expires_at IS NULL OR up.expires_at > NOW())
    LIMIT 1;
    
    -- If user has explicit permission (granted or denied), return that
    IF has_user_permission IS NOT NULL THEN
        RETURN has_user_permission;
    END IF;
    
    -- Get user's role
    SELECT role INTO user_role
    FROM users
    WHERE id = p_user_id;
    
    -- Check role permissions through groups
    SELECT EXISTS (
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p ON rp.permission_id = p.id
        WHERE rp.role = user_role
        AND p.name = p_permission_name
    ) INTO has_role_permission;
    
    -- If no role permission found, check through permission groups
    IF NOT has_role_permission THEN
        SELECT EXISTS (
            SELECT 1
            FROM role_permission_groups rpg
            JOIN permission_group_memberships pgm ON rpg.group_id = pgm.group_id
            JOIN permissions p ON pgm.permission_id = p.id
            WHERE rpg.role = user_role
            AND p.name = p_permission_name
        ) INTO has_role_permission;
    END IF;
    
    RETURN COALESCE(has_role_permission, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check current user's permission
CREATE OR REPLACE FUNCTION current_user_has_permission(p_permission_name TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN user_has_permission(
        (SELECT id FROM users WHERE auth_user_id = auth.uid()),
        p_permission_name
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get all permissions for a user
CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE(
    permission_name TEXT,
    resource TEXT,
    action TEXT,
    description TEXT,
    category TEXT,
    granted_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    is_user_specific BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    -- User-specific permissions
    SELECT 
        p.name,
        p.resource,
        p.action,
        p.description,
        p.category,
        up.granted_at,
        up.expires_at,
        TRUE as is_user_specific
    FROM user_permissions up
    JOIN permissions p ON up.permission_id = p.id
    WHERE up.user_id = p_user_id
    AND up.is_active = TRUE
    AND (up.expires_at IS NULL OR up.expires_at > NOW())
    
    UNION ALL
    
    -- Role permissions through groups
    SELECT 
        p.name,
        p.resource,
        p.action,
        p.description,
        p.category,
        rpg.assigned_at,
        NULL as expires_at,
        FALSE as is_user_specific
    FROM users u
    JOIN role_permission_groups rpg ON u.role = rpg.role
    JOIN permission_group_memberships pgm ON rpg.group_id = pgm.group_id
    JOIN permissions p ON pgm.permission_id = p.id
    WHERE u.id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to grant permission to user
CREATE OR REPLACE FUNCTION grant_user_permission(
    p_user_id UUID,
    p_permission_name TEXT,
    p_granted BOOLEAN DEFAULT TRUE,
    p_expires_at TIMESTAMPTZ DEFAULT NULL,
    p_reason TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    permission_id UUID;
    granter_id UUID;
BEGIN
    -- Get permission ID
    SELECT id INTO permission_id
    FROM permissions
    WHERE name = p_permission_name;
    
    IF permission_id IS NULL THEN
        RAISE EXCEPTION 'Permission % does not exist', p_permission_name;
    END IF;
    
    -- Get current user as granter
    granter_id := (SELECT id FROM users WHERE auth_user_id = auth.uid());
    
    -- Insert or update user permission
    INSERT INTO user_permissions (
        user_id,
        permission_id,
        granted,
        granted_by,
        granted_reason,
        expires_at
    ) VALUES (
        p_user_id,
        permission_id,
        p_granted,
        granter_id,
        p_reason,
        p_expires_at
    )
    ON CONFLICT (user_id, permission_id)
    DO UPDATE SET
        granted = p_granted,
        granted_by = granter_id,
        granted_reason = p_reason,
        expires_at = p_expires_at,
        is_active = TRUE,
        granted_at = NOW();
    
    -- Log the permission change
    INSERT INTO audit_logs (
        actor_id,
        action,
        action_category,
        description,
        details,
        success,
        created_at
    ) VALUES (
        granter_id,
        'PERMISSION_GRANTED',
        'admin',
        format('Permission %s %s to user %s', 
               p_permission_name, 
               CASE WHEN p_granted THEN 'granted' ELSE 'denied' END,
               p_user_id),
        jsonb_build_object(
            'permission_name', p_permission_name,
            'target_user_id', p_user_id,
            'granted', p_granted,
            'expires_at', p_expires_at,
            'reason', p_reason
        ),
        TRUE,
        NOW()
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create indexes for performance
CREATE INDEX idx_permissions_resource_action ON permissions(resource, action);
CREATE INDEX idx_permissions_name ON permissions(name);
CREATE INDEX idx_role_permissions_role ON role_permissions(role);
CREATE INDEX idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_active ON user_permissions(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_permission_group_memberships_group_id ON permission_group_memberships(group_id);
CREATE INDEX idx_role_permission_groups_role ON role_permission_groups(role);

-- Enable RLS on permission tables
ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE permission_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE permission_group_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_permission_groups ENABLE ROW LEVEL SECURITY;

-- RLS policies for permissions (read-only for authenticated users)
CREATE POLICY "Authenticated users can read permissions" ON permissions
    FOR SELECT USING (auth.role() = 'authenticated');

-- RLS policies for role permissions (admin only)
CREATE POLICY "Admins can manage role permissions" ON role_permissions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth_user_id = auth.uid() 
            AND role IN ('admin', 'super_admin')
        )
    );

-- RLS policies for user permissions (users can see their own, admins can see all)
CREATE POLICY "Users can read own permissions" ON user_permissions
    FOR SELECT USING (
        user_id = (SELECT id FROM users WHERE auth_user_id = auth.uid())
    );

CREATE POLICY "Admins can manage user permissions" ON user_permissions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE auth_user_id = auth.uid() 
            AND role IN ('admin', 'super_admin')
        )
    );

-- Grant permissions to authenticated users
GRANT SELECT ON permissions TO authenticated;
GRANT EXECUTE ON FUNCTION user_has_permission(UUID, TEXT, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION current_user_has_permission(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_permissions(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION grant_user_permission(UUID, TEXT, BOOLEAN, TIMESTAMPTZ, TEXT) TO authenticated;

-- Log the permissions system setup
INSERT INTO audit_logs (
    action,
    action_category,
    description,
    details,
    success,
    created_at
) VALUES (
    'PERMISSIONS_SYSTEM_SETUP',
    'security',
    'Database-driven permissions system implemented',
    jsonb_build_object(
        'migration', '20240115_permissions_system.sql',
        'permissions_count', (SELECT COUNT(*) FROM permissions),
        'permission_groups_count', (SELECT COUNT(*) FROM permission_groups)
    ),
    TRUE,
    NOW()
);
