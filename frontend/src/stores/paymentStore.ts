"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

/* ══════════════════════════════════════════════════════════════════════════════
   PHONEPE PAYMENT STORE — Raptorflow Payment State Management
   Features:
   - Payment transaction state management
   - Real-time status updates
   - Payment history tracking
   - Error handling and recovery
   - Persistent storage with Zustand
   ══════════════════════════════════════════════════════════════════════════════ */

// --- Types ---
type PaymentMetadata = Record<string, unknown>;

interface PaymentInstrument {
    type: string;
    provider?: string;
    maskedNumber?: string;
    [key: string]: unknown;
}

export interface PaymentTransaction {
    id: string;
    transactionId: string;
    merchantOrderId: string;
    merchantTransactionId: string;
    amount: number;
    currency: string;
    customerInfo: {
        id: string;
        name: string;
        email: string;
        mobile: string;
    };
    status: 'INITIATED' | 'PENDING' | 'COMPLETED' | 'FAILED' | 'REFUNDED' | 'CANCELLED';
    paymentMode?: string;
    phonepeTransactionId?: string;
    paymentInstrument?: PaymentInstrument;
    redirectUrl?: string;
    callbackUrl?: string;
    checkoutUrl?: string;
    metadata?: PaymentMetadata;
    createdAt: string;
    updatedAt: string;
    completedAt?: string;
    error?: string;
}

export interface PaymentRefund {
    id: string;
    refundId: string;
    merchantRefundId: string;
    transactionId: string;
    refundAmount: number;
    refundReason: string;
    status: 'PROCESSING' | 'COMPLETED' | 'FAILED';
    phonepeRefundId?: string;
    metadata?: PaymentMetadata;
    createdAt: string;
    updatedAt: string;
    completedAt?: string;
    error?: string;
}

export interface PaymentStats {
    totalTransactions: number;
    completedTransactions: number;
    failedTransactions: number;
    pendingTransactions: number;
    refundedTransactions: number;
    totalAmount: number;
    totalRefunded: number;
    successRate: number;
    averageTransactionValue: number;
}

export interface PaymentState {
    // Current transaction
    currentTransaction: PaymentTransaction | null;

    // Transaction history
    transactions: PaymentTransaction[];
    refunds: PaymentRefund[];

    // Loading states
    isLoading: boolean;
    isInitiating: boolean;
    isCheckingStatus: boolean;
    isProcessingRefund: boolean;

    // Error handling
    error: string | null;
    lastError: string | null;

    // Statistics
    stats: PaymentStats | null;

    // Filters
    statusFilter: string;
    dateFilter: {
        startDate: string | null;
        endDate: string | null;
    };
    searchQuery: string;

    // Actions
    initiatePayment: (amount: number, customerInfo: PaymentTransaction['customerInfo'], metadata?: PaymentMetadata) => Promise<string>;
    checkPaymentStatus: (transactionId: string) => Promise<void>;
    processRefund: (transactionId: string, refundAmount: number, reason: string) => Promise<void>;
    loadTransactions: () => Promise<void>;
    loadStats: () => Promise<void>;
    setCurrentTransaction: (transaction: PaymentTransaction | null) => void;
    updateTransactionStatus: (transactionId: string, status: PaymentTransaction['status'], data?: Partial<PaymentTransaction>) => void;
    clearError: () => void;
    setFilters: (filters: { statusFilter?: string; dateFilter?: { startDate: string | null; endDate: string | null }; searchQuery?: string }) => void;

    // Computed
    getTransactionById: (transactionId: string) => PaymentTransaction | undefined;
    getTransactionsByStatus: (status: PaymentTransaction['status']) => PaymentTransaction[];
    getFilteredTransactions: () => PaymentTransaction[];
    getRecentTransactions: (limit?: number) => PaymentTransaction[];
}

// --- Helper Functions ---
const generateOrderId = (): string => {
    const timestamp = Date.now().toString();
    const random = Math.random().toString(36).substring(2, 8);
    return `RF${timestamp}${random}`.toUpperCase();
};

const generateTransactionId = (): string => {
    const timestamp = Date.now().toString();
    const random = Math.random().toString(36).substring(2, 8);
    return `TXN${timestamp}${random}`.toUpperCase();
};

