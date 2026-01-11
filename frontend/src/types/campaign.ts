// Core data models for Moves & Campaigns system

export interface Campaign {
  id: string;
  name: string;
  description: string;
  objective: CampaignObjective;
  status: CampaignStatus;
  targetAudience: AudienceSegment;
  budget: CampaignBudget;
  timeline: CampaignTimeline;
  moves: string[];
  plays: string[];
  analytics: CampaignAnalytics;
  team: CampaignTeam;
  settings: CampaignSettings;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  tags: string[];
  templateId?: string;
}

export interface Move {
  id: string;
  name: string;
  type: MoveType;
  category?: string;
  description: string;
  config: MoveConfig;
  status: MoveStatus;
  execution: MoveExecution;
  dependencies: string[]; // IDs of moves that must complete first
  analytics: MoveAnalytics;
  templateId?: string;
  createdAt: Date;
  updatedAt: Date;
  createdBy?: string;
  icon?: any;
}

export interface Play {
  id: string;
  name: string;
  description: string;
  category: PlayCategory;
  moves: string[]; // Array of move IDs in sequence
  conditions?: PlayCondition[];
  isActive: boolean;
  status?: PlayStatus;
  successMetrics?: PlaySuccessMetric[];
  config?: PlayConfig;
  templateId?: string;
  createdAt: Date;
  updatedAt: Date;
  rating?: number;
  usageCount?: number;
  tags?: string[];
  createdBy?: string;
}

export interface AudienceSegment {
  id: string;
  name: string;
  criteria: AudienceCriteria;
  size: number;
  estimatedReach: number;
  customProperties: Record<string, any>;
}

export interface CampaignBudget {
  total: number;
  currency: string;
  allocated: Record<string, number>; // By move type
  spent: number;
  remaining: number;
}

export interface CampaignTimeline {
  startDate: Date;
  endDate: Date;
  phases: CampaignPhase[];
  milestones: CampaignMilestone[];
}

export interface CampaignAnalytics {
  overview: AnalyticsOverview;
  funnel: ConversionFunnel;
  engagement: EngagementMetrics;
  roi: ROIMetrics;
  performance: PerformanceMetrics;
}

export interface CampaignTeam {
  ownerId: string;
  members: TeamMember[];
  roles: Record<string, TeamRole>;
  permissions: Permission[];
}

export interface CampaignSettings {
  autoOptimization: boolean;
  abTesting: boolean;
  notifications: NotificationSettings;
  integrations: IntegrationSettings;
  branding: BrandingSettings;
}

// Enums
export enum CampaignObjective {
  AWARENESS = 'awareness',
  LEAD_GENERATION = 'lead_generation',
  CONVERSION = 'conversion',
  RETENTION = 'retention',
  LAUNCH = 'launch',
  PROMOTION = 'promotion'
}

export enum CampaignStatus {
  DRAFT = 'draft',
  PLANNING = 'planning',
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum MoveType {
  EMAIL = 'email',
  SOCIAL_MEDIA = 'social_media',
  CONTENT = 'content',
  ADS = 'ads',
  OUTREACH = 'outreach',
  WEBINAR = 'webinar',
  LANDING_PAGE = 'landing_page',
  SMS = 'sms',
  PUSH = 'push',
  ANALYTICS = 'analytics'
}

export enum MoveStatus {
  DRAFT = 'draft',
  SCHEDULED = 'scheduled',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export enum PlayStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  PAUSED = 'paused',
  ARCHIVED = 'archived'
}

export enum PlayExecutionStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  SKIPPED = 'skipped',
  SCHEDULED = 'scheduled'
}

export enum PlayCategory {
  ACQUISITION = 'acquisition',
  ACTIVATION = 'activation',
  RETENTION = 'retention',
  REVENUE = 'revenue',
  REFERRAL = 'referral',
  ONBOARDING = 'onboarding',
  CUSTOM = 'custom',
  NURTURING = 'nurturing',
  CONVERSION = 'conversion',
  LAUNCH = 'launch',
  EVENT = 'event',
  CONTENT = 'content',
  REACTIVATION = 'reactivation',
  SALES = 'sales',
  FEEDBACK = 'feedback'
}

