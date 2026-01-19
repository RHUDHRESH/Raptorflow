"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import { User, Session, AuthChangeEvent } from "@supabase/supabase-js";
import { useRouter } from "next/navigation";

// ============================================================================
// 🔐 AUTH TYPES (Strict Supabase)
// ============================================================================

interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  role?: string;
  workspace_id?: string;
  plan_tier?: string;
  created_at?: string;
}

interface AuthContextType {
  user: User | null;
  profile: UserProfile | null;
  session: Session | null;
  isLoading: boolean;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================================================
// 🔐 AUTH PROVIDER
// ============================================================================
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // 1. Initial Session Check
    const initializeAuth = async () => {
      try {
        const { data: { session: initialSession } } = await supabase.auth.getSession();

        if (initialSession) {
          setSession(initialSession);
          setUser(initialSession.user);
          await fetchProfile(initialSession.user.id);
        }
      } catch (error) {
        console.error("🔐 [Auth] Init error:", error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();

    // 2. Real-time Auth Listener
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event: AuthChangeEvent, currentSession: Session | null) => {
        console.log(`🔐 [Auth] Event: ${event}`);

        setSession(currentSession);
        setUser(currentSession?.user ?? null);

        if (currentSession?.user) {
          await fetchProfile(currentSession.user.id);
        } else {
          setProfile(null);
        }

        setIsLoading(false);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Fetch User Profile from 'public.profiles'
  const fetchProfile = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', userId)
        .single();

      if (error) {
        // If no profile found, it might be creating via trigger... warn but don't crash
        console.warn("🔐 [Auth] Profile fetch warning:", error.message);
      }

      if (data) {
        setProfile(data as UserProfile);
      }
    } catch (err) {
      console.error("🔐 [Auth] Profile fetch error:", err);
    }
  };

  /**
   * Login with Google - Strict Supabase OAuth
   */
  const loginWithGoogle = async () => {
    try {
      setIsLoading(true);
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: "offline",
            prompt: "consent",
          },
        },
      });
      if (error) throw error;
    } catch (error) {
      console.error("🔐 [Auth] Google Login Error:", error);
      setIsLoading(false);
    }
  };

  /**
   * Logout
   */
  const logout = async () => {
    try {
      await supabase.auth.signOut();
      setUser(null);
      setSession(null);
      setProfile(null);
      router.push("/login");
    } catch (error) {
      console.error("🔐 [Auth] Logout Error:", error);
    }
  };

  const value: AuthContextType = {
    user,
    profile,
    session,
    isLoading,
    loginWithGoogle,
    logout,
    isAuthenticated: !!user,
    refreshProfile: async () => {
      if (user) await fetchProfile(user.id);
    },
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ============================================================================
// 🔐 HOOK
// ============================================================================
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
