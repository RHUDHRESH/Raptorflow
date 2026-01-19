"use client";

import React, { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintProgress } from "@/components/ui/BlueprintProgress";
import { BlueprintButton } from "@/components/ui/BlueprintButton";

/* ══════════════════════════════════════════════════════════════════════════════
   PHONEPE PAYMENT STATUS TRACKER — Real-time Payment Monitoring
   Features:
   - Live payment status updates
   - Technical blueprint aesthetic
   - Auto-refresh functionality
   - Detailed transaction information
   ══════════════════════════════════════════════════════════════════════════════ */

interface PaymentStatusTrackerProps {
    transactionId: string;
    onStatusChange?: (status: string) => void;
    className?: string;
    autoRefresh?: boolean;
}

interface PaymentInstrument {
    type: string;
    provider?: string;
    maskedNumber?: string;
    [key: string]: unknown;
}

interface PaymentDetails {
    transactionId: string;
    merchantOrderId: string;
    amount: number;
    currency: string;
    status: 'INITIATED' | 'PENDING' | 'COMPLETED' | 'FAILED' | 'REFUNDED';
    paymentMode?: string;
    customerName?: string;
    customerEmail?: string;
    createdAt: string;
    completedAt?: string;
    paymentInstrument?: PaymentInstrument;
    error?: string;
}

