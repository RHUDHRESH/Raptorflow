"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintInput } from "@/components/ui/BlueprintInput";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";

/* ══════════════════════════════════════════════════════════════════════════════
   PHONEPE PAYMENT INITIATION — Raptorflow Payment Gateway Component
   Features:
   - Blueprint paper terminal aesthetic
   - Real-time payment status tracking
   - PhonePe integration with proper error handling
   - Technical annotation and registration marks
   ══════════════════════════════════════════════════════════════════════════════ */

interface PaymentInitiationProps {
    amount: number;
    onSuccess?: (transactionId: string) => void;
    onFailure?: (error: string) => void;
    className?: string;
}

interface PaymentState {
    status: 'idle' | 'initiating' | 'pending' | 'processing' | 'completed' | 'failed';
    transactionId?: string;
    checkoutUrl?: string;
    error?: string;
    orderId?: string;
}

export function PhonePePaymentInitiation({
    amount,
    onSuccess,
    onFailure,
    className
}: PaymentInitiationProps) {
    const [paymentState, setPaymentState] = useState<PaymentState>({ status: 'idle' });
    const [customerInfo, setCustomerInfo] = useState({
        name: '',
        email: '',
        mobile: ''
    });
    const [isProcessing, setIsProcessing] = useState(false);

    // Generate unique order ID
    const generateOrderId = () => {
        const timestamp = Date.now().toString();
        const random = Math.random().toString(36).substring(2, 8);
        return `RF${timestamp}${random}`.toUpperCase();
    };

    // Initiate payment
    const initiatePayment = async () => {
        if (!customerInfo.name || !customerInfo.email || !customerInfo.mobile) {
            setPaymentState(prev => ({ ...prev, error: 'Please fill all customer details' }));
            return;
        }

        setIsProcessing(true);
        setPaymentState(prev => ({ ...prev, status: 'initiating', error: undefined }));

        try {
            const orderId = generateOrderId();
            const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

            // Call your backend API to initiate payment
            const response = await fetch(`${apiBaseUrl}/api/payments/initiate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    amount: amount * 100, // Convert to paise
                    merchant_order_id: orderId,
                    redirect_url: `${window.location.origin}/payment/success`,
                    callback_url: `${window.location.origin}/api/payments/webhook`,
                    customer_info: {
                        id: customerInfo.email,
                        name: customerInfo.name,
                        email: customerInfo.email,
                        mobile: customerInfo.mobile
                    },
                    metadata: {
                        source: 'raptorflow_web',
                        timestamp: new Date().toISOString()
                    }
                })
            });

            const data = await response.json();

            if (data.success) {
                setPaymentState({
                    status: 'pending',
                    transactionId: data.transaction_id,
                    checkoutUrl: data.checkout_url,
                    orderId: orderId
                });

                onSuccess?.(data.transaction_id);

                // Redirect to PhonePe checkout
                window.location.href = data.checkout_url;
            } else {
                throw new Error(data.error || 'Payment initiation failed');
            }

        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Payment initiation failed';
            setPaymentState(prev => ({
                ...prev,
                status: 'failed',
                error: errorMessage
            }));
            onFailure?.(errorMessage);
        } finally {
            setIsProcessing(false);
        }
    };

    // Reset payment state
    const resetPayment = () => {
        setPaymentState({ status: 'idle' });
        setCustomerInfo({ name: '', email: '', mobile: '' });
    };

    // Status badge configuration
    const getStatusBadge = (status: PaymentState['status']) => {
        const config = {
            idle: { variant: 'default' as const, label: 'Ready' },
            initiating: { variant: 'default' as const, label: 'Initiating...' },
            pending: { variant: 'warning' as const, label: 'Pending' },
            processing: { variant: 'blueprint' as const, label: 'Processing' },
            completed: { variant: 'success' as const, label: 'Completed' },
            failed: { variant: 'error' as const, label: 'Failed' }
        };

        return config[status];
    };

    return (
        <BlueprintCard className={cn("max-w-2xl mx-auto", className)}>
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="font-technical text-lg text-[var(--ink)] mb-1">
                        PAYMENT GATEWAY
                    </h3>
                    <p className="text-sm text-[var(--ink)]/60 font-mono">
                        PhonePe Secure Payment Processing
                    </p>
                </div>
                <BlueprintBadge variant={getStatusBadge(paymentState.status).variant}>
                    {getStatusBadge(paymentState.status).label}
                </BlueprintBadge>
            </div>

            {/* Progress Indicator */}
            {paymentState.status !== 'idle' && (
                <div className="mb-6">
                    <BlueprintProgress
                        value={
                            paymentState.status === 'completed' ? 100 :
                            paymentState.status === 'failed' ? 0 :
                            paymentState.status === 'processing' ? 75 :
                            paymentState.status === 'pending' ? 50 :
                            paymentState.status === 'initiating' ? 25 : 0
                        }
                        className="h-2"
                    />
                    <div className="flex justify-between mt-2">
                        <span className="text-xs font-technical text-[var(--blueprint)]">INITIATE</span>
                        <span className="text-xs font-technical text-[var(--blueprint)]">PROCESS</span>
                        <span className="text-xs font-technical text-[var(--blueprint)]">COMPLETE</span>
                    </div>
                </div>
            )}

            {/* Payment Form */}
            {paymentState.status === 'idle' && (
                <div className="space-y-6">
                    {/* Amount Display */}
                    <div className="p-4 bg-[var(--canvas)] rounded-lg border border-[var(--ink)]/20">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-technical text-[var(--ink)]/60">AMOUNT</span>
                            <span className="text-2xl font-bold text-[var(--ink)]">
                                ₹{amount.toLocaleString('en-IN')}
                            </span>
                        </div>
                    </div>

                    {/* Customer Information */}
                    <div className="space-y-4">
                        <h4 className="font-technical text-sm text-[var(--ink)]/80 mb-3">
                            CUSTOMER INFORMATION
                        </h4>

                        <BlueprintInput
                            placeholder="Full Name"
                            value={customerInfo.name}
                            onChange={(e) => setCustomerInfo(prev => ({ ...prev, name: e.target.value }))}
                            className="font-mono"
                        />

                        <BlueprintInput
                            placeholder="Email Address"
                            type="email"
                            value={customerInfo.email}
                            onChange={(e) => setCustomerInfo(prev => ({ ...prev, email: e.target.value }))}
                            className="font-mono"
                        />

                        <BlueprintInput
                            placeholder="Mobile Number"
                            type="tel"
                            value={customerInfo.mobile}
                            onChange={(e) => setCustomerInfo(prev => ({ ...prev, mobile: e.target.value }))}
                            className="font-mono"
                        />
                    </div>

                    {/* Error Display */}
                    {paymentState.error && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                            <p className="text-sm text-red-600 font-mono">{paymentState.error}</p>
                        </div>
                    )}

                    {/* Action Button */}
                    <BlueprintButton
                        onClick={initiatePayment}
                        disabled={isProcessing}
                        className="w-full"
                        label="PAY-001"
                    >
                        {isProcessing ? 'Processing...' : 'Pay with PhonePe'}
                    </BlueprintButton>
                </div>
            )}

            {/* Processing State */}
            {(paymentState.status === 'initiating' || paymentState.status === 'pending') && (
                <div className="text-center py-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-[var(--canvas)] rounded-full border-2 border-[var(--blueprint)] mb-4">
                        <div className="animate-spin w-8 h-8 border-2 border-[var(--blueprint)] border-t-transparent rounded-full"></div>
                    </div>
                    <p className="font-technical text-[var(--ink)] mb-2">
                        {paymentState.status === 'initiating' ? 'Initiating Payment...' : 'Redirecting to PhonePe...'}
                    </p>
                    <p className="text-sm text-[var(--ink)]/60 font-mono">
                        Transaction ID: {paymentState.transactionId}
                    </p>
                </div>
            )}

            {/* Completed State */}
            {paymentState.status === 'completed' && (
                <div className="text-center py-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-green-50 rounded-full border-2 border-green-500 mb-4">
                        <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <p className="font-technical text-[var(--ink)] mb-2">Payment Completed</p>
                    <p className="text-sm text-[var(--ink)]/60 font-mono mb-4">
                        Transaction ID: {paymentState.transactionId}
                    </p>
                    <BlueprintButton onClick={resetPayment} variant="secondary" size="sm">
                        New Payment
                    </BlueprintButton>
                </div>
            )}

            {/* Failed State */}
            {paymentState.status === 'failed' && (
                <div className="text-center py-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-red-50 rounded-full border-2 border-red-500 mb-4">
                        <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </div>
                    <p className="font-technical text-[var(--ink)] mb-2">Payment Failed</p>
                    <p className="text-sm text-[var(--ink)]/60 font-mono mb-4">
                        {paymentState.error}
                    </p>
                    <div className="flex gap-3 justify-center">
                        <BlueprintButton onClick={resetPayment} variant="secondary" size="sm">
                            Try Again
                        </BlueprintButton>
                    </div>
                </div>
            )}

            {/* Technical Footer */}
            <div className="mt-6 pt-4 border-t border-[var(--ink)]/20">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-xs font-technical text-[var(--ink)]/60">
                            PHONEPE GATEWAY v2.0
                        </span>
                    </div>
                    <div className="text-xs font-technical text-[var(--blueprint)]">
                        SECURE • ENCRYPTED • PCI-DSS
                    </div>
                </div>
            </div>
        </BlueprintCard>
    );
}

export default PhonePePaymentInitiation;
