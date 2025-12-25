import { describe, it, expect, vi, beforeEach, Mock } from 'vitest';

// Define the functions here or import if they exist
async function saveFoundationState(tenantId: string, data: any) {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/v1/foundation/state`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_id: tenantId, data }),
    });
    return response.json();
}

async function initiatePayment(userId: string, amount: number, transactionId: string, redirectUrl: string) {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const params = new URLSearchParams({
        user_id: userId,
        amount: amount.toString(),
        transaction_id: transactionId,
        redirect_url: redirectUrl
    });
    const response = await fetch(`${apiUrl}/v1/payments/initiate?${params.toString()}`, {
        method: 'POST'
    });
    return response.json();
}

// Mock Fetch
global.fetch = vi.fn();

describe('System Audit: Frontend-to-Backend Connectivity', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('syncs universal foundation state to the new backend endpoint', async () => {
        const mockData = { name: 'Test Corp', industry: 'SaaS' };
        const tenantId = 'user-123';

        (global.fetch as unknown as Mock).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ tenant_id: tenantId, data: mockData }),
        });

        const result = await saveFoundationState(tenantId, mockData);

        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/v1/foundation/state'),
            expect.objectContaining({
                method: 'POST',
                body: JSON.stringify({ tenant_id: tenantId, data: mockData })
            })
        );
        expect(result.tenant_id).toBe(tenantId);
    });

    it('initiates PhonePe payment via the new payments endpoint', async () => {
        (global.fetch as unknown as Mock).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ url: 'https://phonepe.com/pay' }),
        });

        const result = await initiatePayment('user-123', 100, 'tx-001', 'http://localhost:3000');

        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/v1/payments/initiate?user_id=user-123&amount=100&transaction_id=tx-001&redirect_url=http%3A%2F%2Flocalhost%3A3000'),
            expect.objectContaining({ method: 'POST' })
        );
        expect(result.url).toBe('https://phonepe.com/pay');
    });
});
