"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { Compass, Mail, Lock, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintInput } from '@/components/ui/BlueprintInput';
import { getSupabaseClient } from '@/lib/supabase-auth';
import { getAuthCallbackUrl } from '@/lib/env-utils';
import { getEnvironmentSummary } from '@/lib/env-validation';
import { notify } from "@/lib/notifications";

import { BlueprintButton } from '@/components/ui/BlueprintButton';

export default function LoginPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });

    // Debug environment on mount
    React.useEffect(() => {
        console.log('🔍 Login Page Environment Debug:');
        console.log(getEnvironmentSummary());
        console.log('Auth Callback URL:', getAuthCallbackUrl());
    }, []);

    const handleGoogleLogin = async () => {
        setIsLoading(true);
        try {
            const supabase = getSupabaseClient();
            if (!supabase) {
                throw new Error('Supabase client not available');
            }

            const callbackUrl = getAuthCallbackUrl();
            console.log('🔗 Google OAuth redirect URL:', callbackUrl);

            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: callbackUrl,
                    queryParams: {
                        access_type: 'offline',
                        prompt: 'consent',
                    },
                },
            });

            if (error) throw error;
        } catch (err: any) {
            setError(err.message);
            notify.error("Failed to connect with Google");
            setIsLoading(false);
        }
    };

    const handleGithubLogin = async () => {
        setIsLoading(true);
        try {
            const supabase = getSupabaseClient();
            if (!supabase) {
                throw new Error('Supabase client not available');
            }

            const callbackUrl = getAuthCallbackUrl();
            console.log('🔗 GitHub OAuth redirect URL:', callbackUrl);

            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'github',
                options: {
                    redirectTo: callbackUrl,
                },
            });

            if (error) throw error;
        } catch (err: any) {
            setError(err.message);
            notify.error("Failed to connect with GitHub");
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[var(--canvas)] relative overflow-hidden flex items-center justify-center p-4">
            <div className="fixed inset-0 blueprint-grid-major pointer-events-none opacity-30" />

            <div className="relative z-10 w-full max-w-md">
                <BlueprintCard figure="FIG. 01" code="AUTH-LOGIN" showCorners variant="elevated" padding="lg">
                    <div className="text-center mb-12">
                        <div className="flex justify-center mb-6">
                            <div className="h-16 w-16 rounded-[var(--radius-sm)] bg-[var(--ink)] text-[var(--paper)] flex items-center justify-center ink-bleed-lg">
                                <Compass size={32} strokeWidth={1.5} />
                            </div>
                        </div>
                        <h1 className="font-serif text-4xl text-[var(--ink)] mb-3">RaptorFlow</h1>
                        <p className="text-sm text-[var(--ink-secondary)] font-technical tracking-wider">FOUNDER MARKETING OPERATING SYSTEM</p>
                    </div>

                    {error && (
                        <div className="mb-8 p-4 bg-[var(--error-light)] border border-[var(--error)] rounded-[var(--radius-sm)] flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-[var(--error)] mt-0.5 shrink-0" />
                            <p className="text-sm text-[var(--error)] font-medium leading-relaxed">{error}</p>
                        </div>
                    )}

                    <div className="space-y-4">
                        <div className="text-center space-y-2 mb-8">
                            <p className="text-xs font-mono text-[var(--muted)] uppercase tracking-[0.2em]">Restricted Access</p>
                            <p className="text-sm text-[var(--ink-secondary)]">Sign in with your authorized organization account.</p>
                        </div>

                        <BlueprintButton
                            variant="primary"
                            className="w-full h-14 text-lg font-technical tracking-tight"
                            onClick={handleGoogleLogin}
                            disabled={isLoading}
                            type="button"
                        >
                            {isLoading ? (
                                <Loader2 className="animate-spin w-5 h-5 mr-3" />
                            ) : (
                                <svg className="mr-3 h-5 w-5" viewBox="0 0 24 24">
                                    <path
                                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                        fill="#4285F4"
                                    />
                                    <path
                                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                        fill="#34A853"
                                    />
                                    <path
                                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                        fill="#FBBC05"
                                    />
                                    <path
                                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                        fill="#EA4335"
                                    />
                                </svg>
                            )}
                            {isLoading ? "ESTABLISHING UPLINK..." : "CONTINUE WITH GOOGLE"}
                        </BlueprintButton>

                        <BlueprintButton
                            variant="secondary"
                            className="w-full h-14 text-lg font-technical tracking-tight"
                            onClick={handleGithubLogin}
                            disabled={isLoading}
                            type="button"
                        >
                            {isLoading ? (
                                <Loader2 className="animate-spin w-5 h-5 mr-3" />
                            ) : (
                                <svg className="mr-3 h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                                </svg>
                            )}
                            {isLoading ? "ESTABLISHING UPLINK..." : "CONTINUE WITH GITHUB"}
                        </BlueprintButton>
                    </div>

                    <div className="mt-12 pt-8 border-t border-[var(--border)] text-center">
                        <p className="text-[10px] text-[var(--ink-muted)] font-mono uppercase tracking-widest">
                            Authorized Personnel Only &copy; 2026 RaptorFlow
                        </p>
                    </div>
                </BlueprintCard>
            </div>
        </div>
    );
}
