import { apiFetch } from "../api-core";

export const strategistApi = {
  ensureDefault: async () => {
    const res = await apiFetch<StrategistSoulResponse>("/api/v1/avatars/strategist/default", {
      method: "POST",
      auth: true,
    });
    return res;
  },
  dryRun: async (body: StrategistDryRunRequest) => {
    const res = await apiFetch<StrategistDryRunResponse>("/api/v1/avatars/strategist/dry-run", {
      method: "POST",
      body,
      auth: true,
    });
    return res;
  },
};

export interface StrategistSoulResponse {
  avatar_id: string;
  soul_id: string;
  created: boolean;
  updated: boolean;
}

export interface StrategistDryRunRequest {
  task_summary: string;
  context_summary: string;
}

export interface StrategistDryRunResponse {
  avatar_id: string;
  soul_id: string;
  embodiment_pack: StrategistEmbodimentPack;
  role_lock_prompt: string;
  instinct_frame: StrategistInstinctFrame;
  presence_state: StrategistPresenceState | null;
  debate_event: StrategistDebateEvent | null;
}

export interface StrategistEmbodimentPack {
  avatar_id: string;
  soul_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  operating_principles: string[];
  debate_style: Record<string, unknown>;
  evaluation_bias: Record<string, unknown>;
  memory_edges: StrategistMemoryEdge[];
}

