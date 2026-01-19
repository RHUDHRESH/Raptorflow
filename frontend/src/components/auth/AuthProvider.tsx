/**
 * 🔐 AUTH PROVIDER - Enhanced Implementation
 * 
 * Complete authentication state management with:
 * - Google OAuth integration
 * - Subscription verification
 * - Payment flow handling
 * - Proper error handling
 * - Real-time state updates
 */

'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '@/lib/supabaseClient';

// ============================================================================
// 🔐 AUTH CONTEXT - Enhanced Types
// ============================================================================

interface User {
  userId: string;
  email: string;
  name?: string;
  avatar?: string;
}

interface Subscription {
  hasSubscription: boolean;
  planId?: string;
  planName?: string;
  planSlug?: string;
  status?: string;
  expiresAt?: string;
  canAccessApp: boolean;
  onboardingCompleted: boolean;
  onboardingStep: number;
}

interface Workspace {
  hasWorkspace: boolean;
  workspaceId?: string;
  workspaceName?: string;
  onboardingCompleted: boolean;
  onboardingStep: number;
  businessContextUrl?: string;
}

interface AuthState {
  user: User | null;
  subscription: Subscription | null;
  workspace: Workspace | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  refreshSubscription: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================================================
// 🔐 AUTH PROVIDER COMPONENT - Enhanced Implementation
// ============================================================================

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    subscription: null,
    workspace: null,
    isLoading: true,
    isAuthenticated: false,
    error: null,
  });

  // Clear error function
  const clearError = () => {
    setAuthState(prev => ({ ...prev, error: null }));
  };

  // Check authentication status on mount
  useEffect(() => {
    checkAuthStatus();
    
    // Set up Supabase auth state listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('🔐 [Auth] Auth state changed:', event, session?.user?.email);
        
        if (event === 'SIGNED_IN' && session) {
          await checkAuthStatus();
        } else if (event === 'SIGNED_OUT') {
          setAuthState({
            user: null,
            subscription: null,
            workspace: null,
            isLoading: false,
            isAuthenticated: false,
            error: null,
          });
        }
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  /**
   * Check authentication status - enhanced implementation
   */
  const checkAuthStatus = async () => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

      // Get current Supabase session
      const { data: { session }, error: sessionError } = await supabase.auth.getSession();
      
      if (sessionError || !session) {
        console.log('🔐 [Auth] No active session');
        setAuthState({
          user: null,
          subscription: null,
          workspace: null,
          isLoading: false,
          isAuthenticated: false,
          error: null,
        });
        return;
      }

      // Set user data
      const user: User = {
        userId: session.user.id,
        email: session.user.email!,
        name: session.user.user_metadata?.full_name || session.user.email!.split('@')[0],
        avatar: session.user.user_metadata?.avatar_url,
      };

      setAuthState(prev => ({ ...prev, user, isAuthenticated: true }));

      // Check subscription and workspace status
      await refreshSubscription();

    } catch (error) {
      console.error('🔐 [Auth] Error checking auth status:', error);
      setAuthState(prev => ({
        ...prev,
        user: null,
        subscription: null,
        workspace: null,
        isLoading: false,
        isAuthenticated: false,
        error: error instanceof Error ? error.message : 'Authentication check failed'
      }));
    }
  };

  /**
   * Refresh subscription status - enhanced implementation
   */
  const refreshSubscription = async () => {
    try {
      // Call subscription status endpoint
      const response = await fetch('/api/subscription/status');

      if (response.ok) {
        const data = await response.json();
        
        const subscription: Subscription = {
          hasSubscription: data.subscription?.hasSubscription || false,
          planId: data.subscription?.planId,
          planName: data.subscription?.planName,
          planSlug: data.subscription?.planSlug,
          status: data.subscription?.status,
          expiresAt: data.subscription?.expiresAt,
          canAccessApp: data.canAccessApp || false,
          onboardingCompleted: data.workspace?.onboardingCompleted || false,
          onboardingStep: data.workspace?.onboardingStep || 0,
        };

        const workspace: Workspace = {
          hasWorkspace: data.workspace?.hasWorkspace || false,
          workspaceId: data.workspace?.workspaceId,
          workspaceName: data.workspace?.workspaceName,
          onboardingCompleted: data.workspace?.onboardingCompleted || false,
          onboardingStep: data.workspace?.onboardingStep || 0,
          businessContextUrl: data.workspace?.businessContextUrl,
        };

        setAuthState(prev => ({
          ...prev,
          subscription,
          workspace,
        }));

        console.log('🔐 [Auth] Subscription refreshed:', { subscription, workspace });
      } else {
        console.log('🔐 [Auth] Could not fetch subscription status');
        setAuthState(prev => ({
          ...prev,
          subscription: {
            hasSubscription: false,
            canAccessApp: false,
            onboardingCompleted: false,
            onboardingStep: 0,
          },
          workspace: {
            hasWorkspace: false,
            onboardingCompleted: false,
            onboardingStep: 0,
          },
        }));
      }
    } catch (error) {
      console.error('🔐 [Auth] Error checking subscription status:', error);
      setAuthState(prev => ({
        ...prev,
        subscription: {
          hasSubscription: false,
          canAccessApp: false,
          onboardingCompleted: false,
          onboardingStep: 0,
        },
        workspace: {
          hasWorkspace: false,
          onboardingCompleted: false,
          onboardingStep: 0,
        },
      }));
    }
  };

  /**
   * Login with Google OAuth - enhanced implementation
   */
  const loginWithGoogle = async () => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          },
        },
      });

      if (error) {
        throw error;
      }
      
      // OAuth will redirect, so we don't reset loading state here
      console.log('🔐 [Auth] Google OAuth initiated');
      
    } catch (error) {
      console.error('🔐 [Auth] Google OAuth error:', error);
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Google OAuth failed'
      }));
      throw error;
    }
  };

  /**
   * Login with email/password - enhanced implementation
   */
  const login = async (email: string, password: string) => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true, error: null }));

      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        throw error;
      }

      // Auth state change listener will handle the rest
      console.log('🔐 [Auth] Email login successful');
      
    } catch (error) {
      console.error('🔐 [Auth] Login error:', error);
      setAuthState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed'
      }));
      throw error;
    }
  };

  /**
   * Logout function - enhanced implementation
   */
  const logout = async () => {
    try {
      setAuthState(prev => ({ ...prev, isLoading: true }));

      await supabase.auth.signOut();

      // Clear all state
      setAuthState({
        user: null,
        subscription: null,
        workspace: null,
        isLoading: false,
        isAuthenticated: false,
        error: null,
      });

      // Redirect to login page
      window.location.href = '/login';
      
    } catch (error) {
      console.error('🔐 [Auth] Logout error:', error);
      // Still redirect on error
      window.location.href = '/login';
    }
  };

  // Create context value
  const value: AuthContextType = {
    ...authState,
    login,
    loginWithGoogle,
    logout,
    refreshSubscription,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ============================================================================
// 🔐 USE AUTH HOOK - Enhanced Implementation
// ============================================================================

/**
 * Hook to use auth context - enhanced implementation
 * 
 * @returns Auth context value
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}

// ============================================================================
// 🔐 WITH AUTH HOC - Enhanced Implementation
// ============================================================================

/**
 * Higher-order component for protected routes - enhanced implementation
 * 
 * @param Component - Component to protect
 * @returns Protected component
 */
export function withAuth<T extends object>(Component: React.ComponentType<T>) {
  return function AuthenticatedComponent(props: T) {
    const { isAuthenticated, isLoading, error } = useAuth();

    if (isLoading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--blueprint)] mx-auto"></div>
            <p className="mt-2 text-[var(--ink)]">Loading...</p>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-[var(--ink)] mb-4">Authentication Error</h1>
            <p className="text-[var(--ink)]/60 mb-4">{error}</p>
            <button
              onClick={() => window.location.href = '/login'}
              className="bg-[var(--blueprint)] text-[var(--paper)] px-4 py-2 rounded hover:bg-[var(--blueprint)]/90"
            >
              Go to Login
            </button>
          </div>
        </div>
      );
    }

    if (!isAuthenticated) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-[var(--ink)] mb-4">Authentication Required</h1>
            <p className="text-[var(--ink)]/60 mb-4">Please log in to access this page.</p>
            <button
              onClick={() => window.location.href = '/login'}
              className="bg-[var(--blueprint)] text-[var(--paper)] px-4 py-2 rounded hover:bg-[var(--blueprint)]/90"
            >
              Go to Login
            </button>
          </div>
        </div>
      );
    }

    return <Component {...props} />;
  };
}
