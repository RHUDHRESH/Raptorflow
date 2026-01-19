/**
 * 🔐 SYSTEM CHECK PAGE
 * 
 * Post-login routing page that checks user status and redirects appropriately:
 * - Has subscription + workspace → Dashboard or Onboarding
 * - Has subscription, no workspace → Create workspace
 * - No subscription → Plan selection
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabaseClient';
import { Loader2, Shield, CheckCircle2, AlertCircle } from 'lucide-react';

type CheckStatus = 'checking' | 'success' | 'error';

interface SystemCheckResult {
    user: {
        id: string;
        email: string;
    } | null;
    subscription: {
        hasSubscription: boolean;
        planName: string | null;
        status: string | null;
        expiresAt: string | null;
    } | null;
    workspace: {
        hasWorkspace: boolean;
        workspaceId: string | null;
        workspaceName: string | null;
        onboardingCompleted: boolean;
    } | null;
}

const CHECK_STEPS = [
    { id: 'auth', label: 'Verifying authentication' },
    { id: 'subscription', label: 'Checking subscription status' },
    { id: 'workspace', label: 'Loading workspace' },
    { id: 'routing', label: 'Preparing your experience' },
];

export default function SystemCheckPage() {
    const router = useRouter();
    const [currentStep, setCurrentStep] = useState(0);
    const [status, setStatus] = useState<CheckStatus>('checking');
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<SystemCheckResult | null>(null);

    useEffect(() => {
        performSystemCheck();
    }, []);

    const performSystemCheck = async () => {
        try {
            // Step 1: Verify authentication
            setCurrentStep(0);
            await new Promise(resolve => setTimeout(resolve, 500)); // Small delay for UX

            const { data: { session }, error: authError } = await supabase.auth.getSession();

            if (authError || !session) {
                console.log('No session found, redirecting to login');
                router.replace('/login');
                return;
            }

            const userId = session.user.id;
            const userEmail = session.user.email || '';

            // Step 2: Check subscription status
            setCurrentStep(1);
            await new Promise(resolve => setTimeout(resolve, 400));

            const { data: subscriptionData, error: subError } = await supabase
                .from('subscriptions')
                .select('*')
                .eq('user_id', userId)
                .eq('status', 'active')
                .single();

            const hasSubscription = !subError && subscriptionData;

            // Step 3: Check workspace
            setCurrentStep(2);
            await new Promise(resolve => setTimeout(resolve, 400));

            const { data: workspaceData, error: wsError } = await supabase
                .from('workspaces')
                .select('*')
                .eq('owner_id', userId)
                .single();

            const hasWorkspace = !wsError && workspaceData;

            // Step 4: Determine routing
            setCurrentStep(3);
            await new Promise(resolve => setTimeout(resolve, 300));

            const checkResult: SystemCheckResult = {
                user: { id: userId, email: userEmail },
                subscription: hasSubscription ? {
                    hasSubscription: true,
                    planName: subscriptionData?.plan_name,
                    status: subscriptionData?.status,
                    expiresAt: subscriptionData?.expires_at,
                } : null,
                workspace: hasWorkspace ? {
                    hasWorkspace: true,
                    workspaceId: workspaceData?.id,
                    workspaceName: workspaceData?.name,
                    onboardingCompleted: workspaceData?.onboarding_completed || false,
                } : null,
            };

            setResult(checkResult);
            setStatus('success');

            // Routing logic
            await new Promise(resolve => setTimeout(resolve, 500));

            if (!hasSubscription) {
                // No subscription → Go to plan selection
                router.replace('/pricing');
            } else if (!hasWorkspace) {
                // Has subscription but no workspace → Create workspace
                router.replace('/workspace-setup');
            } else if (!workspaceData?.onboarding_completed) {
                // Has workspace but onboarding not complete → Continue onboarding
                router.replace('/onboarding');
            } else {
                // Everything ready → Go to dashboard
                router.replace('/(shell)/dashboard');
            }

        } catch (err) {
            console.error('System check failed:', err);
            setStatus('error');
            setError(err instanceof Error ? err.message : 'System check failed');
        }
    };

    return (
        <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center p-4">
            {/* Background texture */}
            <div
                className="fixed inset-0 opacity-[0.03] pointer-events-none"
                style={{
                    backgroundImage: "url('/textures/paper-grain.png')",
                    backgroundRepeat: "repeat",
                }}
            />

            <div className="relative z-10 w-full max-w-md">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="w-16 h-16 bg-[var(--ink)] rounded-[var(--radius-lg)] flex items-center justify-center mx-auto mb-6">
                        <Shield size={32} className="text-[var(--paper)]" />
                    </div>
                    <h1 className="font-serif text-3xl text-[var(--ink)] mb-2">
                        System Check
                    </h1>
                    <p className="text-[var(--ink-secondary)]">
                        Preparing your workspace...
                    </p>
                </div>

                {/* Check Steps */}
                <div className="bg-[var(--paper)] rounded-[var(--radius-lg)] border border-[var(--border)] p-6 shadow-sm">
                    <div className="space-y-4">
                        {CHECK_STEPS.map((step, index) => {
                            const isActive = index === currentStep && status === 'checking';
                            const isComplete = index < currentStep || status === 'success';
                            const isFailed = status === 'error' && index <= currentStep;

                            return (
                                <div
                                    key={step.id}
                                    className={`flex items-center gap-3 py-2 transition-opacity duration-300 ${index > currentStep && status === 'checking' ? 'opacity-40' : 'opacity-100'
                                        }`}
                                >
                                    {/* Status Icon */}
                                    <div className="w-6 h-6 flex items-center justify-center">
                                        {isFailed ? (
                                            <AlertCircle size={20} className="text-[var(--error)]" />
                                        ) : isComplete ? (
                                            <CheckCircle2 size={20} className="text-[var(--success)]" />
                                        ) : isActive ? (
                                            <Loader2 size={20} className="text-[var(--ink)] animate-spin" />
                                        ) : (
                                            <div className="w-4 h-4 rounded-full border-2 border-[var(--border)]" />
                                        )}
                                    </div>

                                    {/* Label */}
                                    <span className={`text-sm ${isComplete ? 'text-[var(--ink)]' :
                                        isActive ? 'text-[var(--ink)] font-medium' :
                                            'text-[var(--ink-muted)]'
                                        }`}>
                                        {step.label}
                                    </span>
                                </div>
                            );
                        })}
                    </div>

                    {/* Error State */}
                    {status === 'error' && error && (
                        <div className="mt-6 p-4 bg-[var(--error-light)] border border-[var(--error)] rounded-[var(--radius-sm)]">
                            <p className="text-sm text-[var(--error)] text-center">{error}</p>
                            <button
                                onClick={() => {
                                    setStatus('checking');
                                    setCurrentStep(0);
                                    setError(null);
                                    performSystemCheck();
                                }}
                                className="mt-3 w-full py-2 text-sm font-medium text-[var(--error)] hover:underline"
                            >
                                Try Again
                            </button>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="mt-8 text-center">
                    <p className="text-xs text-[var(--ink-muted)] font-technical tracking-wider">
                        SECURE_CONNECTION // SYS.V.2.0.4
                    </p>
                </div>
            </div>
        </div>
    );
}
