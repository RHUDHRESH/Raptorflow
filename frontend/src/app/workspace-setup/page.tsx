/**
 * 🏢 WORKSPACE SETUP PAGE
 * 
 * Creates a workspace after successful payment/authentication.
 * Shown when user has subscription but no workspace yet.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabaseClient';
import { Loader2, Building2, CheckCircle2, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

type SetupStatus = 'checking' | 'creating' | 'success' | 'error';

export default function WorkspaceSetupPage() {
    const router = useRouter();
    const [status, setStatus] = useState<SetupStatus>('checking');
    const [workspaceName, setWorkspaceName] = useState('');
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        checkAndCreateWorkspace();
    }, []);

    const checkAndCreateWorkspace = async () => {
        try {
            // Get current session
            const { data: { session } } = await supabase.auth.getSession();

            if (!session) {
                router.replace('/login');
                return;
            }

            const userId = session.user.id;
            const email = session.user.email || '';

            // Check if workspace already exists
            const { data: existingWorkspace, error: checkError } = await supabase
                .from('workspaces')
                .select('*')
                .eq('owner_id', userId)
                .single();

            if (existingWorkspace) {
                // Workspace exists, redirect to onboarding or dashboard
                if (existingWorkspace.onboarding_completed) {
                    router.replace('/(shell)/dashboard');
                } else {
                    router.replace('/onboarding');
                }
                return;
            }

            // No workspace, show creation UI
            setWorkspaceName(`${email.split('@')[0]}'s Workspace`);
            setStatus('creating');

            // Auto-create after brief delay
            await createWorkspace(userId, email);

        } catch (err) {
            console.error('Setup error:', err);
            setStatus('error');
            setError(err instanceof Error ? err.message : 'Setup failed');
        }
    };

    const createWorkspace = async (userId: string, email: string) => {
        setStatus('creating');

        try {
            // Get subscription to determine plan
            const { data: subscription } = await supabase
                .from('subscriptions')
                .select('*')
                .eq('user_id', userId)
                .eq('status', 'active')
                .single();

            // Create workspace
            const { data: workspace, error: createError } = await supabase
                .from('workspaces')
                .insert({
                    owner_id: userId,
                    name: workspaceName || `${email.split('@')[0]}'s Workspace`,
                    plan_id: subscription?.plan_id || 'free',
                    onboarding_completed: false,
                    onboarding_step: 1,
                    settings: {
                        theme: 'light',
                        notifications: true,
                    },
                })
                .select()
                .single();

            if (createError) {
                throw createError;
            }

            // Create membership
            await supabase
                .from('workspace_members')
                .insert({
                    workspace_id: workspace.id,
                    user_id: userId,
                    role: 'owner',
                });

            setStatus('success');

            // Redirect to onboarding after brief success message
            setTimeout(() => {
                router.push('/onboarding');
            }, 1500);

        } catch (err) {
            console.error('Workspace creation error:', err);
            setStatus('error');
            setError(err instanceof Error ? err.message : 'Failed to create workspace');
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

            <div className="relative z-10 w-full max-w-md text-center">
                {/* Icon */}
                <div className={`w-20 h-20 rounded-[var(--radius-lg)] flex items-center justify-center mx-auto mb-8 ${status === 'success' ? 'bg-[var(--success)]' :
                        status === 'error' ? 'bg-[var(--error)]' :
                            'bg-[var(--ink)]'
                    }`}>
                    {status === 'success' ? (
                        <CheckCircle2 size={40} className="text-[var(--paper)]" />
                    ) : status === 'checking' || status === 'creating' ? (
                        <Loader2 size={40} className="text-[var(--paper)] animate-spin" />
                    ) : (
                        <Building2 size={40} className="text-[var(--paper)]" />
                    )}
                </div>

                {/* Title */}
                <h1 className="font-serif text-3xl text-[var(--ink)] mb-4">
                    {status === 'success' ? 'Workspace Ready!' :
                        status === 'error' ? 'Setup Failed' :
                            status === 'creating' ? 'Creating Workspace...' :
                                'Setting Up...'}
                </h1>

                {/* Message */}
                <p className="text-[var(--ink-secondary)] mb-8">
                    {status === 'success' ? 'Redirecting to onboarding...' :
                        status === 'error' ? error :
                            status === 'creating' ? 'Preparing your command center...' :
                                'Checking your account status...'}
                </p>

                {/* Actions */}
                {status === 'success' && (
                    <Button
                        onClick={() => router.push('/onboarding')}
                        className="bg-[var(--ink)] text-[var(--paper)]"
                    >
                        Start Onboarding <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                )}

                {status === 'error' && (
                    <div className="space-x-4">
                        <Button
                            onClick={() => checkAndCreateWorkspace()}
                            variant="outline"
                        >
                            Retry
                        </Button>
                        <Button
                            onClick={() => router.push('/login')}
                            className="bg-[var(--ink)] text-[var(--paper)]"
                        >
                            Back to Login
                        </Button>
                    </div>
                )}

                {/* Progress indicator */}
                {(status === 'checking' || status === 'creating') && (
                    <div className="mt-8">
                        <div className="flex justify-center gap-2">
                            <div className="w-2 h-2 bg-[var(--ink)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-2 h-2 bg-[var(--ink)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-2 h-2 bg-[var(--ink)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
