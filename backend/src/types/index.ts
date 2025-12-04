/**
 * RaptorFlow Core Types
 * Domain objects for the marketing operating system
 */

// =====================================================
// ENUMS
// =====================================================

export type BarrierType = 
  | 'OBSCURITY'   // Not known, low visibility
  | 'RISK'        // Known but not trusted
  | 'INERTIA'     // Trusted but not urgent
  | 'FRICTION'    // Signed up but not activated
  | 'CAPACITY'    // Active but not expanding
  | 'ATROPHY';    // Churning or at risk

export type ProtocolType = 
  | 'A_AUTHORITY_BLITZ'
  | 'B_TRUST_ANCHOR'
  | 'C_COST_OF_INACTION'
  | 'D_HABIT_HARDCODE'
  | 'E_ENTERPRISE_WEDGE'
  | 'F_CHURN_INTERCEPT';

export type GoalType = 'velocity' | 'efficiency' | 'penetration';

export type DemandSourceType = 'capture' | 'creation' | 'expansion';

export type PersuasionAxisType = 'money' | 'time' | 'risk_image';

export type CampaignStatus = 'draft' | 'planned' | 'active' | 'paused' | 'completed' | 'cancelled';

export type MoveStatus = 'planned' | 'generating_assets' | 'ready' | 'running' | 'paused' | 'completed' | 'failed';

export type AssetStatus = 'draft' | 'generating' | 'needs_review' | 'approved' | 'deployed' | 'archived';

export type RAGStatus = 'green' | 'amber' | 'red' | 'unknown';

export type SpikeType = 'pipeline' | 'efficiency' | 'expansion';

export type SpikeStatus = 'configuring' | 'active' | 'paused' | 'completed' | 'cancelled';

export type GuardrailAction = 'alert_only' | 'pause_and_alert' | 'auto_pause';

// =====================================================
// ICP TYPES - 6D Intelligence
// =====================================================

export interface ICPFirmographics {
  employee_range?: string;         // '1-10', '11-50', '51-200', '201-1000', '1000+'
  industries?: string[];
  stages?: string[];               // 'bootstrap', 'seed', 'series-a', 'series-b+', 'enterprise'
  regions?: string[];
  exclude?: string[];
  revenue_range?: string;
  business_model?: string;
}

export interface ICPTechnographics {
  must_have?: string[];            // Required tech in stack
  nice_to_have?: string[];         // Preferred tech
  red_flags?: string[];            // Tech that disqualifies
  current_stack?: string[];        // Known current stack
}

export interface ICPPsychographics {
  pain_points?: string[];
  motivations?: string[];
  internal_triggers?: string[];    // Events that create urgency
  buying_constraints?: string[];   // What slows down buying
  risk_tolerance?: 'low' | 'medium' | 'high';
}

export interface ICPBehavioralTrigger {
  signal: string;
  source: string;
  urgency_boost: number;           // 0-100
  description?: string;
}

export interface ICPBuyingCommitteeMember {
  role: string;                    // 'Champion', 'Economic Buyer', 'Blocker', 'Influencer'
  typical_title: string;
  concerns: string[];
  success_criteria: string[];
  influence_level?: 'low' | 'medium' | 'high';
}

export interface ICPCategoryContext {
  market_position?: string;        // 'leader', 'challenger', 'newcomer'
  current_solution?: string;
  switching_triggers?: string[];
  awareness_level?: 'unaware' | 'problem_aware' | 'solution_aware' | 'product_aware';
}

export interface ICP {
  id: string;
  user_id: string;
  intake_id?: string;
  
  // Core identity
  label: string;
  slug?: string;
  summary?: string;
  
  // 6D Dimensions
  firmographics: ICPFirmographics;
  technographics: ICPTechnographics;
  psychographics: ICPPsychographics;
  behavioral_triggers: ICPBehavioralTrigger[];
  buying_committee: ICPBuyingCommitteeMember[];
  category_context: ICPCategoryContext;
  
  // Scoring
  fit_score: number;               // 0-100
  fit_reasoning?: string;
  priority_rank: number;
  
  // Messaging
  messaging_angle?: string;
  qualification_questions: string[];
  
  // Barrier association
  primary_barriers: BarrierType[];
  
