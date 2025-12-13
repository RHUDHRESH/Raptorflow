import { z } from 'zod';

// =====================================================
// AGENT I/O CONTRACTS
// =====================================================

export const AgentIO = z.object({
  inputs: z.record(z.any()),
  outputs: z.record(z.any()),
  metadata: z.object({
    agent_name: z.string(),
    execution_time: z.number(),
    token_usage: z.number().optional(),
    cost_estimate: z.number().optional(),
    model_used: z.string().optional(),
    success: z.boolean(),
    errors: z.array(z.string()).optional(),
    timestamp: z.string()
  })
});

export type AgentIO = z.infer<typeof AgentIO>;

// =====================================================
// DEPARTMENT DEFINITIONS
// =====================================================

export enum Department {
  ORCHESTRATION = 'orchestration',
  MARKET_INTELLIGENCE = 'market_intelligence',
  OFFER_POSITIONING = 'offer_positioning',
  MOVES_CAMPAIGNS = 'moves_campaigns',
  CREATIVE = 'creative',
  DISTRIBUTION = 'distribution',
  ANALYTICS = 'analytics',
  MEMORY_LEARNING = 'memory_learning',
  SAFETY_QUALITY = 'safety_quality'
}

// =====================================================
// AGENT ROSTER DEFINITIONS
// =====================================================

export const AGENT_ROSTER = {
  // Department 0: Orchestration
  [Department.ORCHESTRATION]: ['orchestrator'],

  // Department 1: Market Intelligence
  [Department.MARKET_INTELLIGENCE]: [
    'market_intel_agent',
    'competitor_intelligence_agent',
    'keyword_topic_miner_agent',
    'trend_radar_agent',
    'audience_insight_agent',
    'objection_miner_agent',
    'emotional_angle_architect'
  ],

  // Department 2: Offer & Positioning
  [Department.OFFER_POSITIONING]: [
    'positioning_architect_agent',
    'offer_architect_agent',
    'value_proposition_agent',
    'rtb_agent',
    'message_pillar_agent',
    'revenue_model_agent'
  ],

  // Department 3: Funnels, Moves, Campaigns
  [Department.MOVES_CAMPAIGNS]: [
    'move_designer_agent',
    'campaign_architect_agent',
    'funnel_engineer_agent',
    'channel_mix_strategist',
    'experiment_generator_agent',
    'budget_allocation_agent',
    'sequencing_agent'
  ],

  // Department 4: Creative & Muse
  [Department.CREATIVE]: [
    'creative_director_agent',
    'copywriter_agent',
    'visual_concept_agent',
    'social_content_agent',
    'ad_variants_agent',
    'longform_writer_agent',
    'asset_repurposing_agent'
  ],

  // Department 5: Media, Distribution & Automation
  [Department.DISTRIBUTION]: [
    'distribution_strategist_agent',
    'posting_scheduler_agent',
    'email_automation_agent',
    'whatsapp_engagement_agent',
    'ads_targeting_agent',
    'retargeting_agent',
    'lead_nurture_agent'
  ],

  // Department 6: Analytics, Matrix & Optimization
  [Department.ANALYTICS]: [
    'metrics_interpreter_agent',
    'attribution_lite_agent',
    'rag_status_agent',
    'forecasting_agent',
    'insight_engine_agent',
    'kill_scale_agent',
    'lessons_learned_agent'
  ],

  // Department 7: Memory, Personalization & Learning
  [Department.MEMORY_LEARNING]: [
    'brand_memory_agent',
    'user_preference_agent',
    'template_weighting_agent',
    'behavior_tracking_agent',
    'knowledge_base_builder_agent',
    'periodic_internet_learner_agent',
    'persona_evolution_agent'
  ],

  // Department 8: Safety, Quality & Guardrails
  [Department.SAFETY_QUALITY]: [
    'brand_safety_agent',
    'compliance_agent',
    'ethical_guardrail_agent',
    'quality_rater_agent',
    'rewrite_fixer_agent'
  ]
} as const;

// =====================================================
// ORCHESTRATOR STATE MACHINE
// =====================================================

export enum OrchestratorState {
  INITIALIZING = 'initializing',
  PLANNING = 'planning',
  EXECUTING = 'executing',
  VALIDATING = 'validating',
  COMPLETING = 'completing',
  ERROR = 'error',
  DEAD_END = 'dead_end'
}

