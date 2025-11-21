// KOA Move System - TypeScript Type Definitions

export type ManeuverCategory = 'Offensive' | 'Defensive' | 'Logistical' | 'Recon';
export type FoggRole = 'Spark' | 'Facilitator' | 'Signal';
export type CapabilityTier = 'Foundation' | 'Traction' | 'Scale' | 'Dominance';
export type MoveStatus = 'Planning' | 'OODA_Observe' | 'OODA_Orient' | 'OODA_Decide' | 'OODA_Act' | 'Complete' | 'Killed';
export type SeasonType = 'High_Season' | 'Low_Season' | 'Shoulder';
export type CapabilityStatus = 'Locked' | 'In_Progress' | 'Unlocked';
export type AnomalyType = 'Tone_Clash' | 'Fatigue' | 'Drift' | 'Rule_Violation' | 'Capacity_Overload';
export type AnomalyStatus = 'Open' | 'Acknowledged' | 'Resolved' | 'Ignored';
export type SprintStatus = 'Planning' | 'Active' | 'Review' | 'Complete';
export type LoOStatus = 'Active' | 'Paused' | 'Complete';

export interface ManeuverType {
  id: string;
  name: string;
  category: ManeuverCategory;
  baseDurationDays: number;
  foggRole: FoggRole | null;
  intensityScore: number; // 1-10
  riskProfile: 'Low' | 'Medium' | 'Brand_Risk' | 'Budget_Risk';
  description: string;
  defaultConfig: {
    suggestedChannels?: string[];
    suggestedContentTypes?: string[];
    recommendedFrequency?: string;
  };
  requiredCapabilityIds: string[];
  typicalICPs?: string[];
  createdAt?: Date;
}

export interface CapabilityNode {
  id: string;
  name: string;
  tier: CapabilityTier;
  status: CapabilityStatus;
  workspaceId: string;
  parentNodeIds: string[];
  unlocksManeuverIds: string[];
  description: string;
  completionCriteria: {
    type: 'manual' | 'automatic';
    conditions?: Record<string, any>;
  };
  unlockedAt?: Date | null;
  createdAt?: Date;
}

export interface LineOfOperation {
  id: string;
  workspaceId: string;
  name: string;
  strategicObjective: string;
  seasonalityTag: 'Harvest' | 'Planting' | 'Agnostic';
  centerOfGravity: string;
  status: LoOStatus;
  startDate: Date | null;
  targetDate?: Date | null;
  createdAt?: Date;
}

export interface Sprint {
  id: string;
  workspaceId: string;
  name: string;
  startDate: Date;
  endDate: Date;
  theme?: string;
  capacityBudget: number; // Total intensity points available
  currentLoad: number; // Sum of move intensities
  seasonType: SeasonType;
  status: SprintStatus;
  createdAt?: Date;
}

export interface OODAConfig {
  observeSources: string[]; // ['analytics', 'competitor_pricing', 'social_sentiment']
  orientRules: string; // Context and strategy alignment rules
  decideLogic: string; // Decision criteria and thresholds
  actTriggers: {
    condition: string;
    action: string;
  }[];
  actTasks?: {
    day: number;
    task: string;
    channel: string;
    status: 'pending' | 'complete';
  }[];
}

export interface FoggConfig {
  targetMotivation: 'High' | 'Medium' | 'Low';
  targetAbility: 'High' | 'Medium' | 'Low';
  promptFrequency: 'Daily' | 'Weekly' | 'Triggered';
}

export interface Move {
  id: string;
  workspaceId: string;
  maneuverTypeId: string;
  maneuverType?: ManeuverType; // Populated via join
  sprintId: string | null;
  sprint?: Sprint;
  lineOfOperationId: string | null;
  lineOfOperation?: LineOfOperation;
  name: string;
  primaryIcpId: string;
  secondaryIcpIds: string[];
  
  status: MoveStatus;
  oodaConfig: OODAConfig;
  foggConfig: FoggConfig;
  
  goal: string;
  channels: string[];
  contentFrequency: string;
  actionTypes: string[];
  keyMetrics: Record<string, any>;
  decisionCheckpoints: {
    name: string;
    dueDate: Date;
    completed: boolean;
    notes?: string;
  }[];
  
  startDate: Date | null;
  endDate: Date | null;
  progressPercentage: number;
  ownerId: string | null;
  healthStatus: 'green' | 'amber' | 'red';
  
  anomalies?: MoveAnomaly[];
  logs?: MoveLog[];
  createdAt?: Date;
  updatedAt?: Date;
}

export interface MoveAnomaly {
  id: string;
  moveId: string;
  type: AnomalyType;
  severity: 1 | 2 | 3 | 4 | 5;
  description: string;
  detectedAt: Date;
  resolution?: string;
  resolvedAt?: Date | null;
  status: AnomalyStatus;
}

export interface MoveLog {
  id: string;
  moveId: string;
  date: Date;
  actionsCompleted: number;
  notes?: string;
  metricsSnapshot: Record<string, any>;
  createdAt?: Date;
}

export interface Quest {
  id: string;
  name: string;
  objective: string;
  prerequisiteNodeIds: string[];
  recommendedMoveIds: string[];
  rewardNodeId: string | null;
  lineOfOperationId: string | null;
  progress: number;
  status: 'locked' | 'active' | 'complete';
  createdAt?: Date;
}

// Database row types (for Supabase)
export interface ManeuverTypeRow {
  id: string;
  name: string;
  category: string;
  base_duration_days: number;
  fogg_role: string | null;
  intensity_score: number;
  risk_profile: string;
  description: string;
  default_config: Record<string, any>;
  created_at: string;
}

export interface CapabilityNodeRow {
  id: string;
  name: string;
  tier: string;
  status: string;
  workspace_id: string;
  parent_node_ids: string[];
  unlocks_maneuver_ids: string[];
  description: string;
  completion_criteria: Record<string, any>;
  unlocked_at: string | null;
  created_at: string;
}

export interface MoveRow {
  id: string;
  workspace_id: string;
  maneuver_type_id: string;
  sprint_id: string | null;
  line_of_operation_id: string | null;
  name: string;
  primary_icp_id: string;
  secondary_icp_ids: string[];
  status: string;
  ooda_config: Record<string, any>;
  fogg_config: Record<string, any>;
  goal: string;
  channels: string[];
  content_frequency: string;
  action_types: string[];
  key_metrics: Record<string, any>;
  decision_checkpoints: Record<string, any>[];
  start_date: string | null;
  end_date: string | null;
  progress_percentage: number;
  owner_id: string | null;
  created_at: string;
  updated_at: string;
}


