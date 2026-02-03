// Campaign Types

export enum CampaignObjective {
  LAUNCH = 'launch',
  LEAD_GENERATION = 'lead_generation',
  CONVERSION = 'conversion',
  AWARENESS = 'awareness',
  RETENTION = 'retention',
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

export enum MoveStatus {
  DRAFT = 'draft',
  SCHEDULED = 'scheduled',
  RUNNING = 'running',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  FAILED = 'failed'
}

export interface Campaign {
  id: string;
  name: string;
  description?: string;
  status: 'draft' | 'active' | 'paused' | 'completed';
  createdAt: string;
  updatedAt: string;
  analytics?: CampaignAnalytics;
  tags?: string[];
  type?: string;
  startDate?: string;
  endDate?: string;
  budget?: number;
  spend?: number;
  targetAudience?: string;
  moves?: CampaignMove[];
}

export interface CampaignAnalytics {
  overview: {
    totalReach: number;
    totalEngagement: number;
    totalConversions: number;
    totalRevenue: number;
    roi: number;
  };
  roi: {
    cac?: number;
    roas?: number;
    ltv?: number;
  };
  funnel?: CampaignFunnelStage[];
  channels?: CampaignChannel[];
  daily?: CampaignDailyMetric[];
  performance?: CampaignPerformance;
}

export interface CampaignChannel {
  name: string;
  spend: number;
  conversions: number;
  revenue: number;
  roi: number;
}

export interface CampaignDailyMetric {
  date: string;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  revenue: number;
}

export interface CampaignPerformance {
  ctr: number;
  cpc: number;
  cpm: number;
}

export interface CampaignTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
}

export interface CampaignMove {
  id: string;
  title: string;
  description?: string;
  status: string;
  order: number;
  dueDate?: string;
  assignee?: string;
}

export interface CampaignFunnelStage {
  stage: string;
  count: number;
}

export interface CreateCampaignRequest {
  name: string;
  description?: string;
  type?: string;
  objective?: CampaignObjective | string;
  startDate?: string;
  endDate?: string;
  budget?: number | { total: number; currency: string; allocated?: Record<string, number>; spent?: number; remaining?: number };
  targetAudience?: string | { name: string; criteria?: Record<string, unknown>; size?: number; estimatedReach?: number; customProperties?: Record<string, unknown> };
  tags?: string[];
  timeline?: { startDate?: Date | string; endDate?: Date | string; phases?: unknown[]; milestones?: unknown[] };
  settings?: Record<string, unknown>;
}
