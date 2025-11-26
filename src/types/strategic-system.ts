// ============================================
// RAPTORFLOW STRATEGIC SYSTEM TYPES
// TypeScript type definitions for new database tables
// ============================================

// ============================================
// POSITIONING TYPES
// ============================================

export interface Positioning {
    id: string;
    workspace_id: string;
    name: string;
    for_cohort_id?: string;

    // Positioning Statement Components
    who_statement?: string;
    category_frame?: string;
    differentiator?: string;
    reason_to_believe?: string;
    competitive_alternative?: string;

    // Status
    is_active: boolean;
    is_validated: boolean;

    // Metadata
    created_at: string;
    updated_at: string;
}

export interface MessageArchitecture {
    id: string;
    positioning_id: string;

    // Message Hierarchy
    primary_claim: string;
    proof_points: ProofPoint[];

    // Messaging Variants
    tagline?: string;
    elevator_pitch?: string;
    long_form_narrative?: string;

    // Metadata
    created_at: string;
    updated_at: string;
}

export interface ProofPoint {
    claim: string;
    evidence: string[];
    for_journey_stages: JourneyStage[];
}

// ============================================
// CAMPAIGN TYPES
// ============================================

export type CampaignObjective = 'awareness' | 'consideration' | 'conversion' | 'retention' | 'advocacy';
export type CampaignStatus = 'draft' | 'planning' | 'active' | 'paused' | 'completed' | 'cancelled';
export type ChannelRole = 'reach' | 'engage' | 'convert' | 'retain';

export interface Campaign {
    id: string;
    workspace_id: string;
    positioning_id?: string;

    // Basic Info
    name: string;
    description?: string;

    // Objective
    objective: CampaignObjective;
    objective_statement?: string;
    primary_metric?: string;
    target_value?: number;

    // Timeline
    start_date?: string;
    end_date?: string;

    // Budget
    budget_total?: number;
    budget_currency?: string;

    // Channel Strategy
    channel_strategy: ChannelStrategy[];

    // Status
    status: CampaignStatus;

    // Performance
    health_score?: number;
    current_performance: Record<string, number>;

    // Metadata
    created_at: string;
    updated_at: string;
    launched_at?: string;
    completed_at?: string;
}

export interface ChannelStrategy {
    channel: string;
    role: ChannelRole;
    budget_percentage?: number;
    frequency?: string;
}

export interface CampaignCohort {
    id: string;
    campaign_id: string;
    cohort_id: string;
    priority: 'primary' | 'secondary';
    journey_stage_current?: JourneyStage;
    journey_stage_target?: JourneyStage;
    created_at: string;
}

// ============================================
// JOURNEY STAGE TYPES
// ============================================

export type JourneyStage =
    | 'unaware'
    | 'problem_aware'
    | 'solution_aware'
    | 'product_aware'
    | 'most_aware';

export interface JourneyStageDefinition {
    id: JourneyStage;
    name: string;
    description: string;
    sort_order: number;
    created_at: string;
}

export interface JourneyDistribution {
    unaware?: number;
    problem_aware?: number;
    solution_aware?: number;
    product_aware?: number;
    most_aware?: number;
}

// ============================================
// COHORT ENHANCEMENT TYPES
// ============================================

export interface BuyingTrigger {
    trigger: string;
    strength: 'low' | 'medium' | 'high';
    timing?: string;
    signal?: string;
}

export interface DecisionCriterion {
    criterion: string;
    weight: number; // Must sum to 1.0 across all criteria
    description?: string;
}

export interface Objection {
    objection: string;
    frequency: 'rare' | 'occasional' | 'common' | 'very_common';
    stage?: JourneyStage;
    response: string;
    linked_asset_ids?: string[];
}

export interface AttentionWindow {
    best_times: string[];
    receptivity: 'low' | 'medium' | 'high';
    preferred_formats: string[];
}

export interface AttentionWindows {
    [channel: string]: AttentionWindow;
}

export interface CompetitiveFrame {
    direct_competitors: string[];
    category_alternatives: string[];
    switching_triggers: string[];
}

export interface DecisionMakingUnit {
    roles: string[];
    influencers: string[];
    decision_maker?: string;
    approval_chain: string[];
}

// Enhanced Cohort interface (extends existing)
export interface EnhancedCohort {
    // ... existing cohort fields ...

    // New strategic attributes
    buying_triggers?: BuyingTrigger[];
    decision_criteria?: DecisionCriterion[];
    objection_map?: Objection[];
    attention_windows?: AttentionWindows;
    journey_distribution?: JourneyDistribution;
    competitive_frame?: CompetitiveFrame;
    decision_making_unit?: DecisionMakingUnit;
    health_score?: number;
    last_validated?: string;
}

// ============================================
// MOVE ENHANCEMENT TYPES
// ============================================

export type MoveIntensity = 'light' | 'standard' | 'aggressive';

export interface MessageVariant {
    proof_point_id?: string;
    angle?: string;
    tone?: string;
    emphasis?: string[];
}

