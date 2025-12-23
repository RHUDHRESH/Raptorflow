import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createCampaign, triggerCampaignInference } from '@/lib/campaigns';
import { Campaign } from '@/lib/campaigns-types';

// Mock Supabase
vi.mock('@/lib/supabase', () => ({
    supabase: {
        from: vi.fn(() => ({
            insert: vi.fn().mockResolvedValue({ error: null }),
            select: vi.fn().mockReturnThis(),
            eq: vi.fn().mockReturnThis(),
            single: vi.fn().mockResolvedValue({ data: {}, error: null }),
        })),
    },
}));

// Mock Fetch
global.fetch = vi.fn();

describe('Campaign Creation-to-Persistence Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('successfully creates a campaign and triggers inference', async () => {
        const mockCampaign: Campaign = {
            id: 'test-uuid',
            name: 'Test Campaign',
            objective: 'acquire',
            offer: 'book_call',
            channels: ['linkedin'],
            duration: 90,
            moveLength: 14,
            dailyEffort: 30,
            status: 'active',
            createdAt: new Date().toISOString(),
        };

        // 1. Test createCampaign (Supabase call)
        await createCampaign(mockCampaign);

        // 2. Test triggerCampaignInference (Backend API call)
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'started', campaign_id: 'test-uuid' }),
        });

        const result = await triggerCampaignInference('test-uuid');

        expect(result).toEqual({ status: 'started', campaign_id: 'test-uuid' });
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/v1/campaigns/generate-arc/test-uuid'),
            expect.objectContaining({ method: 'POST' })
        );
    });

    it('handles inference failure gracefully', async () => {
        (global.fetch as any).mockResolvedValueOnce({
            ok: false,
            status: 500,
        });

        const result = await triggerCampaignInference('test-uuid');
        expect(result).toBeNull();
    });
});
