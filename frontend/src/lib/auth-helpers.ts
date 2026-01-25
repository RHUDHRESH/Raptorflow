/**
 * Authentication helpers for API calls
 * Ensures auth context flows properly between frontend and backend
 */

export interface AuthContext {
  user: {
    id: string;
    email: string;
  } | null;
  session: {
    access_token: string;
    refresh_token?: string;
  } | null;
  profile: {
    id: string;
    workspace_id: string;
  } | null;
}

/**
 * Get current auth context from localStorage or Supabase
 */
export function getAuthContext(): AuthContext {
  // Try to get from localStorage first (fallback)
  const storedUser = localStorage.getItem('supabase.auth.token');
  
  if (storedUser) {
    try {
      const parsed = JSON.parse(storedUser);
      return {
        user: parsed.user ? {
          id: parsed.user.id,
          email: parsed.user.email
        } : null,
        session: parsed.session ? {
          access_token: parsed.session.access_token,
          refresh_token: parsed.session.refresh_token
        } : null,
        profile: parsed.profile ? {
          id: parsed.profile.id,
          workspace_id: parsed.profile.workspace_id
        } : null
      };
    } catch (error) {
      console.error('Failed to parse stored auth:', error);
    }
  }

  // Return empty context if nothing found
  return {
    user: null,
    session: null,
    profile: null
  };
}

/**
 * Get auth headers for API requests
 */
export function getAuthHeaders(): Record<string, string> {
  const auth = getAuthContext();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (auth.session?.access_token) {
    headers['Authorization'] = `Bearer ${auth.session.access_token}`;
  }

  if (auth.profile?.workspace_id) {
    headers['X-Workspace-ID'] = auth.profile.workspace_id;
  }

  if (auth.user?.id) {
    headers['X-User-ID'] = auth.user.id;
  }

  return headers;
}

/**
 * Enhanced fetch with auth context
 */
export async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const headers = {
    ...getAuthHeaders(),
    ...options.headers,
  };

  return fetch(url, {
    ...options,
    headers,
  });
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const auth = getAuthContext();
  return !!(auth.user && auth.session?.access_token);
}

/**
 * Get current user ID
 */
export function getCurrentUserId(): string | null {
  const auth = getAuthContext();
  return auth.user?.id || null;
}

/**
 * Get current workspace ID
 */
export function getCurrentWorkspaceId(): string | null {
  const auth = getAuthContext();
  return auth.profile?.workspace_id || null;
}

/**
 * Store auth context to localStorage
 */
export function setAuthContext(auth: AuthContext): void {
  try {
    localStorage.setItem('supabase.auth.token', JSON.stringify(auth));
  } catch (error) {
    console.error('Failed to store auth context:', error);
  }
}

/**
 * Clear auth context from localStorage
 */
export function clearAuthContext(): void {
  try {
    localStorage.removeItem('supabase.auth.token');
  } catch (error) {
    console.error('Failed to clear auth context:', error);
  }
}
