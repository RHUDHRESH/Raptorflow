"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { User, Session, AuthError, PostgrestError } from '@supabase/supabase-js';
import { supabase } from '@/lib/supabaseClient';
import { useRouter } from 'next/navigation';

interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  subscription_plan?: 'soar' | 'glide' | 'ascent' | null;
  subscription_status?: 'active' | 'cancelled' | 'expired' | null;
  subscription_expires_at?: string | null;
}

interface AuthContextType {
  user: User | null;
  profile: UserProfile | null;
  session: Session | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signInWithEmail: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  signUpWithEmail: (email: string, password: string, fullName: string) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const isMissingTableError = (error?: Pick<PostgrestError, 'code' | 'message'> | null) => {
    if (!error) return false;
    return (
      error.code === 'PGRST116' || // Supabase meta code for missing relation
      error.code === '42P01' || // Postgres undefined table
      /does not exist|relation .*user_profiles/i.test(error.message ?? '')
    );
  };

  // Fetch user profile from database
  const fetchProfile = useCallback(async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('user_profiles')
        .select('*')
        .eq('id', userId)
        .single();

      if (error && !isMissingTableError(error)) {
        // Log error in development only if needed, or handle silently
        if (error && !isMissingTableError(error)) {
          // console.error('Error fetching profile:', error);
        }
      }

      if (data) {
        setProfile(data);
      } else if (isMissingTableError(error)) {
        // Create a basic profile from user metadata if table doesn't exist
        // User profiles table not found, using basic profile
        // Get user data to fill email
        const { data: userData } = await supabase.auth.getUser();
        const basicProfile: UserProfile = {
          id: userId,
          email: userData.user?.email || '',
          subscription_plan: 'soar',
          subscription_status: 'active'
        };
        setProfile(basicProfile);
      }
    } catch (profileError) {
      // console.error('Error fetching profile:', profileError);
      // Set basic profile as fallback
      const basicProfile: UserProfile = {
        id: userId,
        email: '',
        subscription_plan: 'soar',
        subscription_status: 'active'
      };
      setProfile(basicProfile);
    }
  }, []);

  // Initialize auth state
  useEffect(() => {
    supabase.auth.getSession().then(({ data }: { data: { session: Session | null } }) => {
      const currentSession = data.session;
      setSession(currentSession);
      setUser(currentSession?.user ?? null);
      if (currentSession?.user) {
        fetchProfile(currentSession.user.id);
      }
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session: Session | null) => {
      setSession(session);
      setUser(session?.user ?? null);

      if (session?.user) {
        await fetchProfile(session.user.id);
      } else {
        setProfile(null);
      }

      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, [fetchProfile]);

  // Sign in with Google
  const signInWithGoogle = async () => {
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
      // console.error('Error signing in with Google:', error);
    }
  };

  // Sign in with email
  const signInWithEmail = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    return { error };
  };

  // Sign up with email
  const signUpWithEmail = async (email: string, password: string, fullName: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
        },
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    // If signup successful and user is created (not requiring confirmation)
    if (data.user && !error) {
      // Profile will be created automatically by the trigger
      try {
        await fetchProfile(data.user.id);
      } catch (profileFetchError) {
        // Ignore profile fetch errors (e.g., table missing) to avoid blocking auth
        // Ignore profile fetch errors (e.g., table missing) to avoid blocking auth
      }
    }

    return { error };
  };

  // Sign out
  const signOut = async () => {
    await supabase.auth.signOut();
    router.push('/');
  };

  // Refresh profile
  const refreshProfile = async () => {
    if (user) {
      await fetchProfile(user.id);
    }
  };

  const value: AuthContextType = {
    user,
    profile,
    session,
    loading,
    signInWithGoogle,
    signInWithEmail,
    signUpWithEmail,
    signOut,
    refreshProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
