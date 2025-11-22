/**
 * Permissions Utility
 * Role-based access control helpers
 */

export type UserRole = 'Owner' | 'Strategist' | 'Creator' | 'Analyst' | 'Viewer';

/**
 * Check if user can create moves
 */
export const canCreateMove = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return ['Owner', 'Strategist'].includes(userRole);
};

/**
 * Check if user can edit strategy
 */
export const canEditStrategy = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return ['Owner', 'Strategist'].includes(userRole);
};

/**
 * Check if user can approve high-risk moves
 */
export const canApproveHighRiskMove = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return userRole === 'Owner';
};

/**
 * Check if user can create/edit cohorts
 */
export const canManageCohorts = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return ['Owner', 'Strategist'].includes(userRole);
};

/**
 * Check if user can create/edit assets
 */
export const canManageAssets = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return ['Owner', 'Strategist', 'Creator'].includes(userRole);
};

/**
 * Check if user can view analytics
 */
export const canViewAnalytics = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  // All roles can view analytics
  return true;
};

/**
 * Check if user can export data
 */
export const canExportData = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return ['Owner', 'Strategist', 'Analyst'].includes(userRole);
};

/**
 * Check if user can manage workspace settings
 */
export const canManageWorkspace = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return userRole === 'Owner';
};

/**
 * Check if user can invite members
 */
export const canInviteMembers = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return ['Owner', 'Strategist'].includes(userRole);
};

/**
 * Check if user can manage team members
 */
export const canManageMembers = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return userRole === 'Owner';
};

/**
 * Check if user can delete moves
 */
export const canDeleteMove = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return ['Owner', 'Strategist'].includes(userRole);
};

/**
 * Check if user can execute moves (mark tasks complete, etc.)
 */
export const canExecuteMove = (userRole?: UserRole): boolean => {
  if (!userRole) return false;
  return ['Owner', 'Strategist', 'Creator'].includes(userRole);
};

/**
 * Get role display name
 */
export const getRoleDisplayName = (role?: UserRole): string => {
  if (!role) return 'Unknown';
  return role;
};

/**
 * Get role description
 */
export const getRoleDescription = (role?: UserRole): string => {
  if (!role) return '';
  
  const descriptions: Record<UserRole, string> = {
    Owner: 'Full access to all features, billing, and workspace management',
    Strategist: 'Can create and edit strategy, moves, cohorts, and lines of operation',
    Creator: 'Can create and edit assets, execute moves, and manage content',
    Analyst: 'Can view analytics, reports, and dashboards (read-only on moves)',
    Viewer: 'Read-only access to workspace content'
  };
  
  return descriptions[role] || '';
};

/**
 * Get all available roles
 */
export const getAllRoles = (): Array<{ value: UserRole; label: string; description: string }> => {
  const roles: UserRole[] = ['Owner', 'Strategist', 'Creator', 'Analyst', 'Viewer'];
  return roles.map(role => ({
    value: role,
    label: getRoleDisplayName(role),
    description: getRoleDescription(role)
  }));
};

/**
 * Check if a role can be assigned by the current user
 */
export const canAssignRole = (currentUserRole?: UserRole, roleToAssign?: UserRole): boolean => {
  if (!currentUserRole || !roleToAssign) return false;
  
  // Only owners can assign any role
  if (currentUserRole === 'Owner') return true;
  
  // Strategists can assign Creator, Analyst, Viewer
  if (currentUserRole === 'Strategist') {
    return ['Creator', 'Analyst', 'Viewer'].includes(roleToAssign);
  }
  
  return false;
};

