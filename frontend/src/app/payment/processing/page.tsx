/**
 * 💳 PAYMENT PROCESSING PAGE
 * 
 * Handles PhonePe payment callback:
 * 1. Verifies payment status
 * 2. Creates subscription record
 * 3. Creates workspace
 * 4. Redirects to onboarding
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase } from '@/lib/supabaseClient';
import { Loader2, CheckCircle2, XCircle, ArrowRight, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

type PaymentStatus = 'verifying' | 'success' | 'failed' | 'pending';

interface PaymentResult {
    status: PaymentStatus;
    message: string;
    transactionId?: string;
    workspaceId?: string;
}

export default function PaymentProcessingPage() {
    const router = useRouter();
    const searchParams = useSearchParams();

    const [status, setStatus] = useState<PaymentStatus>('verifying');
    const [message, setMessage] = useState('Verifying your payment...');
    const [result, setResult] = useState<PaymentResult | null>(null);

    useEffect(() => {
        processPayment();
    }, []);

    const processPayment = async () => {
        try {
            // Get pending payment from session storage
            const pendingPaymentStr = sessionStorage.getItem('pendingPayment');

            if (!pendingPaymentStr) {
                // Check URL params for transaction ID (PhonePe callback)
                const transactionId = searchParams.get('transactionId') || searchParams.get('merchantTransactionId');

                if (!transactionId) {
                    setStatus('failed');
                    setMessage('No payment information found');
                    return;
                }

                // Verify using URL params
                await verifyPayment(transactionId);
                return;
            }

            const pendingPayment = JSON.parse(pendingPaymentStr);
            await verifyPayment(pendingPayment.transactionId, pendingPayment);

        } catch (err) {
            console.error('Payment processing error:', err);
            setStatus('failed');
            setMessage(err instanceof Error ? err.message : 'Payment processing failed');
        }
    };

    const verifyPayment = async (transactionId: string, pendingPayment?: any) => {
        try {
            setStatus('verifying');
            setMessage('Verifying payment status...');

            // Call backend to verify payment
            const verifyResponse = await fetch('/api/payment/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ transactionId }),
            });

            const verifyData = await verifyResponse.json();

            if (!verifyData.success || verifyData.status === 'FAILED') {
                setStatus('failed');
                setMessage(verifyData.message || 'Payment verification failed');
                return;
            }

            if (verifyData.status === 'PENDING') {
                setStatus('pending');
                setMessage('Payment is being processed. Please wait...');
                // Retry after 5 seconds
                setTimeout(() => verifyPayment(transactionId, pendingPayment), 5000);
                return;
            }

            // Payment successful - create subscription and workspace
            setMessage('Payment verified! Setting up your workspace...');

            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                throw new Error('Session expired. Please login again.');
            }

            const userId = session.user.id;
            const planDetails = pendingPayment || verifyData.planDetails;

            // Create subscription
            setMessage('Creating your subscription...');
            const { data: subscription, error: subError } = await supabase
                .from('subscriptions')
                .insert({
                    user_id: userId,
                    plan_id: planDetails.planId,
                    plan_name: planDetails.planName,
                    plan_slug: planDetails.planId.toLowerCase(),
                    status: 'active',
                    amount_paid: planDetails.amount,
                    transaction_id: transactionId,
                    expires_at: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(), // 1 year
                })
                .select()
                .single();

            if (subError) {
                console.error('Subscription creation error:', subError);
                // Continue anyway - might already exist
            }

            // Create workspace
            setMessage('Creating your workspace...');
            const { data: workspace, error: wsError } = await supabase
                .from('workspaces')
                .insert({
                    owner_id: userId,
                    name: `${session.user.email?.split('@')[0] || 'My'}'s Workspace`,
                    plan_id: planDetails.planId,
                    onboarding_completed: false,
                    onboarding_step: 1,
                })
                .select()
                .single();

            if (wsError) {
                console.error('Workspace creation error:', wsError);
                // Check if workspace already exists
                const { data: existingWs } = await supabase
                    .from('workspaces')
                    .select('*')
                    .eq('owner_id', userId)
                    .single();

                if (existingWs) {
                    // Workspace exists, continue
                } else {
                    throw new Error('Failed to create workspace');
                }
            }

            // Clear pending payment from session
            sessionStorage.removeItem('pendingPayment');

            // Success!
            setStatus('success');
            setMessage('Welcome to RaptorFlow!');
            setResult({
                status: 'success',
                message: 'Your workspace is ready',
                transactionId,
                workspaceId: workspace?.id,
            });

            // Redirect to onboarding after 2 seconds
            setTimeout(() => {
                router.push('/onboarding');
            }, 2000);

        } catch (err) {
            console.error('Payment verification error:', err);
            setStatus('failed');
            setMessage(err instanceof Error ? err.message : 'Payment verification failed');
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
                {/* Status Icon */}
                <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-8 ${status === 'success' ? 'bg-[var(--success)]' :
                        status === 'failed' ? 'bg-[var(--error)]' :
                            'bg-[var(--ink)]'
                    }`}>
                    {status === 'verifying' || status === 'pending' ? (
                        <Loader2 size={40} className="text-[var(--paper)] animate-spin" />
                    ) : status === 'success' ? (
                        <CheckCircle2 size={40} className="text-[var(--paper)]" />
                    ) : (
                        <XCircle size={40} className="text-[var(--paper)]" />
                    )}
                </div>

                {/* Status Message */}
                <h1 className="font-serif text-3xl text-[var(--ink)] mb-4">
                    {status === 'success' ? 'Payment Successful!' :
                        status === 'failed' ? 'Payment Failed' :
                            status === 'pending' ? 'Processing...' :
                                'Verifying Payment'}
                </h1>

                <p className="text-[var(--ink-secondary)] mb-8">
                    {message}
                </p>

                {/* Actions */}
                {status === 'success' && (
                    <div className="space-y-4">
                        <p className="text-sm text-[var(--ink-muted)]">
                            Redirecting to onboarding...
                        </p>
                        <Button
                            onClick={() => router.push('/onboarding')}
                            className="bg-[var(--ink)] text-[var(--paper)]"
                        >
                            Start Onboarding <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    </div>
                )}

                {status === 'failed' && (
                    <div className="space-y-4">
                        <Button
                            onClick={() => processPayment()}
                            variant="outline"
                            className="mr-4"
                        >
                            <RefreshCw className="mr-2 h-4 w-4" />
                            Retry
                        </Button>
                        <Button
                            onClick={() => router.push('/pricing')}
                            className="bg-[var(--ink)] text-[var(--paper)]"
                        >
                            Back to Pricing
                        </Button>
                    </div>
                )}

                {status === 'pending' && (
                    <div className="space-y-4">
                        <p className="text-sm text-[var(--ink-muted)]">
                            This may take a few moments...
                        </p>
                        <div className="flex justify-center gap-2">
                            <div className="w-2 h-2 bg-[var(--ink)] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <div className="w-2 h-2 bg-[var(--ink)] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <div className="w-2 h-2 bg-[var(--ink)] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                    </div>
                )}

                {/* Transaction ID */}
                {result?.transactionId && (
                    <div className="mt-8 p-4 bg-[var(--surface)] rounded-[var(--radius-sm)]">
                        <p className="text-xs text-[var(--ink-muted)] mb-1">Transaction ID</p>
                        <p className="text-sm font-mono text-[var(--ink)]">{result.transactionId}</p>
                    </div>
                )}
            </div>
        </div>
    );
}
