/**
 * Payment API Service
 * Handles all payment-related API calls to the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const paymentAPI = {
    /**
     * Get all available subscription plans
     */
    async getPlans() {
        const response = await fetch(`${API_BASE_URL}/api/v1/payments/plans`);
        if (!response.ok) {
            throw new Error('Failed to fetch plans');
        }
        return response.json();
    },

    /**
     * Create a checkout session for a plan
     */
    async createCheckout(plan, billingPeriod, successUrl) {
        const token = localStorage.getItem('supabase.auth.token');

        const response = await fetch(`${API_BASE_URL}/api/v1/payments/checkout/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                plan,
                billing_period: billingPeriod,
                success_url: successUrl
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create checkout');
        }

        return response.json();
    },

    /**
     * Get current subscription status
     */
    async getSubscriptionStatus() {
        const token = localStorage.getItem('supabase.auth.token');

        const response = await fetch(`${API_BASE_URL}/api/v1/payments/subscription/status`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch subscription status');
        }

        return response.json();
    },

    /**
     * Get billing history
     */
    async getBillingHistory() {
        const token = localStorage.getItem('supabase.auth.token');

        const response = await fetch(`${API_BASE_URL}/api/v1/payments/billing/history`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch billing history');
        }

        return response.json();
    },

    /**
     * Check payment status
     */
    async checkPaymentStatus(merchantTransactionId) {
        const token = localStorage.getItem('supabase.auth.token');

        const response = await fetch(
            `${API_BASE_URL}/api/v1/payments/payment/status/${merchantTransactionId}`,
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );

        if (!response.ok) {
            throw new Error('Failed to check payment status');
        }

        return response.json();
    },

    /**
     * Cancel subscription
     */
    async cancelSubscription(reason) {
        const token = localStorage.getItem('supabase.auth.token');

        const response = await fetch(`${API_BASE_URL}/api/v1/payments/subscription/cancel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ reason })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to cancel subscription');
        }

        return response.json();
    }
};
