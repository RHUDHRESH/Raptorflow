import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
    createCampaign,
    triggerCampaignInference,
    getCampaignGantt,
    generateWeeklyMoves,
    updateMoveStatus
} from '@/lib/campaigns';

// Mock Supabase
vi.mock('@/lib/supabase', () => ({
    supabase: {
        from: vi.fn(() => ({
            insert: vi.fn().mockResolvedValue({ error: null }),
            update: vi.fn().mockReturnThis(),
            select: vi.fn().mockReturnThis(),
            eq: vi.fn().mockReturnThis(),
            order: vi.fn().mockReturnThis(),
            single: vi.fn().mockResolvedValue({ data: {}, error: null }),
        })),
    },
}));

// Mock Fetch
global.fetch = vi.fn();

describe('E2E Smoke Test: Full User Journey', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('completes the full campaign-to-move lifecycle', async () => {
        const campaignId = 'e2e-test-uuid';

        // 1. Create Campaign
        await createCampaign({
            id: campaignId,
            name: 'E2E Campaign',
            objective: 'acquire',
            offer: 'book_call',
            channels: ['linkedin'],
            duration: 90,
            moveLength: 14,
            dailyEffort: 30,
            status: 'active',
            createdAt: new Date().toISOString(),
        });

        // 2. Trigger Inference
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'started', campaign_id: campaignId }),
        });
        const inferenceResult = await triggerCampaignInference(campaignId);
        expect(inferenceResult.status).toBe('started');

        // 3. Fetch Gantt Chart
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ items: [{ id: 'milestone-1', task: 'Setup', progress: 0 }] }),
        });
        const gantt = await getCampaignGantt(campaignId);
        expect(gantt.items.length).toBeGreaterThan(0);

        // 4. Decompose Milestone into Moves
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'started', message: 'Decomposing...' }),
        });
        const decompositionResult = await generateWeeklyMoves(campaignId);
        expect(decompositionResult.status).toBe('started');

        // 5. Complete a Move
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'updated' }),
        });
        const updateResult = await updateMoveStatus('move-1', 'completed', { result: 'Success' });
        expect(updateResult.status).toBe('updated');
    });
});