// Supporting Types
export interface MoveConfig {
  [key: string]: any;
  // Email specific
  subject?: string;
  content?: string;
  template?: string;
  list?: string;
  // Social specific
  platform?: string;
  postContent?: string;
  media?: string[];
  // Ads specific
  adPlatform?: string;
  adCopy?: string;
  targeting?: AdTargeting;
  bidStrategy?: string;
  budget?: number;
  // Content specific
  contentType?: string;
  title?: string;
  body?: string;
  cta?: string;
  // Common
  schedule?: ScheduleConfig;
  triggers?: TriggerConfig[];
}

export interface MoveExecution {
  scheduledAt?: Date;
  startedAt?: Date;
  completedAt?: Date;
  attempts: number;
  lastError?: string;
  logs: ExecutionLog[];
  results: ExecutionResults;
}

export interface MoveAnalytics {
  sent?: number;
  delivered?: number;
  opened?: number;
  clicked?: number;
  converted?: number;
  revenue?: number;
  cost?: number;
  engagementRate?: number;
  conversionRate?: number;
}

export interface AudienceCriteria {
  demographics?: DemographicCriteria;
  behavior?: BehavioralCriteria;
  firmographic?: FirmographicCriteria;
  custom?: Record<string, any>;
}

export interface CampaignPhase {
  id: string;
  name: string;
  startDate: Date;
  endDate: Date;
  description: string;
  moves: string[];
}

export interface CampaignMilestone {
  id: string;
  name: string;
  date: Date;
  description: string;
  achieved: boolean;
}

export interface AnalyticsOverview {
  totalReach: number;
  totalEngagement: number;
  totalConversions: number;
  totalRevenue: number;
  totalCost: number;
  roi: number;
}

export interface ConversionFunnel {
  stages: FunnelStage[];
  conversionRates: Record<string, number>;
}

export interface FunnelStage {
  name: string;
  count: number;
  rate: number;
  value?: number;
}

export interface EngagementMetrics {
  byChannel: Record<string, ChannelMetrics>;
  byContentType: Record<string, ContentMetrics>;
  byTimeframe: Record<string, TimeframeMetrics>;
}

export interface ROIMetrics {
  spend: number;
  revenue: number;
  profit: number;
  roi: number;
  roas: number;
  cac: number;
  ltv: number;
}

export interface PerformanceMetrics {
  kpis: KPIData[];
  benchmarks: BenchmarkData[];
  trends: TrendData[];
}

export interface TeamMember {
  userId: string;
  name: string;
  email: string;
  role: TeamRole;
  permissions: Permission[];
  joinedAt: Date;
}

export interface NotificationSettings {
  email: boolean;
  push: boolean;
  slack: boolean;
  frequency: 'realtime' | 'daily' | 'weekly';
  events: NotificationEvent[];
}

export interface IntegrationSettings {
  emailProvider?: EmailProviderConfig;
  crm?: CRMConfig;
  analytics?: AnalyticsConfig;
  social?: SocialConfig;
  ads?: AdsConfig[];
}

export interface BrandingSettings {
  logo?: string;
  colors: BrandColors;
  fonts: BrandFonts;
  voice: BrandVoice;
}

// Additional supporting types
export interface DemographicCriteria {
  age?: Range;
  gender?: string[];
  location?: LocationCriteria;
  language?: string[];
  income?: Range;
}

export interface BehavioralCriteria {
  pastPurchases?: boolean;
  emailEngagement?: EngagementLevel;
  webActivity?: WebActivityCriteria;
  socialActivity?: SocialActivityCriteria;
}

export interface FirmographicCriteria {
  companySize?: string[];
  industry?: string[];
  revenue?: Range;
  location?: LocationCriteria;
}

export interface ScheduleConfig {
  scheduleType: 'immediate' | 'scheduled' | 'recurring';
  datetime?: Date;
  timezone?: string;
  frequency?: RecurrencePattern;
}

export interface TriggerConfig {
  type: TriggerType;
  conditions: TriggerCondition[];
  delay?: number;
}

export interface ExecutionLog {
  timestamp: Date;
  level: 'info' | 'warn' | 'error';
  message: string;
  data?: any;
}

export interface ExecutionResults {
  success: boolean;
  metrics: Record<string, number>;
  artifacts?: string[];
  errors?: string[];
  nextRun?: Date;
}

// Type aliases and constants
export type CampaignObjectiveType = keyof typeof CampaignObjective;
export type MoveTypeType = keyof typeof MoveType;
export type CampaignStatusType = keyof typeof CampaignStatus;

