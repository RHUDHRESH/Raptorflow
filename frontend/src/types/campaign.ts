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
  moves: Move[];
  plays: Play[];
  analytics: CampaignAnalytics;
  team: CampaignTeam[];
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
  description: string;
  config: MoveConfig;
  status: MoveStatus;
  execution: MoveExecution;
  dependencies: string[]; // IDs of moves that must complete first
  analytics: MoveAnalytics;
  templateId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Play {
  id: string;
  name: string;
  description: string;
  category: PlayCategory;
  moves: string[]; // Array of move IDs in sequence
  conditions: PlayCondition[];
  isActive: boolean;
  successMetrics: PlaySuccessMetric[];
  templateId?: string;
  createdAt: Date;
  updatedAt: Date;
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

export enum PlayCategory {
  ACQUISITION = 'acquisition',
  ACTIVATION = 'activation',
  RETENTION = 'retention',
  REVENUE = 'revenue',
  REFERRAL = 'referral'
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
  type: 'immediate' | 'scheduled' | 'recurring';
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
