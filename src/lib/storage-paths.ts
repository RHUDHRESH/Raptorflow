/**
 * Supabase Storage Path Utilities
 * Standardized path convention for all storage operations
 */

// ============================================================================
// BUCKET CONFIGURATION
// ============================================================================

export const BUCKETS = {
  WORKSPACE_UPLOADS: 'workspace-uploads',
  WORKSPACE_EXPORTS: 'workspace-exports',
  WORKSPACE_BACKUPS: 'workspace-backups',
  WORKSPACE_ASSETS: 'workspace-assets',
  WORKSPACE_LOGS: 'workspace-logs',
  INTELLIGENCE_VAULT: 'intelligence-vault',
  USER_AVATARS: 'user-avatars',
  USER_DOCUMENTS: 'user-documents',
  USER_DATA: 'user-data'
} as const;

// ============================================================================
// PATH GENERATION FUNCTIONS
// ============================================================================

/**
 * Generate standardized workspace storage path
 * Format: workspace/<workspace-slug>/<category>/<YYYY-MM-DD>/<uuid>-<filename>
 */
export function generateWorkspacePath(
  workspaceSlug: string,
  category: string,
  filename: string
): string {
  const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const uuid = crypto.randomUUID();
  const cleanFilename = filename.replace(/[^a-zA-Z0-9.-]/g, '_');

  return `workspace/${workspaceSlug}/${category}/${date}/${uuid}-${cleanFilename}`;
}

/**
 * Generate standardized user storage path
 * Format: users/<user-id>/<category>/<YYYY-MM-DD>/<uuid>-<filename>
 */
export function generateUserPath(
  userId: string,
  category: string,
  filename: string
): string {
  const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const uuid = crypto.randomUUID();
  const cleanFilename = filename.replace(/[^a-zA-Z0-9.-]/g, '_');

  return `users/${userId}/${category}/${date}/${uuid}-${cleanFilename}`;
}

/**
 * Generate intelligence vault path
 * Format: intelligence-vault/<workspace-slug>/<YYYY-MM-DD>/<uuid>.json
 */
export function generateIntelligencePath(
  workspaceSlug: string,
  queryId?: string
): string {
  const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const uuid = queryId || crypto.randomUUID();

  return `intelligence-vault/${workspaceSlug}/${date}/${uuid}.json`;
}

// ============================================================================
// BUCKET SELECTION
// ============================================================================

/**
 * Get appropriate bucket for file category
 */
export function getBucketForCategory(category: string): string {
  switch (category.toLowerCase()) {
    case 'avatar':
    case 'avatars':
      return BUCKETS.USER_AVATARS;

    case 'document':
    case 'documents':
    case 'uploads':
      return BUCKETS.WORKSPACE_UPLOADS;

    case 'export':
    case 'exports':
      return BUCKETS.WORKSPACE_EXPORTS;

    case 'backup':
    case 'backups':
      return BUCKETS.WORKSPACE_BACKUPS;

    case 'asset':
    case 'assets':
      return BUCKETS.WORKSPACE_ASSETS;

    case 'log':
    case 'logs':
      return BUCKETS.WORKSPACE_LOGS;

    case 'intelligence':
    case 'evidence':
      return BUCKETS.INTELLIGENCE_VAULT;

    case 'user-data':
      return BUCKETS.USER_DATA;

    default:
      return BUCKETS.WORKSPACE_UPLOADS;
  }
}

// ============================================================================
// PATH PARSING
// ============================================================================

/**
 * Parse storage path to extract components
 */
export function parseStoragePath(storagePath: string): {
  type: 'workspace' | 'user' | 'intelligence';
  workspaceSlug?: string;
  userId?: string;
  category?: string;
  date?: string;
  filename?: string;
} | null {
  // Workspace path: workspace/<workspace-slug>/<category>/<date>/<filename>
  const workspaceMatch = storagePath.match(/^workspace\/([^/]+)\/([^/]+)\/([^/]+)\/(.+)$/);
  if (workspaceMatch) {
    return {
      type: 'workspace',
      workspaceSlug: workspaceMatch[1],
      category: workspaceMatch[2],
      date: workspaceMatch[3],
      filename: workspaceMatch[4]
    };
  }

  // User path: users/<user-id>/<category>/<date>/<filename>
  const userMatch = storagePath.match(/^users\/([^/]+)\/([^/]+)\/([^/]+)\/(.+)$/);
  if (userMatch) {
    return {
      type: 'user',
      userId: userMatch[1],
      category: userMatch[2],
      date: userMatch[3],
      filename: userMatch[4]
    };
  }

  // Intelligence path: intelligence-vault/<workspace-slug>/<date>/<filename>
  const intelligenceMatch = storagePath.match(/^intelligence-vault\/([^/]+)\/([^/]+)\/(.+)$/);
  if (intelligenceMatch) {
    return {
      type: 'intelligence',
      workspaceSlug: intelligenceMatch[1],
      date: intelligenceMatch[2],
      filename: intelligenceMatch[3]
    };
  }

  return null;
}

// ============================================================================
// VALIDATION
// ============================================================================

/**
 * Validate storage path format
 */
export function validateStoragePath(storagePath: string): boolean {
  const parsed = parseStoragePath(storagePath);
  return parsed !== null;
}

/**
 * Check if path belongs to workspace
 */
export function isWorkspacePath(storagePath: string): boolean {
  const parsed = parseStoragePath(storagePath);
  return parsed?.type === 'workspace';
}

/**
 * Check if path belongs to user
 */
export function isUserPath(storagePath: string): boolean {
  const parsed = parseStoragePath(storagePath);
  return parsed?.type === 'user';
}

/**
 * Check if path belongs to intelligence vault
 */
export function isIntelligencePath(storagePath: string): boolean {
  const parsed = parseStoragePath(storagePath);
  return parsed?.type === 'intelligence';
}

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Extract workspace slug from storage path
 */
export function extractWorkspaceSlug(storagePath: string): string | null {
  const parsed = parseStoragePath(storagePath);
  return parsed?.workspaceSlug || null;
}

/**
 * Extract user ID from storage path
 */
export function extractUserId(storagePath: string): string | null {
  const parsed = parseStoragePath(storagePath);
  return parsed?.userId || null;
}

/**
 * Extract category from storage path
 */
export function extractCategory(storagePath: string): string | null {
  const parsed = parseStoragePath(storagePath);
  return parsed?.category || null;
}

/**
 * Generate public URL for storage path
 */
export function generatePublicUrl(bucket: string, storagePath: string): string {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  if (!supabaseUrl) {
    throw new Error('NEXT_PUBLIC_SUPABASE_URL not configured');
  }

  return `${supabaseUrl}/storage/v1/object/public/${bucket}/${storagePath}`;
}
