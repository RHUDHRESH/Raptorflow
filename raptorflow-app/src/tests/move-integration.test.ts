import { describe, it, expect, vi, beforeEach, Mock } from 'vitest';
import { generateWeeklyMoves, getMovesStatus } from '@/lib/campaigns';

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

describe('Move Generation & Status Tracking Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('successfully triggers move generation', async () => {
        (global.fetch as unknown as Mock).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'started', campaign_id: 'test-camp-id' }),
        });

        const result = await generateWeeklyMoves('test-camp-id');

        expect(result).toEqual({ status: 'started', campaign_id: 'test-camp-id' });
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/v1/moves/generate-weekly/test-camp-id'),
            expect.objectContaining({ method: 'POST' })
        );
    });

    it('successfully polls move generation status', async () => {
        (global.fetch as unknown as Mock).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'execution', messages: ['Processing...'] }),
        });

        const result = await getMovesStatus('test-camp-id');

        expect(result?.status).toBe('execution');
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/v1/moves/generate-weekly/test-camp-id/status')
        );
    });

    it('handles status errors gracefully', async () => {
        (global.fetch as unknown as Mock).mockResolvedValueOnce({
            ok: false,
            status: 404,
        });

        const result = await getMovesStatus('non-existent');
        expect(result).toBeNull();
    });

    it('correctly maps complex Move DB records including refinement and tools', async () => {
        const { getMovesByCampaign } = await import('@/lib/campaigns');

        const mockDBData = [{
            id: 'move-uuid-1',
            campaign_id: 'camp-id',
            title: 'Hardened Move',
            description: 'Execute deep research on SaaS founders.',
            status: 'active',
            priority: 1,
            created_at: new Date().toISOString(),
            tool_requirements: ['Search', 'Copy'],
            refinement_data: {
                estimated_effort: 'High',
                deadline: '2025-12-31',
                rationale: 'High priority research'
            }
        }];

        const { supabase } = await import('@/lib/supabase');
        (supabase.from as unknown as Mock).mockReturnValueOnce({
            select: vi.fn().mockReturnThis(),
            eq: vi.fn().mockReturnThis(),
            order: vi.fn().mockResolvedValueOnce({ data: mockDBData, error: null }),
        });

        const moves = await getMovesByCampaign('camp-id');
        const m = moves[0];

        expect(m.id).toBe('move-uuid-1');
        expect(m.description).toBe(mockDBData[0].description);
        expect(m.owner).toBe('AI Agent'); // Priority 1 heuristic
        expect(m.toolRequirements).toEqual(['Search', 'Copy']);
        expect(m.refinementData?.estimated_effort).toBe('High');
    });
});