  // Status
  is_selected: boolean;
  is_archived: boolean;
  version: number;
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface CreateICPInput {
  label: string;
  summary?: string;
  firmographics?: ICPFirmographics;
  technographics?: ICPTechnographics;
  psychographics?: ICPPsychographics;
  behavioral_triggers?: ICPBehavioralTrigger[];
  buying_committee?: ICPBuyingCommitteeMember[];
  category_context?: ICPCategoryContext;
  fit_score?: number;
  fit_reasoning?: string;
  messaging_angle?: string;
  qualification_questions?: string[];
  primary_barriers?: BarrierType[];
  is_selected?: boolean;
  intake_id?: string;
}

// =====================================================
// COHORT TYPES
// =====================================================

export interface CohortRule {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than' | 'in' | 'not_in';
  value: any;
}

export interface CohortDefinition {
  rules: CohortRule[];
  data_sources: string[];
  refresh_frequency?: 'realtime' | 'hourly' | 'daily' | 'weekly';
}

export interface Cohort {
  id: string;
  user_id: string;
  icp_id?: string;
  
  name: string;
  description?: string;
  definition: CohortDefinition;
  
  member_count: number;
  last_synced_at?: string;
  is_active: boolean;
  
  created_at: string;
  updated_at: string;
}

// =====================================================
// BARRIER TYPES
// =====================================================

export interface BarrierSignal {
  signal_name: string;
  value: number;
  threshold: number;
  source: string;
  timestamp: string;
}

export interface Barrier {
  id: string;
  user_id: string;
  icp_id?: string;
  cohort_id?: string;
  
  barrier_type: BarrierType;
  confidence: number;              // 0-1
  
  supporting_signals: BarrierSignal[];
  metrics_snapshot: Record<string, any>;
  analysis_notes?: string;
  
  recommended_protocols: ProtocolType[];
  
  diagnosed_at: string;
  updated_at: string;
}

// =====================================================
// PROTOCOL TYPES
// =====================================================

export interface ProtocolTriggerCondition {
  metric: string;
  operator: 'less_than' | 'greater_than' | 'equals' | 'between';
  threshold: number;
  threshold_upper?: number;
  description?: string;
}

export interface ProtocolMetricTarget {
  target: number;
  unit: string;
  rag_thresholds?: {
    green_above?: number;
    red_below?: number;
  };
}

export interface ProtocolChecklistItem {
  task: string;
  category: string;
  is_required: boolean;
}

export interface Protocol {
  id: string;
  code: ProtocolType;
  name: string;
  description?: string;
  
  targets_barrier: BarrierType;
  
  trigger_conditions: ProtocolTriggerCondition[];
  required_asset_types: string[];
  channel_rules: {
    primary: string[];
    secondary: string[];
    exclude: string[];
  };
  metric_targets: Record<string, ProtocolMetricTarget>;
  standard_checklist: ProtocolChecklistItem[];
  
  is_active: boolean;
  display_order: number;
  
  created_at: string;
  updated_at: string;
}

// =====================================================
// MOVE TEMPLATE TYPES
// =====================================================

export interface MoveTemplateInput {
  key: string;
  label: string;
  type: 'text' | 'number' | 'select' | 'multiselect' | 'textarea' | 'boolean';
  required: boolean;
  options?: string[];
}

export interface MoveTemplateTask {
  task: string;
  category: string;
  estimated_hours: number;
  dependencies?: string[];
}

export interface MoveTemplateAssetRequirement {
  type: string;
  quantity: number;
  description?: string;
}

export interface MoveTemplateMetric {
  metric: string;
  target: number;
  unit: string;
}

export interface MoveTemplate {
  id: string;
  slug: string;
  name: string;
  description?: string;
  
  protocol_type: ProtocolType;
  barrier_type: BarrierType;
  funnel_stage?: 'tofu' | 'mofu' | 'bofu' | 'lifecycle';
  
  required_inputs: MoveTemplateInput[];
  channels: string[];
  task_template: MoveTemplateTask[];
  asset_requirements: MoveTemplateAssetRequirement[];
  automation_hooks: {
    triggers?: string[];
    actions?: string[];
    integrations?: string[];
  };
  success_metrics: MoveTemplateMetric[];
  
  base_impact_score: number;
  base_effort_score: number;
  
  is_active: boolean;
  display_order: number;
  tags: string[];
  
  created_at: string;
  updated_at: string;
}

// =====================================================
// CAMPAIGN TYPES
// =====================================================

export interface CampaignBudgetPlan {
  total: number;
  currency: string;
  allocation: Record<string, number>;  // channel -> percentage
}

export interface CampaignTargets {
  pipeline_value?: number;
  opps?: number;
  conversion_rate?: number;
  cac_ceiling?: number;
  payback_months?: number;
  [key: string]: number | undefined;
}

export interface Campaign {
  id: string;
  user_id: string;
  
  name: string;
  description?: string;
  
  // Strategy
  goal: GoalType;
  demand_source: DemandSourceType;
  persuasion_axis: PersuasionAxisType;
  
  // Targeting
  icp_ids: string[];
  cohort_ids: string[];
  
