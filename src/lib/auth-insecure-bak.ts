// Authentication utilities for Raptorflow

export interface User {
  id: string;
  email: string;
  fullName: string;
  subscriptionPlan: 'soar' | 'glide' | 'ascent';
  subscriptionStatus: 'active' | 'cancelled' | 'expired';
  createdAt: string;
}

export interface Session {
  access_token: string;
  user: User;
  expires_at: string;
}

// Check if user is authenticated - ALWAYS TRUE (BYPASS MODE)
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return true;

  try {
    const sessionStr = localStorage.getItem('raptorflow_session');
    if (!sessionStr) {
      // Auto-create session if none exists
      const mockUser: User = {
        id: 'user-bypass',
        email: 'demo@raptorflow.com',
        fullName: 'Demo User',
        subscriptionPlan: 'soar',
        subscriptionStatus: 'active',
        createdAt: new Date().toISOString()
      };
      signIn(mockUser);
      return true;
    }

    const session: Session = JSON.parse(sessionStr);

    // Check if session is expired
  const now = new Date();
  const expiresAt = new Date(session.expires_at);

  if (now > expiresAt) {
    // Session expired, create new one
    const mockUser: User = {
      id: 'user-bypass',
      email: 'demo@raptorflow.com',
      fullName: 'Demo User',
      subscriptionPlan: 'soar',
      subscriptionStatus: 'active',
      createdAt: new Date().toISOString()
    };
    signIn(mockUser);
    return true;
  }

    return true;
  } catch (error) {
    // On any error, create a bypass session
    const mockUser: User = {
      id: 'user-bypass',
      email: 'demo@raptorflow.com',
      fullName: 'Demo User',
      subscriptionPlan: 'soar',
      subscriptionStatus: 'active',
      createdAt: new Date().toISOString()
    };
    signIn(mockUser);
    return true;
  }
}

// Get current user - ALWAYS RETURNS A USER (BYPASS MODE)
export function getCurrentUser(): User | null {
  if (typeof window === 'undefined') return null;

  try {
    const sessionStr = localStorage.getItem('raptorflow_session');
    if (!sessionStr) {
      // Create and return mock user
      const mockUser: User = {
        id: 'user-bypass',
        email: 'demo@raptorflow.com',
        fullName: 'Demo User',
        subscriptionPlan: 'soar',
        subscriptionStatus: 'active',
        createdAt: new Date().toISOString()
      };
      signIn(mockUser);
      return mockUser;
    }
    const session: Session = JSON.parse(sessionStr);
    return session.user;
  } catch (error) {
    // Return mock user on error
    const mockUser: User = {
      id: 'user-bypass',
      email: 'demo@raptorflow.com',
      fullName: 'Demo User',
      subscriptionPlan: 'soar',
      subscriptionStatus: 'active',
      createdAt: new Date().toISOString()
    };
    signIn(mockUser);
    return mockUser;
  }
}

// Get current session
export function getCurrentSession(): Session | null {
  if (!isAuthenticated()) return null;

  try {
    const sessionStr = localStorage.getItem('raptorflow_session');
    if (!sessionStr) return null;
    return JSON.parse(sessionStr);
  } catch (error) {
    console.error('Error getting current session:', error);
    return null;
  }
}

// Sign out user
export function signOut(): void {
  if (typeof window === 'undefined') return;

  localStorage.removeItem('raptorflow_session');
  localStorage.removeItem('raptorflow_user');

  // Redirect to login page
  window.location.href = '/login';
}

// Sign in user (for bypass system)
export function signIn(user: User): void {
  if (typeof window === 'undefined') return;

  const session: Session = {
    access_token: 'bypass-access-token',
    user: user,
    expires_at: new Date(Date.now() + 3600000).toISOString() // 1 hour
  };

  localStorage.setItem('raptorflow_user', JSON.stringify(user));
  localStorage.setItem('raptorflow_session', JSON.stringify(session));
}

// Sign up user (for bypass system)
export function signUp(email: string, fullName: string): User {
  const user: User = {
    id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    email: email,
    fullName: fullName,
    subscriptionPlan: 'soar',
    subscriptionStatus: 'active',
    createdAt: new Date().toISOString()
  };

  signIn(user);
  return user;
}

// Protected route check - ALWAYS RETURNS USER (BYPASS MODE)
export function requireAuth(): User | null {
  // Always return a user, no auth required
  return getCurrentUser();
}
