// SECURE Authentication utilities for Raptorflow
// Replaces the insecure bypass implementation with proper Supabase auth

import { createBrowserClient } from '@supabase/ssr';

export interface User {
  id: string;
  email: string;
  fullName?: string;
  subscriptionPlan: 'ascent' | 'glide' | 'soar' | 'free';
  subscriptionStatus: 'active' | 'cancelled' | 'expired' | 'none';
  createdAt: string;
  role?: string;
  workspaceId?: string;
}

export interface Session {
  access_token: string;
  refresh_token?: string;
  user: User;
  expires_at?: string;
}

// Create Supabase client
const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Check if user is authenticated - SECURE IMPLEMENTATION
export async function isAuthenticated(): Promise<boolean> {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();

    if (error) {
      console.error('Auth session error:', error);
      return false;
    }

    return !!session;
  } catch (error) {
    console.error('Auth check error:', error);
    return false;
  }
}

// Get current user
export async function getCurrentUser(): Promise<User | null> {
  try {
    const { data: { user }, error } = await supabase.auth.getUser();

    if (error) {
      console.error('Get user error:', error);
      return null;
    }

    if (!user) {
      return null;
    }

    // Get user profile from database
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single();

    if (profileError) {
      console.error('Get profile error:', profileError);
      // Return basic user info if profile not found
      return {
        id: user.id,
        email: user.email!,
        fullName: user.user_metadata?.full_name || user.email!,
        subscriptionPlan: 'free',
        subscriptionStatus: 'none',
        createdAt: user.created_at,
        role: 'user'
      };
    }

    return {
      id: user.id,
      email: user.email!,
      fullName: profile.full_name || user.user_metadata?.full_name || user.email!,
      subscriptionPlan: profile.subscription_plan || 'free',
      subscriptionStatus: profile.subscription_status || 'none',
      createdAt: profile.created_at || user.created_at,
      role: profile.role || 'user',
      workspaceId: profile.workspace_id
    };
  } catch (error) {
    console.error('Get current user error:', error);
    return null;
  }
}

// Sign in with email and password
export async function signInWithEmail(email: string, password: string): Promise<{ user: User | null; error: string | null }> {
  try {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      return { user: null, error: error.message };
    }

    if (!data.user) {
      return { user: null, error: 'No user returned' };
    }

    const user = await getCurrentUser();
    return { user, error: null };
  } catch (error) {
    return {
      user: null,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}

// Sign in with Google OAuth
export async function signInWithGoogle(): Promise<{ user: User | null; error: string | null }> {
  try {
    const { data, error } = await supabase.auth.signInWithOAuth({
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
      return { user: null, error: error.message };
    }

    // OAuth will redirect, so we don't return user immediately
    return { user: null, error: null };
  } catch (error) {
    return {
      user: null,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}

// Sign up with email and password
export async function signUp(email: string, password: string, fullName?: string): Promise<{ user: User | null; error: string | null }> {
  try {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName || email,
        },
      },
    });

    if (error) {
      return { user: null, error: error.message };
    }

    if (!data.user) {
      return { user: null, error: 'No user returned' };
    }

    // Create user profile
    const { error: profileError } = await supabase
      .from('profiles')
      .insert({
        id: data.user.id,
        email: data.user.email!,
        full_name: fullName || data.user.email!,
        role: 'user',
        subscription_plan: 'free',
        subscription_status: 'none',
        onboarding_status: 'pending',
      });

    if (profileError) {
      console.error('Profile creation error:', profileError);
    }

    const user = await getCurrentUser();
    return { user, error: null };
  } catch (error) {
    return {
      user: null,
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}

// Sign out
export async function signOut(): Promise<{ error: string | null }> {
  try {
    const { error } = await supabase.auth.signOut();

    if (error) {
      return { error: error.message };
    }

    // Clear any local storage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('raptorflow_session');
    }

    return { error: null };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}

// Reset password
export async function resetPassword(email: string): Promise<{ error: string | null }> {
  try {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    });

    if (error) {
      return { error: error.message };
    }

    return { error: null };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}

// Update password
export async function updatePassword(newPassword: string): Promise<{ error: string | null }> {
  try {
    const { error } = await supabase.auth.updateUser({
      password: newPassword,
    });

    if (error) {
      return { error: error.message };
    }

    return { error: null };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}

// Get session
export async function getSession(): Promise<Session | null> {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();

    if (error) {
      console.error('Get session error:', error);
      return null;
    }

    if (!session) {
      return null;
    }

    const user = await getCurrentUser();
    if (!user) {
      return null;
    }

    return {
      access_token: session.access_token,
      refresh_token: session.refresh_token,
      user,
      expires_at: session.expires_at ? new Date(session.expires_at).toISOString() : undefined,
    };
  } catch (error) {
    console.error('Get session error:', error);
    return null;
  }
}

// Subscribe to auth changes
export function onAuthStateChange(callback: (event: string, session: Session | null) => void) {
  return supabase.auth.onAuthStateChange(async (event, session) => {
    if (session) {
      const user = await getCurrentUser();
      callback(event, user ? {
        access_token: session.access_token,
        refresh_token: session.refresh_token,
        user,
        expires_at: session.expires_at ? new Date(session.expires_at * 1000).toISOString() : undefined,
      } : null);
    } else {
      callback(event, null);
    }
  });
}

// Export Supabase client for direct use
export { supabase };