  // Barriers and protocols
  primary_barriers: BarrierType[];
  protocols: ProtocolType[];
  
  // Time
  start_date?: string;
  end_date?: string;
  
  // Budget
  budget_plan: CampaignBudgetPlan;
  
  // Targets
  targets: CampaignTargets;
  
  // Status
  status: CampaignStatus;
  rag_status: RAGStatus;
  rag_details: Record<string, any>;
  
  // Relations
  created_from_spike?: string;
  
  created_at: string;
  updated_at: string;
}

export interface CreateCampaignInput {
  name: string;
  description?: string;
  goal: GoalType;
  demand_source: DemandSourceType;
  persuasion_axis: PersuasionAxisType;
  icp_ids?: string[];
  cohort_ids?: string[];
  primary_barriers?: BarrierType[];
  protocols?: ProtocolType[];
  start_date?: string;
  end_date?: string;
  budget_plan?: Partial<CampaignBudgetPlan>;
  targets?: CampaignTargets;
}

// =====================================================
// MOVE TYPES
// =====================================================

export interface MoveTask {
  id: string;
  task: string;
  status: 'pending' | 'in_progress' | 'completed' | 'skipped';
  assignee?: string;
  due_date?: string;
  completed_at?: string;
}

export interface MoveKPI {
  target: number;
  actual?: number;
  unit: string;
}

export interface Move {
  id: string;
  user_id: string;
  
  campaign_id?: string;
  spike_id?: string;
  template_id?: string;
  
  name: string;
  description?: string;
  
  protocol?: ProtocolType;
  icp_id?: string;
  
  channels: string[];
  tasks: MoveTask[];
  
  impact_score: number;
  effort_score: number;
  ev_score?: number;
  
  status: MoveStatus;
  progress_percentage: number;
  
  rag_status: RAGStatus;
  rag_details: Record<string, any>;
  
  kpis: Record<string, MoveKPI>;
  
  planned_start?: string;
  planned_end?: string;
  actual_start?: string;
  actual_end?: string;
  
  created_at: string;
  updated_at: string;
}

export interface CreateMoveInput {
  campaign_id?: string;
  spike_id?: string;
  template_id?: string;
  name: string;
  description?: string;
  protocol?: ProtocolType;
  icp_id?: string;
  channels?: string[];
  planned_start?: string;
  planned_end?: string;
}

// =====================================================
// ASSET TYPES
// =====================================================

export interface AssetVariant {
  id: string;
  name: string;
  content: string;
  performance_data?: Record<string, any>;
}

export interface Asset {
  id: string;
  user_id: string;
  
  move_id?: string;
  campaign_id?: string;
  icp_id?: string;
  protocol?: ProtocolType;
  
  name: string;
  asset_type: string;
  
  content?: string;
  content_format: 'markdown' | 'html' | 'json';
  
  variants: AssetVariant[];
  
  status: AssetStatus;
  
  distribution_links: Record<string, string>;
  performance_data: Record<string, any>;
  
  tags: string[];
  version: number;
  
  created_at: string;
  updated_at: string;
  approved_at?: string;
  deployed_at?: string;
}

export interface CreateAssetInput {
  move_id?: string;
  campaign_id?: string;
  icp_id?: string;
  protocol?: ProtocolType;
  name: string;
  asset_type: string;
  content?: string;
  content_format?: 'markdown' | 'html' | 'json';
}

// =====================================================
// METRIC TYPES
// =====================================================

export interface MetricRAGThresholds {
  green_above?: number;
  red_below?: number;
}

export interface Metric {
  id: string;
  user_id: string;
  
  scope_type: 'channel' | 'move' | 'protocol' | 'campaign' | 'icp' | 'business';
  scope_id?: string;
  
  metric_name: string;
  metric_category?: string;
  
  value?: number;
  unit?: string;
  
  period_start?: string;
  period_end?: string;
  
  target_value?: number;
  rag_status: RAGStatus;
  rag_thresholds: MetricRAGThresholds;
  
  source?: string;
  raw_data: Record<string, any>;
  
  recorded_at: string;
  created_at: string;
}

export interface CreateMetricInput {
  scope_type: 'channel' | 'move' | 'protocol' | 'campaign' | 'icp' | 'business';
  scope_id?: string;
  metric_name: string;
  metric_category?: string;
  value?: number;
  unit?: string;
  period_start?: string;
  period_end?: string;
  target_value?: number;
  rag_thresholds?: MetricRAGThresholds;
  source?: string;
}

// =====================================================
// SPIKE TYPES
// =====================================================

export interface SpikeTargets {
  pipeline_value?: number;
  opps?: number;
  cac_ceiling?: number;
  max_payback_months?: number;
  [key: string]: number | undefined;
}

export interface SpikeResults {
  pipeline_generated?: number;
  opps_created?: number;
  actual_cac?: number;
  conversion_rate?: number;
  [key: string]: number | undefined;
}

export interface SpikeLearning {
  type: 'worked' | 'failed' | 'insight';
  description: string;
  protocol?: ProtocolType;
  move_id?: string;
  evidence?: string;
}

export interface Spike {
  id: string;
  user_id: string;
  
