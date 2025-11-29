import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User, Session } from '@supabase/supabase-js';
import { authService } from '../services/authService';
import { supabase, isSupabaseConfigured } from '../lib/supabase';
import { sanitizeInput, sanitizeEmail } from '../utils/sanitize';
import { validateEmail, validatePassword } from '../utils/validation';

/**
 * Auth Status Type
 * 
 * Represents the current authentication state of the application.
 */
export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

/**
 * Subscription Type
 * 
 * Represents a user's subscription information.
 */
export interface Subscription {
    plan: string;
    status: string;
    billing_period?: string;
    current_period_start?: string;
    current_period_end?: string;
}

/**
 * Auth Context Value
 * 
 * The shape of the context value provided by AuthProvider.
 */
export interface AuthContextValue {
    // State
    status: AuthStatus;
    user: User | null;
    session: Session | null;
    subscription: Subscription | null;
    onboardingCompleted: boolean;
    loading: boolean;
    error: string | null;
    isAuthenticated: boolean;

    // Auth methods
    login: (email: string, password: string) => Promise<{ success: boolean; error?: string; user?: any }>;
    loginWithGoogle: () => Promise<{ success: boolean; error?: string }>;
    register: (name: string, email: string, password: string, confirmPassword: string) => Promise<{ success: boolean; error?: string; user?: any }>;
    logout: () => Promise<void>;
    updateProfile: (updates: { name?: string; email?: string }) => Promise<{ success: boolean; error?: string; user?: any }>;
    markOnboardingComplete: () => Promise<{ success: boolean; error?: string }>;
    skipLoginDev: () => { success: boolean; error?: string; user?: any };
}

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * useAuth Hook
 * 
 * Custom hook to access auth context. Must be used within an AuthProvider.
 * 
 * @throws Error if used outside of AuthProvider
 */
export const useAuth = (): AuthContextValue => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: React.ReactNode;
}

