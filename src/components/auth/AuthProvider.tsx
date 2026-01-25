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
  login: (email: string, password: string) => Promise<any>;
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

    // 3. Token Refresh Interval - Check every 4 minutes
    const tokenRefreshInterval = setInterval(async () => {
      try {
        const { data: { session: currentSession } } = await supabase.auth.getSession();

        if (currentSession) {
          const expiresAt = currentSession.expires_at;
          if (expiresAt) {
            const expiresAtTimestamp = expiresAt * 1000;
            const now = Date.now();
            const timeUntilExpiry = expiresAtTimestamp - now;

            // Refresh if less than 5 minutes until expiry
            if (timeUntilExpiry < 5 * 60 * 1000) {
              console.log("🔐 [Auth] Token refresh triggered");
              await supabase.auth.refreshSession();
            }
          }
        }
      } catch (error) {
        console.error("🔐 [Auth] Token refresh error:", error);
      }
    }, 4 * 60 * 1000); // Check every 4 minutes

    return () => {
      subscription.unsubscribe();
      clearInterval(tokenRefreshInterval);
    };
  }, []);

  // Fetch User Profile from 'public.users'
  const fetchProfile = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('auth_user_id', userId)
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
   * Login with Email and Password
   */
  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        // Distinguish different error types
        if (error.message.includes("Invalid login credentials")) {
          throw new Error("Invalid email or password. Please try again.");
        } else if (error.message.includes("Email not confirmed")) {
          throw new Error("Please verify your email address before logging in.");
        } else if (error.message.includes("User not found")) {
          throw new Error("No account found with this email address.");
        } else if (error.message.includes("Too many requests")) {
          throw new Error("Too many login attempts. Please try again later.");
        } else {
          throw new Error(error.message || "Login failed. Please try again.");
        }
      }

      // Session will be set automatically by onAuthStateChange
      return data;
    } catch (error) {
      setIsLoading(false);
      throw error;
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
      throw error;
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
      throw error;
    }
  };

  const value: AuthContextType = {
    user,
    profile,
    session,
    isLoading,
    login,
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