  name: string;
  
  spike_type: SpikeType;
  goal: GoalType;
  demand_source?: DemandSourceType;
  
  primary_icp_id?: string;
  secondary_icp_ids: string[];
  
  barriers: BarrierType[];
  protocols: ProtocolType[];
  
  targets: SpikeTargets;
  
  start_date: string;
  end_date: string;
  
  campaign_id?: string;
  move_ids: string[];
  
  status: SpikeStatus;
  
  current_day: number;
  progress_percentage: number;
  
  rag_status: RAGStatus;
  rag_details: Record<string, any>;
  
  results: SpikeResults;
  learnings: SpikeLearning[];
  
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface CreateSpikeInput {
  name: string;
  spike_type: SpikeType;
  goal: GoalType;
  demand_source?: DemandSourceType;
  primary_icp_id?: string;
  secondary_icp_ids?: string[];
  barriers?: BarrierType[];
  protocols?: ProtocolType[];
  targets: SpikeTargets;
  start_date: string;
  end_date: string;
}

// =====================================================
// GUARDRAIL TYPES
// =====================================================

export interface Guardrail {
  id: string;
  user_id: string;
  
  spike_id?: string;
  campaign_id?: string;
  icp_id?: string;
  
  name: string;
  description?: string;
  
  metric: string;
  operator: 'greater_than' | 'less_than' | 'equals' | 'between';
  threshold: number;
  threshold_upper?: number;
  
  action: GuardrailAction;
  
  is_active: boolean;
  is_triggered: boolean;
  last_triggered_at?: string;
  trigger_count: number;
  
  created_at: string;
  updated_at: string;
}

export interface CreateGuardrailInput {
  spike_id?: string;
  campaign_id?: string;
  icp_id?: string;
  name: string;
  description?: string;
  metric: string;
  operator: 'greater_than' | 'less_than' | 'equals' | 'between';
  threshold: number;
  threshold_upper?: number;
  action?: GuardrailAction;
}

export interface GuardrailEvent {
  id: string;
  guardrail_id: string;
  user_id: string;
  
  event_type: 'triggered' | 'resolved' | 'overridden' | 'paused';
  
  metric_value?: number;
  threshold_value?: number;
  
  action_taken?: string;
  affected_entities: {
    campaigns?: string[];
    moves?: string[];
    assets?: string[];
  };
  
  override_reason?: string;
  overridden_by?: string;
  
  occurred_at: string;
}

// =====================================================
// EXPERIMENT TYPES
// =====================================================

export interface Experiment {
  id: string;
  user_id: string;
  
  spike_id?: string;
  campaign_id?: string;
  move_id?: string;
  
  name: string;
  hypothesis?: string;
  
  bet_type: 'core' | 'growth' | 'frontier';
  
  expected_impact: number;
  probability: number;
  effort: number;
  ev_score?: number;
  
  status: 'planned' | 'running' | 'completed' | 'killed';
  
  actual_outcome?: string;
  learnings?: string;
  promoted_to_baseline: boolean;
  
  started_at?: string;
  ended_at?: string;
  created_at: string;
}

// =====================================================
// API RESPONSE TYPES
// =====================================================

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface APIError {
  error: string;
  code?: string;
  details?: Record<string, any>;
}

export interface APISuccess<T> {
  success: true;
  data: T;
}

// =====================================================
// AGENT TYPES
// =====================================================

export interface AgentInput {
  [key: string]: any;
}

export interface AgentOutput {
  success: boolean;
  data?: any;
  error?: string;
  fallback?: boolean;
}

export interface ICPGenerationInput {
  positioning: any;
  company: any;
  product: any;
  market: any;
  strategy: any;
}

export interface BarrierAnalysisInput {
  icp_id: string;
  metrics: Record<string, number>;
  cohort_data?: any;
}

export interface MoveGenerationInput {
  campaign_id: string;
  icp_id: string;
  barrier: BarrierType;
  protocol: ProtocolType;
  template_slug?: string;
}

export interface AssetGenerationInput {
  move_id: string;
  asset_type: string;
  positioning: any;
  icp: ICP;
  context?: Record<string, any>;
}

