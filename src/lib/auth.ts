/**
 * @deprecated This file is deprecated. Use '@/lib/auth-service' instead.
 * 
 * This file is kept for backward compatibility but all new code should
 * import from auth-service.ts which is the single source of truth.
 * 
 * Migration guide:
 * - import { clientAuth } from '@/lib/auth-service'
 * - Use clientAuth.getSession(), clientAuth.getCurrentUser(), etc.
 */

import { createClient } from '@/lib/supabase/client';

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

// Use shared Supabase client singleton instead of creating a new instance
const getSupabase = () => {
  if (typeof window === 'undefined') {
    console.warn('auth.ts should only be used on client-side. Use auth-service.ts for server-side auth.');
    return null;
  }
  return createClient();
};

// Lazy initialization to avoid issues during SSR
let _supabase: ReturnType<typeof createClient> | null = null;
const supabase = new Proxy({} as ReturnType<typeof createClient>, {
  get(_, prop) {
    if (!_supabase) {
      _supabase = getSupabase();
    }
    if (!_supabase) {
      throw new Error('Supabase client not available');
    }
    return (_supabase as any)[prop];
  }
});

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

    const { data: profile } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .maybeSingle();

    if (profile) {
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
    }

    const { data: userProfile } = await supabase
      .from('user_profiles')
      .select('*')
      .eq('id', user.id)
      .maybeSingle();

    if (userProfile) {
      return {
        id: user.id,
        email: user.email!,
        fullName: userProfile.full_name || user.user_metadata?.full_name || user.email!,
        subscriptionPlan: userProfile.subscription_plan || 'free',
        subscriptionStatus: userProfile.subscription_status || 'none',
        createdAt: userProfile.created_at || user.created_at,
        role: 'user',
      };
    }

    const { data: usersRecord } = await supabase
      .from('users')
      .select('id, auth_user_id, email, full_name, role, subscription_plan, subscription_tier, subscription_status, workspace_id, created_at')
      .eq('auth_user_id', user.id)
      .maybeSingle();

    if (usersRecord) {
      return {
        id: usersRecord.id || user.id,
        email: usersRecord.email || user.email!,
        fullName: usersRecord.full_name || user.user_metadata?.full_name || user.email!,
        subscriptionPlan: usersRecord.subscription_plan || usersRecord.subscription_tier || 'free',
        subscriptionStatus: usersRecord.subscription_status || 'none',
        createdAt: usersRecord.created_at || user.created_at,
        role: usersRecord.role || 'user',
        workspaceId: usersRecord.workspace_id
      };
    }

    return {
      id: user.id,
      email: user.email!,
      fullName: user.user_metadata?.full_name || user.email!,
      subscriptionPlan: 'free',
      subscriptionStatus: 'none',
      createdAt: user.created_at,
      role: 'user'
    };
  } catch (error) {
    console.error('Get current user error:', error);
    return null;
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

    // expires_at from Supabase is a unix timestamp in seconds
    const expiresAtMs = session.expires_at 
      ? (typeof session.expires_at === 'number' ? session.expires_at * 1000 : new Date(session.expires_at).getTime())
      : undefined;

    return {
      access_token: session.access_token,
      refresh_token: session.refresh_token,
      user,
      expires_at: expiresAtMs ? new Date(expiresAtMs).toISOString() : undefined,
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
      // expires_at from Supabase is a unix timestamp in seconds
      const expiresAtMs = session.expires_at 
        ? (typeof session.expires_at === 'number' ? session.expires_at * 1000 : new Date(session.expires_at).getTime())
        : undefined;
      callback(event, user ? {
        access_token: session.access_token,
        refresh_token: session.refresh_token,
        user,
        expires_at: expiresAtMs ? new Date(expiresAtMs).toISOString() : undefined,
      } : null);
    } else {
      callback(event, null);
    }
  });
}

// Export Supabase client for direct use
export { supabase };
