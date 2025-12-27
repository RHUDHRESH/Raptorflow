/**
 * Foundation Data Types
 * TypeScript interfaces matching foundation_test.json structure
 */

// === Meta & Confidence ===
export interface FoundationMeta {
    schema_version: string;
    client_id: string;
    workspace_id: string;
    created_at: string;
    updated_at: string;
    confidence: {
        overall: number;
        positioning: number;
        icps: number;
        sizing: number;
    };
    lock_state: Record<string, boolean>;
    notes?: string;
}

// === Business Identity ===
export interface BusinessIdentity {
    brand_name: string;
    tagline_seed: string;
    website: string;
    hq_location: string;
    regions_served: string[];
    team_size: number;
    stage: string;
    contact: {
        name: string;
        email: string;
        role: string;
    };
}

export interface BusinessStory {
    origin: string;
    why_now: string;
    mission: string;
    vision: string;
    values: string[];
}

export interface PricingTier {
    tier: string;
    price: number;
    limits: Record<string, number | string>;
    best_for: string;
}

export interface BusinessOffer {
    product_type: string;
    category_guess: string;
    primary_outcome: string;
    time_to_value: string;
    pricing: {
        model: string;
        currency: string;
        anchor: number;
        min: number;
        max: number;
    };
    packaging: PricingTier[];
    delivery: {
        onboarding: string;
        impl_support: string;
        integrations: string[];
    };
    inputs_expected: string[];
    outputs_promised: string[];
}

export interface UspItem {
    usp: string;
    type: string;
    evidence: string[];
    confidence: number;
}

export interface BusinessData {
    identity: BusinessIdentity;
    story: BusinessStory;
    offer: BusinessOffer;
    constraints: {
        industries_to_avoid: string[];
        claims_cannot_make: string[];
        compliance: string[];
        brand_words_to_use: string[];
        brand_words_to_avoid: string[];
    };
    usp_bank: UspItem[];
}

// === Market Data ===
export interface MarketData {
    category: {
        primary: string;
        secondary: string[];
        keywords: string[];
    };
    scope: {
        b2b_or_b2c: string;
        verticals: string[];
        geo: string[];
        exclusions: string[];
    };
    maturity: string;
    price_sensitivity: string;
    purchase_friction: {
        switching_cost: string;
        security_reviews: string;
    };
}

export interface MarketSizing {
    tam: { value: number; currency: string; assumptions: string[]; sources: string[] };
    sam: { value: number; currency: string; filters: Record<string, string[]>; assumptions: string[]; sources: string[] };
    som: { value: number; currency: string; months: number; win_rate: number; assumptions: string[]; sources: string[] };
}

// === Positioning ===
export interface PositioningData {
    components: {
        competitive_alternatives: {
            status_quo: string[];
            indirect: string[];
            direct: string[];
        };
        differentiated_capabilities: string[];
        value_themes: string[];
        target_segments: string[];
        market_category: string;
    };
    derived: {
        attribute_to_own: string;
        positioning_statement: {
            template: string;
            final: string;
            variants: Record<string, string>;
        };
        attribute_ladder: Array<{ attribute: string; advantage: string; value: string }>;
        perceptual_map: {
            x_axis: string;
            y_axis: string;
            points: Array<{ name: string; x: number; y: number }>;
        };
        two_by_two: {
            x: string;
            y: string;
            quadrants: Record<string, string>;
            plots: Array<{ name: string; x: number; y: number }>;
        };
    };
    uvp_usp: {
        uvp: string;
        usp: string;
        rtb: string[];
    };
    risks: Record<string, number>;
}

// === Blue Ocean ===
export interface BlueOceanData {
    strategy_canvas: {
        value_factors: string[];
        curves: Record<string, Record<string, number>>;
    };
    errc: {
        eliminate: string[];
        reduce: string[];
        raise: string[];
        create: string[];
    };
    value_innovation: {
        hypothesis: string;
        value_cost_tradeoff_break: string;
    };
    noncustomers: Record<string, string[]>;
}

// === Competition ===
export interface DirectCompetitor {
    name: string;
    strength: string;
    weakness: string;
}

export interface CompetitionData {
    status_quo: string[];
    indirect: string[];
    direct: DirectCompetitor[];
    battlecards: {
        primary_rival: string;
        why_we_win: string[];
        landmines: string[];
        talk_tracks: Array<{ objection: string; response: string }>;
    };
    signals: {
        keywords_they_use: string[];
        ads_they_run: string[];
        channels_they_dominate: string[];
    };
}

