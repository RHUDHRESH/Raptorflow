import { TitanMode, TitanResearchRequest, TitanResearchResult } from '../types';
import { TitanDomain } from '../domain/TitanDomain';
import { createClient } from '../../../lib/supabaseServer';

export class TitanService {
  /**
   * Orchestrates a research request.
   * Note: Actual scraping still happens via Python/Playwright for now (Stealth Pool),
   * but the orchestration and synthesis result handling is moved here.
   */
  async startResearch(request: TitanResearchRequest): Promise<string> {
    const settings = TitanDomain.getResearchSettings(request.mode);
    const supabase = await createClient();

    // Log the research initiation
    const { data, error } = await supabase
      .from('intelligence_logs')
      .insert({
        workspace_id: request.workspace_id,
        topic: request.topic,
        mode: request.mode,
        settings,
        status: 'initiated',
        created_at: new Date().toISOString()
      })
      .select()
      .single();

    if (error) throw new Error(`Failed to initiate research: ${error.message}`);

    return data.id;
  }

  async getResearchResult(id: string): Promise<TitanResearchResult | null> {
    const supabase = await createClient();
    const { data, error } = await supabase
      .from('intelligence_results')
      .select('*')
      .eq('id', id)
      .single();

    if (error || !data) return null;
    return data as TitanResearchResult;
  }
}

export const titanService = new TitanService();
