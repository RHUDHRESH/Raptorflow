import { StrategicMove } from '../types';

export class OperationsDomain {
  /**
   * Resolves whether a move is blocked by its dependencies.
   */
  static isMoveBlocked(move: StrategicMove, dependentMoves: StrategicMove[]): boolean {
    if (!move.dependencies || move.dependencies.length === 0) {
      return false;
    }

    const uncompletedDependencies = dependentMoves.filter(
      dm => move.dependencies.includes(dm.id) && dm.status !== 'completed'
    );

    return uncompletedDependencies.length > 0;
  }

  /**
   * 'Breathing Arcs' logic:
   * If a move is delayed (end_date in the past but not completed), 
   * calculate the necessary shift for all subsequent dependent moves.
   */
  static calculateArcShift(moves: StrategicMove[]): Map<string, number> {
    const shifts = new Map<string, number>();
    const now = new Date();

    // 1. Identify delayed moves and their delay in days
    moves.forEach(move => {
      const endDate = new Date(move.end_date);
      if (move.status !== 'completed' && endDate < now) {
        const delayDays = Math.ceil((now.getTime() - endDate.getTime()) / (1000 * 3600 * 24));
        shifts.set(move.id, delayDays);
      }
    });

    // 2. Propagate shifts to dependent moves (Simplified version)
    // In a full implementation, this would handle complex dependency trees.
    moves.forEach(move => {
      move.dependencies.forEach(depId => {
        if (shifts.has(depId)) {
          const currentShift = shifts.get(move.id) || 0;
          const depShift = shifts.get(depId)!;
          shifts.set(move.id, Math.max(currentShift, depShift));
        }
      });
    });

    return shifts;
  }
}
