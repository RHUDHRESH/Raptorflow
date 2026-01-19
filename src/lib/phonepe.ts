import crypto from 'crypto'

export class PhonePeService {
    generateTransactionId(): string {
        return 'MT' + Date.now() + crypto.randomBytes(4).toString('hex').substr(0, 4)
    }

    /**
     * Initiates payment by calling the backend SDK gateway
     */
    async initiatePayment(transactionId: string, amount: number, userId: string): Promise<{ url: string; error?: string }> {
        try {
            const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            console.log('Initiating PhonePe payment via backend proxy:', { transactionId, amount, userId, apiBaseUrl });

            const response = await fetch(`${apiBaseUrl}/api/v1/payments/v2/initiate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    amount: amount,
                    merchant_order_id: transactionId,
                    redirect_url: `${window.location.origin}/onboarding/payment/status`,
                    callback_url: `${apiBaseUrl}/api/v1/payments/v2/webhook`,
                    customer_info: {
                        id: userId,
                        name: 'User', // In production, get from profile
                        email: 'user@example.com',
                        mobile: '9999999999'
                    }
                })
            });

            const data = await response.json();

            if (response.ok && data.checkout_url) {
                return { url: data.checkout_url };
            }

            console.error('PhonePe Backend Init Failed:', data);
            return { url: '', error: data.error || 'Payment initialization failed' };
        } catch (err) {
            console.error('PhonePe Proxy Error:', err);
            return { url: '', error: 'Failed to connect to payment gateway' };
        }
    }

    /**
     * Verifies payment status via backend
     */
    async checkStatus(transactionId: string): Promise<{ status: string; error?: string }> {
        try {
            const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiBaseUrl}/api/v1/payments/v2/status/${transactionId}`);
            const data = await response.json();

            if (response.ok) {
                return { status: data.status };
            }

            return { status: 'ERROR', error: data.error };
        } catch (err) {
            return { status: 'ERROR', error: 'Failed to check status' };
        }
    }
}

export const phonePeService = new PhonePeService()
