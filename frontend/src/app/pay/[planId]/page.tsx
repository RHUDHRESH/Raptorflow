/**
 * 💳 PAYMENT PAGE - PhonePe Integration
 * 
 * Displays plan details and initiates PhonePe payment.
 * Uses the backend payment API for secure payment processing.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { supabase } from '@/lib/supabaseClient';
import { Loader2, Shield, CheckCircle2, CreditCard, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface PlanDetails {
    planId: string;
    planName: string;
    priceValue: number; // in paise
}

const PLAN_DETAILS: Record<string, PlanDetails> = {
    'PLN-ASC': { planId: 'PLN-ASC', planName: 'Ascent', priceValue: 500000 },
    'PLN-GLD': { planId: 'PLN-GLD', planName: 'Glide', priceValue: 700000 },
    'PLN-SOA': { planId: 'PLN-SOA', planName: 'Soar', priceValue: 1000000 },
};

export default function PaymentPage() {
    const router = useRouter();
    const params = useParams();
    const planId = params.planId as string;

    const [plan, setPlan] = useState<PlanDetails | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [user, setUser] = useState<{ id: string; email: string } | null>(null);

    useEffect(() => {
        // Get plan details
        const planDetails = PLAN_DETAILS[planId];
        if (!planDetails) {
            setError('Invalid plan selected');
            return;
        }
        setPlan(planDetails);

        // Check if user is authenticated
        checkAuth();
    }, [planId]);

    const checkAuth = async () => {
        const { data: { session } } = await supabase.auth.getSession();
        if (!session) {
            // Store intended plan and redirect to login
            sessionStorage.setItem('paymentRedirect', `/pay/${planId}`);
            router.push('/login');
            return;
        }
        setUser({
            id: session.user.id,
            email: session.user.email || '',
        });
    };

    const formatPrice = (paise: number) => {
        return `₹${(paise / 100).toLocaleString('en-IN')}`;
    };

    const initiatePayment = async () => {
        if (!plan || !user) return;

        setIsLoading(true);
        setError(null);

        try {
            // Call backend API to initiate payment
            const response = await fetch('/api/payment/create-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    planId: plan.planId,
                    planName: plan.planName,
                    amount: plan.priceValue, // in paise
                    userId: user.id,
                    email: user.email,
                    redirectUrl: `${window.location.origin}/payment/processing`,
                }),
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to initiate payment');
            }

            // Store transaction details for verification
            sessionStorage.setItem('pendingPayment', JSON.stringify({
                transactionId: data.transactionId,
                planId: plan.planId,
                planName: plan.planName,
                amount: plan.priceValue,
                userId: user.id,
            }));

            // Redirect to PhonePe checkout
            if (data.paymentUrl) {
                window.location.href = data.paymentUrl;
            } else if (data.checkoutUrl) {
                window.location.href = data.checkoutUrl;
            } else {
                throw new Error('No payment URL received');
            }

        } catch (err) {
            console.error('Payment initiation error:', err);
            setError(err instanceof Error ? err.message : 'Payment initiation failed');
            setIsLoading(false);
        }
    };

    if (!plan) {
        return (
            <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
                {error ? (
                    <div className="text-center">
                        <p className="text-[var(--error)] mb-4">{error}</p>
                        <Button onClick={() => router.push('/pricing')}>
                            Back to Pricing
                        </Button>
                    </div>
                ) : (
                    <Loader2 className="w-8 h-8 animate-spin text-[var(--ink)]" />
                )}
            </div>
        );
    }

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
                {/* Back Link */}
                <Link
                    href="/pricing"
                    className="inline-flex items-center gap-2 text-sm text-[var(--ink-muted)] hover:text-[var(--ink)] mb-8 transition-colors"
                >
                    <ArrowLeft size={16} />
                    Back to Plans
                </Link>

                {/* Payment Card */}
                <div className="bg-[var(--paper)] rounded-[var(--radius-lg)] border border-[var(--border)] overflow-hidden shadow-sm">
                    {/* Header */}
                    <div className="bg-[var(--ink)] text-[var(--paper)] p-6 text-center">
                        <div className="w-12 h-12 bg-[var(--paper)] rounded-[var(--radius-md)] flex items-center justify-center mx-auto mb-4">
                            <CreditCard size={24} className="text-[var(--ink)]" />
                        </div>
                        <h1 className="font-serif text-2xl mb-1">Complete Payment</h1>
                        <p className="text-sm opacity-80">Secure checkout powered by PhonePe</p>
                    </div>

                    {/* Plan Summary */}
                    <div className="p-6 border-b border-[var(--border)]">
                        <div className="flex justify-between items-center mb-4">
                            <span className="text-sm text-[var(--ink-muted)]">Plan</span>
                            <span className="font-medium text-[var(--ink)]">{plan.planName}</span>
                        </div>
                        <div className="flex justify-between items-center mb-4">
                            <span className="text-sm text-[var(--ink-muted)]">Duration</span>
                            <span className="font-medium text-[var(--ink)]">1 Year</span>
                        </div>
                        <div className="flex justify-between items-center pt-4 border-t border-[var(--border-subtle)]">
                            <span className="text-lg font-medium text-[var(--ink)]">Total</span>
                            <span className="text-2xl font-bold text-[var(--ink)]">{formatPrice(plan.priceValue)}</span>
                        </div>
                    </div>

                    {/* User Info */}
                    {user && (
                        <div className="px-6 py-4 bg-[var(--surface)]">
                            <p className="text-xs text-[var(--ink-muted)] mb-1">Billing Email</p>
                            <p className="text-sm text-[var(--ink)]">{user.email}</p>
                        </div>
                    )}

                    {/* Payment Button */}
                    <div className="p-6">
                        {error && (
                            <div className="mb-4 p-3 bg-[var(--error-light)] border border-[var(--error)] rounded-[var(--radius-sm)]">
                                <p className="text-sm text-[var(--error)] text-center">{error}</p>
                            </div>
                        )}

                        <Button
                            onClick={initiatePayment}
                            disabled={isLoading || !user}
                            className="w-full h-12 bg-[var(--ink)] hover:bg-[var(--ink)]/90 text-[var(--paper)] text-sm font-medium"
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Initiating Payment...
                                </>
                            ) : (
                                <>
                                    <Shield className="mr-2 h-4 w-4" />
                                    Pay {formatPrice(plan.priceValue)}
                                </>
                            )}
                        </Button>

                        <div className="mt-4 flex items-center justify-center gap-2 text-xs text-[var(--ink-muted)]">
                            <Shield size={12} />
                            <span>256-bit SSL Encrypted</span>
                        </div>
                    </div>
                </div>

                {/* Trust Badges */}
                <div className="mt-6 text-center">
                    <div className="flex items-center justify-center gap-4 text-xs text-[var(--ink-muted)]">
                        <div className="flex items-center gap-1">
                            <CheckCircle2 size={12} className="text-[var(--success)]" />
                            <span>Secure Payment</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <CheckCircle2 size={12} className="text-[var(--success)]" />
                            <span>Instant Activation</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