export const OrchestratorContext = z.object({
  user_id: z.string(),
  goal: z.string(),
  campaign_context: z.record(z.unknown()).optional(),
  icp_context: z.record(z.unknown()).optional(),
  current_state: z.nativeEnum(OrchestratorState),
  execution_plan: z.array(z.object({
    department: z.nativeEnum(Department),
    agents: z.array(z.string()),
    dependencies: z.array(z.string()).optional(),
    priority: z.enum(['high', 'medium', 'low'])
  })),
  completed_agents: z.array(z.string()),
  failed_agents: z.array(z.string()),
  results: z.record(z.unknown()),
  dead_end_detected: z.boolean(),
  dead_end_reason: z.string().optional(),
  token_budget: z.object({
    total: z.number(),
    used: z.number(),
    remaining: z.number(),
    last_checkpoint: z.number()
  }),
  execution_metadata: z.object({
    start_time: z.string(),
    estimated_completion: z.string().optional(),
    current_step: z.string().optional(),
    progress_percentage: z.number()
  })
});

export type OrchestratorContext = z.infer<typeof OrchestratorContext>;

// =====================================================
// TOOL REGISTRY
// =====================================================

export interface ToolDescriptor {
  name: string;
  description: string;
  parameters: z.ZodSchema;
  execute: (params: any) => Promise<any>;
  cost_estimate?: number;
  timeout?: number;
  retry_policy?: {
    max_attempts: number;
    backoff_ms: number;
  };
  // SOTA enhancements
  output_schema?: z.ZodSchema;
  examples?: Array<{
    input: any;
    output: any;
    description: string;
  }>;
  category?: string;
  version?: string;
  deprecation_date?: string;
  requires_auth?: boolean;
}

// =====================================================
// AGENT INTERFACE
// =====================================================

export interface BaseAgent {
  name: string;
  department: Department;
  description: string;
  input_schema: z.ZodSchema;
  output_schema: z.ZodSchema;

  execute(input: any, context: OrchestratorContext): Promise<AgentIO>;
  validate_input(input: any): boolean;
  get_required_tools(): string[];
}

// =====================================================
// WORKFLOW DEFINITIONS
// =====================================================

export const WORKFLOW_TEMPLATES = {
  CAMPAIGN_LAUNCH: {
    departments: [
      Department.MARKET_INTELLIGENCE,
      Department.OFFER_POSITIONING,
      Department.MOVES_CAMPAIGNS,
      Department.CREATIVE,
      Department.DISTRIBUTION,
      Department.ANALYTICS
    ],
    estimated_duration: '4-6 hours',
    token_budget: 50000
  },

  ICP_DEVELOPMENT: {
    departments: [
      Department.MARKET_INTELLIGENCE,
      Department.MEMORY_LEARNING
    ],
    estimated_duration: '2-3 hours',
    token_budget: 15000
  },

  CREATIVE_GENERATION: {
    departments: [
      Department.CREATIVE,
      Department.SAFETY_QUALITY
    ],
    estimated_duration: '1-2 hours',
    token_budget: 25000
  },

  OPTIMIZATION_REVIEW: {
    departments: [
      Department.ANALYTICS,
      Department.MEMORY_LEARNING
    ],
    estimated_duration: '1-2 hours',
    token_budget: 10000
  }
} as const;

// =====================================================
// ERROR HANDLING
// =====================================================

export class OrchestratorError extends Error {
  constructor(
    message: string,
    public code: string,
    public context?: any
  ) {
    super(message);
    this.name = 'OrchestratorError';
  }
}

export class AgentError extends Error {
  constructor(
    message: string,
    public agent_name: string,
    public input?: any,
    public context?: any
  ) {
    super(message);
    this.name = 'AgentError';
  }
}

// =====================================================
// TOKEN BUDGET MANAGEMENT
// =====================================================

export interface TokenBudget {
  total: number;
  used: number;
  remaining: number;
  checkpoints: number[];
  alerts: {
    warning_threshold: number;  // 80% used
    critical_threshold: number; // 95% used
  };
}

export const createTokenBudget = (total: number): TokenBudget => ({
  total,
  used: 0,
  remaining: total,
  checkpoints: [],
  alerts: {
    warning_threshold: total * 0.8,
    critical_threshold: total * 0.95
  }
});