export interface AssetRequirement {
    channel: string;
    format: string;
    quantity: number;
    brief_data?: CreativeBrief;
}

// Enhanced Move interface (extends existing)
export interface EnhancedMove {
    // ... existing move fields ...

    // New campaign linkage
    campaign_id?: string;
    journey_stage_from?: JourneyStage;
    journey_stage_to?: JourneyStage;
    message_variant?: MessageVariant;
    asset_requirements?: AssetRequirement[];
    intensity?: MoveIntensity;
}

// ============================================
// CREATIVE BRIEF TYPES
// ============================================

export interface CreativeBrief {
    single_minded_proposition: string;
    key_message: string;
    target_cohort_context: {
        psychographics?: Record<string, any>;
        decision_criteria?: DecisionCriterion[];
        objections_to_handle?: Objection[];
    };
    tone_and_manner: string;
    mandatories: string[];
    no_gos: string[];
    success_definition: string;
}

// ============================================
// STRATEGY INSIGHTS TYPES
// ============================================

export type InsightSourceType = 'campaign' | 'move' | 'cohort' | 'asset' | 'positioning';
export type InsightType =
    | 'cohort_preference'
    | 'campaign_pacing'
    | 'move_effectiveness'
    | 'asset_optimization'
    | 'positioning_validation';
export type InsightStatus = 'new' | 'reviewed' | 'actioned' | 'dismissed';

export interface StrategyInsight {
    id: string;
    workspace_id: string;

    // Source
    source_type: InsightSourceType;
    source_id?: string;

    // Insight Details
    insight_type: InsightType;
    title: string;
    description: string;

    // Evidence
    evidence: Record<string, any>;

    // Recommendation
    recommended_action?: string;

    // Confidence & Impact
    confidence_score?: number; // 0.0 to 1.0
    impact_score?: number; // 1 to 10

    // Status
    status: InsightStatus;

    // Metadata
    created_at: string;
    reviewed_at?: string;
    actioned_at?: string;
}

// ============================================
// COMPETITOR TYPES
// ============================================

export type PricePosition = 'premium' | 'mid-market' | 'budget';

export interface Competitor {
    id: string;
    workspace_id: string;

    // Basic Info
    name: string;
    website?: string;

    // Competitive Intelligence
    positioning_statement?: string;
    key_messages?: string[];

    // Analysis
    strengths?: string[];
    weaknesses?: string[];

    // Market Position
    price_position?: PricePosition;
    market_share_estimate?: number;

    // Metadata
    created_at: string;
    updated_at: string;
}

// ============================================
// HELPER TYPES
// ============================================

export interface CampaignHealthSummary {
    id: string;
    name: string;
    status: CampaignStatus;
    health_score?: number;
    objective: CampaignObjective;
    start_date?: string;
    end_date?: string;
    total_moves: number;
    total_cohorts: number;
    health_status: 'completed' | 'upcoming' | 'healthy' | 'on_track' | 'at_risk' | 'critical';
}

export interface CohortJourneySummary {
    id: string;
    name: string;
    workspace_id: string;
    pct_unaware: number;
    pct_problem_aware: number;
    pct_solution_aware: number;
    pct_product_aware: number;
    pct_most_aware: number;
    health_score?: number;
}

// ============================================
// VALIDATION HELPERS
// ============================================

export function validateDecisionCriteriaWeights(criteria: DecisionCriterion[]): boolean {
    if (criteria.length === 0) return true;
    const total = criteria.reduce((sum, c) => sum + c.weight, 0);
    return Math.abs(total - 1.0) < 0.01;
}

export function validateJourneyDistribution(distribution: JourneyDistribution): boolean {
    const total = (distribution.unaware || 0) +
        (distribution.problem_aware || 0) +
        (distribution.solution_aware || 0) +
        (distribution.product_aware || 0) +
        (distribution.most_aware || 0);
    return Math.abs(total - 1.0) < 0.01;
}

// ============================================
// CONSTANTS
// ============================================

export const JOURNEY_STAGES: JourneyStage[] = [
    'unaware',
    'problem_aware',
    'solution_aware',
    'product_aware',
    'most_aware'
];

export const CAMPAIGN_OBJECTIVES: CampaignObjective[] = [
    'awareness',
    'consideration',
    'conversion',
    'retention',
    'advocacy'
];

export const CHANNEL_ROLES: ChannelRole[] = [
    'reach',
    'engage',
    'convert',
    'retain'
];

export const JOURNEY_STAGE_LABELS: Record<JourneyStage, string> = {
    unaware: 'Unaware',
    problem_aware: 'Problem Aware',
    solution_aware: 'Solution Aware',
    product_aware: 'Product Aware',
    most_aware: 'Most Aware'
};

export const JOURNEY_STAGE_DESCRIPTIONS: Record<JourneyStage, string> = {
    unaware: "Don't know they have a problem",
    problem_aware: "Know the problem, don't know solutions exist",
    solution_aware: "Know solutions exist, don't know your product",
    product_aware: "Know your product, not yet convinced",
    most_aware: "Ready to buy, need final push"
};
