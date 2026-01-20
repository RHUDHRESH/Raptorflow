import { createClient } from '../../../lib/supabaseServer';
import { FoundationDomain } from '../domain/FoundationDomain';
import { Foundation } from '../types';

export class FoundationService {
  /**
   * Retrieves the foundation data for a given workspace.
   */
  async getFoundation(workspaceId: string): Promise<Foundation | null> {
    const supabase = createClient();
    
    const { data, error } = await supabase
      .from('foundations')
      .select('*')
      .eq('workspace_id', workspaceId)
      .single();

    if (error || !data) {
      return null;
    }

    return data as Foundation;
  }

  /**
   * Updates foundation data for a workspace.
   */
  async updateFoundation(workspaceId: string, data: Partial<Foundation>): Promise<Foundation> {
    // 1. Validate domain rules
    FoundationDomain.validate(data);

    const supabase = createClient();
    
    const { data: updated, error } = await supabase
      .from('foundations')
      .update({
        ...data,
        updated_at: new Date().toISOString()
      })
      .eq('workspace_id', workspaceId)
      .select()
      .single();

    if (error) {
      throw new Error(`Failed to update foundation: ${error.message}`);
    }

    return updated as Foundation;
  }
}

export const foundationService = new FoundationService();