export function PhonePePaymentStatusTracker({
    transactionId,
    onStatusChange,
    className,
    autoRefresh = true
}: PaymentStatusTrackerProps) {
    const [paymentDetails, setPaymentDetails] = useState<PaymentDetails | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

    // Fetch payment status
    const fetchPaymentStatus = React.useCallback(async () => {
        try {
            const response = await fetch(`/api/payments/status/${transactionId}`);
            const data = await response.json();

            if (data.success) {
                const updatedDetails: PaymentDetails = {
                    transactionId: data.transaction_id,
                    merchantOrderId: data.merchant_order_id || '',
                    amount: data.amount || 0,
                    currency: data.currency || 'INR',
                    status: data.status,
                    paymentMode: data.payment_mode,
                    customerName: data.customer_name,
                    customerEmail: data.customer_email,
                    createdAt: data.created_at || new Date().toISOString(),
                    completedAt: data.completed_at,
                    paymentInstrument: data.payment_instrument,
                    error: data.error
                };

                setPaymentDetails(updatedDetails);
                setLastUpdated(new Date());
                setError(null);

                // Notify parent of status change
                if (onStatusChange) {
                    onStatusChange(data.status);
                }
            } else {
                throw new Error(data.error || 'Failed to fetch payment status');
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    }, [transactionId, onStatusChange]);

    // Auto-refresh effect
    useEffect(() => {
        fetchPaymentStatus();
    }, [fetchPaymentStatus]);

    useEffect(() => {
        if (!autoRefresh || paymentDetails?.status !== 'PENDING') return;

        const interval = setInterval(fetchPaymentStatus, 5000);
        return () => clearInterval(interval);
    }, [autoRefresh, paymentDetails?.status, fetchPaymentStatus]);

    // Get status configuration
    const getStatusConfig = (status: string) => {
        const configs = {
            INITIATED: {
                color: 'blue',
                label: 'Initiated',
                icon: '⏳',
                description: 'Payment has been initiated'
            },
            PENDING: {
                color: 'yellow',
                label: 'Pending',
                icon: '⏱️',
                description: 'Payment is being processed'
            },
            COMPLETED: {
                color: 'green',
                label: 'Completed',
                icon: '✅',
                description: 'Payment completed successfully'
            },
            FAILED: {
                color: 'red',
                label: 'Failed',
                icon: '❌',
                description: 'Payment failed'
            },
            REFUNDED: {
                color: 'purple',
                label: 'Refunded',
                icon: '↩️',
                description: 'Payment has been refunded'
            }
        };

        return configs[status as keyof typeof configs] || configs.INITIATED;
    };

    // Format currency
    const formatCurrency = (amount: number, currency: string = 'INR') => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount / 100); // Convert from paise
    };

    // Format date
    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('en-IN', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (isLoading) {
        return (
            <BlueprintCard className={className}>
                <div className="flex items-center justify-center py-12">
                    <div className="animate-spin w-8 h-8 border-2 border-[var(--blueprint)] border-t-transparent rounded-full"></div>
                    <span className="ml-3 font-technical text-[var(--ink)]">Loading payment status...</span>
                </div>
            </BlueprintCard>
        );
    }

    if (error || !paymentDetails) {
        return (
            <BlueprintCard className={className}>
                <div className="text-center py-12">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-red-50 rounded-full border-2 border-red-500 mb-4">
                        <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <h3 className="font-technical text-lg text-[var(--ink)] mb-2">Status Unavailable</h3>
                    <p className="text-sm text-[var(--ink)]/60 font-mono mb-4">{error || 'Payment details not found'}</p>
                    <BlueprintButton onClick={fetchPaymentStatus} size="sm">
                        Retry
                    </BlueprintButton>
                </div>
            </BlueprintCard>
        );
    }

    const statusConfig = getStatusConfig(paymentDetails.status);
    const isCompleted = paymentDetails.status === 'COMPLETED';
    const isFailed = paymentDetails.status === 'FAILED';

    return (
        <BlueprintCard className={className}>
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="font-technical text-lg text-[var(--ink)] mb-1">
                        PAYMENT STATUS
                    </h3>
                    <p className="text-sm text-[var(--ink)]/60 font-mono">
                        Transaction: {transactionId}
                    </p>
                </div>
                <BlueprintBadge variant={isCompleted ? 'success' : isFailed ? 'error' : 'default'}>
                    {statusConfig.icon} {statusConfig.label}
                </BlueprintBadge>
            </div>

            {/* Status Progress */}
            <div className="mb-6">
                <BlueprintProgress
                    value={
                        paymentDetails.status === 'COMPLETED' ? 100 :
                        paymentDetails.status === 'FAILED' ? 0 :
                        paymentDetails.status === 'REFUNDED' ? 100 :
                        paymentDetails.status === 'PENDING' ? 60 :
                        paymentDetails.status === 'INITIATED' ? 20 : 0
                    }
                    className="h-3"
                />
                <div className="flex justify-between mt-2">
                    <span className="text-xs font-technical text-[var(--blueprint)]">INITIATE</span>
                    <span className="text-xs font-technical text-[var(--blueprint)]">PROCESS</span>
                    <span className="text-xs font-technical text-[var(--blueprint)]">COMPLETE</span>
                </div>
            </div>

            {/* Status Description */}
            <div className={cn(
                "p-4 rounded-lg border mb-6",
                isCompleted ? "bg-green-50 border-green-200" :
                isFailed ? "bg-red-50 border-red-200" :
                "bg-blue-50 border-blue-200"
            )}>
                <div className="flex items-center gap-3">
                    <span className="text-2xl">{statusConfig.icon}</span>
                    <div>
                        <p className={cn(
                            "font-medium",
                            isCompleted ? "text-green-800" :
                            isFailed ? "text-red-800" :
                            "text-blue-800"
                        )}>
                            {statusConfig.description}
                        </p>
                        {paymentDetails.error && (
                            <p className="text-sm text-red-600 mt-1 font-mono">{paymentDetails.error}</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Payment Details */}
            <div className="space-y-4">
                <h4 className="font-technical text-sm text-[var(--ink)]/80 mb-3">
                    TRANSACTION DETAILS
                </h4>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Amount */}
                    <div className="p-3 bg-[var(--canvas)] rounded-lg border border-[var(--ink)]/20">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-technical text-[var(--ink)]/60">AMOUNT</span>
                            <span className="text-lg font-bold text-[var(--ink)]">
                                {formatCurrency(paymentDetails.amount, paymentDetails.currency)}
                            </span>
                        </div>
                    </div>

                    {/* Order ID */}
                    <div className="p-3 bg-[var(--canvas)] rounded-lg border border-[var(--ink)]/20">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-technical text-[var(--ink)]/60">ORDER ID</span>
                            <span className="text-sm font-mono text-[var(--ink)]">
                                {paymentDetails.merchantOrderId}
                            </span>
                        </div>
                    </div>

                    {/* Customer */}
                    {paymentDetails.customerName && (
                        <div className="p-3 bg-[var(--canvas)] rounded-lg border border-[var(--ink)]/20">
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-technical text-[var(--ink)]/60">CUSTOMER</span>
                                <span className="text-sm text-[var(--ink)]">
                                    {paymentDetails.customerName}
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Payment Mode */}
                    {paymentDetails.paymentMode && (
                        <div className="p-3 bg-[var(--canvas)] rounded-lg border border-[var(--ink)]/20">
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-technical text-[var(--ink)]/60">MODE</span>
                                <span className="text-sm text-[var(--ink)]">
                                    {paymentDetails.paymentMode}
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Created At */}
                    <div className="p-3 bg-[var(--canvas)] rounded-lg border border-[var(--ink)]/20">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-technical text-[var(--ink)]/60">CREATED</span>
                            <span className="text-sm font-mono text-[var(--ink)]">
                                {formatDate(paymentDetails.createdAt)}
                            </span>
                        </div>
                    </div>

                    {/* Completed At */}
                    {paymentDetails.completedAt && (
                        <div className="p-3 bg-[var(--canvas)] rounded-lg border border-[var(--ink)]/20">
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-technical text-[var(--ink)]/60">COMPLETED</span>
                                <span className="text-sm font-mono text-[var(--ink)]">
                                    {formatDate(paymentDetails.completedAt)}
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Actions */}
            <div className="mt-6 pt-4 border-t border-[var(--ink)]/20">
                <div className="flex items-center justify-between">
                    <div className="text-xs font-technical text-[var(--ink)]/60">
                        Last updated: {formatDate(lastUpdated.toISOString())}
                    </div>
                    <div className="flex gap-2">
                        {paymentDetails.status === 'PENDING' && (
                            <BlueprintButton onClick={fetchPaymentStatus} size="sm" variant="ghost">
                                Refresh
                            </BlueprintButton>
                        )}
                        {isCompleted && (
                            <BlueprintButton size="sm" variant="secondary">
                                Download Receipt
                            </BlueprintButton>
                        )}
                    </div>
                </div>
            </div>
        </BlueprintCard>
    );
}

export default PhonePePaymentStatusTracker;