export interface StrategistMemoryEdge {
  memory_edge_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface StrategistInstinctFrame {
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: string[];
  recommended_posture: string;
  visible_summary: string;
}

export interface StrategistPresenceState {
  presence_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  visible_summary: string;
  confidence: number;
}

export interface StrategistDebateEvent {
  debate_event_id: string;
  event_type: string;
  stance: string;
  content: Record<string, unknown>;
  confidence: number;
}

export const researcherApi = {
  ensureDefault: async () => {
    const res = await apiFetch<ResearcherSoulResponse>("/api/v1/avatars/researcher/default", {
      method: "POST",
      auth: true,
    });
    return res;
  },
  dryRun: async (body: ResearcherDryRunRequest) => {
    const res = await apiFetch<ResearcherDryRunResponse>("/api/v1/avatars/researcher/dry-run", {
      method: "POST",
      body,
      auth: true,
    });
    return res;
  },
};

export interface ResearcherSoulResponse {
  avatar_id: string;
  soul_id: string;
  created: boolean;
  updated: boolean;
}

export interface ResearcherDryRunRequest {
  task_summary: string;
  context_summary: string;
}

export interface ResearcherDryRunResponse {
  avatar_id: string;
  soul_id: string;
  embodiment_pack: ResearcherEmbodimentPack;
  role_lock_prompt: string;
  instinct_frame: ResearcherInstinctFrame;
  presence_state: ResearcherPresenceState | null;
  debate_event: ResearcherDebateEvent | null;
  claim_audit: ResearcherClaimAudit | null;
}

export interface ResearcherEmbodimentPack {
  avatar_id: string;
  soul_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  operating_principles: string[];
  debate_style: Record<string, unknown>;
  evaluation_bias: Record<string, unknown>;
  memory_edges: ResearcherMemoryEdge[];
}

export interface ResearcherMemoryEdge {
  memory_edge_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface ResearcherInstinctFrame {
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: string[];
  recommended_posture: string;
  visible_summary: string;
}

export interface ResearcherPresenceState {
  presence_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  visible_summary: string;
  confidence: number;
}

export interface ResearcherDebateEvent {
  debate_event_id: string;
  event_type: string;
  stance: string;
  content: Record<string, unknown>;
  confidence: number;
}

export interface ResearcherClaimAudit {
  known_facts: string[];
  claims: ClaimAnalysis[];
  unsupported_claims: string[];
  assumptions: string[];
  needed_sources: string[];
  competitor_notes: string[];
  open_questions: string[];
}

export interface ClaimAnalysis {
  claim: string;
  evidence_level: string;
  source: string;
  risk: string;
  recommended_action: string;
  safer_rewrite: string;
}

export const copywriterApi = {
  ensureDefault: async () => {
    const res = await apiFetch<CopywriterSoulResponse>("/api/v1/avatars/copywriter/default", {
      method: "POST",
      auth: true,
    });
    return res;
  },
  dryRun: async (body: CopywriterDryRunRequest) => {
    const res = await apiFetch<CopywriterDryRunResponse>("/api/v1/avatars/copywriter/dry-run", {
      method: "POST",
      body,
      auth: true,
    });
    return res;
  },
};

export interface CopywriterSoulResponse {
  avatar_id: string;
  soul_id: string;
  created: boolean;
  updated: boolean;
}

export interface CopywriterDryRunRequest {
  task_summary: string;
  context_summary: string;
  copy_draft?: string;
}

export interface CopywriterDryRunResponse {
  avatar_id: string;
  soul_id: string;
  embodiment_pack: CopywriterEmbodimentPack;
  role_lock_prompt: string;
  instinct_frame: CopywriterInstinctFrame;
  presence_state: CopywriterPresenceState | null;
  debate_event: CopywriterDebateEvent | null;
  copy_audit: CopywriterCopyAudit | null;
}

export interface CopywriterEmbodimentPack {
  avatar_id: string;
  soul_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  operating_principles: string[];
  debate_style: Record<string, unknown>;
  evaluation_bias: Record<string, unknown>;
  memory_edges: CopywriterMemoryEdge[];
}

export interface CopywriterMemoryEdge {
  memory_edge_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface CopywriterInstinctFrame {
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: string[];
  recommended_posture: string;
  visible_summary: string;
}

export interface CopywriterPresenceState {
  presence_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  visible_summary: string;
  confidence: number;
}

export interface CopywriterDebateEvent {
  debate_event_id: string;
  event_type: string;
  stance: string;
  content: Record<string, unknown>;
  confidence: number;
}

export interface CopywriterCopyAudit {
  copy_elements: CopyElementAnalysis[];
  proof_claims: CopyProofClaimAnalysis[];
  generic_risk_flags: string[];
  hook_assessment: CopyHookAssessment;
  cta_assessment: CopyCtaAssessment;
  voice_assessment: CopyVoiceAssessment;
  open_questions: string[];
}

export interface CopyElementAnalysis {
  element: string;
  element_type: string;
  assessment: string;
  risk_level: string;
  recommended_action: string;
}

export interface CopyProofClaimAnalysis {
  claim: string;
  has_evidence: boolean;
  evidence_quality: string;
  safer_language: string;
}

export interface CopyHookAssessment {
  has_hook: boolean;
  hook_clarity: string;
  icp_specific: boolean;
  risk_flags: string[];
}

export interface CopyCtaAssessment {
  has_cta: boolean;
  cta_specificity: string;
  cta_actionability: string;
  risk_flags: string[];
}

export interface CopyVoiceAssessment {
  voice_consistent: boolean;
  icp_voice_match: boolean;
  tone: string;
  risk_flags: string[];
}

export const growthOperatorApi = {
  ensureDefault: async () => {
    const res = await apiFetch<GrowthOperatorSoulResponse>(
      "/api/v1/avatars/growth-operator/default",
      {
        method: "POST",
        auth: true,
      },
    );
    return res;
  },
  dryRun: async (body: GrowthOperatorDryRunRequest) => {
    const res = await apiFetch<GrowthOperatorDryRunResponse>(
      "/api/v1/avatars/growth-operator/dry-run",
      {
        method: "POST",
        body,
        auth: true,
      },
    );
    return res;
  },
};

export interface GrowthOperatorSoulResponse {
  avatar_id: string;
  soul_id: string;
  created: boolean;
  updated: boolean;
}

export interface GrowthOperatorDryRunRequest {
  task_summary: string;
  context_summary: string;
  move_draft?: string;
}

export interface GrowthOperatorDryRunResponse {
  avatar_id: string;
  soul_id: string;
  embodiment_pack: GrowthOperatorEmbodimentPack;
  role_lock_prompt: string;
  instinct_frame: GrowthOperatorInstinctFrame;
  presence_state: GrowthOperatorPresenceState | null;
  debate_event: GrowthOperatorDebateEvent | null;
  execution_audit: GrowthOperatorExecutionAudit | null;
}

export interface GrowthOperatorEmbodimentPack {
  avatar_id: string;
  soul_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  operating_principles: string[];
  debate_style: Record<string, unknown>;
  evaluation_bias: Record<string, unknown>;
  memory_edges: GrowthOperatorMemoryEdge[];
}

export interface GrowthOperatorMemoryEdge {
  memory_edge_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface GrowthOperatorInstinctFrame {
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: string[];
  recommended_posture: string;
  visible_summary: string;
}

export interface GrowthOperatorPresenceState {
  presence_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  visible_summary: string;
  confidence: number;
}

export interface GrowthOperatorDebateEvent {
  debate_event_id: string;
  event_type: string;
  stance: string;
  content: Record<string, unknown>;
  confidence: number;
}

export interface GrowthOperatorExecutionAudit {
  move_analysis: MoveAnalysis[];
  cadence_assessment: CadenceAssessment;
  channel_coordination: ChannelCoordinationAssessment;
  feedback_loops: FeedbackLoopAssessment;
  velocity_signals: VelocityAssessment;
  open_questions: string[];
}

export interface MoveAnalysis {
  move_name: string;
  has_owner: boolean;
  has_deadline: boolean;
  has_success_signal: boolean;
  sequencing_justified: boolean;
  risk_level: string;
  recommended_action: string;
}

export interface CadenceAssessment {
  has_rhythm: boolean;
  cadence_quality: string;
  consistency_score: number;
  risk_flags: string[];
}

export interface ChannelCoordinationAssessment {
  multi_channel: boolean;
  coordination_quality: string;
  handoff_explicit: boolean;
  risk_flags: string[];
}

export interface FeedbackLoopAssessment {
  has_feedback_tracking: boolean;
  adaptation_triggers_defined: boolean;
  loop_quality: string;
  risk_flags: string[];
}

export interface VelocityAssessment {
  has_velocity_tracking: boolean;
  velocity_defined: boolean;
  measurement_quality: string;
  risk_flags: string[];
}

export const analystApi = {
  ensureDefault: async () => {
    const res = await apiFetch<AnalystSoulResponse>("/api/v1/avatars/analyst/default", {
      method: "POST",
      auth: true,
    });
    return res;
  },
  dryRun: async (body: AnalystDryRunRequest) => {
    const res = await apiFetch<AnalystDryRunResponse>("/api/v1/avatars/analyst/dry-run", {
      method: "POST",
      body,
      auth: true,
    });
    return res;
  },
};

export interface AnalystSoulResponse {
  avatar_id: string;
  soul_id: string;
  created: boolean;
  updated: boolean;
}

export interface AnalystDryRunRequest {
  task_summary: string;
  context_summary: string;
}

export interface AnalystDryRunResponse {
  avatar_id: string;
  soul_id: string;
  embodiment_pack: AnalystEmbodimentPack;
  role_lock_prompt: string;
  instinct_frame: AnalystInstinctFrame;
  presence_state: AnalystPresenceState | null;
  debate_event: AnalystDebateEvent | null;
  signal_quality_review: AnalystSignalQualityReview | null;
}

export interface AnalystEmbodimentPack {
  avatar_id: string;
  soul_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  operating_principles: string[];
  debate_style: Record<string, unknown>;
  evaluation_bias: Record<string, unknown>;
  memory_edges: AnalystMemoryEdge[];
}

export interface AnalystMemoryEdge {
  memory_edge_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface AnalystInstinctFrame {
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: string[];
  recommended_posture: string;
  visible_summary: string;
}

export interface AnalystPresenceState {
  presence_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  visible_summary: string;
  confidence: number;
}

export interface AnalystDebateEvent {
  debate_event_id: string;
  event_type: string;
  stance: string;
  content: Record<string, unknown>;
  confidence: number;
}

export interface AnalystSignalQualityReview {
  known_facts: string[];
  metrics: MetricAnalysisItem[];
  vanity_metrics: string[];
  missing_metrics: string[];
  attribution_limits: string[];
  recommended_decision: string;
  next_test: string;
  open_questions: string[];
}

export interface MetricAnalysisItem {
  metric_name: string;
  metric_type: string;
  value_summary: string;
  source: string;
  baseline: string;
  sample_size: string;
  signal_strength: string;
  decision_usefulness: string;
  risk: string;
}

export const creativeDirectorApi = {
  ensureDefault: async () => {
    const res = await apiFetch<CreativeDirectorSoulResponse>(
      "/api/v1/avatars/creative-director/default",
      {
        method: "POST",
        auth: true,
      },
    );
    return res;
  },
  dryRun: async (body: CreativeDirectorDryRunRequest) => {
    const res = await apiFetch<CreativeDirectorDryRunResponse>(
      "/api/v1/avatars/creative-director/dry-run",
      {
        method: "POST",
        body,
        auth: true,
      },
    );
    return res;
  },
};

export interface CreativeDirectorSoulResponse {
  avatar_id: string;
  soul_id: string;
  created: boolean;
  updated: boolean;
}

export interface CreativeDirectorDryRunRequest {
  task_summary: string;
  context_summary: string;
}

export interface CreativeDirectorDryRunResponse {
  avatar_id: string;
  soul_id: string;
  embodiment_pack: CreativeDirectorEmbodimentPack;
  role_lock_prompt: string;
  instinct_frame: CreativeDirectorInstinctFrame;
  presence_state: CreativeDirectorPresenceState | null;
  debate_event: CreativeDirectorDebateEvent | null;
  creative_review: CreativeQualityReview | null;
}

export interface CreativeDirectorEmbodimentPack {
  avatar_id: string;
  soul_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  operating_principles: string[];
  debate_style: Record<string, unknown>;
  evaluation_bias: Record<string, unknown>;
  memory_edges: CreativeDirectorMemoryEdge[];
}

export interface CreativeDirectorMemoryEdge {
  memory_edge_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface CreativeDirectorInstinctFrame {
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: string[];
  recommended_posture: string;
  visible_summary: string;
}

export interface CreativeDirectorPresenceState {
  presence_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  visible_summary: string;
  confidence: number;
}

export interface CreativeDirectorDebateEvent {
  debate_event_id: string;
  event_type: string;
  stance: string;
  content: Record<string, unknown>;
  confidence: number;
}

export interface CreativeQualityReview {
  aesthetic_quality: AestheticQualityAssessment;
  brand_consistency: BrandConsistencyAssessment;
  emotional_resonance: EmotionalResonanceAssessment;
  message_clarity: MessageClarityAssessment;
  creative_risk: CreativeRiskAssessment;
  overall_verdict: string;
  recommended_action: string;
  open_questions: string[];
}

export interface AestheticQualityAssessment {
  visual_hierarchy_clear: boolean;
  design_unity: boolean;
  first_impression_score: number;
  quality_concerns: string[];
  strengths: string[];
}

export interface BrandConsistencyAssessment {
  voice_consistent: boolean;
  tone_appropriate: boolean;
  brand_values_aligned: boolean;
  consistency_score: number;
  deviations: string[];
}

export interface EmotionalResonanceAssessment {
  has_emotional_hook: boolean;
  audience_empathy_present: boolean;
  resonance_level: string;
  emotional_tone: string;
  concerns: string[];
}

export interface MessageClarityAssessment {
  primary_message_clear: boolean;
  cta_visible: boolean;
  cta_compelling: boolean;
  hierarchy_clarity_score: number;
  confusion_points: string[];
}

export interface CreativeRiskAssessment {
  risk_level: string;
  audience_tolerance_appropriate: boolean;
  differentiation_achieved: boolean;
  risk_concerns: string[];
}

export const proofCollectorApi = {
  ensureDefault: async () => {
    const res = await apiFetch<ProofCollectorSoulResponse>(
      "/api/v1/avatars/proof-collector/default",
      {
        method: "POST",
        auth: true,
      },
    );
    return res;
  },
  dryRun: async (body: ProofCollectorDryRunRequest) => {
    const res = await apiFetch<ProofCollectorDryRunResponse>(
      "/api/v1/avatars/proof-collector/dry-run",
      {
        method: "POST",
        body,
        auth: true,
      },
    );
    return res;
  },
};

export interface ProofCollectorSoulResponse {
  avatar_id: string;
  soul_id: string;
  created: boolean;
  updated: boolean;
}

export interface ProofCollectorDryRunRequest {
  task_summary: string;
  context_summary: string;
}

export interface ProofCollectorDryRunResponse {
  avatar_id: string;
  soul_id: string;
  embodiment_pack: ProofCollectorEmbodimentPack;
  role_lock_prompt: string;
  instinct_frame: ProofCollectorInstinctFrame;
  presence_state: ProofCollectorPresenceState | null;
  debate_event: ProofCollectorDebateEvent | null;
  proof_map: ProofMap | null;
}

export interface ProofCollectorEmbodimentPack {
  avatar_id: string;
  soul_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  operating_principles: string[];
  debate_style: Record<string, unknown>;
  evaluation_bias: Record<string, unknown>;
  memory_edges: ProofCollectorMemoryEdge[];
}

export interface ProofCollectorMemoryEdge {
  memory_edge_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface ProofCollectorInstinctFrame {
  instinct_frame_id: string;
  dominant_concern: string;
  risk_flags: string[];
  recommended_posture: string;
  visible_summary: string;
}

export interface ProofCollectorPresenceState {
  presence_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  visible_summary: string;
  confidence: number;
}

export interface ProofCollectorDebateEvent {
  debate_event_id: string;
  event_type: string;
  stance: string;
  content: Record<string, unknown>;
  confidence: number;
}

export interface ProofMap {
  known_facts: string[];
  claims: ClaimProofAssessment[];
  proof_gaps: string[];
  assets_to_collect: string[];
  unsafe_claims: string[];
  legal_review_flags: string[];
  ripple_candidates: string[];
}

export interface ClaimProofAssessment {
  claim: string;
  proof_available: string;
  proof_type: string;
  proof_strength: string;
  source: string;
  permission_status: string;
  metric_context: MetricContext;
  risk: string;
  recommended_action: string;
  safer_wording: string;
}

export interface MetricContext {
  source: string;
  time_window: string;
  baseline: string;
  sample_size: string;
}
