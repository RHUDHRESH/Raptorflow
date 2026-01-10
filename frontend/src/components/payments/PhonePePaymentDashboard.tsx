"use client";

import React, { useState, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintTable } from "@/components/ui/BlueprintTable";
import type { Column } from "@/components/ui/BlueprintTable";
import { BlueprintKPI } from "@/components/ui/BlueprintKPI";

/* ══════════════════════════════════════════════════════════════════════════════
   PHONEPE PAYMENT DASHBOARD — Complete Payment Management Interface
   Features:
   - Payment history and analytics
   - Transaction filtering and search
   - Real-time statistics
   - Technical blueprint design system
   ══════════════════════════════════════════════════════════════════════════════ */

interface PaymentTransaction extends Record<string, unknown> {
    id: string;
    transactionId: string;
    merchantOrderId: string;
    amount: number;
    currency: string;
    status: 'INITIATED' | 'PENDING' | 'COMPLETED' | 'FAILED' | 'REFUNDED';
    paymentMode?: string;
    customerName: string;
    customerEmail: string;
    createdAt: string;
    completedAt?: string;
    refundedAmount?: number;
}

interface PaymentStats extends Record<string, unknown> {
    totalTransactions: number;
    completedTransactions: number;
    failedTransactions: number;
    totalAmount: number;
    totalRefunded: number;
    successRate: number;
}

