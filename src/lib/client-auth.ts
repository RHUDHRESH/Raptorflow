/**
 * 🔐 CLIENT-SIDE AUTHENTICATION - Textbook Implementation
 * 
 * This file contains client-only authentication functions that can be
 * used in Client Components with "use client".
 */

// ============================================================================
// 🔐 CLIENT-SIDE AUTH HELPERS - Textbook Simple
// ============================================================================

/**
 * Create a simple user account (for local development)
 * This is a simplified auth system for development purposes
 * 
 * @param username - Username (used as password for simplicity)
 * @returns Success status
 */
export function createUser(username: string): boolean {
  try {
    // For local development, store user in localStorage
    if (typeof window !== 'undefined') {
      const users = JSON.parse(localStorage.getItem('users') || '{}');
      users[username] = {
        username,
        createdAt: new Date().toISOString(),
        // In this simple system, username = password
        password: username
      };
      localStorage.setItem('users', JSON.stringify(users));
      return true;
    }
    return false;
  } catch (error) {
    console.error('🔐 [Auth] Error creating user:', error);
    return false;
  }
}

/**
 * Login with username/password
 * 
 * @param username - Username
 * @param password - Password (same as username in this simple system)
 * @returns Success status
 */
export function loginUser(username: string, password: string): boolean {
  try {
    if (typeof window !== 'undefined') {
      const users = JSON.parse(localStorage.getItem('users') || '{}');
      const user = users[username];
      
      // Check if user exists and password matches (username = password)
      if (user && user.password === password) {
        localStorage.setItem('currentUser', username);
        return true;
      }
    }
    return false;
  } catch (error) {
    console.error('🔐 [Auth] Error logging in:', error);
    return false;
  }
}

/**
 * Logout current user
 */
export function logoutUser(): void {
  try {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('currentUser');
    }
  } catch (error) {
    console.error('🔐 [Auth] Error logging out:', error);
  }
}

/**
 * Get current user
 * 
 * @returns Current username or null
 */
export function getCurrentClientUser(): string | null {
  try {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('currentUser');
    }
    return null;
  } catch (error) {
    console.error('🔐 [Auth] Error getting current user:', error);
    return null;
  }
}

/**
 * Check if user is authenticated
 * 
 * @returns True if authenticated, false otherwise
 */
export function clientIsAuthenticated(): boolean {
  return getCurrentClientUser() !== null;
}

/**
 * Client-side redirect to login
 */
export function clientRedirectToLogin(): void {
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

/**
 * Check if a user exists
 * 
 * @param username - Username to check
 * @returns True if user exists, false otherwise
 */
export function userExists(username: string): boolean {
  try {
    if (typeof window !== 'undefined') {
      const users = JSON.parse(localStorage.getItem('users') || '{}');
      return users.hasOwnProperty(username);
    }
    return false;
  } catch (error) {
    console.error('🔐 [Auth] Error checking user existence:', error);
    return false;
  }
}

/**
 * Get all users (for development purposes)
 * 
 * @returns Array of user objects
 */
export function getAllUsers(): Array<{ username: string; createdAt: string }> {
  try {
    if (typeof window !== 'undefined') {
      const users = JSON.parse(localStorage.getItem('users') || '{}');
      return Object.values(users);
    }
    return [];
  } catch (error) {
    console.error('🔐 [Auth] Error getting all users:', error);
    return [];
  }
}

// ============================================================================
// 🔐 TYPESCRIPT TYPES - Textbook Simple
// ============================================================================

export type ClientUser = {
  username: string;
  createdAt: string;
  password: string;
};