const calculateStats = (transactions: PaymentTransaction[], refunds: PaymentRefund[]): PaymentStats => {
    const totalTransactions = transactions.length;
    const completedTransactions = transactions.filter(t => t.status === 'COMPLETED').length;
    const failedTransactions = transactions.filter(t => t.status === 'FAILED').length;
    const pendingTransactions = transactions.filter(t => t.status === 'PENDING').length;
    const refundedTransactions = transactions.filter(t => t.status === 'REFUNDED').length;

    const totalAmount = transactions.reduce((sum, t) => sum + t.amount, 0);
    const totalRefunded = refunds.reduce((sum, r) => sum + r.refundAmount, 0);

    const successRate = totalTransactions > 0 ? (completedTransactions / totalTransactions) * 100 : 0;
    const averageTransactionValue = completedTransactions > 0 ? totalAmount / completedTransactions : 0;

    return {
        totalTransactions,
        completedTransactions,
        failedTransactions,
        pendingTransactions,
        refundedTransactions,
        totalAmount,
        totalRefunded,
        successRate,
        averageTransactionValue
    };
};

// --- Store ---
export const usePaymentStore = create<PaymentState>()(
    persist(
        (set, get) => ({
            // Initial state
            currentTransaction: null,
            transactions: [],
            refunds: [],
            isLoading: false,
            isInitiating: false,
            isCheckingStatus: false,
            isProcessingRefund: false,
            error: null,
            lastError: null,
            stats: null,
            statusFilter: 'all',
            dateFilter: {
                startDate: null,
                endDate: null
            },
            searchQuery: '',

            // Actions
            initiatePayment: async (amount, customerInfo, metadata = {}) => {
                set({ isInitiating: true, error: null });

                try {
                    const merchantOrderId = generateOrderId();
                    const merchantTransactionId = generateTransactionId();

                    // Create transaction record
                    const newTransaction: PaymentTransaction = {
                        id: merchantTransactionId,
                        transactionId: merchantTransactionId,
                        merchantOrderId,
                        merchantTransactionId,
                        amount,
                        currency: 'INR',
                        customerInfo,
                        status: 'INITIATED',
                        redirectUrl: `${window.location.origin}/payment/success`,
                        callbackUrl: `${window.location.origin}/api/payments/webhook`,
                        metadata: {
                            source: 'raptorflow_web',
                            timestamp: new Date().toISOString(),
                            ...metadata
                        },
                        createdAt: new Date().toISOString(),
                        updatedAt: new Date().toISOString()
                    };

                    // Call backend API
                    const response = await fetch('/api/payments/initiate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            amount,
                            merchant_order_id: merchantOrderId,
                            redirect_url: newTransaction.redirectUrl,
                            callback_url: newTransaction.callbackUrl,
                            customer_info: customerInfo,
                            metadata: newTransaction.metadata
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Update transaction with response data
                        const updatedTransaction = {
                            ...newTransaction,
                            transactionId: data.transaction_id,
                            phonepeTransactionId: data.phonepe_transaction_id,
                            checkoutUrl: data.checkout_url,
                            status: 'PENDING' as const
                        };

                        set(state => ({
                            currentTransaction: updatedTransaction,
                            transactions: [updatedTransaction, ...state.transactions],
                            isInitiating: false,
                            stats: calculateStats([updatedTransaction, ...get().transactions], get().refunds)
                        }));

                        // Redirect to PhonePe
                        if (data.checkout_url) {
                            window.location.href = data.checkout_url;
                        }

                        return data.transaction_id;
                    } else {
                        throw new Error(data.error || 'Payment initiation failed');
                    }

                } catch (error) {
                    const errorMessage = error instanceof Error ? error.message : 'Payment initiation failed';
                    set({
                        error: errorMessage,
                        lastError: errorMessage,
                        isInitiating: false
                    });
                    throw error;
                }
            },

            checkPaymentStatus: async (transactionId) => {
                set({ isCheckingStatus: true, error: null });

                try {
                    const response = await fetch(`/api/payments/status/${transactionId}`);
                    const data = await response.json();

                    if (data.success) {
                        const updatedTransaction: Partial<PaymentTransaction> = {
                            status: data.status,
                            paymentMode: data.payment_mode,
                            paymentInstrument: data.payment_instrument,
                            completedAt: data.status === 'COMPLETED' ? new Date().toISOString() : undefined,
                            updatedAt: new Date().toISOString(),
                            error: data.error
                        };

                        get().updateTransactionStatus(transactionId, data.status, updatedTransaction);
                    } else {
                        throw new Error(data.error || 'Failed to check payment status');
                    }

                } catch (error) {
                    const errorMessage = error instanceof Error ? error.message : 'Failed to check payment status';
                    set({
                        error: errorMessage,
                        lastError: errorMessage,
                        isCheckingStatus: false
                    });
                } finally {
                    set({ isCheckingStatus: false });
                }
            },

            processRefund: async (transactionId, refundAmount, reason) => {
                set({ isProcessingRefund: true, error: null });

                try {
                    const response = await fetch('/api/payments/refund', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            transaction_id: transactionId,
                            refund_amount: refundAmount,
                            refund_reason: reason
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        const newRefund: PaymentRefund = {
                            id: data.refund_id,
                            refundId: data.refund_id,
                            merchantRefundId: data.refund_id,
                            transactionId,
                            refundAmount,
                            refundReason: reason,
                            status: 'PROCESSING',
                            phonepeRefundId: data.phonepe_refund_id,
                            createdAt: new Date().toISOString(),
                            updatedAt: new Date().toISOString()
                        };

                        set(state => ({
                            refunds: [newRefund, ...state.refunds],
                            isProcessingRefund: false
                        }));
                    } else {
                        throw new Error(data.error || 'Refund processing failed');
                    }

                } catch (error) {
                    const errorMessage = error instanceof Error ? error.message : 'Refund processing failed';
                    set({
                        error: errorMessage,
                        lastError: errorMessage,
                        isProcessingRefund: false
                    });
                }
            },

            loadTransactions: async () => {
                set({ isLoading: true, error: null });

                try {
                    // Replace with actual API call
                    // const response = await fetch('/api/payments/transactions');
                    // const data = await response.json();

                    // Mock data for now
                    const mockTransactions: PaymentTransaction[] = [];

                    set({
                        transactions: mockTransactions,
                        isLoading: false,
                        stats: calculateStats(mockTransactions, get().refunds)
                    });

                } catch (error) {
                    const errorMessage = error instanceof Error ? error.message : 'Failed to load transactions';
                    set({
                        error: errorMessage,
                        lastError: errorMessage,
                        isLoading: false
                    });
                }
            },

            loadStats: async () => {
                try {
                    // Replace with actual API call
                    // const response = await fetch('/api/payments/stats');
                    // const data = await response.json();

                    const stats = calculateStats(get().transactions, get().refunds);
                    set({ stats });

                } catch (error) {
                    const errorMessage = error instanceof Error ? error.message : 'Failed to load stats';
                    set({ error: errorMessage, lastError: errorMessage });
                }
            },

            setCurrentTransaction: (transaction) => {
                set({ currentTransaction: transaction });
            },

            updateTransactionStatus: (transactionId, status, data = {}) => {
                set(state => ({
                    transactions: state.transactions.map(t =>
                        t.transactionId === transactionId
                            ? {
                                ...t,
                                status,
                                ...data,
                                updatedAt: new Date().toISOString(),
                                completedAt: status === 'COMPLETED' ? new Date().toISOString() : t.completedAt
                            }
                            : t
                    ),
                    currentTransaction: state.currentTransaction?.transactionId === transactionId
                        ? { ...state.currentTransaction, status, ...data, updatedAt: new Date().toISOString() }
                        : state.currentTransaction,
                    stats: calculateStats(
                        state.transactions.map(t =>
                            t.transactionId === transactionId
                                ? { ...t, status, ...data, updatedAt: new Date().toISOString() }
                                : t
                        ),
                        state.refunds
                    )
                }));
            },

            clearError: () => {
                set({ error: null });
            },

            setFilters: (filters) => {
                set(state => ({
                    statusFilter: filters.statusFilter ?? state.statusFilter,
                    dateFilter: filters.dateFilter ?? state.dateFilter,
                    searchQuery: filters.searchQuery ?? state.searchQuery
                }));
            },

            // Computed
            getTransactionById: (transactionId) => {
                return get().transactions.find(t => t.transactionId === transactionId);
            },

            getTransactionsByStatus: (status) => {
                return get().transactions.filter(t => t.status === status);
            },

            getFilteredTransactions: () => {
                const { transactions, statusFilter, dateFilter, searchQuery } = get();

                return transactions.filter(transaction => {
                    // Status filter
                    if (statusFilter !== 'all' && transaction.status !== statusFilter) {
                        return false;
                    }

                    // Date filter
                    if (dateFilter.startDate && new Date(transaction.createdAt) < new Date(dateFilter.startDate)) {
                        return false;
                    }
                    if (dateFilter.endDate && new Date(transaction.createdAt) > new Date(dateFilter.endDate)) {
                        return false;
                    }

                    // Search query
                    if (searchQuery) {
                        const query = searchQuery.toLowerCase();
                        return (
                            transaction.customerInfo.name.toLowerCase().includes(query) ||
                            transaction.customerInfo.email.toLowerCase().includes(query) ||
                            transaction.transactionId.toLowerCase().includes(query) ||
                            transaction.merchantOrderId.toLowerCase().includes(query)
                        );
                    }

                    return true;
                });
            },

            getRecentTransactions: (limit = 10) => {
                return get().transactions
                    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
                    .slice(0, limit);
            }
        }),
        {
            name: "raptorflow-payments",
            partialize: (state) => ({
                transactions: state.transactions,
                refunds: state.refunds,
                currentTransaction: state.currentTransaction,
                stats: state.stats
            })
        }
    )
);
