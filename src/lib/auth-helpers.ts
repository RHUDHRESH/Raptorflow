/**
 * 🔐 AUTHENTICATION HELPERS - Textbook Implementation
 *
 * This file contains helper functions for authentication.
 * No magic, no complexity, just pure textbook authentication.
 *
 * 📚 TEXTBOOK EXAMPLE:
 * 1. Check if user is authenticated
 * 2. Get user data from JWT
 * 3. Handle auth errors
 * 4. Redirect to login
 */

/**
 * Check if user is authenticated - textbook implementation
 *
 * @returns True if authenticated, false otherwise
 */
export async function isAuthenticated(): Promise<boolean> {
  try {
    const response = await fetch('/api/auth/me');
    return response.ok;
  } catch (error) {
    console.error('🔐 [Auth] Error checking authentication:', error);
    return false;
  }
}

/**
 * Get current user data - textbook implementation
 *
 * @returns User data or null
 */
export async function getCurrentUser(): Promise<{
  userId: string;
  email: string;
} | null> {
  try {
    const response = await fetch('/api/auth/me');

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    return data.user;
  } catch (error) {
    console.error('🔐 [Auth] Error getting current user:', error);
    return null;
  }
}

/**
 * Handle authentication error - textbook implementation
 *
 * @param error - Error object
 * @returns Error message string
 */
export function handleAuthError(error: any): string {
  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  return 'An unknown error occurred';
}

/**
 * Redirect to sign in page - textbook implementation
 */
export function redirectToLogin(): void {
  if (typeof window !== 'undefined') {
    window.location.href = '/signin';
  }
}

/**
 * Redirect to dashboard - textbook implementation
 */
export function redirectToDashboard(): void {
  if (typeof window !== 'undefined') {
    window.location.href = '/dashboard';
  }
}

/**
 * Check if client is authenticated - textbook implementation
 *
 * @returns True if authenticated, false otherwise
 */
export function clientIsAuthenticated(): boolean {
  if (typeof window === 'undefined') {
    return false;
  }

  // Check for auth cookie
  return document.cookie.includes('auth-token=');
}

/**
 * Get user ID from JWT - textbook implementation
 *
 * @returns User ID or null
 */
export async function getUserId(): Promise<string | null> {
  const user = await getCurrentUser();
  return user?.userId || null;
}

/**
 * Get user email from JWT - textbook implementation
 *
 * @returns User email or null
 */
export async function getUserEmail(): Promise<string | null> {
  const user = await getCurrentUser();
  return user?.email || null;
}