export function PhonePePaymentDashboard({ className }: { className?: string }) {
    const [transactions, setTransactions] = useState<PaymentTransaction[]>([]);
    const [stats, setStats] = useState<PaymentStats | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filter, setFilter] = useState<string>('all');
    const [searchTerm, setSearchTerm] = useState('');

    // Mock data for demonstration (replace with actual API calls)
    const mockTransactions: PaymentTransaction[] = [
        {
            id: '1',
            transactionId: 'TXN001',
            merchantOrderId: 'MO001',
            amount: 10000,
            currency: 'INR',
            status: 'COMPLETED',
            paymentMode: 'UPI',
            customerName: 'John Doe',
            customerEmail: 'john@example.com',
            createdAt: '2024-01-05T10:30:00Z',
            completedAt: '2024-01-05T10:32:15Z'
        },
        {
            id: '2',
            transactionId: 'TXN002',
            merchantOrderId: 'MO002',
            amount: 25000,
            currency: 'INR',
            status: 'PENDING',
            paymentMode: 'Credit Card',
            customerName: 'Jane Smith',
            customerEmail: 'jane@example.com',
            createdAt: '2024-01-05T11:15:00Z'
        },
        {
            id: '3',
            transactionId: 'TXN003',
            merchantOrderId: 'MO003',
            amount: 5000,
            currency: 'INR',
            status: 'FAILED',
            customerName: 'Bob Johnson',
            customerEmail: 'bob@example.com',
            createdAt: '2024-01-05T09:45:00Z'
        },
        {
            id: '4',
            transactionId: 'TXN004',
            merchantOrderId: 'MO004',
            amount: 15000,
            currency: 'INR',
            status: 'COMPLETED',
            paymentMode: 'Debit Card',
            customerName: 'Alice Brown',
            customerEmail: 'alice@example.com',
            createdAt: '2024-01-05T08:20:00Z',
            completedAt: '2024-01-05T08:22:30Z',
            refundedAmount: 5000
        }
    ];

    // Mock stats
    const mockStats: PaymentStats = {
        totalTransactions: 4,
        completedTransactions: 2,
        failedTransactions: 1,
        totalAmount: 55000,
        totalRefunded: 5000,
        successRate: 50
    };

    // Fetch payment data
    const fetchPaymentData = useCallback(async () => {
        setIsLoading(true);
        try {
            // Replace with actual API calls
            // const [transactionsResponse, statsResponse] = await Promise.all([
            //     fetch('/api/payments/transactions'),
            //     fetch('/api/payments/stats')
            // ]);

            // const transactionsData = await transactionsResponse.json();
            // const statsData = await statsResponse.json();

            // Using mock data for now
            setTransactions(mockTransactions);
            setStats(mockStats);
            setError(null);
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch payment data';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchPaymentData();
    }, [fetchPaymentData]);

    // Filter transactions
    const filteredTransactions = transactions.filter(transaction => {
        const matchesFilter = filter === 'all' || transaction.status === filter;
        const matchesSearch = searchTerm === '' ||
            transaction.customerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
            transaction.customerEmail.toLowerCase().includes(searchTerm.toLowerCase()) ||
            transaction.transactionId.toLowerCase().includes(searchTerm.toLowerCase()) ||
            transaction.merchantOrderId.toLowerCase().includes(searchTerm.toLowerCase());

        return matchesFilter && matchesSearch;
    });

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

    // Get status badge variant
    const getStatusVariant = (status: string) => {
        switch (status) {
            case 'COMPLETED': return 'success';
            case 'FAILED': return 'error';
            case 'PENDING': return 'warning';
            case 'INITIATED': return 'info';
            case 'REFUNDED': return 'blueprint';
            default: return 'default';
        }
    };

    const columns: Column<PaymentTransaction>[] = [
        {
            key: 'transactionId',
            header: 'Transaction ID',
            render: (value) => (
                <span className="font-mono text-sm">{value as string}</span>
            )
        },
        {
            key: 'customerName',
            header: 'Customer',
            render: (value, row) => (
                <div>
                    <div className="font-medium">{value as string}</div>
                    <div className="text-xs text-[var(--ink)]/60 font-mono">{row.customerEmail}</div>
                </div>
            )
        },
        {
            key: 'amount',
            header: 'Amount',
            render: (value, row) => (
                <div>
                    <div className="font-medium">{formatCurrency(value as number, row.currency)}</div>
                    {row.refundedAmount && (
                        <div className="text-xs text-[var(--error)]">
                            Refunded: {formatCurrency(row.refundedAmount, row.currency)}
                        </div>
                    )}
                </div>
            )
        },
        {
            key: 'status',
            header: 'Status',
            render: (value) => (
                <BlueprintBadge variant={getStatusVariant(value as string)}>
                    {value as string}
                </BlueprintBadge>
            )
        },
        {
            key: 'paymentMode',
            header: 'Mode',
            render: (value) => (value as string) || '-'
        },
        {
            key: 'createdAt',
            header: 'Created',
            render: (value) => (
                <span className="font-mono text-sm">{formatDate(value as string)}</span>
            )
        },
        {
            key: 'actions',
            header: 'Actions',
            render: (_value, row) => (
                <div className="flex gap-2">
                    <BlueprintButton size="sm" variant="ghost">
                        View
                    </BlueprintButton>
                    {row.status === 'COMPLETED' && !row.refundedAmount && (
                        <BlueprintButton size="sm" variant="ghost">
                            Refund
                        </BlueprintButton>
                    )}
                </div>
            )
        }
    ];

    if (isLoading) {
        return (
            <BlueprintCard className={className}>
                <div className="text-center py-12">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-[var(--blueprint-light)] rounded-full border-2 border-[var(--blueprint)] mb-4">
                        <div className="w-8 h-8 text-[var(--blueprint)] animate-spin">⚙️</div>
                    </div>
                    <h3 className="font-technical text-lg text-[var(--ink)] mb-2">Loading Payment Data</h3>
                    <p className="text-sm text-[var(--ink)]/60 font-mono">Fetching transactions...</p>
                </div>
            </BlueprintCard>
        );
    }

    if (error) {
        return (
            <BlueprintCard className={className}>
                <div className="text-center py-12">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-[var(--error-light)] rounded-full border-2 border-[var(--error)] mb-4">
                        <svg className="w-8 h-8 text-[var(--error)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <h3 className="font-technical text-lg text-[var(--ink)] mb-2">Data Unavailable</h3>
                    <p className="text-sm text-[var(--ink)]/60 font-mono mb-4">{error}</p>
                    <BlueprintButton onClick={fetchPaymentData} size="sm">
                        Retry
                    </BlueprintButton>
                </div>
            </BlueprintCard>
        );
    }

    return (
        <div className={cn("space-y-6", className)}>
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="font-technical text-2xl text-[var(--ink)] mb-1">
                        PAYMENT DASHBOARD
                    </h2>
                    <p className="text-sm text-[var(--ink)]/60 font-mono">
                        PhonePe Payment Gateway Management
                    </p>
                </div>
                <BlueprintButton onClick={fetchPaymentData} variant="secondary" size="sm">
                    Refresh Data
                </BlueprintButton>
            </div>

            {/* Statistics Cards */}
            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <BlueprintKPI
                        label="Total Transactions"
                        value={stats.totalTransactions}
                        code="TRANS-001"
                    />
                    <BlueprintKPI
                        label="Success Rate"
                        value={`${stats.successRate}%`}
                        code="SUCCESS-001"
                        trend={stats.successRate >= 70 ? 'up' : 'down'}
                    />
                    <BlueprintKPI
                        label="Total Revenue"
                        value={formatCurrency(stats.totalAmount - stats.totalRefunded)}
                        code="REVENUE-001"
                    />
                    <BlueprintKPI
                        label="Total Refunded"
                        value={formatCurrency(stats.totalRefunded)}
                        code="REFUND-001"
                    />
                </div>
            )}

            {/* Filters and Search */}
            <BlueprintCard>
                <div className="flex flex-col lg:flex-row gap-4">
                    <div className="flex-1">
                        <input
                            type="text"
                            aria-label="Search transactions"
                            placeholder="Search by customer, email, transaction ID..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full px-4 py-2 border border-[var(--ink)]/20 rounded-lg bg-[var(--canvas)] font-mono text-sm focus:outline-none focus:border-[var(--blueprint)]"
                        />
                    </div>
                    <div className="flex gap-2">
                        {['all', 'COMPLETED', 'PENDING', 'FAILED', 'REFUNDED'].map((status) => (
                            <BlueprintButton
                                key={status}
                                type="button"
                                onClick={() => setFilter(status)}
                                variant={filter === status ? 'primary' : 'ghost'}
                                size="sm"
                                className="capitalize"
                            >
                                {status}
                            </BlueprintButton>
                        ))}
                    </div>
                </div>
            </BlueprintCard>

            {/* Transactions Table */}
            <BlueprintCard>
                <div className="mb-4">
                    <h3 className="font-technical text-lg text-[var(--ink)] mb-1">
                        TRANSACTION HISTORY
                    </h3>
                    <p className="text-sm text-[var(--ink)]/60 font-mono">
                        {filteredTransactions.length} of {transactions.length} transactions
                    </p>
                </div>

                <BlueprintTable<PaymentTransaction>
                    data={filteredTransactions}
                    columns={columns}
                    className="border-0"
                />
            </BlueprintCard>

            {/* Footer */}
            <div className="text-center py-4">
                <div className="text-xs font-technical text-[var(--ink)]/60">
                    PHONEPE GATEWAY v2.0 • SECURE • ENCRYPTED • PCI-DSS COMPLIANT
                </div>
            </div>
        </div>
    );
}

export default PhonePePaymentDashboard;
