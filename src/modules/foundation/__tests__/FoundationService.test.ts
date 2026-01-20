import { describe, test, expect, vi, beforeEach } from 'vitest';
import { FoundationService } from '../services/FoundationService';

// Mock Supabase
vi.mock('../../../lib/supabaseServer', () => ({
  createClient: vi.fn(() => ({
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          single: vi.fn(() => Promise.resolve({ data: { id: '1', workspace_id: 'ws1', company_name: 'Test' }, error: null })),
        })),
      })),
      update: vi.fn(() => ({
        eq: vi.fn(() => ({
          select: vi.fn(() => ({
            single: vi.fn(() => Promise.resolve({ data: { id: '1', workspace_id: 'ws1', company_name: 'Updated' }, error: null })),
          })),
        })),
      })),
    })),
  })),
}));

describe('Foundation Service', () => {
  const service = new FoundationService();

  test('should get foundation', async () => {
    const data = await service.getFoundation('ws1');
    expect(data).toBeDefined();
    expect(data?.company_name).toBe('Test');
  });

  test('should update foundation', async () => {
    const data = await service.updateFoundation('ws1', { company_name: 'Updated' });
    expect(data.company_name).toBe('Updated');
  });
});
