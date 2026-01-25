import { BlackboxStrategyRequest, BlackboxStrategy } from '../types';
import { BlackboxDomain } from '../domain/BlackboxDomain';
import { createClient } from '../../../lib/supabaseServer';

export class BlackboxService {
  /**
   * Generates a new strategy based on objective and risk tolerance.
   */
  async generateStrategy(request: BlackboxStrategyRequest): Promise<BlackboxStrategy> {
    const prompt = BlackboxDomain.generateStrategyPrompt(request);
    
    // In a real implementation, this would call Vertex AI
    // For now, we simulate the database persistence of a generated strategy
    const supabase = await createClient();
    
    const { data, error } = await supabase
      .from('strategies')
      .insert({
        workspace_id: request.workspace_id,
        objective: request.objective,
        risk_tolerance: request.risk_tolerance,
        status: 'generated',
        created_at: new Date().toISOString()
      })
      .select()
      .single();

    if (error) throw new Error(`Failed to save strategy: ${error.message}`);
    
    return data as BlackboxStrategy;
  }
}

export const blackboxService = new BlackboxService();
