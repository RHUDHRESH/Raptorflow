/**
 * RaptorFlow 2.0 - Comprehensive TypeScript Types
 * Type definitions for all backend APIs and responses
 */

// ============================================================================
// Critic Agent Types
// ============================================================================

export interface DimensionScore {
  score: number;
  feedback: string;
  suggestions?: string[];
}

export interface ReadabilityScore {
  score: number;
  flesch_kincaid_grade: number;
  estimated_reading_time: number;
  average_sentence_length: number;
  complex_word_count?: number;
}

export interface CriticReview {
  overall_score: number;
  dimensions: {
    clarity: DimensionScore;
    brand_alignment: DimensionScore;
    audience_fit: DimensionScore;
    engagement: DimensionScore;
    factual_accuracy: DimensionScore;
    seo_optimization: DimensionScore;
    readability: ReadabilityScore;
  };
  approval_recommendation: 'approve' | 'approve_with_revisions' | 'reject';
  priority_fixes: string[];
  reviewed_at: string;
  reviewer_confidence: number;
}

// ============================================================================
// Guardian Agent Types
// ============================================================================

export interface CheckResult {
  status: 'passed' | 'warning' | 'failed';
  message: string;
  confidence: number;
  issues?: string[];
  suggestions?: string[];
}

export interface GuardianCheck {
  status: 'approved' | 'flagged' | 'blocked';
  confidence: number;
  checks: {
    legal_compliance: CheckResult;
    brand_safety: CheckResult;
    copyright_risk: CheckResult;
    inclusive_language: CheckResult;
    competitor_mentions?: CheckResult;
    regulatory_compliance?: CheckResult;
  };
  reviewed_at: string;
  requires_human_review: boolean;
}

// ============================================================================
// Performance Prediction Types
// ============================================================================

export interface Prediction {
  predicted_value: number;
  confidence: number;
  confidence_interval: {
    lower: number;
    upper: number;
  };
}

export interface OptimalPostingTime {
  day_of_week: string;
  hour: number;
  expected_boost: number;
  confidence: number;
}

export interface PerformancePrediction {
  likes: Prediction;
  shares: Prediction;
  comments: Prediction;
  click_through_rate: Prediction;
  conversion_rate: Prediction;
  engagement_score: number;
  viral_potential: number;
  optimal_posting_time?: OptimalPostingTime;
  predicted_at: string;
  model_version: string;
}

export interface ABTestPrediction {
  winner: 'variant_a' | 'variant_b' | 'tie';
  confidence: number;
  variant_a_score: number;
  variant_b_score: number;
  expected_improvement: number;
  sample_size_required: number;
}

// ============================================================================
// Memory System Types
// ============================================================================

export interface MemoryEntry {
  key: string;
  value: any;
  memory_type: 'workspace' | 'conversation' | 'agent' | 'semantic' | 'working';
  workspace_id: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
  expires_at?: string;
}

export interface SemanticSearchResult {
  key: string;
  value: any;
  similarity_score: number;
  memory_type: string;
  metadata?: Record<string, any>;
}

export interface MemoryContext {
  workspace_memory: Record<string, any>;
  relevant_conversations: any[];
  agent_learnings: any[];
  semantic_matches: SemanticSearchResult[];
  context_summary: string;
}

// ============================================================================
// Brand Voice Types
// ============================================================================

export interface BrandVoice {
  tone: string[];
  vocabulary: string[];
  forbidden_words: string[];
  sentence_structure: string;
  formality_level: number; // 1-10
  humor_level: number; // 1-10
  examples: string[];
  personality_traits: string[];
  voice_guidelines: string;
}

// ============================================================================
// Cohort/ICP Types
// ============================================================================

export interface Cohort {
  cohort_id: string;
  workspace_id: string;
  nickname: string;
  role: string;
  biggest_pain_point: string;
  demographics?: {
    age_range?: string;
    location?: string;
    company_size?: string;
    industry?: string;
  };
  psychographic_tags: string[];
  behavioral_attributes: string[];
  goals: string[];
  challenges: string[];
  preferred_channels: string[];
  persona_narrative?: string;
  created_at: string;
  updated_at: string;
}

export interface CohortGenerateRequest {
  nickname: string;
  role: string;
  biggest_pain_point: string;
  known_attributes?: string[];
}

// ============================================================================
// Content Types
// ============================================================================

