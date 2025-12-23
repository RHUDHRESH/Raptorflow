import { describe, it, expect, vi, beforeEach } from 'vitest';
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
        (global.fetch as any).mockResolvedValueOnce({
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
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'execution', messages: ['Processing...'] }),
        });

        const result = await getMovesStatus('test-camp-id');

        expect(result.status).toBe('execution');
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/v1/moves/generate-weekly/test-camp-id/status')
        );
    });

    it('handles status errors gracefully', async () => {
        (global.fetch as any).mockResolvedValueOnce({
            ok: false,
            status: 404,
        });

        const result = await getMovesStatus('non-existent');
        expect(result).toBeNull();
    });
});
