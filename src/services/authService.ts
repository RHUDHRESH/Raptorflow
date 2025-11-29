import { supabase } from '../lib/supabase';
import type { User, Session, AuthError } from '@supabase/supabase-js';

/**
 * Auth Service
 * 
 * Centralized authentication service that wraps Supabase auth methods.
 * This service provides a clean abstraction layer over Supabase auth,
 * making it easier to maintain and test auth-related functionality.
 * 
 * All auth operations should go through this service rather than
 * calling supabase.auth.* directly.
 */

// Type definitions for service responses
export interface AuthResponse {
    user: User | null;
    session: Session | null;
    error: AuthError | Error | null;
}

export interface SessionResponse {
    session: Session | null;
    user: User | null;
    error: AuthError | Error | null;
}

export interface SignOutResponse {
    error: AuthError | Error | null;
}

export interface AuthStateChangeCallback {
    (event: string, session: Session | null): void;
}

export interface AuthSubscription {
    unsubscribe: () => void;
}

/**
 * Auth Service Object
 * 
 * Provides typed methods for all authentication operations.
 */
export const authService = {
    /**
     * Get the current session
     * 
     * Retrieves the active session from Supabase. This should be called
     * on app initialization to check if a user is already logged in.
     * 
     * @returns Promise with session, user, and error
     */
    async getSession(): Promise<SessionResponse> {
        if (!supabase) {
            return {
                session: null,
                user: null,
                error: new Error('Supabase client is not configured'),
            };
        }

        try {
            const { data, error } = await supabase.auth.getSession();

            if (error) {
                console.error('[AuthService] Error getting session:', error);
                return { session: null, user: null, error };
            }

            return {
                session: data.session,
                user: data.session?.user ?? null,
                error: null,
            };
        } catch (error) {
            console.error('[AuthService] Unexpected error getting session:', error);
            return {
                session: null,
                user: null,
                error: error instanceof Error ? error : new Error('Unknown error'),
            };
        }
    },

    /**
     * Subscribe to auth state changes
     * 
     * Sets up a listener for authentication state changes (sign in, sign out, token refresh).
     * The callback will be invoked whenever the auth state changes.
     * 
     * @param callback - Function to call when auth state changes
     * @returns Subscription object with unsubscribe method
     */
    onAuthStateChange(callback: AuthStateChangeCallback): AuthSubscription {
        if (!supabase) {
            console.warn('[AuthService] Cannot subscribe to auth changes: Supabase not configured');
            return { unsubscribe: () => { } };
        }

        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            (event, session) => {
                callback(event, session);
            }
        );

        return {
            unsubscribe: () => {
                subscription.unsubscribe();
            },
        };
    },

    /**
     * Sign in with email and password
     * 
     * Authenticates a user with their email and password credentials.
     * 
     * @param credentials - Object containing email and password
     * @returns Promise with user, session, and error
     */
    async signInWithEmail(credentials: {
        email: string;
        password: string;
    }): Promise<AuthResponse> {
        if (!supabase) {
            return {
                user: null,
                session: null,
                error: new Error('Supabase client is not configured'),
            };
        }

        try {
            const { data, error } = await supabase.auth.signInWithPassword({
                email: credentials.email,
                password: credentials.password,
            });

            if (error) {
                console.error('[AuthService] Error signing in:', error);

                // Provide user-friendly error messages
                let userMessage = error.message;
                if (error.message.includes('Invalid login credentials')) {
                    userMessage = 'Invalid email or password';
                } else if (error.message.includes('Email not confirmed')) {
                    userMessage = 'Please verify your email address before signing in';
                }

                return {
                    user: null,
                    session: null,
                    error: new Error(userMessage),
                };
            }

            return {
                user: data.user,
                session: data.session,
                error: null,
            };
        } catch (error) {
            console.error('[AuthService] Unexpected error signing in:', error);
            return {
                user: null,
                session: null,
                error: error instanceof Error ? error : new Error('Failed to sign in'),
            };
        }
    },

    /**
     * Sign up with email and password
     * 
     * Creates a new user account with email and password.
     * 
     * @param credentials - Object containing email, password, and optional metadata
     * @returns Promise with user, session, and error
     */
    async signUpWithEmail(credentials: {
        email: string;
        password: string;
        metadata?: {
            full_name?: string;
            [key: string]: any;
        };
    }): Promise<AuthResponse> {
        if (!supabase) {
            return {
                user: null,
                session: null,
                error: new Error('Supabase client is not configured'),
            };
        }

        try {
            const { data, error } = await supabase.auth.signUp({
                email: credentials.email,
                password: credentials.password,
                options: {
                    data: credentials.metadata || {},
                },
            });

            if (error) {
                console.error('[AuthService] Error signing up:', error);

                // Provide user-friendly error messages
                let userMessage = error.message;
                if (error.message.includes('already registered')) {
                    userMessage = 'An account with this email already exists';
                } else if (error.message.includes('Password should be')) {
                    userMessage = 'Password must be at least 6 characters';
                }

                return {
                    user: null,
                    session: null,
                    error: new Error(userMessage),
                };
            }

            return {
                user: data.user,
                session: data.session,
                error: null,
            };
        } catch (error) {
            console.error('[AuthService] Unexpected error signing up:', error);
            return {
                user: null,
                session: null,
                error: error instanceof Error ? error : new Error('Failed to sign up'),
            };
        }
    },

    /**
     * Sign out the current user
     * 
     * Ends the current user session and clears all auth tokens.
     * 
     * @returns Promise with error (null if successful)
     */
    async signOut(): Promise<SignOutResponse> {
        if (!supabase) {
            return {
                error: new Error('Supabase client is not configured'),
            };
        }

        try {
            const { error } = await supabase.auth.signOut();

            if (error) {
                console.error('[AuthService] Error signing out:', error);
                return { error };
            }

            return { error: null };
        } catch (error) {
            console.error('[AuthService] Unexpected error signing out:', error);
            return {
                error: error instanceof Error ? error : new Error('Failed to sign out'),
            };
        }
    },

    /**
     * Sign in with OAuth provider
     * 
     * Initiates OAuth flow with the specified provider (e.g., Google, GitHub).
     * This will redirect the user to the provider's login page.
     * 
     * @param provider - OAuth provider name
     * @param redirectTo - Optional redirect URL after successful auth
     * @returns Promise with error (null if redirect initiated successfully)
     */
    async signInWithOAuth(
        provider: 'google' | 'github' | 'gitlab' | 'bitbucket',
        redirectTo?: string
    ): Promise<SignOutResponse> {
        if (!supabase) {
            return {
                error: new Error('Supabase client is not configured'),
            };
        }

        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider,
                options: {
                    redirectTo: redirectTo || `${window.location.origin}/`,
                },
            });

            if (error) {
                console.error('[AuthService] Error signing in with OAuth:', error);

                // Provide user-friendly error messages
                let userMessage = error.message;
                if (error.message.includes('provider is not enabled') ||
                    error.message.includes('Unsupported provider')) {
                    userMessage = `${provider} OAuth is not enabled. Please contact support.`;
                }

                return { error: new Error(userMessage) };
            }

            return { error: null };
        } catch (error) {
            console.error('[AuthService] Unexpected error with OAuth:', error);
            return {
                error: error instanceof Error ? error : new Error('Failed to sign in with OAuth'),
            };
        }
    },

    /**
     * Reset password for email
     * 
     * Sends a password reset email to the specified address.
     * 
     * @param email - Email address to send reset link to
     * @returns Promise with error (null if successful)
     */
    async resetPasswordForEmail(email: string): Promise<SignOutResponse> {
        if (!supabase) {
            return {
                error: new Error('Supabase client is not configured'),
            };
        }

        try {
            const { error } = await supabase.auth.resetPasswordForEmail(email, {
                redirectTo: `${window.location.origin}/reset-password`,
            });

            if (error) {
                console.error('[AuthService] Error resetting password:', error);
                return { error };
            }

            return { error: null };
        } catch (error) {
            console.error('[AuthService] Unexpected error resetting password:', error);
            return {
                error: error instanceof Error ? error : new Error('Failed to reset password'),
            };
        }
    },
};
