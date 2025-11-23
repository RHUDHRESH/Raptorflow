// Shared API-facing types generated to mirror the current backend Pydantic models.
// These are intentionally broad enough to stay compatible with backend evolution while
// remaining strongly typed for the frontend.

export type UUID = string;
export type ISODateString = string;

// ---------- Cohorts / ICP ----------
export interface ICPRequest {
  company_name: string;
  industry: string;
  product_description: string;
  target_market?: string;
  goals?: string[];
  primary_channels?: string[];
}

export interface Demographics {
  age_range?: string;
  gender?: string;
  education?: string;
  income_range?: string;
  geography?: string[];
}

export interface Firmographics {
  company_size?: string;
  revenue_range?: string;
  industry?: string[] | string;
  geography?: string[];
  funding_stage?: string;
  tech_stack?: string[];
}

export interface Psychographics {
  values?: string[];
  pain_points?: string[];
  goals?: string[];
  buying_behavior?: string;
  motivations?: string[];
  objections?: string[];
}

export interface PainPoints {
  operational?: string[];
  financial?: string[];
  strategic?: string[];
  technical?: string[];
}

export interface Cohort {
  id: UUID;
  icp_name: string;
  demographics?: Demographics;
  firmographics?: Firmographics;
  psychographics?: Psychographics;
  pain_points?: PainPoints;
  tags?: string[];
  created_at?: ISODateString;
  updated_at?: ISODateString;
  workspace_id?: UUID;
  funnel_stage?: string;
}

export type ICPResponse = Cohort;

// ---------- Content ----------
export interface BaseContentRequest {
  icp_id: UUID;
  topic?: string;
  tone?: string;
  brand_voice?: BrandVoiceProfile;
  length?: number;
  cta?: string;
  audience?: string;
}

export interface BlogRequest extends BaseContentRequest {
  word_count?: number;
}

export interface EmailRequest extends BaseContentRequest {
  subject?: string;
  sequence_step?: number;
  personalization?: Record<string, unknown>;
}

export interface SocialPostRequest extends BaseContentRequest {
  platform: "linkedin" | "x" | "twitter" | "instagram" | string;
  hook_style?: string;
  hashtags?: string[];
}

export interface HookResponse {
  hooks: string[];
  scores?: number[];
}

export interface DimensionScore {
  score: number;
  issues?: string[];
  suggestions?: string[];
  metadata?: Record<string, unknown>;
}

export interface ReadabilityScore extends DimensionScore {
  flesch_reading_ease?: number;
  grade_level?: string;
}

export interface CriticReview {
  overall_score: number;
  dimensions?: {
    clarity?: DimensionScore;
    brand_alignment?: DimensionScore;
    audience_fit?: DimensionScore;
    engagement?: DimensionScore;
    factual_accuracy?: DimensionScore;
    seo_optimization?: DimensionScore;
    readability?: ReadabilityScore;
  };
  approval_recommendation?: "approve" | "approve_with_revisions" | "reject";
  priority_fixes?: string[];
  optional_improvements?: string[];
}

export interface CheckResult {
  passed: boolean;
  issues?: string[];
  suggestions?: string[];
  metadata?: Record<string, unknown>;
}

export interface GuardianCheck {
  status: "approved" | "flagged" | "blocked";
  checks?: {
    legal_compliance?: CheckResult;
    brand_safety?: CheckResult;
    copyright_risk?: CheckResult;
    inclusive_language?: CheckResult;
    competitor_mentions?: CheckResult;
    regulatory_compliance?: CheckResult;
  };
  required_actions?: string[];
  recommended_actions?: string[];
}

export interface Prediction {
  estimated: number;
  range?: [number, number];
  confidence?: number;
}

export interface PerformancePrediction {
  likes?: Prediction;
  shares?: Prediction;
  comments?: Prediction;
  ctr?: Prediction;
  conversion_rate?: Prediction;
  viral_potential?: number;
}

export interface ContentResponse {
  id?: UUID;
  content: string;
  critic_review?: CriticReview;
  guardian_check?: GuardianCheck;
  performance_prediction?: PerformancePrediction;
  metadata?: Record<string, unknown>;
  created_at?: ISODateString;
}

// ---------- Strategy / Campaigns ----------
export interface StrategyRequest {
  icp_id: UUID;
  goals: string[];
  budget?: number | string;
  channels?: string[];
  timeframe?: string;
}

export type AdaptStage = "assess" | "diagnose" | "analyze" | "plan" | "track";

export interface Move {
  id: UUID;
  name: string;
  stage: AdaptStage;
  description?: string;
  kpis?: string[];
  timeline?: string;
  tasks?: Task[];
}

export interface StrategyResponse {
  id: UUID;
  moves: Move[];
  summary?: string;
}

export interface CampaignRequest {
  move_id?: UUID;
  strategy_id?: UUID;
  objective?: string;
  timeline?: string;
  budget?: number;
}

export interface Task {
  id: UUID;
  name: string;
  status: "todo" | "in_progress" | "done";
  due_date?: ISODateString;
  assignee?: string;
  checklist?: string[];
}

export interface Campaign {
  id: UUID;
  move_id?: UUID;
  objective?: string;
  tasks?: Task[];
  status?: string;
  start_date?: ISODateString;
  end_date?: ISODateString;
}

// ---------- Analytics ----------
export interface AnalyticsInsight {
  message: string;
  severity?: "info" | "warning" | "success";
  action?: string;
  metadata?: Record<string, unknown>;
}

export interface AnalyticsResponse {
  move_id?: UUID;
  insights?: AnalyticsInsight[];
  metrics?: Record<string, number | string | number[] | string[]>;
  critic_averages?: CriticReview["dimensions"];
}

// ---------- Memory ----------
export interface BrandVoiceProfile {
  tone?: string;
  formality?: number;
  personality?: string[];
  banned_words?: string[];
  preferred_phrases?: string[];
  sample_texts?: string[];
}

export interface UserPreferences {
  paragraph_length?: number | string;
  emoji_usage?: "never" | "light" | "medium" | "heavy";
  oxford_comma?: boolean;
  avoid_words?: string[];
  defaults?: Record<string, unknown>;
}

export interface ContentSample {
  id?: UUID;
  title?: string;
  content: string;
  tags?: string[];
  performance?: PerformancePrediction;
  created_at?: ISODateString;
}

export interface MemoryContext {
  workspace_id: UUID;
  brand_voice?: BrandVoiceProfile;
  preferences?: UserPreferences;
  gold_samples?: ContentSample[];
  metadata?: Record<string, unknown>;
}

// ---------- Onboarding ----------
export interface OnboardingQuestion {
  id: string;
  prompt: string;
  helper_text?: string;
  field?: string;
}

export interface OnboardingProfileSummary {
  session_id: string;
  icp_id?: UUID;
  icp_name?: string;
  top_pain_points?: string[];
  suggested_primary_channel?: string;
}

// ---------- Generic API shapes ----------
export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
