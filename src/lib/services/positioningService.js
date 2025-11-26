/**
 * Positioning Service
 * 
 * Manages positioning statements and message architecture.
 * Positioning is the strategic foundation that everything else builds on.
 */

import { supabase } from '../supabase';

// =============================================================================
// POSITIONING CRUD
// =============================================================================

/**
 * Create a new positioning statement
 */
export const createPositioning = async (data) => {
    const { data: positioning, error } = await supabase
        .from('positioning')
        .insert([{
            workspace_id: data.workspace_id,
            name: data.name,
            for_cohort_id: data.for_cohort_id,
            problem_statement: data.problem_statement,
            category_frame: data.category_frame,
            differentiator: data.differentiator,
            reason_to_believe: data.reason_to_believe,
            competitive_alternative: data.competitive_alternative,
            is_active: data.is_active ?? true,
        }])
        .select()
        .single();

    if (error) throw error;
    return positioning;
};

/**
 * Get all positionings for a workspace
 */
export const getPositionings = async (workspaceId) => {
    const { data, error } = await supabase
        .from('positioning')
        .select(`
      *,
      cohort:cohorts(id, name, description),
      message_architecture(*)
    `)
        .eq('workspace_id', workspaceId)
        .order('created_at', { ascending: false });

    if (error) throw error;
    return data;
};

/**
 * Get a single positioning by ID
 */
export const getPositioningById = async (id) => {
    const { data, error } = await supabase
        .from('positioning')
        .select(`
      *,
      cohort:cohorts(id, name, description),
      message_architecture(*)
    `)
        .eq('id', id)
        .single();

    if (error) throw error;
    return data;
};

/**
 * Update positioning
 */
export const updatePositioning = async (id, updates) => {
    const { data, error } = await supabase
        .from('positioning')
        .update(updates)
        .eq('id', id)
        .select()
        .single();

    if (error) throw error;
    return data;
};

/**
 * Delete positioning
 */
export const deletePositioning = async (id) => {
    const { error } = await supabase
        .from('positioning')
        .delete()
        .eq('id', id);

    if (error) throw error;
};

/**
 * Set positioning as active (deactivates others)
 */
export const setActivePositioning = async (id, workspaceId) => {
    // Deactivate all others
    await supabase
        .from('positioning')
        .update({ is_active: false })
        .eq('workspace_id', workspaceId);

    // Activate this one
    const { data, error } = await supabase
        .from('positioning')
        .update({ is_active: true })
        .eq('id', id)
        .select()
        .single();

    if (error) throw error;
    return data;
};

// =============================================================================
// MESSAGE ARCHITECTURE
// =============================================================================

/**
 * Create message architecture for a positioning
 */
export const createMessageArchitecture = async (data) => {
    const { data: messageArch, error } = await supabase
        .from('message_architecture')
        .insert([{
            positioning_id: data.positioning_id,
            primary_claim: data.primary_claim,
            tagline: data.tagline,
            elevator_pitch: data.elevator_pitch,
            proof_points: data.proof_points, // Array of {id, claim, evidence, priority}
        }])
        .select()
        .single();

    if (error) throw error;
    return messageArch;
};

/**
 * Get message architecture for a positioning
 */
export const getMessageArchitecture = async (positioningId) => {
    const { data, error } = await supabase
        .from('message_architecture')
        .select('*')
        .eq('positioning_id', positioningId)
        .single();

    if (error && error.code !== 'PGRST116') throw error; // PGRST116 = not found
    return data;
};

/**
 * Update message architecture
 */
export const updateMessageArchitecture = async (id, updates) => {
    const { data, error } = await supabase
        .from('message_architecture')
        .update(updates)
        .eq('id', id)
        .select()
        .single();

    if (error) throw error;
    return data;
};

// =============================================================================
// AI-POWERED HELPERS
// =============================================================================

/**
 * Generate positioning suggestions based on cohort
 */
export const generatePositioningSuggestions = async (cohortId) => {
    // TODO: Implement AI generation
    // For now, return mock suggestions
    return {
        category_frames: [
            "The strategic marketing command center",
            "The marketing orchestration platform",
            "The campaign intelligence system"
        ],
        differentiators: [
            "that turns scattered activities into coordinated campaigns",
            "that connects strategy to execution",
            "that makes marketing measurable and repeatable"
        ],
        reasons_to_believe: [
            "because we combine AI-powered cohort intelligence with battle-tested frameworks",
            "because we track every move from positioning to performance",
            "because top marketing teams use systematic approaches, not random acts"
        ]
    };
};

/**
 * Generate message architecture from positioning
 */
export const generateMessageArchitecture = async (positioningId) => {
    const positioning = await getPositioningById(positioningId);

    // TODO: Implement AI generation
    // For now, return mock message architecture
    return {
        primary_claim: `Ship campaigns 3x faster with half the chaos`,
        tagline: "Strategic marketing, systematized",
        elevator_pitch: `${positioning.category_frame} ${positioning.differentiator}, ${positioning.reason_to_believe}.`,
        proof_points: [
            {
                id: '1',
                claim: 'AI-powered cohort intelligence',
                evidence: 'Deep audience understanding drives every decision',
                priority: 1,
                for_journey_stage: 'problem_aware'
            },
            {
                id: '2',
                claim: 'Battle-tested campaign frameworks',
                evidence: 'Proven structures that top teams use',
                priority: 2,
                for_journey_stage: 'solution_aware'
            },
            {
                id: '3',
                claim: 'Real-time performance insights',
                evidence: 'Know what works, double down on winners',
                priority: 3,
                for_journey_stage: 'product_aware'
            }
        ]
    };
};

/**
 * Test positioning in market (future: actual market testing)
 */
export const testPositioning = async (positioningId) => {
    // TODO: Implement market testing
    return {
        clarity_score: 0.85,
        differentiation_score: 0.78,
        credibility_score: 0.92,
        feedback: [
            { type: 'positive', message: 'Clear category definition' },
            { type: 'warning', message: 'Differentiator could be more specific' },
            { type: 'positive', message: 'Strong reason to believe' }
        ]
    };
};
