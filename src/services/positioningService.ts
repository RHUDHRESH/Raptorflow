import { supabase, isSupabaseConfigured } from '../lib/supabase';
import { PositioningFormValues, PositioningRecord } from '../lib/validation/positioning';

// Mock data for demo/dev mode
const MOCK_POSITIONING: PositioningRecord = {
    id: 'mock-pos-1',
    workspace_id: 'mock-workspace-1',
    status: 'published',
    founder_name: 'Demo Founder',
    founder_background: 'Serial Entrepreneur',
    brand_name: 'RaptorFlow',
    category: 'Agentic Workspace',
    audience_summary: 'Product Leaders',
    core_pain: 'Fragmented workflows',
    core_promise: 'Accelerate your GTM by 10x',
    differentiator: 'The only workspace that unifies strategy, content, and execution with autonomous agents.',
    positioning_statement: 'For Product Leaders who struggle with Fragmented workflows, RaptorFlow is a Agentic Workspace that Accelerate your GTM by 10x. Unlike competitors, we The only workspace that unifies strategy, content, and execution with autonomous agents.',
    mission_statement: 'To empower every team with AI agents.',
    origin_story: 'Born from the frustration of disjointed tools.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
};

export const positioningService = {
    /**
     * Get positioning for a specific workspace
     */
    async getPositioningByWorkspaceId(workspaceId: string) {
        if (!workspaceId) throw new Error('Workspace ID is required');

        // If Supabase is not configured, return mock data for demo experience
        if (!isSupabaseConfigured()) {
            console.warn('[PositioningService] Supabase not configured. Returning mock data.');
            // Simulate network delay
            await new Promise(resolve => setTimeout(resolve, 800));
            return { data: MOCK_POSITIONING, error: null };
        }

        const { data, error } = await supabase
            .from('positioning')
            .select('*')
            .eq('workspace_id', workspaceId)
            .maybeSingle();

        if (error) {
            console.error('Error fetching positioning:', error);
            // Fallback to mock data in dev if fetch fails (optional, but good for stability)
            if ((import.meta as any).env.DEV) {
                 return { data: MOCK_POSITIONING, error: null };
            }
            throw error;
        }

        return { data: data as PositioningRecord | null, error: null };
    },

    /**
     * Create or update positioning for a workspace
     */
    async upsertPositioningForWorkspace(workspaceId: string, values: Partial<PositioningFormValues>) {
        if (!workspaceId) throw new Error('Workspace ID is required');

        // First check if a record exists
        const { data: existing } = await supabase
            .from('positioning')
            .select('id')
            .eq('workspace_id', workspaceId)
            .maybeSingle();

        let result;

        if (existing) {
            // Update
            result = await supabase
                .from('positioning')
                .update({
                    ...values,
                    updated_at: new Date().toISOString(),
                })
                .eq('id', existing.id)
                .select()
                .single();
        } else {
            // Insert
            result = await supabase
                .from('positioning')
                .insert({
                    workspace_id: workspaceId,
                    ...values,
                    status: 'draft',
                })
                .select()
                .single();
        }

        if (result.error) {
            console.error('Error saving positioning:', result.error);
            throw result.error;
        }

        return { data: result.data as PositioningRecord, error: null };
    },

    /**
     * Generate a positioning statement using AI (Stub)
     */
    async generatePositioningStatement(values: Partial<PositioningFormValues>) {
        // TODO: Connect to backend AI service
        // For now, return a template based on inputs
        const { brand_name, category, audience_summary, core_pain, core_promise, differentiator } = values;

        if (!brand_name || !category || !audience_summary || !core_pain || !core_promise || !differentiator) {
            return null;
        }

        return `For ${audience_summary} who struggle with ${core_pain}, ${brand_name} is a ${category} that ${core_promise}. Unlike competitors, we ${differentiator}.`;
    }
};