/**
 * Auth Provider
 * 
 * Provides authentication state and methods to the entire application.
 * Handles session initialization, auth state changes, and user data management.
 */
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [status, setStatus] = useState<AuthStatus>('loading');
    const [user, setUser] = useState<User | null>(null);
    const [session, setSession] = useState<Session | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [subscription, setSubscription] = useState<Subscription | null>(null);
    const [onboardingCompleted, setOnboardingCompleted] = useState(false);

    // Initialize auth state on mount
    useEffect(() => {
        let mounted = true;

        // SQL Snippet to reset onboarding for a user:
        // UPDATE user_profiles
        // SET onboarding_completed = false,
        //     onboarding_skipped = false
        // WHERE id = 'USER_UUID_HERE';

        // Check for dev mode persistence
        const devMode = localStorage.getItem('rf_dev_mode');
        if (devMode === 'true' && (import.meta as any).env?.DEV) {
            console.log('[AuthProvider] Restoring dev session');
            const devUser: any = {
                id: 'dev-user-123',
                email: 'dev@raptorflow.local',
                user_metadata: {
                    full_name: 'Dev User',
                },
            };

            setUser(devUser);
            setStatus('authenticated');
            setSubscription({
                plan: 'soar',
                status: 'active',
                billing_period: 'monthly',
                current_period_start: new Date().toISOString(),
                current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
            });
            setOnboardingCompleted(true);
            setLoading(false);
            return;
        }

        if (!isSupabaseConfigured() || !supabase) {
            console.warn('[AuthProvider] Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
            if (mounted) {
                setStatus('unauthenticated');
                setLoading(false);
            }
            return;
        }

        // Check for OAuth callback in URL hash
        const handleOAuthCallback = async () => {
            try {
                const { session: currentSession, error: sessionError } = await authService.getSession();

                if (!mounted) return;

                if (sessionError) {
                    console.error('[AuthProvider] Error handling OAuth callback:', sessionError);
                    setStatus('unauthenticated');
                    setLoading(false);
                    return;
                }

                if (currentSession?.user) {
                    setUser(currentSession.user);
                    setSession(currentSession);
                    setStatus('authenticated');

                    // Fetch additional user data
                    await fetchUserStatus(currentSession.user.id);

                    // Clear OAuth callback from URL
                    if (window.location.hash) {
                        window.history.replaceState(null, '', window.location.pathname);
                    }
                } else {
                    setStatus('unauthenticated');
                }
            } catch (err) {
                console.error('[AuthProvider] Error handling OAuth callback:', err);
                if (mounted) setStatus('unauthenticated');
            } finally {
                if (mounted) setLoading(false);
            }
        };

        // Check current auth state
        const checkAuth = async () => {
            try {
                const { session: currentSession, error: sessionError } = await authService.getSession();

                if (!mounted) return;

                if (sessionError) {
                    console.error('[AuthProvider] Error checking auth:', sessionError);
                    setUser(null);
                    setSession(null);
                    setStatus('unauthenticated');
                    setLoading(false);
                    return;
                }

                if (currentSession?.user) {
                    setUser(currentSession.user);
                    setSession(currentSession);
                    setStatus('authenticated');

                    // Fetch additional user data
                    await fetchUserStatus(currentSession.user.id);
                } else {
                    setUser(null);
                    setSession(null);
                    setStatus('unauthenticated');
                }
            } catch (err) {
                console.error('[AuthProvider] Error checking auth:', err);
                if (mounted) {
                    setUser(null);
                    setSession(null);
                    setStatus('unauthenticated');
                }
            } finally {
                if (mounted) setLoading(false);
            }
        };

        // Check for OAuth callback first
        if (window.location.hash.includes('access_token') || window.location.hash.includes('error')) {
            handleOAuthCallback();
        } else {
            // Normal session check
            checkAuth();
        }

        // Subscribe to auth state changes
        const subscription = authService.onAuthStateChange(async (event, currentSession) => {
            console.log('[AuthProvider] Auth state changed:', event);
            if (!mounted) return;

            if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
                if (currentSession?.user) {
                    setUser(currentSession.user);
                    setSession(currentSession);
                    setStatus('authenticated');

                    // Fetch additional user data
                    await fetchUserStatus(currentSession.user.id);

                    // Clear OAuth callback from URL if present
                    if (window.location.hash) {
                        window.history.replaceState(null, '', window.location.pathname);
                    }
                }
            } else if (event === 'SIGNED_OUT') {
                setUser(null);
                setSession(null);
                setSubscription(null);
                setOnboardingCompleted(false);
                setStatus('unauthenticated');
            }

            setLoading(false);
        });

        // Cleanup subscription on unmount
        return () => {
            mounted = false;
            subscription.unsubscribe();
        };
    }, []);

    /**
     * Fetch user subscription and onboarding status
     */
    const fetchUserStatus = async (userId: string) => {
        if (!supabase) return;

        try {
            // Fetch user profile for onboarding status
            const { data: profile, error: profileError } = await supabase
                .from('user_profiles')
                .select('onboarding_completed, onboarding_skipped')
                .eq('id', userId)
                .single();

            console.log('[AuthContext] Fetched user profile:', { userId, profile, error: profileError });

            if (!profileError && profile) {
                const isCompleted = !!(profile.onboarding_completed || profile.onboarding_skipped);
                console.log('[AuthContext] Setting onboardingCompleted:', isCompleted);
                setOnboardingCompleted(isCompleted);
            } else {
                // If no profile found or error, assume false (safe default)
                console.log('[AuthContext] No profile or error, defaulting onboardingCompleted to false');
                setOnboardingCompleted(false);
            }

            // Fetch subscription
            const { data: subscriptionData, error: subError } = await supabase
                .from('subscriptions')
                .select('*')
                .eq('user_id', userId)
                .in('status', ['active', 'trialing'])
                .order('created_at', { ascending: false })
                .limit(1)
                .single();

            if (!subError && subscriptionData) {
                setSubscription(subscriptionData);
            } else {
                // If no subscription found, user might be on free plan
                setSubscription({ plan: 'free', status: 'active' });
            }
        } catch (err) {
            console.error('[AuthProvider] Error fetching user status:', err);
        }
    };

    /**
     * Login with email and password
     */
    const login = async (email: string, password: string) => {
        try {
            setError(null);
            setLoading(true);

            if (!isSupabaseConfigured() || !supabase) {
                throw new Error('Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
            }

            // Validate inputs
            const emailValidation = validateEmail(email) as { isValid: boolean; error: string | null };
            if (!emailValidation.isValid) {
                throw new Error(emailValidation.error || 'Invalid email');
            }

            const passwordValidation = validatePassword(password) as { isValid: boolean; error: string | null };
            if (!passwordValidation.isValid) {
                throw new Error(passwordValidation.error || 'Invalid password');
            }

            // Sanitize inputs
            const sanitizedEmail = sanitizeEmail(email) || email;

            // Sign in using auth service
            const { user: authUser, session: authSession, error: signInError } = await authService.signInWithEmail({
                email: sanitizedEmail,
                password: password,
            });

            if (signInError) {
                throw signInError;
            }

            if (authUser && authSession) {
                setUser(authUser);
                setSession(authSession);
                setStatus('authenticated');

                // Fetch subscription and onboarding status
                await fetchUserStatus(authUser.id);

                setLoading(false);
                return { success: true, user: authUser };
            }

            throw new Error('Login failed');
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Login failed';
            setError(errorMessage);
            setLoading(false);
            return { success: false, error: errorMessage };
        }
    };

    /**
     * Login with Google OAuth
     */
    const loginWithGoogle = async () => {
        try {
            setError(null);
            setLoading(true);

            if (!isSupabaseConfigured() || !supabase) {
                throw new Error('Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
            }

            // Redirect to Google OAuth using auth service
            // Redirect back to /login page so we can handle post-login routing logic
            const { error: oauthError } = await authService.signInWithOAuth('google', `${window.location.origin}/login`);

            if (oauthError) {
                throw oauthError;
            }

            // The redirect will happen automatically
            // The auth state change listener will handle setting the user
            return { success: true };
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to sign in with Google';
            setError(errorMessage);
            setLoading(false);
            return { success: false, error: errorMessage };
        }
    };

    /**
     * Register new user
     */
    const register = async (name: string, email: string, password: string, confirmPassword: string) => {
        try {
            setError(null);
            setLoading(true);

            if (!isSupabaseConfigured() || !supabase) {
                throw new Error('Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
            }

            // Validate inputs
            const emailValidation = validateEmail(email) as { isValid: boolean; error: string | null };
            if (!emailValidation.isValid) {
                throw new Error(emailValidation.error || 'Invalid email');
            }

            const passwordValidation = validatePassword(password) as { isValid: boolean; error: string | null };
            if (!passwordValidation.isValid) {
                throw new Error(passwordValidation.error || 'Invalid password');
            }

            if (password !== confirmPassword) {
                throw new Error('Passwords do not match');
            }

            // Sanitize inputs
            const sanitizedName = sanitizeInput(name.trim()) || name.trim();
            const sanitizedEmail = sanitizeEmail(email) || email;

            if (!sanitizedName || sanitizedName.length < 2) {
                throw new Error('Name must be at least 2 characters');
            }

            // Sign up using auth service
            const { user: authUser, session: authSession, error: signUpError } = await authService.signUpWithEmail({
                email: sanitizedEmail,
                password: password,
                metadata: {
                    full_name: sanitizedName,
                },
            });

            if (signUpError) {
                throw signUpError;
            }

            if (authUser) {
                setUser(authUser);
                setSession(authSession);
                setStatus('authenticated');

                // Fetch subscription and onboarding status
                await fetchUserStatus(authUser.id);

                setLoading(false);
                return { success: true, user: authUser };
            }

            throw new Error('Registration failed');
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Registration failed';
            setError(errorMessage);
            setLoading(false);
            return { success: false, error: errorMessage };
        }
    };

    /**
     * Logout current user
     */
    const logout = async () => {
        try {
            localStorage.removeItem('rf_dev_mode');
            // Sign out using auth service
            await authService.signOut();

            // Clear local state
            setUser(null);
            setSession(null);
            setSubscription(null);
            setOnboardingCompleted(false);
            setStatus('unauthenticated');
            setError(null);
        } catch (err) {
            console.error('[AuthProvider] Error during logout:', err);
        }
    };

    /**
     * Update user profile
     */
    const updateProfile = async (updates: { name?: string; email?: string }) => {
        try {
            setError(null);

            if (!isSupabaseConfigured() || !supabase) {
                throw new Error('Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.');
            }

            const sanitizedUpdates: any = {};

            if (updates.name) {
                sanitizedUpdates.full_name = sanitizeInput(updates.name.trim());
            }

            if (updates.email) {
                const emailValidation = validateEmail(updates.email) as { isValid: boolean; error: string | null };
                if (!emailValidation.isValid) {
                    throw new Error(emailValidation.error || 'Invalid email');
                }
                sanitizedUpdates.email = sanitizeEmail(updates.email) || updates.email;
            }

            // Update user metadata in Supabase
            const { data, error: updateError } = await supabase.auth.updateUser({
                data: sanitizedUpdates,
            });

            if (updateError) {
                throw new Error(updateError.message || 'Failed to update profile');
            }

            if (data?.user) {
                setUser(data.user);
                return { success: true, user: data.user };
            }

            throw new Error('Profile update failed');
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to update profile';
            setError(errorMessage);
            return { success: false, error: errorMessage };
        }
    };

    /**
     * Mark onboarding as complete
     */
    const markOnboardingComplete = async () => {
        setOnboardingCompleted(true);
        if (!user || !supabase) return { success: false, error: 'No user authenticated' };

        try {
            const { error } = await supabase
                .from('user_profiles')
                .update({ onboarding_completed: true })
                .eq('id', user.id);

            if (error) {
                console.error('[AuthProvider] Error marking onboarding complete:', error);
                return { success: false, error: error.message };
            }

            setOnboardingCompleted(true);
            return { success: true };
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to mark onboarding complete';
            console.error('[AuthProvider] Error marking onboarding complete:', err);
            return { success: false, error: errorMessage };
        }
    };

    /**
     * DEV ONLY: Skip login for development
     */
    const skipLoginDev = () => {
        if ((import.meta as any).env?.DEV) {
            localStorage.setItem('rf_dev_mode', 'true');
            const devUser: any = {
                id: 'dev-user-123',
                email: 'dev@raptorflow.local',
                user_metadata: {
                    full_name: 'Dev User',
                },
            };

            setUser(devUser);
            setStatus('authenticated');

            // Set dev subscription (Soar plan - full access)
            setSubscription({
                plan: 'soar',
                status: 'active',
                billing_period: 'monthly',
                current_period_start: new Date().toISOString(),
                current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
            });

            // Mark onboarding as complete for dev user
            setOnboardingCompleted(true);

            setLoading(false);
            return { success: true, user: devUser };
        }
        return { success: false, error: 'Skip login is only available in development mode' };
    };

    const value: AuthContextValue = {
        status,
        user,
        session,
        loading,
        error,
        subscription,
        onboardingCompleted,
        login,
        loginWithGoogle,
        register,
        logout,
        updateProfile,
        markOnboardingComplete,
        skipLoginDev,
        isAuthenticated: status === 'authenticated',
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
