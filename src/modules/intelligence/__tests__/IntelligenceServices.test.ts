import { describe, test, expect, vi } from 'vitest';
import { TitanService } from '../services/TitanService';
import { BlackboxService } from '../services/BlackboxService';
import { TitanMode } from '../types';

// Mock Supabase
vi.mock('../../../lib/supabaseServer', () => ({
  createClient: vi.fn(() => ({
    from: vi.fn(() => ({
      insert: vi.fn(() => ({
        select: vi.fn(() => ({
          single: vi.fn(() => Promise.resolve({ data: { id: 'test-id' }, error: null })),
        })),
      })),
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          single: vi.fn(() => Promise.resolve({ data: { id: 'test-id', topic: 'AI' }, error: null })),
        })),
      })),
    })),
  })),
}));

describe('Intelligence Services', () => {
  test('TitanService should start research', async () => {
    const service = new TitanService();
    const id = await service.startResearch({
      topic: 'Future of AI',
      mode: TitanMode.LITE,
      workspace_id: 'ws1'
    });
    expect(id).toBe('test-id');
  });

  test('BlackboxService should generate strategy', async () => {
    const service = new BlackboxService();
    const strategy = await service.generateStrategy({
      workspace_id: 'ws1',
      objective: 'Dominate Market',
      risk_tolerance: 0.5
    });
    expect(strategy.id).toBe('test-id');
  });
});