export interface ContentPiece {
  content_id: string;
  workspace_id: string;
  content_type: 'blog' | 'email' | 'social' | 'hook' | 'carousel' | 'meme';
  title?: string;
  content: string;
  metadata: {
    persona_id?: string;
    topic?: string;
    keywords?: string[];
    tone?: string;
    target_cohort_ids?: string[];
  };
  status: 'draft' | 'reviewed' | 'approved' | 'published' | 'rejected';
  critic_review?: CriticReview;
  guardian_check?: GuardianCheck;
  performance_prediction?: PerformancePrediction;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export interface ContentGenerateRequest {
  persona_id: string;
  topic: string;
  goal?: string;
  keywords?: string[];
  tone?: string;
  content_type: 'blog' | 'email' | 'social';
}

// ============================================================================
// Strategy Types
// ============================================================================

export interface Move {
  move_number: number;
  move_name: string;
  move_type: 'awareness' | 'desire' | 'action' | 'persistence' | 'trust';
  objective: string;
  tactics: string[];
  channels: string[];
  duration_days: number;
  success_metrics: {
    [key: string]: {
      metric_name: string;
      target_value: number;
      unit: string;
    };
  };
  dependencies: number[];
  sprints?: Sprint[];
}

export interface Sprint {
  sprint_number: number;
  sprint_name: string;
  tasks: Task[];
  start_date?: string;
  end_date?: string;
}

export interface Task {
  task_id: string;
  task_name: string;
  task_type: 'content' | 'campaign' | 'analysis' | 'optimization' | 'research';
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  assigned_agent?: string;
  due_date: string;
  estimated_hours?: number;
  dependencies?: string[];
}

export interface Strategy {
  strategy_id: string;
  workspace_id: string;
  goal: string;
  timeframe_days: number;
  target_cohorts: Cohort[];
  moves: Move[];
  constraints: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Campaign Types
// ============================================================================

export interface Campaign {
  move_id: string;
  strategy_id: string;
  workspace_id: string;
  name: string;
  status: 'planning' | 'active' | 'paused' | 'completed' | 'cancelled';
  current_sprint?: number;
  progress_percentage: number;
  metrics: CampaignMetrics;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface CampaignMetrics {
  impressions: number;
  clicks: number;
  conversions: number;
  engagement_rate: number;
  roi: number;
  cost: number;
  revenue: number;
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface WorkspaceMetrics {
  workspace_id: string;
  total_reach: number;
  engagement_rate: number;
  total_conversions: number;
  roi: number;
  active_campaigns: number;
  content_pieces_published: number;
  time_series?: TimeSeriesData[];
  top_performing_content: ContentPiece[];
}

export interface TimeSeriesData {
  date: string;
  impressions: number;
  clicks: number;
  conversions: number;
  engagement_rate: number;
}

export interface CampaignInsight {
  insight_id: string;
  insight_type: 'performance' | 'audience' | 'content' | 'timing' | 'channel';
  title: string;
  description: string;
  confidence: number;
  impact_level: 'low' | 'medium' | 'high' | 'critical';
  recommended_actions: string[];
  supporting_data: Record<string, any>;
  generated_at: string;
}

export interface PivotSuggestion {
  should_pivot: boolean;
  confidence: number;
  reason: string;
  current_performance: {
    metric: string;
    value: number;
    trend: 'improving' | 'stable' | 'declining';
  }[];
  suggested_changes: string[];
  expected_improvement: number;
  risk_level: 'low' | 'medium' | 'high';
}

export interface CrossCampaignLearning {
  learning_id: string;
  title: string;
  insight: string;
  confidence: number;
  impact_level: 'low' | 'medium' | 'high' | 'critical';
  applicable_to: string[];
  supporting_campaigns: string[];
  discovered_at: string;
}

// ============================================================================
// Agent Orchestration Types
// ============================================================================

export interface AgentRun {
  run_id: string;
  correlation_id: string;
  graph_name: string;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  total_steps: number;
  completed_steps: number;
  error?: string;
}

export interface ExecutionTraceStep {
  step_number: number;
  agent_name: string;
  action: string;
  input: any;
  output: any;
  duration_ms: number;
  timestamp: string;
  metadata?: Record<string, any>;
  error?: string;
}

export interface ExecutionTrace {
  correlation_id: string;
  graph_name: string;
  total_duration_ms: number;
  steps: ExecutionTraceStep[];
  status: 'completed' | 'failed' | 'partial';
}

export interface AgentMetrics {
  agent_name: string;
  total_executions: number;
  success_rate: number;
  average_duration_ms: number;
  p50_duration_ms: number;
  p95_duration_ms: number;
  p99_duration_ms: number;
  error_count: number;
  last_execution: string;
}

// ============================================================================
// Onboarding Types
// ============================================================================

export interface OnboardingQuestion {
  question_id: string;
  question_text: string;
  question_type: 'text' | 'single_choice' | 'multiple_choice' | 'number' | 'date';
  options?: string[];
  required: boolean;
  validation_rules?: Record<string, any>;
  help_text?: string;
}

export interface OnboardingSession {
  session_id: string;
  workspace_id: string;
  current_question: OnboardingQuestion;
  answers: Record<string, any>;
  progress_percentage: number;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface OnboardingProfile {
  entity_type: 'business' | 'personal_brand' | 'executive' | 'agency';
  industry: string;
  goals: string[];
  target_audience: string;
  budget_range?: string;
  team_size?: number;
  current_marketing_efforts: string[];
  pain_points: string[];
  preferred_channels: string[];
}

// ============================================================================
// Integration Types
// ============================================================================

export interface Integration {
  platform: string;
  status: 'connected' | 'disconnected' | 'error';
  account_id?: string;
  account_name?: string;
  connected_at?: string;
  last_sync?: string;
  metadata?: Record<string, any>;
}

export interface IntegrationStatus {
  platform: string;
  connected: boolean;
  health: 'healthy' | 'degraded' | 'down';
  capabilities: string[];
  last_error?: string;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  correlation_id?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

// ============================================================================
// Error Types
// ============================================================================

export class APIError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: any,
    public correlationId?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class ValidationError extends APIError {
  constructor(message: string, details?: any) {
    super(message, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends APIError {
  constructor(message: string = 'Authentication required') {
    super(message, 'AUTHENTICATION_ERROR');
    this.name = 'AuthenticationError';
  }
}

export class NotFoundError extends APIError {
  constructor(resource: string, id: string) {
    super(`${resource} not found: ${id}`, 'NOT_FOUND');
    this.name = 'NotFoundError';
  }
}

// ============================================================================
// Payment & Subscription Types
// ============================================================================

export interface SubscriptionPlan {
  name: 'ascent' | 'glide' | 'soar';
  price_monthly: number;
  price_yearly: number;
  features: {
    cohorts: number;
    moves: number;
    analytics: boolean;
    integrations: string[];
    support: string;
  };
  limits: {
    cohorts: number;
    moves_per_month: number;
  };
}

export interface Subscription {
  id: string;
  user_id: string;
  workspace_id: string;
  plan: 'free' | 'ascent' | 'glide' | 'soar';
  status: 'active' | 'inactive' | 'cancelled' | 'expired' | 'trial';
  billing_period: 'monthly' | 'yearly';
  current_period_start?: string;
  current_period_end?: string;
  trial_start?: string;
  trial_end?: string;
  phonepe_customer_id?: string;
  phonepe_subscription_id?: string;
  phonepe_transaction_id?: string;
  created_at: string;
  updated_at: string;
  cancelled_at?: string;
}

export interface CreateCheckoutRequest {
  plan: 'ascent' | 'glide' | 'soar';
  billing_period: 'monthly' | 'yearly';
  success_url: string;
  cancel_url: string;
}

export interface CreateCheckoutResponse {
  checkout_url: string;
  session_id: string;
  expires_at: string;
}

export interface PaymentStatus {
  transaction_id: string;
  merchant_transaction_id: string;
  status: 'pending' | 'success' | 'failed' | 'cancelled';
  amount: number;
  payment_method?: string;
}

export interface BillingHistoryItem {
  id: string;
  user_id: string;
  workspace_id: string;
  transaction_id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'success' | 'failed' | 'refunded';
  plan: string;
  billing_period: string;
  payment_method?: string;
  invoice_url?: string;
  created_at: string;
}

export interface PlanLimits {
  plan: 'free' | 'ascent' | 'glide' | 'soar';
  limits: {
    cohorts: number;
    moves_per_month: number;
  };
  current_usage: {
    cohorts: number;
    moves_this_month: number;
  };
  is_limit_reached: boolean;
  upgrade_required: boolean;
  recommended_plan?: string;
}