// Notification events for settings
export type NotificationEvent =
  | 'launch'
  | 'milestone'
  | 'error'
  | 'lead'
  | 'demo'
  | 'conversion'
  | 'download'
  | 'publish'
  | 'inventory'
  | 'mention'
  | 'engagement'
  | 'registration'
  | 'upload';



// Utility types
export interface CreateCampaignRequest {
  name: string;
  description: string;
  objective: CampaignObjective;
  targetAudience: Partial<AudienceSegment>;
  budget: Partial<CampaignBudget>;
  timeline: Partial<CampaignTimeline>;
  settings?: Partial<CampaignSettings>;
}

export interface UpdateCampaignRequest extends Partial<CreateCampaignRequest> {
  id: string;
  status?: CampaignStatus;
}

export interface CampaignTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  objective: CampaignObjective;
  structure: CampaignStructure;
  isPublic: boolean;
  usageCount: number;
  rating: number;
}

export interface CampaignStructure {
  phases: Omit<CampaignPhase, 'id' | 'moves'>[];
  recommendedMoves: RecommendedMove[];
  defaultSettings: Partial<CampaignSettings>;
}

export interface RecommendedMove {
  type: MoveType;
  name: string;
  description: string;
  config: Partial<MoveConfig>;
  optional: boolean;
}

// Helper functions
export const createCampaignId = (): string => {
  return `campaign_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const createMoveId = (): string => {
  return `move_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const calculateCampaignROI = (revenue: number, cost: number): number => {
  return cost > 0 ? ((revenue - cost) / cost) * 100 : 0;
};

export const isCampaignActive = (campaign: Campaign): boolean => {
  return campaign.status === CampaignStatus.ACTIVE;
};

export const canEditCampaign = (campaign: Campaign, userId: string): boolean => {
  return campaign.team.ownerId === userId ||
    campaign.team.members.some(m => m.userId === userId && m.permissions.includes('edit'));
};

export type TriggerType = 'event' | 'time' | 'condition';

export interface LocationCriteria {
  country?: string[];
  region?: string[];
  city?: string[];
}

export interface Range {
  min: number;
  max: number;
}

export type EngagementLevel = 'high' | 'medium' | 'low';

export interface WebActivityCriteria {
  visitedPages?: string[];
  timeOnSite?: number;
}

export interface SocialActivityCriteria {
  platforms?: string[];
  interactions?: string[];
}

export type RecurrencePattern = 'daily' | 'weekly' | 'monthly';

export interface TriggerCondition {
  field: string;
  operator: string;
  value: any;
}

export interface EmailProviderConfig {
  provider: string;
  apiKey: string;
}

export interface CRMConfig {
  provider: string;
  apiKey: string;
}

export interface AnalyticsConfig {
  provider: string;
  trackingId: string;
}

export interface SocialConfig {
  platforms: Record<string, { accessToken: string }>;
}

export interface AdsConfig {
  platform: string;
  accountId: string;
}

export interface BrandColors {
  primary: string;
  secondary: string;
}

export interface BrandFonts {
  heading: string;
  body: string;
}

export interface BrandVoice {
  tone: string;
  style: string;
}

export interface PlaySuccessMetric {
  metric: string;
  target: number;
}

export interface PlayCondition {
  type: string;
  operator?: string;
  value: any;
  moveId?: string;
  metric?: string;
}

export type Permission = string;

export type TeamRole = 'owner' | 'admin' | 'editor' | 'viewer';

export interface AdTargeting {
  locations?: string[];
  interests?: string[];
  ageRange?: Range;
}

export interface ChannelMetrics {
  impressions: number;
  clicks: number;
}

export interface ContentMetrics {
  views: number;
  shares: number;
}

export interface TimeframeMetrics {
  start: Date;
  end: Date;
  data: any;
}

export interface KPIData {
  name: string;
  value: number;
  trend: number;
  change?: number;
}

export interface BenchmarkData {
  name: string;
  value: number;
}

export interface TrendData {
  date: string;
  value: number;
}

export interface PlayConfig {
  steps: PlayStep[];
  triggers?: any[];
  conditions?: any[];
}

export interface PlayStep {
  id: string;
  name: string;
  moves: string[];
  conditions?: PlayCondition[];
  delay?: number;
  parallel?: boolean;
}
