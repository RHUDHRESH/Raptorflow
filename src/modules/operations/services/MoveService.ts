import { createClient } from '../../../lib/supabaseServer';
import { StrategicMove } from '../types';
import { OperationsDomain } from '../domain/OperationsDomain';

export class MoveService {
  /**
   * Retrieves all moves for a workspace.
   */
  async getMoves(workspaceId: string): Promise<StrategicMove[]> {
    const supabase = await createClient();
    const { data, error } = await supabase
      .from('moves')
      .select('*')
      .eq('workspace_id', workspaceId);

    if (error) throw new Error(`Failed to fetch moves: ${error.message}`);
    return data as StrategicMove[];
  }

  /**
   * Synchronizes moves within a campaign, applying 'Breathing Arcs' logic.
   */
  async synchronizeCampaign(campaignId: string): Promise<void> {
    const supabase = await createClient();
    const { data: moves, error } = await supabase
      .from('moves')
      .select('*')
      .eq('campaign_id', campaignId);

    if (error || !moves) return;

    const typedMoves = moves as StrategicMove[];
    const shifts = OperationsDomain.calculateArcShift(typedMoves);

    if (shifts.size === 0) return;

    // Apply shifts to the database (In a real implementation, this would be a bulk update)
    for (const [moveId, days] of shifts.entries()) {
      const move = typedMoves.find(m => m.id === moveId);
      if (!move) continue;

      const newEndDate = new Date(new Date(move.end_date).getTime() + days * 24 * 60 * 60 * 1000);

      await supabase
        .from('moves')
        .update({ end_date: newEndDate.toISOString() })
        .eq('id', moveId);
    }
  }
}

export const moveService = new MoveService();
