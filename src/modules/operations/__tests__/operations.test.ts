import { describe, test, expect } from 'vitest';
import { OperationsDomain } from '../domain/OperationsDomain';
import { StrategicMove } from '../types';

describe('Operations Domain', () => {
  describe('Dependency Resolution', () => {
    test('should block move if dependencies are not completed', () => {
      const move: any = { id: '2', dependencies: ['1'], status: 'pending' };
      const deps: any[] = [{ id: '1', status: 'active' }];
      
      expect(OperationsDomain.isMoveBlocked(move, deps)).toBe(true);
    });

    test('should NOT block move if dependencies are completed', () => {
      const move: any = { id: '2', dependencies: ['1'], status: 'pending' };
      const deps: any[] = [{ id: '1', status: 'completed' }];
      
      expect(OperationsDomain.isMoveBlocked(move, deps)).toBe(false);
    });
  });

  describe('Breathing Arcs', () => {
    test('should calculate shift for delayed moves', () => {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      
      const moves: any[] = [
        { id: '1', status: 'active', end_date: yesterday.toISOString(), dependencies: [] }
      ];

      const shifts = OperationsDomain.calculateArcShift(moves);
      expect(shifts.get('1')).toBeGreaterThanOrEqual(1);
    });

    test('should propagate shift to dependent moves', () => {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      
      const moves: any[] = [
        { id: '1', status: 'active', end_date: yesterday.toISOString(), dependencies: [] },
        { id: '2', status: 'pending', end_date: new Date().toISOString(), dependencies: ['1'] }
      ];

      const shifts = OperationsDomain.calculateArcShift(moves);
      expect(shifts.get('2')).toBe(shifts.get('1'));
    });
  });
});
