/**
 * Campaign Service
 * 
 * Manages campaigns - the strategic orchestration layer that sits above moves.
 * Campaigns have a singular objective and contain multiple moves that work together.
 */

import { supabase } from '../supabase';

// =============================================================================
// CAMPAIGN CRUD
// =============================================================================

/**
 * Create a new campaign with cohorts and channels
 */
export const createCampaign = async (data) => {
    // Create the campaign
    const { data: campaign, error: campaignError } = await supabase
        .from('campaigns')
        .insert([{
            workspace_id: data.workspace_id,
            name: data.name,
            description: data.description,
            positioning_id: data.positioning_id,
            message_architecture_id: data.message_architecture_id,
            objective: data.objective,
            objective_type: data.objective_type,
            objective_statement: data.objective_statement,
            success_definition: data.success_definition,
            primary_metric: data.primary_metric,
            target_value: data.target_value,
            secondary_metrics: data.secondary_metrics,
            budget: data.budget,
            start_date: data.start_date,
            end_date: data.end_date,
            status: data.status || 'draft',
        }])
        .select()
        .single();

    if (campaignError) throw campaignError;

    // Add cohorts if provided
    if (data.target_cohorts && data.target_cohorts.length > 0) {
        const cohortInserts = data.target_cohorts.map(tc => ({
            campaign_id: campaign.id,
            cohort_id: tc.cohort_id,
            priority: tc.priority,
            journey_stage_current: tc.journey_stage_current,
            journey_stage_target: tc.journey_stage_target,
        }));

        const { error: cohortsError } = await supabase
            .from('campaign_cohorts')
            .insert(cohortInserts);

        if (cohortsError) throw cohortsError;
    }

    // Add channels if provided
    if (data.channel_strategy && data.channel_strategy.length > 0) {
        const channelInserts = data.channel_strategy.map(cs => ({
            campaign_id: campaign.id,
            channel: cs.channel,
            role: cs.role,
            budget_percentage: cs.budget_percentage,
            frequency: cs.frequency,
            key_messages: cs.key_messages,
        }));

        const { error: channelsError } = await supabase
            .from('campaign_channels')
            .insert(channelInserts);

        if (channelsError) throw channelsError;
    }

    return getCampaignById(campaign.id);
};

/**
 * Get all campaigns for a workspace
 */
export const getCampaigns = async (workspaceId, filters = {}) => {
    let query = supabase
        .from('campaigns')
        .select(`
      *,
      positioning:positioning(id, name, category_frame),
      message_architecture:message_architecture(id, primary_claim),
      campaign_cohorts(
        cohort_id,
        priority,
        journey_stage_current,
        journey_stage_target,
        cohort:cohorts(id, name, description, health_score)
      ),
      campaign_channels(channel, role, frequency)
    `)
        .eq('workspace_id', workspaceId);

    // Apply filters
    if (filters.status) {
        query = query.eq('status', filters.status);
    }
    if (filters.objective_type) {
        query = query.eq('objective_type', filters.objective_type);
    }

    query = query.order('created_at', { ascending: false });

    const { data, error } = await query;

    if (error) throw error;
    return data;
};

/**
 * Get a single campaign by ID with full details
 */
export const getCampaignById = async (id) => {
    const { data, error } = await supabase
        .from('campaigns')
        .select(`
      *,
      positioning:positioning(*),
      message_architecture:message_architecture(*),
      campaign_cohorts(
        cohort_id,
        priority,
        journey_stage_current,
        journey_stage_target,
        cohort:cohorts(*)
      ),
      campaign_channels(*),
      moves(*)
    `)
        .eq('id', id)
        .single();

    if (error) throw error;
    return data;
};

/**
 * Update campaign
 */
export const updateCampaign = async (id, updates) => {
    const { data, error } = await supabase
        .from('campaigns')
        .update(updates)
        .eq('id', id)
        .select()
        .single();

    if (error) throw error;
    return data;
};

/**
 * Delete campaign
 */
export const deleteCampaign = async (id) => {
    const { error } = await supabase
        .from('campaigns')
        .delete()
        .eq('id', id);

    if (error) throw error;
};

/**
 * Update campaign status
 */
export const updateCampaignStatus = async (id, status) => {
    return updateCampaign(id, { status });
};

// =============================================================================
// CAMPAIGN COHORTS
// =============================================================================

/**
 * Add cohort to campaign
 */
export const addCohortToCampaign = async (campaignId, cohortData) => {
    const { data, error } = await supabase
        .from('campaign_cohorts')
        .insert([{
            campaign_id: campaignId,
            cohort_id: cohortData.cohort_id,
            priority: cohortData.priority,
            journey_stage_current: cohortData.journey_stage_current,
            journey_stage_target: cohortData.journey_stage_target,
        }])
        .select()
        .single();

    if (error) throw error;
    return data;
};

/**
 * Remove cohort from campaign
 */
