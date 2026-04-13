export type Ulid = string;
export type OrgId = string;
export type AvatarRole = "strategist" | "council" | "support_specialist" | "intern";
export type ProtectionBand = "protected" | "important" | "normal" | "disposable";

export interface TenantScoped {
  orgId: OrgId;
}

export interface FoundationSnapshot extends TenantScoped {
  foundationVersion: number;
  sections: Record<string, unknown>;
}

export interface FoundationPatch extends TenantScoped {
  section: string;
  value: unknown;
}

export type FoundationScanMode = "quick" | "deep";

export type FoundationScanStatus = "queued" | "running" | "streaming" | "completed" | "failed";

export interface FoundationVersion extends TenantScoped {
  versionId: Ulid;
  foundationVersion: number;
  scannedAt: string;
  sourceScanId?: Ulid;
  snapshot: FoundationSnapshot;
}

export interface FoundationScanRequest extends TenantScoped {
  scanId: Ulid;
  mode: FoundationScanMode;
  requestedBy: string;
  sessionId?: Ulid;
  versionId?: Ulid;
  sectionKeys: string[];
}

export interface FoundationScanStatusRecord extends TenantScoped {
  scanId: Ulid;
  mode: FoundationScanMode;
  status: FoundationScanStatus;
  progress: number;
  versionId?: Ulid;
  activeSection?: string;
  websocketEventType?: string;
}

export interface FoundationCacheEvent extends TenantScoped {
  eventId: Ulid;
  foundationVersion: number;
  eventType: string;
  affectedSections: string[];
  invalidationScope: string;
  createdAt: string;
}

export interface CampaignBrief extends TenantScoped {
  briefId: Ulid;
  goal: string;
  timeline: string;
  channels: string[];
}

export interface Campaign extends TenantScoped {
  campaignId: Ulid;
  status: "draft" | "pending_approval" | "active" | "paused" | "archived";
  name: string;
}

export interface Move extends TenantScoped {
  moveId: Ulid;
  campaignId: Ulid;
  sequenceNumber: number;
  moveType: "awareness" | "consideration" | "conversion" | "retention" | "launch";
}

export interface Task extends TenantScoped {
  taskId: Ulid;
  campaignId: Ulid;
  moveId: Ulid;
  title: string;
  status: "pending" | "ready" | "in_progress" | "completed" | "missed" | "overridden";
}

export interface CouncilSession extends TenantScoped {
  sessionId: Ulid;
  sessionType: "tactical" | "operational" | "strategic" | "war_room" | "replanning";
  status: "queued" | "running" | "streaming" | "completed" | "failed";
}

export interface CouncilAgentPosition extends TenantScoped {
  positionId: Ulid;
  sessionId: Ulid;
  avatarKey: string;
  roundNumber: number;
  content: string;
}

export interface AvatarRegistryEntry extends TenantScoped {
  avatarKey: string;
  displayName: string;
  role: AvatarRole;
  supportDomain?: string;
  officeZoneId: string;
  reflectionProfile: string;
}

export interface ContextPack extends TenantScoped {
  foundationSections: string[];
  retrievedRippleIds: Ulid[];
  skillAtomIds: Ulid[];
}

export type ResearchRequestKind =
  | "web_search"
  | "browser"
  | "competitive_analysis"
  | "performance_analysis"
  | "content_research";

export type ResearchUrgency = "blocking" | "background";

export type StreamCoordinatorPhase = "precheck" | "blocking_research" | "generation" | "post_processing";

export interface ToolGatewayRequest extends TenantScoped {
  requestId: Ulid;
  sessionId?: Ulid;
  toolName: string;
  arguments: Record<string, unknown>;
  timeoutMs: number;
}

export interface ToolGatewayResponse extends TenantScoped {
  requestId: Ulid;
  accepted: boolean;
  output: Record<string, unknown>;
  nextAction?: string;
}

export interface ResearchRequest extends TenantScoped {
  requestId: Ulid;
  parentSessionId?: Ulid;
  parentAgentId: string;
  kind: ResearchRequestKind;
  urgency: ResearchUrgency;
  query: string;
  requiredSources: string[];
  outputFormat: string;
}