// === ICPs & Cohorts ===
export interface IcpFirmographics {
    industry: string[];
    employee_range: string;
    revenue_range: string;
    geo: string[];
}

export interface IcpJtbd {
    functional: string[];
    emotional: string[];
    social: string[];
}

export interface IcpPains {
    primary: string;
    secondary: string[];
    cost: string[];
}

export interface IcpPsychographics {
    values: string[];
    fears: string[];
    aspirations: string[];
    beliefs: string[];
}

export interface IcpBehavior {
    day_in_life: string[];
    social_media_use: string;
    content_diet: string[];
    tools_stack: string[];
}

export interface IcpWhereTheyExist {
    platforms: string[];
    communities: string[];
    events: string[];
    influencers: string[];
}

export interface IcpProfile {
    icp_id: string;
    name: string;
    b2b_or_b2c: string;
    firmographics: IcpFirmographics;
    roles: {
        buyer: string[];
        users: string[];
        influencers: string[];
    };
    jtbd: IcpJtbd;
    pains: IcpPains;
    triggers: string[];
    alternatives_in_use: string[];
    objections: string[];
    buying_process: {
        motion: string;
        cycle_days: number;
        committee: string[];
        procurement: string;
    };
    psychographics: IcpPsychographics;
    behavior: IcpBehavior;
    where_they_exist: IcpWhereTheyExist;
    inter_icp_relationships: {
        feeds: string[];
        blocked_by: string[];
        adjacent: string[];
    };
    message_angles: {
        hooks: string[];
        promises: string[];
        proof: string[];
    };
}

export interface CohortSegment {
    segment_id: string;
    name: string;
    icp_ids: string[];
}

export interface CohortsData {
    icps: IcpProfile[];
    segments: CohortSegment[];
    relationship_graph: {
        nodes: Array<{ id: string; label: string }>;
        edges: Array<{ from: string; to: string; type: string }>;
    };
}

// === Messaging ===
export interface MessagingData {
    message_house: {
        controlling_idea: string;
        pillars: Array<{ pillar: string; proof: string }>;
        proof_points: string[];
    };
    soundbites_v1: Record<string, string>;
    story_spine: {
        character: string;
        problem: { external: string; internal: string; philosophical: string };
        guide: { empathy: string; authority: string };
        plan: string[];
        cta: { direct: string; transitional: string };
        failure: string;
        success: string;
    };
    voice: {
        tone: string[];
        banned_words: string[];
        must_use_phrases: string[];
    };
}

// === Proof Stack ===
export interface ProofStackData {
    tiered_proof: Record<string, string[]>;
    case_studies: Array<{ company: string; problem: string; solution: string; result: string }>;
    metrics: string[];
    guarantees: string[];
    credibility_gaps: string[];
}

// === Ops ===
export interface OpsData {
    go_to_market: {
        motion: string;
        channels_top3: string[];
        cycle_days: number;
    };
    sales: {
        qualification_rules: string[];
        pricing_objections: string[];
        discount_policy: string;
    };
    implementation: {
        time_days: number;
        steps: string[];
        success_criteria: string[];
    };
    tracking: {
        north_star_metric: string;
        inputs: string[];
        outputs: string[];
        dashboards: string[];
    };
}

// === Agent Handoff ===
export interface AgentHandoff {
    truth_file: string;
    embedding_snapshot_id: string;
    retrieval_rules: Record<string, boolean>;
    red_lines: string[];
    open_questions: string[];
    assumptions: string[];
    change_log: Array<{ ts: string; actor: string; change: string }>;
}

// === Root Foundation Data ===
export interface FoundationData {
    meta: FoundationMeta;
    inputs: {
        links: Array<{ url: string; label: string; type: string }>;
        files: Array<{ file_id: string; filename: string; type: string }>;
        free_text: string;
        unknowns: string[];
    };
    business: BusinessData;
    market: MarketData;
    market_sizing: MarketSizing;
    positioning: PositioningData;
    blue_ocean: BlueOceanData;
    competition: CompetitionData;
    cohorts: CohortsData;
    messaging: MessagingData;
    proof_stack: ProofStackData;
    ops: OpsData;
    agent_handoff: AgentHandoff;
}

// === Helper types for module consumption ===

/** Simplified cohort for @ mentions */
export interface SimpleCohort {
    id: string;
    name: string;
}

/** Simplified competitor for @ mentions */
export interface SimpleCompetitor {
    name: string;
    strength?: string;
    weakness?: string;
}

/** Simplified campaign derived from positioning */
export interface SimpleCampaign {
    id: string;
    name: string;
}
