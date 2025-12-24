/**
 * Black Box Z — Core Type Definitions (v1 Spec)
 */

export type RiskLevel = "safe" | "spicy" | "unreasonable";

export type GoalType =
    | "replies"
    | "leads"
    | "calls"
    | "clicks"
    | "sales"
    | "followers";

export type ChannelType =
    | "email"
    | "linkedin"
    | "twitter"
    | "whatsapp"
    | "youtube"
    | "instagram"
    | "other";

export type ExperimentStatus = "draft" | "generated" | "launched" | "checked_in" | "expired";

export type BehavioralPrinciple =
    | "friction"           // Friction Killers
    | "identity"           // Identity & Status
    | "loss_aversion"      // Loss Aversion / Regret
    | "social_proof"       // Social Proof & Herd
    | "pattern_interrupt"  // Surprise / Pattern interrupt
    | "commitment"         // Commitment escalation
    | "pricing_psych";     // Pricing psychology

export type SkillRole =
    | "hook"
    | "structure"
    | "tone"
    | "cta"
    | "proof"
    | "edit_polish";

export type SkillOwner = "system" | "user";

export interface SkillRef {
    skill_id: string;
    version: string;
    owner: SkillOwner;
    role: SkillRole;
}

export type AssetType = "email" | "social_post" | "meme" | "text";

export interface AssetPlan {
    asset_type: AssetType;
    variants: number;
    target_length?: "short" | "medium" | "long";
    notes?: string;
}

export type WhyChip =
    | "wrong_audience"
    | "weak_hook"
    | "offer_unclear"
    | "too_spicy"
    | "timing"
    | "format_mismatch"
    | "other";

export type Outcome = "bombed" | "meh" | "worked" | "great";

export interface SelfReport {
    submitted_at: string;
    outcome: Outcome;
    metric_name: GoalType;
    metric_value: number;
    run_again: boolean;
    why_chips?: WhyChip[];
}

export interface SkillWeightDelta {
    skill_id: string;
    delta: number;
}

export interface SkillPreset {
    name: string;
    intent: GoalType;
    channel: ChannelType;
    skill_stack: SkillRef[];
}

export interface LearningArtifact {
    id: string;
    summary: string;
    content?: string;
    learning_type?: 'strategic' | 'tactical';
    skill_weight_deltas: SkillWeightDelta[];
    suggested_preset?: SkillPreset;
}

export interface Experiment {
    id: string;

    // Core inputs
    goal: GoalType;
    risk_level: RiskLevel;
    channel: ChannelType;

    // Content
    title: string;          // 6-10 words
    bet: string;            // One sentence
    why: string;            // One sentence explanation
    principle: BehavioralPrinciple;

    // Meta
    effort: "10m" | "30m" | "2h";
    time_to_signal: "24h" | "48h" | "7d";

    // Execution
    skill_stack: SkillRef[];
    asset_plan?: AssetPlan;
    asset_ids: string[];

    // Lifecycle
    status: ExperimentStatus;
    created_at: string;
    launched_at?: string;
    checkin_due_at?: string;
    checkin_remind_at?: string;
    checkin_expire_at?: string;

    // Results
    self_report?: SelfReport;
    learning?: LearningArtifact;
    confidence?: number;
}

// State Management
export interface BlackboxState {
    experiments: Experiment[];
    learnings: LearningArtifact[];
    skill_weights: Record<string, number>;
    last_run_at?: string;
}
