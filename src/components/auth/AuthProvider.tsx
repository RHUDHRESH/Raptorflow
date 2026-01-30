"use client";

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from "react";
import { clientAuth, type AuthUser } from "@/lib/auth-service";
import { useRouter, usePathname } from "next/navigation";

// ============================================================================
// 🔐 AUTH TYPES (Using Consolidated Auth Service)
// ============================================================================

type ProfileStatus = {
  workspaceId: string | null;
  subscriptionPlan: string | null;
  subscriptionStatus: string | null;
  needsPayment: boolean;
  profileExists: boolean;
  workspaceExists: boolean;
  isReady: boolean;
  error?: string;
};

type PaymentState = {
  isProcessingPayment: boolean;
  currentPaymentId: string | null;
  paymentError: string | null;
  paymentStatus: 'idle' | 'initiating' | 'pending' | 'completed' | 'failed';
};

interface AuthContextType {
  user: AuthUser | null;
  session: any; // Session type from Supabase
  isLoading: boolean;
  isAuthenticated: boolean;
  profileStatus: ProfileStatus;
  isCheckingProfile: boolean;
  paymentState: PaymentState;
  refreshProfileStatus: () => Promise<void>;
  login: (email: string, password: string) => Promise<any>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  initiatePayment: (plan: string) => Promise<{ success: boolean; paymentUrl?: string; error?: string }>;
  checkPaymentStatus: (merchantOrderId: string) => Promise<{ success: boolean; status?: string; error?: string }>;
  clearPaymentError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================================================
// 🔐 AUTH PROVIDER (Consolidated Implementation)
// ============================================================================
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [session, setSession] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCheckingProfile, setIsCheckingProfile] = useState(false);
  const [profileStatus, setProfileStatus] = useState<ProfileStatus>({
    workspaceId: null,
    subscriptionPlan: null,
    subscriptionStatus: null,
    needsPayment: false,
    profileExists: false,
    workspaceExists: false,
    isReady: false,
  });
  const [paymentState, setPaymentState] = useState<PaymentState>({
    isProcessingPayment: false,
    currentPaymentId: null,
    paymentError: null,
    paymentStatus: 'idle',
  });

  const router = useRouter();
  const pathname = usePathname();

  // Refs for debouncing and caching
  const profileCheckTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastProfileCheckRef = useRef<number>(0);
  const profileCacheRef = useRef<ProfileStatus | null>(null);
  const redirectStateRef = useRef<Set<string>>(new Set());

  // Cache duration: 30 seconds
  const CACHE_DURATION = 30000;
  // Debounce delay: 500ms
  const DEBOUNCE_DELAY = 500;

  useEffect(() => {
    // Initialize auth state
    const initializeAuth = async () => {
      try {
        const currentUser = await clientAuth.getCurrentUser();
        const currentSession = await clientAuth.getSession();

        setUser(currentUser);
        setSession(currentSession);
      } catch (error) {
        console.error("🔐 [Auth] Init error:", error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();

    // Set up session listener
    const supabaseClient = clientAuth.getSupabaseClient();
    const { data: { subscription } } = supabaseClient.auth.onAuthStateChange(
      async (event, currentSession) => {
        console.log(`🔐 [Auth] Event: ${event}`);

        if (currentSession?.user) {
          const currentUser = await clientAuth.getCurrentUser();
          setUser(currentUser);
          setSession(currentSession);
        } else {
          setUser(null);
          setSession(null);
          setProfileStatus({
            workspaceId: null,
            subscriptionPlan: null,
            subscriptionStatus: null,
            needsPayment: false,
            profileExists: false,
            workspaceExists: false,
            isReady: false,
          });
        }

        setIsLoading(false);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const runProfileChecks = useCallback(async (forceRefresh: boolean = false) => {
    if (!user) {
      setProfileStatus((prev) => ({
        ...prev,
        workspaceId: null,
        subscriptionPlan: null,
        subscriptionStatus: null,
        needsPayment: false,
        profileExists: false,
        workspaceExists: false,
        isReady: false,
        error: undefined,
      }));
      profileCacheRef.current = null;
      return;
    }

    // Check cache first (unless force refresh)
    const now = Date.now();
    if (!forceRefresh && profileCacheRef.current && (now - lastProfileCheckRef.current) < CACHE_DURATION) {
      setProfileStatus(profileCacheRef.current);
      return;
    }

    // Clear existing timeout
    if (profileCheckTimeoutRef.current) {
      clearTimeout(profileCheckTimeoutRef.current);
    }

    // Optimized profile verification with parallel execution and performance metrics
    profileCheckTimeoutRef.current = setTimeout(async () => {
      const startTime = performance.now();
      setIsCheckingProfile(true);
      try {
        // Parallel execution: ensure profile and verify profile simultaneously
        const [ensureResponse, verifyResponse] = await Promise.all([
          fetch('/api/proxy/v1/auth/ensure-profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
          }),
          fetch('/api/proxy/v1/auth/verify-profile', {
            method: 'GET',
            credentials: 'include',
            cache: 'no-store',
          })
        ]);

        // Handle ensure profile response (fire-and-forget optimization)
        if (!ensureResponse.ok) {
          console.warn('Profile ensure failed:', ensureResponse.status);
        }

        // Process verification response
        if (!verifyResponse.ok) {
          const errorData = await verifyResponse.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Failed to verify profile');
        }

        const verifyData = await verifyResponse.json();
        const hasActiveSubscription = verifyData.subscription_status === 'active';
        const isReady = Boolean(
          verifyData.profile_exists &&
          verifyData.workspace_exists &&
          hasActiveSubscription &&
          !verifyData.needs_payment
        );

        const newProfileStatus: ProfileStatus = {
          workspaceId: verifyData.workspace_id || null,
          subscriptionPlan: verifyData.subscription_plan || null,
          subscriptionStatus: verifyData.subscription_status || null,
          needsPayment: Boolean(verifyData.needs_payment),
          profileExists: Boolean(verifyData.profile_exists),
          workspaceExists: Boolean(verifyData.workspace_exists),
          isReady,
          error: verifyData.error,
        };

        // Update cache and state
        profileCacheRef.current = newProfileStatus;
        lastProfileCheckRef.current = now;
        setProfileStatus(newProfileStatus);

        // Performance metrics tracking
        const endTime = performance.now();
        const verificationTime = endTime - startTime;

        // Log performance metrics for monitoring
        if (verificationTime > 1000) {
          console.warn(`Profile verification took ${verificationTime.toFixed(2)}ms - above 1s SLA`);
        } else {
          console.log(`Profile verification completed in ${verificationTime.toFixed(2)}ms`);
        }

        // Optimistic caching with preloaded workspace data
        if (verifyData.workspace_id && verifyData.profile_exists) {
          // Preload workspace data for faster subsequent operations
          fetch('/api/proxy/v1/auth/me/workspace', {
            credentials: 'include',
            cache: 'force-cache',
          }).catch(() => {
            // Ignore preloading errors - it's just an optimization
          });
        }

        // Smart redirects with state tracking to prevent loops
        const redirectKey = `${verifyData.profile_exists}-${verifyData.workspace_exists}-${verifyData.needs_payment}-${hasActiveSubscription}`;

        if (!verifyData.workspace_exists && !redirectStateRef.current.has('no-workspace')) {
          redirectStateRef.current.add('no-workspace');
          router.replace(hasActiveSubscription ? '/onboarding/start' : '/onboarding/plans');
        } else if ((verifyData.needs_payment || !hasActiveSubscription) && !redirectStateRef.current.has('needs-payment')) {
          redirectStateRef.current.add('needs-payment');
          router.replace('/onboarding/plans');
        } else if (isReady && pathname?.startsWith('/onboarding/plans') && !redirectStateRef.current.has('ready')) {
          redirectStateRef.current.add('ready');
          router.replace('/dashboard');
        } else if (isReady && verifyData.workspace_exists && !verifyData.needs_payment) {
          // Clear redirect states when profile is ready
          redirectStateRef.current.clear();
        }
      } catch (error) {
        console.error('🔐 [Auth] Profile verification failed:', error);
        setProfileStatus(prev => ({
          ...prev,
          isReady: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        }));
        profileCacheRef.current = null;
      } finally {
        setIsCheckingProfile(false);
      }
    }, DEBOUNCE_DELAY);
  }, [user, router, pathname]);

  useEffect(() => {
    if (user) {
      runProfileChecks();
    }
  }, [user, runProfileChecks]);

  useEffect(() => {
    if (user) {
      runProfileChecks();
    }
  }, [pathname, user, runProfileChecks]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (profileCheckTimeoutRef.current) {
        clearTimeout(profileCheckTimeoutRef.current);
      }
    };
  }, []);

  /**
   * Login with Email and Password
   */
  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const result = await clientAuth.signIn({ email, password });

      if (!result.success) {
        throw new Error(result.error || 'Login failed');
      }

      // Force refresh profile check after login
      await runProfileChecks(true);
      return result.data;
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  /**
   * Login with Google OAuth
   */
  const loginWithGoogle = async () => {
    try {
      setIsLoading(true);
      const result = await clientAuth.signInWithOAuth('google');

      if (!result.success) {
        throw new Error(result.error || 'Google login failed');
      }
      // OAuth will redirect, so we don't set loading to false here
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
      await clientAuth.signOut();
      setUser(null);
      setSession(null);
      setProfileStatus({
        workspaceId: null,
        subscriptionPlan: null,
        subscriptionStatus: null,
        needsPayment: false,
        profileExists: false,
        workspaceExists: false,
        isReady: false,
      });
      // Clear cache and redirect state on logout
      profileCacheRef.current = null;
      redirectStateRef.current.clear();
      router.push("/signin");
    } catch (error) {
      console.error("🔐 [Auth] Logout Error:", error);
      throw error;
    }
  };

  /**
   * Refresh user data
   */
  const refreshUser = async () => {
    try {
      const currentUser = await clientAuth.getCurrentUser();
      setUser(currentUser);
      // Force refresh profile check
      await runProfileChecks(true);
    } catch (error) {
      console.error("🔐 [Auth] Refresh user error:", error);
    }
  };

  /**
   * Initiate payment for a plan
   */
  const initiatePayment = async (plan: string) => {
    try {
      setPaymentState(prev => ({
        ...prev,
        isProcessingPayment: true,
        paymentStatus: 'initiating',
        paymentError: null,
      }));

      const response = await fetch('/api/proxy/payments/v2/initiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan,
          redirect_url: `${window.location.origin}/onboarding/plans/callback`,
          webhook_url: `${window.location.origin}/api/webhooks/phonepe`
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to initiate payment');
      }

      if (data.success && data.payment_url) {
        setPaymentState(prev => ({
          ...prev,
          currentPaymentId: data.merchant_order_id,
          paymentStatus: 'pending',
        }));

        return { success: true, paymentUrl: data.payment_url };
      } else {
        throw new Error(data.error || 'Payment initiation failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Payment initiation failed';
      setPaymentState(prev => ({
        ...prev,
        isProcessingPayment: false,
        paymentStatus: 'failed',
        paymentError: errorMessage,
      }));
      return { success: false, error: errorMessage };
    }
  };

  /**
   * Check payment status
   */
  const checkPaymentStatus = async (merchantOrderId: string) => {
    try {
      const response = await fetch(`/api/proxy/payments/v2/status/${merchantOrderId}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to check payment status');
      }

      if (data.success && data.status === 'completed') {
        setPaymentState(prev => ({
          ...prev,
          isProcessingPayment: false,
          paymentStatus: 'completed',
          paymentError: null,
        }));

        // Refresh profile status to update subscription info
        await runProfileChecks(true);

        return { success: true, status: 'completed' };
      } else if (data.success && data.status === 'failed') {
        setPaymentState(prev => ({
          ...prev,
          isProcessingPayment: false,
          paymentStatus: 'failed',
          paymentError: 'Payment failed',
        }));
        return { success: true, status: 'failed' };
      } else {
        return { success: true, status: 'pending' };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Status check failed';
      setPaymentState(prev => ({
        ...prev,
        paymentError: errorMessage,
      }));
      return { success: false, error: errorMessage };
    }
  };

  /**
   * Clear payment error
   */
  const clearPaymentError = () => {
    setPaymentState(prev => ({
      ...prev,
      paymentError: null,
    }));
  };

  const value: AuthContextType = {
    user,
    session,
    isLoading,
    isAuthenticated: !!user,
    profileStatus,
    isCheckingProfile,
    paymentState,
    refreshProfileStatus: runProfileChecks,
    login,
    loginWithGoogle,
    logout,
    refreshUser,
    initiatePayment,
    checkPaymentStatus,
    clearPaymentError,
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
