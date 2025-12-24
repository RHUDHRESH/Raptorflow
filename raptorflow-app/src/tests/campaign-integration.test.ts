import { describe, it, expect, vi, beforeEach, Mock } from 'vitest';
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
        (global.fetch as unknown as vi.Mock).mockResolvedValueOnce({
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
        (global.fetch as unknown as vi.Mock).mockResolvedValueOnce({
            ok: false,
            status: 500,
        });

        const result = await triggerCampaignInference('test-uuid');
        expect(result).toBeNull();
    });

    it('polls status correctly', async () => {
        // Mock initial status check
        (global.fetch as unknown as vi.Mock).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'planning', messages: ['Starting...'] }),
        });

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/campaigns/generate-arc/test-uuid/status`);
        const data = await response.json();

        expect(data.status).toBe('planning');
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/v1/campaigns/generate-arc/test-uuid/status')
        );
    });

    it('successfully fetches Gantt data', async () => {
        const mockGantt = { items: [{ id: '1', task: 'Task 1', progress: 0.5 }] };
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => mockGantt,
        });

        const { getCampaignGantt } = await import('@/lib/campaigns');
        const result = await getCampaignGantt('test-uuid');

        expect(result).toEqual(mockGantt);
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/v1/campaigns/test-uuid/gantt')
        );
    });

    it('correctly maps complex DB records including strategy arc and audit data', async () => {
        const { getCampaigns } = await import('@/lib/campaigns');

        const mockDBData = [{
            id: 'test-uuid-2',
            title: 'Hardened Campaign',
            objective: 'convert',
            status: 'active',
            created_at: new Date().toISOString(),
            start_date: new Date().toISOString(),
            arc_data: {
                campaign_title: 'SOTA Growth Plan',
                monthly_plans: [{ month_number: 1, theme: 'Launch' }]
            },
            audit_data: {
                alignments: [
                    { uvp_title: 'UVP 1', is_aligned: true, score: 0.9, feedback: 'Perfect' }
                ],
                overall_score: 0.95
            }
        }];

        const { supabase } = await import('@/lib/supabase');
        (supabase.from as unknown as Mock).mockReturnValueOnce({
            select: vi.fn().mockReturnThis(),
            order: vi.fn().mockResolvedValueOnce({ data: mockDBData, error: null }),
        });

        const campaigns = await getCampaigns();
        const c = campaigns[0];

        expect(c.id).toBe('test-uuid-2');
        expect(c.strategyArc).toEqual(mockDBData[0].arc_data);
        expect(c.auditData).toHaveLength(1);
        expect(c.auditData?.[0].uvp_title).toBe('UVP 1');
        expect(c.qualityScore).toBe(0.95);
    });
});
