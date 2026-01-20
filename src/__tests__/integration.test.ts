import { describe, test, expect, vi } from 'vitest';
import { foundationService } from '../modules/foundation/services/FoundationService';
import { blackboxService } from '../modules/intelligence/services/BlackboxService';
import { moveService } from '../modules/operations/services/MoveService';

// Mock all services
vi.mock('../modules/foundation/services/FoundationService', () => ({
  foundationService: {
    getFoundation: vi.fn().mockResolvedValue({ id: 'f1', company_name: 'Journey Inc' }),
  }
}));

vi.mock('../modules/intelligence/services/BlackboxService', () => ({
  blackboxService: {
    generateStrategy: vi.fn().mockResolvedValue({ id: 's1', objective: 'Growth' }),
  }
}));

vi.mock('../modules/operations/services/MoveService', () => ({
  moveService: {
    getMoves: vi.fn().mockResolvedValue([{ id: 'm1', name: 'Launch' }]),
  }
}));

describe('Full Journey Integration (Mocked)', () => {
  test('should execute full user journey from foundation to moves', async () => {
    const workspaceId = 'ws-journey';

    // 1. Foundation
    const foundation = await foundationService.getFoundation(workspaceId);
    expect(foundation?.company_name).toBe('Journey Inc');

    // 2. Intelligence (Strategy)
    const strategy = await blackboxService.generateStrategy({
      workspace_id: workspaceId,
      objective: 'Scalable Growth',
      risk_tolerance: 0.5
    });
    expect(strategy.id).toBe('s1');

    // 3. Operations (Moves)
    const moves = await moveService.getMoves(workspaceId);
    expect(moves.length).toBe(1);
    expect(moves[0].name).toBe('Launch');
  });
});