export interface StreamCoordinatorRequest extends TenantScoped {
  sessionId: Ulid;
  phase: StreamCoordinatorPhase;
  blockingResearch: ResearchRequest[];
  backgroundResearch: ResearchRequest[];
  toolRequests: ToolGatewayRequest[];
  foundationSections: string[];
}

export interface EventHarvesterRecord extends TenantScoped {
  eventId: Ulid;
  sourceType: string;
  sourceId: string;
  eventType: string;
  payload: Record<string, unknown>;
  ingestedAt: string;
}

export interface RippleData {
  coreClaim: string;
  keyReasoning: string;
  prediction?: string;
}

export interface MemoryEvent extends TenantScoped {
  eventId: Ulid;
  agentId: string;
  sessionId?: Ulid;
  campaignId?: Ulid;
  source: string;
  rawContent: string;
  rippleData?: RippleData;
}

export interface PrlDecayPolicy extends TenantScoped {
  policyId: Ulid;
  memoryClass: string;
  protectionBand: ProtectionBand;
  decayHalfLifeHours: number;
  consolidationThreshold: number;
}

export interface PredictionResolutionRecord extends TenantScoped {
  resolutionId: Ulid;
  rippleId: Ulid;
  predictedOutcome: string;
  actualOutcome?: string;
  resolvedAt?: string;
}

export interface EelLatticeState extends TenantScoped {
  avatarKey: string;
  role: AvatarRole;
  essenceCore: Record<string, unknown>;
  egoSignature: Record<string, unknown>;
  skillWeave: Record<string, unknown>;
  reflectionGate: string;
}

export interface InternTask extends TenantScoped {
  taskId: Ulid;
  parentSessionId: Ulid;
  parentAgentId: string;
  internAvatarKey: string;
  taskType:
    | "web_search"
    | "browser"
    | "competitive_analysis"
    | "performance_analysis"
    | "content_research"
    | "foundation_update"
    | "replanning_support";
  urgency: ResearchUrgency;
  query: string;
  specificRequirements: string[];
  outputFormat: string;
}

export interface OfficeEventMessage extends TenantScoped {
  type: "office.event";
  eventType: string;
  payload: Record<string, unknown>;
}

export interface MuseConversation extends TenantScoped {
  conversationId: Ulid;
  route: "strategic" | "content" | "tactical" | "foundation_update";
}

export interface DailyWinsBrief extends TenantScoped {
  briefingId: Ulid;
  generatedAt: string;
  leadSummary: string;
  fullBriefing: string;
  recommendedAction: string;
  recommendedActionType: string;
  recommendedActionData?: Record<string, unknown>;
  viewedAt?: string;
  actedOnAt?: string;
  actionOutcome?: string;
}

export interface IntelAlert extends TenantScoped {
  alertId: Ulid;
  campaignId?: Ulid;
  sourceType: string;
  sourceId: string;
  alertType: string;
  significance: string;
  title: string;
  summary: string;
  payload: Record<string, unknown>;
  capturedAt: string;
  deliveredAt?: string;
  resolvedAt?: string;
}

export interface Nudge extends TenantScoped {
  nudgeId: Ulid;
  userId: Ulid;
  nudgeType: string;
  priority: string;
  title: string;
  body: string;
  actionType?: string;
  actionData?: Record<string, unknown>;
  sourceType: string;
  sourceId: string;
  createdAt: string;
  deliveredAt?: string;
  viewedAt?: string;
  actedOnAt?: string;
  dismissedAt?: string;
  suppressed: boolean;
}

export interface ContentFeedbackLoop extends TenantScoped {
  loopId: Ulid;
  campaignId?: Ulid;
  sourceAssetId?: string;
  performanceSignal: string;
  routedTo: string;
  createdAt: string;
}

export interface SessionTokenUsage extends TenantScoped {
  sessionId: Ulid;
  modelTier: string;
  inputTokens: number;
  outputTokens: number;
}

export interface OrgMonthlyCost extends TenantScoped {
  month: string;
  inferenceCostUsd: number;
  scrapingCostUsd: number;
  storageCostUsd: number;
  sessionCount: number;
}

export interface CostThresholdAlert extends TenantScoped {
  alertId: Ulid;
  month: string;
  thresholdName: string;
  thresholdValueUsd: number;
  observedCostUsd: number;
  createdAt: string;
}
