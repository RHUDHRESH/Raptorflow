"use client";

import React, { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintInput } from "@/components/ui/BlueprintInput";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";

// TypeScript declarations for PhonePe SDK
declare global {
  interface Window {
    PhonePe?: {
      PhonePe: new (config: any) => {
        open: (paymentRequest: any) => Promise<any>;
      };
    };
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   PHONEPE PAYMENT INITIATION — Raptorflow Payment Gateway Component
   Features:
   - Blueprint paper terminal aesthetic
   - Real-time payment status tracking
   - PhonePe SDK integration with proper error handling
   - Technical annotation and registration marks
   - UPI and Card payment methods
   ══════════════════════════════════════════════════════════════════════════════ */

interface PaymentInitiationProps {
    amount: number;
    planSlug: string;
    billingCycle: 'monthly' | 'annual';
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
    paymentMethod?: 'upi' | 'card' | 'netbanking';
}

// PhonePe SDK configuration
const PHONEPE_CONFIG = {
    environment: process.env.NODE_ENV === 'production' ? 'PRODUCTION' : 'UAT',
    merchantId: process.env.NEXT_PUBLIC_PHONEPE_MERCHANT_ID || '',
    appId: process.env.NEXT_PUBLIC_PHONEPE_APP_ID || '',
    enableInstrument: true,
    instrumentList: ['UPI', 'CARD', 'NETBANKING']
};

export function PhonePePaymentInitiation({
    amount,
    planSlug,
    billingCycle,
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
    const [selectedPaymentMethod, setSelectedPaymentMethod] = useState<'upi' | 'card'>('upi');
    const [cardInfo, setCardInfo] = useState({
        number: '',
        expiry: '',
        cvv: '',
        name: ''
    });
    const [isProcessing, setIsProcessing] = useState(false);
    const [phonePeSDK, setPhonePeSDK] = useState<any>(null);

    // Initialize PhonePe SDK
    useEffect(() => {
        const initializeSDK = async () => {
            try {
                // Load PhonePe SDK script
                const script = document.createElement('script');
                script.src = 'https://mercury.phonepe.com/web/bundle/merchant/1.0.0/phonepe.merchant.bundle.js';
                script.async = true;
                script.onload = () => {
                    if (window.PhonePe) {
                        const sdk = new window.PhonePe.PhonePe(PHONEPE_CONFIG);
                        setPhonePeSDK(sdk);
                        console.log('PhonePe SDK initialized successfully');
                    }
                };
                script.onerror = () => {
                    console.error('Failed to load PhonePe SDK');
                };
                document.body.appendChild(script);

                return () => {
                    document.body.removeChild(script);
                };
            } catch (error) {
                console.error('Error initializing PhonePe SDK:', error);
            }
        };

        initializeSDK();
    }, []);

    // Generate unique order ID
    const generateOrderId = () => {
        const timestamp = Date.now().toString();
        const random = Math.random().toString(36).substring(2, 8);
        return `RF${timestamp}${random}`.toUpperCase();
    };

    // Initiate payment with PhonePe SDK
    const initiatePayment = async () => {
        if (!customerInfo.name || !customerInfo.email || !customerInfo.mobile) {
            setPaymentState(prev => ({ ...prev, error: 'Please fill all customer details' }));
            return;
        }

        if (selectedPaymentMethod === 'card' && (!cardInfo.number || !cardInfo.expiry || !cardInfo.cvv)) {
            setPaymentState(prev => ({ ...prev, error: 'Please fill complete card details' }));
            return;
        }

        setIsProcessing(true);
        setPaymentState(prev => ({ ...prev, status: 'initiating', error: undefined }));

        try {
            const orderId = generateOrderId();

            // Create payment order via backend API
            const response = await fetch('/api/payments/create-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    planSlug,
                    billingCycle,
                    userEmail: customerInfo.email,
                    userId: customerInfo.email, // Will be replaced with actual user ID
                    paymentMethod: selectedPaymentMethod,
                    customerInfo: {
                        name: customerInfo.name,
                        email: customerInfo.email,
                        mobile: customerInfo.mobile
                    },
                    cardInfo: selectedPaymentMethod === 'card' ? {
                        number: cardInfo.number.replace(/\s/g, ''),
                        expiry: cardInfo.expiry,
                        cvv: cardInfo.cvv,
                        name: cardInfo.name
                    } : undefined
                })
            });

            const data = await response.json();

            if (data.success && phonePeSDK) {
                setPaymentState({
                    status: 'pending',
                    transactionId: data.transactionId,
                    checkoutUrl: data.checkoutUrl,
                    orderId: orderId,
                    paymentMethod: selectedPaymentMethod
                });

                // Initiate payment with PhonePe SDK
                const paymentRequest = {
                    merchantId: PHONEPE_CONFIG.merchantId,
                    merchantTransactionId: data.transactionId,
                    amount: amount * 100, // Convert to paise
                    redirectUrl: `${window.location.origin}/payment/success`,
                    redirectMode: 'REDIRECT',
                    callbackUrl: `${window.location.origin}/api/payments/webhook`,
                    paymentInstrument: {
                        type: selectedPaymentMethod === 'upi' ? 'UPI_INTENT' : 'CARD',
                        targetApp: selectedPaymentMethod === 'upi' ? 'PHONEPE' : undefined,
                        cardInfo: selectedPaymentMethod === 'card' ? {
                            cardNumber: cardInfo.number.replace(/\s/g, ''),
                            cardExpiry: cardInfo.expiry,
                            cardCvv: cardInfo.cvv,
                            cardHolder: cardInfo.name
                        } : undefined
                    },
                    userInfo: {
                        customerName: customerInfo.name,
                        customerEmail: customerInfo.email,
                        customerMobile: customerInfo.mobile
                    }
                };

                // Open PhonePe payment window
                phonePeSDK.open(paymentRequest)
                    .then((result: any) => {
                        if (result.status === 'SUCCESS') {
                            setPaymentState(prev => ({ ...prev, status: 'completed' }));
                            onSuccess?.(data.transactionId);
                        } else {
                            setPaymentState(prev => ({
                                ...prev,
                                status: 'failed',
                                error: result.message || 'Payment failed'
                            }));
                            onFailure?.(result.message || 'Payment failed');
                        }
                    })
                    .catch((error: any) => {
                        console.error('PhonePe payment error:', error);
                        setPaymentState(prev => ({
                            ...prev,
                            status: 'failed',
                            error: error.message || 'Payment processing failed'
                        }));
                        onFailure?.(error.message || 'Payment processing failed');
                    });

            } else {
                throw new Error(data.error || 'Failed to create payment order');
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
        setCardInfo({ number: '', expiry: '', cvv: '', name: '' });
    };

    // Format card number
    const formatCardNumber = (value: string) => {
        const v = value.replace(/\s/g, '');
        const matches = v.match(/\d{4,16}/g);
        const match = matches && matches[0] || '';
        const parts = [];
        for (let i = 0, len = match.length; i < len; i += 4) {
            parts.push(match.substring(i, i + 4));
        }
        if (parts.length) {
            return parts.join(' ');
        } else {
            return v;
        }
    };

    // Format expiry date
    const formatExpiry = (value: string) => {
        const v = value.replace(/\s/g, '').replace(/[^0-9]/g, '');
        if (v.length >= 2) {
            return v.slice(0, 2) + '/' + v.slice(2, 4);
        }
        return v;
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
                        <div className="flex items-center justify-between mt-2">
                            <span className="text-xs font-technical text-[var(--ink)]/60">PLAN</span>
                            <span className="text-sm font-mono text-[var(--ink)]">
                                {planSlug.toUpperCase()} - {billingCycle.toUpperCase()}
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

                    {/* Payment Method Selection */}
                    <div className="space-y-4">
                        <h4 className="font-technical text-sm text-[var(--ink)]/80 mb-3">
                            PAYMENT METHOD
                        </h4>

                        <div className="grid grid-cols-2 gap-3">
                            <button
                                type="button"
                                onClick={() => setSelectedPaymentMethod('upi')}
                                className={cn(
                                    "p-3 border rounded-lg font-mono text-sm transition-all",
                                    selectedPaymentMethod === 'upi'
                                        ? "border-[var(--blueprint)] bg-[var(--canvas)] text-[var(--ink)]"
                                        : "border-[var(--border)] text-[var(--ink)]/60"
                                )}
                            >
                                UPI
                            </button>
                            <button
                                type="button"
                                onClick={() => setSelectedPaymentMethod('card')}
                                className={cn(
                                    "p-3 border rounded-lg font-mono text-sm transition-all",
                                    selectedPaymentMethod === 'card'
                                        ? "border-[var(--blueprint)] bg-[var(--canvas)] text-[var(--ink)]"
                                        : "border-[var(--border)] text-[var(--ink)]/60"
                                )}
                            >
                                CARD
                            </button>
                        </div>

                        {/* Card Details */}
                        {selectedPaymentMethod === 'card' && (
                            <div className="space-y-3 p-4 bg-[var(--canvas)] rounded-lg border border-[var(--ink)]/20">
                                <BlueprintInput
                                    placeholder="Card Number"
                                    value={cardInfo.number}
                                    onChange={(e) => setCardInfo(prev => ({ ...prev, number: formatCardNumber(e.target.value) }))}
                                    maxLength={19}
                                    className="font-mono"
                                />
                                <div className="grid grid-cols-2 gap-3">
                                    <BlueprintInput
                                        placeholder="MM/YY"
                                        value={cardInfo.expiry}
                                        onChange={(e) => setCardInfo(prev => ({ ...prev, expiry: formatExpiry(e.target.value) }))}
                                        maxLength={5}
                                        className="font-mono"
                                    />
                                    <BlueprintInput
                                        placeholder="CVV"
                                        value={cardInfo.cvv}
                                        onChange={(e) => setCardInfo(prev => ({ ...prev, cvv: e.target.value.replace(/\D/g, '') }))}
                                        maxLength={3}
                                        type="password"
                                        className="font-mono"
                                    />
                                </div>
                                <BlueprintInput
                                    placeholder="Cardholder Name"
                                    value={cardInfo.name}
                                    onChange={(e) => setCardInfo(prev => ({ ...prev, name: e.target.value }))}
                                    className="font-mono"
                                />
                            </div>
                        )}
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
                        disabled={isProcessing || !phonePeSDK}
                        className="w-full"
                        label="PAY-001"
                    >
                        {isProcessing ? 'Processing...' : `Pay ₹${amount.toLocaleString('en-IN')} with PhonePe`}
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
                        {paymentState.status === 'initiating' ? 'Initiating Payment...' : 'Opening PhonePe...'}
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