export const removeCohortFromCampaign = async (campaignId, cohortId) => {
    const { error } = await supabase
        .from('campaign_cohorts')
        .delete()
        .eq('campaign_id', campaignId)
        .eq('cohort_id', cohortId);

    if (error) throw error;
};

/**
 * Update cohort journey goals
 */
export const updateCohortJourneyGoals = async (campaignId, cohortId, updates) => {
    const { data, error } = await supabase
        .from('campaign_cohorts')
        .update(updates)
        .eq('campaign_id', campaignId)
        .eq('cohort_id', cohortId)
        .select()
        .single();

    if (error) throw error;
    return data;
};

// =============================================================================
// MOVE GENERATION
// =============================================================================

/**
 * Generate move recommendations for a campaign
 * Based on objective, cohorts, and journey stages
 */
export const generateMoveRecommendations = async (campaignId) => {
    const campaign = await getCampaignById(campaignId);

    const moves = [];
    const primaryCohort = campaign.campaign_cohorts.find(cc => cc.priority === 'primary');

    if (!primaryCohort) {
        throw new Error('Campaign must have a primary cohort');
    }

    // Generate moves based on objective type
    switch (campaign.objective_type) {
        case 'awareness':
            moves.push({
                name: 'Authority Establishment Sprint',
                description: 'Build credibility with thought leadership content',
                journey_from: 'unaware',
                journey_to: 'problem_aware',
                duration: 14,
                channels: campaign.campaign_channels.filter(c => c.role === 'reach').map(c => c.channel),
                proof_point: campaign.message_architecture?.proof_points?.[0]?.claim,
            });
            break;

        case 'consideration':
        case 'conversion':
            moves.push({
                name: 'Proof Delivery Campaign',
                description: 'Show evidence with case studies and testimonials',
                journey_from: 'problem_aware',
                journey_to: 'solution_aware',
                duration: 14,
                channels: campaign.campaign_channels.filter(c => c.role === 'engage').map(c => c.channel),
                proof_point: campaign.message_architecture?.proof_points?.[1]?.claim,
            });
            moves.push({
                name: 'Objection Handling Sequence',
                description: 'Address common concerns proactively',
                journey_from: 'solution_aware',
                journey_to: 'product_aware',
                duration: 7,
                channels: campaign.campaign_channels.filter(c => ['engage', 'convert'].includes(c.role)).map(c => c.channel),
                proof_point: campaign.message_architecture?.proof_points?.[2]?.claim,
            });

            if (campaign.objective_type === 'conversion') {
                moves.push({
                    name: 'Conversion Sprint',
                    description: 'Push for action with urgency and clear CTAs',
                    journey_from: 'product_aware',
                    journey_to: 'most_aware',
                    duration: 7,
                    channels: campaign.campaign_channels.filter(c => c.role === 'convert').map(c => c.channel),
                    proof_point: 'Clear value + risk reversal',
                });
            }
            break;

        case 'retention':
            moves.push({
                name: 'Value Reinforcement Loop',
                description: 'Remind them why they chose you',
                journey_from: 'most_aware',
                journey_to: 'most_aware',
                duration: 28,
                channels: campaign.campaign_channels.filter(c => c.role === 'retain').map(c => c.channel),
                proof_point: 'Success stories and new features',
            });
            break;

        case 'advocacy':
            moves.push({
                name: 'Advocacy Activation',
                description: 'Turn customers into promoters',
                journey_from: 'most_aware',
                journey_to: 'most_aware',
                duration: 21,
                channels: campaign.campaign_channels.map(c => c.channel),
                proof_point: 'Community and recognition',
            });
            break;
    }

    return moves;
};

// =============================================================================
// CAMPAIGN PERFORMANCE
// =============================================================================

/**
 * Get campaign performance metrics
 */
export const getCampaignPerformance = async (id) => {
    const campaign = await getCampaignById(id);

    // TODO: Implement actual performance tracking
    // For now, return mock data
    const totalDays = Math.ceil((new Date(campaign.end_date) - new Date(campaign.start_date)) / (1000 * 60 * 60 * 24));
    const daysPassed = Math.ceil((new Date() - new Date(campaign.start_date)) / (1000 * 60 * 60 * 24));
    const progress = Math.min(100, (daysPassed / totalDays) * 100);

    return {
        campaign_id: id,
        progress: Math.round(progress),
        health_score: 75,
        metrics: {
            primary: {
                name: campaign.primary_metric,
                current: 23,
                target: campaign.target_value,
                unit: 'count'
            },
            pacing: {
                expected: Math.round(progress),
                actual: 65,
                status: 'behind'
            }
        },
        moves: {
            total: campaign.moves?.length || 0,
            completed: 0,
            in_progress: 1,
            upcoming: (campaign.moves?.length || 0) - 1
        },
        insights: [
            { type: 'warning', message: 'Campaign pacing is behind target' },
            { type: 'positive', message: 'Cohort engagement is above average' }
        ]
    };
};
