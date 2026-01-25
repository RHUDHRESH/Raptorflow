/**
 * 🔐 OAUTH BUTTON - Quiet Luxury Edition
 *
 * Google OAuth integration using Supabase Auth.
 * Clean, premium design following RaptorFlow guidelines.
 */

'use client';

import React, { useState } from 'react';
import { supabase } from '@/lib/supabaseClient';
import { Loader2 } from 'lucide-react';

interface OAuthButtonProps {
    provider: 'google' | 'github' | 'azure';
    redirectTo?: string;
    className?: string;
}

const PROVIDER_CONFIG = {
    google: {
        name: 'Google',
        icon: (
            <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
            </svg>
        ),
    },
    github: {
        name: 'GitHub',
        icon: (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path
                    fillRule="evenodd"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                    clipRule="evenodd"
                />
            </svg>
        ),
    },
    azure: {
        name: 'Microsoft',
        icon: (
            <svg className="w-5 h-5" viewBox="0 0 23 23">
                <path fill="#f35325" d="M1 1h10v10H1z" />
                <path fill="#81bc06" d="M12 1h10v10H12z" />
                <path fill="#05a6f0" d="M1 12h10v10H1z" />
                <path fill="#ffba08" d="M12 12h10v10H12z" />
            </svg>
        ),
    },
};

export function OAuthButton({
    provider,
    redirectTo = '/system-check',
    className = ''
}: OAuthButtonProps) {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const config = PROVIDER_CONFIG[provider];

    const handleOAuthLogin = async () => {
        try {
            setIsLoading(true);
            setError(null);

            // 🛠️ MOCK LOGIN FOR DEVELOPMENT
            if (provider === 'google' && process.env.NEXT_PUBLIC_MOCK_GOOGLE_LOGIN === 'true') {
                console.log('🔹 Using Mock Google Login');
                await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay

                const { error } = await supabase.auth.signInWithPassword({
                    email: 'test@raptorflow.local',
                    password: 'test123456'
                });

                if (error) throw error;

                // Redirect manually since signInWithPassword doesn't auto-redirect like OAuth
                window.location.href = redirectTo;
                return;
            }

            // Generate CSRF state token
            const stateToken = crypto.randomUUID();

            // Store state in cookie for server-side validation
            if (typeof window !== 'undefined') {
                document.cookie = `oauth_state=${stateToken}; path=/; max-age=600; SameSite=Lax; Secure`;
                document.cookie = `oauth_redirect=${encodeURIComponent(redirectTo)}; path=/; max-age=600; SameSite=Lax; Secure`;
            }

            const { error: authError } = await supabase.auth.signInWithOAuth({
                provider: provider,
                options: {
                    redirectTo: `${window.location.origin}/auth/callback?state=${stateToken}`,
                    queryParams: {
                        access_type: 'offline',
                        prompt: 'consent',
                    },
                },
            });

            if (authError) {
                throw authError;
            }

            // OAuth will redirect, so we don't need to do anything here
        } catch (err) {
            console.error(`OAuth ${provider} error:`, err);
            setError(err instanceof Error ? err.message : 'Authentication failed');
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full">
            <button
                type="button"
                onClick={handleOAuthLogin}
                disabled={isLoading}
                className={`
          w-full h-12 flex items-center justify-center gap-3
          bg-[var(--paper)] hover:bg-[var(--surface)]
          border border-[var(--border)] hover:border-[var(--ink-muted)]
          rounded-[var(--radius-sm)]
          text-[var(--ink)] text-sm font-medium
          transition-all duration-200
          disabled:opacity-60 disabled:cursor-not-allowed
          ${className}
        `}
            >
                {isLoading ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Connecting...</span>
                    </>
                ) : (
                    <>
                        {config.icon}
                        <span>Continue with {config.name}</span>
                    </>
                )}
            </button>

            {error && (
                <p className="mt-2 text-xs text-[var(--error)] text-center">{error}</p>
            )}
        </div>
    );
}

/**
 * Google OAuth Button - Convenience export
 */
export function GoogleOAuthButton({
    redirectTo,
    className
}: {
    redirectTo?: string;
    className?: string;
}) {
    return <OAuthButton provider="google" redirectTo={redirectTo} className={className} />;
}

export default OAuthButton;
