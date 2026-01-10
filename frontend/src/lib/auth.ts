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

// Check if user is authenticated
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;

  try {
    const sessionStr = localStorage.getItem('raptorflow_session');
    if (!sessionStr) return false;

    const session: Session = JSON.parse(sessionStr);

    // Check if session is expired
  const now = new Date();
  const expiresAt = new Date(session.expires_at);

  if (now > expiresAt) {
    // Session expired, clean up
    localStorage.removeItem('raptorflow_session');
    localStorage.removeItem('raptorflow_user');
    return false;
  }

    return true;
  } catch (error) {
    console.error('Error checking authentication:', error);
    return false;
  }
}

// Get current user
export function getCurrentUser(): User | null {
  if (!isAuthenticated()) return null;

  try {
    const sessionStr = localStorage.getItem('raptorflow_session');
    if (!sessionStr) return null;
    const session: Session = JSON.parse(sessionStr);
    return session.user;
  } catch (error) {
    console.error('Error getting current user:', error);
    return null;
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

// Protected route check
export function requireAuth(): User | null {
  if (!isAuthenticated()) {
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    return null;
  }

  return getCurrentUser();
}
