/**
 * RaptorFlow Campaign Feature Types
 *
 * Canonical frontend view models for Campaigns, Moves, and Tasks.
 * These types reflect what the backend ACTUALLY returns, not what we wish it returned.
 * Runtime guards are provided for unknown JSON boundaries.
 */

/* ────────────────────────────────────────────────────────────────────────────
   CAMPAIGN
   ──────────────────────────────────────────────────────────────────────────── */

export interface CampaignSummary {
  campaignId: string;
  name: string;
  goal: string | null;
  status: string;
  createdAt: string;
  updatedAt: string | null;
  moveCount?: number;
  taskCount?: number;
  artifactCount?: number;
  evaluationScore?: number | null;
}

export interface CampaignDetail extends CampaignSummary {
  moves: CampaignMove[];
  tasks: CampaignTask[];
  evaluation: CampaignEvaluation | null;
}

/* ────────────────────────────────────────────────────────────────────────────
   EVALUATION
   ──────────────────────────────────────────────────────────────────────────── */

export interface CampaignEvaluation {
  overallScore: number;
  summary?: string | null;
  strengths: string[];
  weaknesses: string[];
  opportunities: string[];
  threats: string[];
  recommendations: string[];
  evaluatedAt: string;
}

/* ────────────────────────────────────────────────────────────────────────────
   MOVE
   ──────────────────────────────────────────────────────────────────────────── */

export interface CampaignMove {
  moveId: string;
  campaignId: string;
  sequenceNumber: number;
  moveType: string;
  title?: string | null;
  description?: string | null;
  expectedImpact?: string | null;
  confidence?: number | null;
  status: string;
  createdAt: string;
  updatedAt?: string | null;
  tasks?: CampaignTask[];
  artifacts?: CampaignArtifact[];
}

/* ────────────────────────────────────────────────────────────────────────────
   TASK
   ──────────────────────────────────────────────────────────────────────────── */

export type TaskStatus = "pending" | "in_progress" | "completed" | "cancelled";

export interface CampaignTask {
  taskId: string;
  campaignId: string;
  moveId?: string | null;
  title: string;
  description?: string | null;
  status: TaskStatus;
  owner?: string | null;
  dueAt?: string | null;
  artifactId?: string | null;
  createdAt: string;
  updatedAt?: string | null;
}

/* ────────────────────────────────────────────────────────────────────────────
   ARTIFACT (lightweight reference)
   ──────────────────────────────────────────────────────────────────────────── */

export interface CampaignArtifact {
  id: string;
  contentType: string;
  title?: string | null;
  createdAt: string;
}

/* ────────────────────────────────────────────────────────────────────────────
   CREATE REQUESTS
   ──────────────────────────────────────────────────────────────────────────── */

export interface CreateCampaignRequest {
  name: string;
  goal?: string | null;
}

export interface CreateMoveRequest {
  moveType: string;
  sequenceNumber?: number;
}

export interface CreateTaskRequest {
  title: string;
  moveId?: string | null;
  scheduledDate?: string | null;
}

/* ────────────────────────────────────────────────────────────────────────────
   RUNTIME GUARDS
   No `as any`. No `as unknown as`. Honest validation.
   ──────────────────────────────────────────────────────────────────────────── */

function isObject(val: unknown): val is Record<string, unknown> {
  return typeof val === "object" && val !== null && !Array.isArray(val);
}

function isStringArray(val: unknown): val is string[] {
  return Array.isArray(val) && val.every((v) => typeof v === "string");
}

export function isCampaignSummary(val: unknown): val is CampaignSummary {
  if (!isObject(val)) return false;
  const v = val as Record<string, unknown>;
  return (
    typeof v.campaign_id === "string" &&
    typeof v.name === "string" &&
    (v.goal === null || v.goal === undefined || typeof v.goal === "string") &&
    typeof v.status === "string" &&
    typeof v.created_at === "string"
  );
}

export function isCampaignListResponse(val: unknown): val is { campaigns: CampaignSummary[] } {
  if (!isObject(val)) return false;
  const campaigns = (val as Record<string, unknown>).campaigns;
  if (!Array.isArray(campaigns)) return false;
  return campaigns.every(isCampaignSummary);
}

export function isCampaignEvaluation(val: unknown): val is CampaignEvaluation {
  if (!isObject(val)) return false;
  const v = val as Record<string, unknown>;
  return (
    typeof v.overall_score === "number" &&
    isStringArray(v.strengths) &&
    isStringArray(v.weaknesses) &&
    isStringArray(v.opportunities) &&
    isStringArray(v.threats) &&
    isStringArray(v.recommendations)
  );
}

export function isCampaignMove(val: unknown): val is CampaignMove {
  if (!isObject(val)) return false;
  const v = val as Record<string, unknown>;
  return (
    typeof v.move_id === "string" &&
    typeof v.campaign_id === "string" &&
    typeof v.sequence_number === "number" &&
    typeof v.move_type === "string" &&
    typeof v.status === "string" &&
    typeof v.created_at === "string"
  );
}

export function isCampaignTask(val: unknown): val is CampaignTask {
  if (!isObject(val)) return false;
  const v = val as Record<string, unknown>;
  return (
    typeof v.task_id === "string" &&
    typeof v.campaign_id === "string" &&
    typeof v.title === "string" &&
    typeof v.status === "string" &&
    typeof v.created_at === "string"
  );
}

/* ────────────────────────────────────────────────────────────────────────────
   NORMALIZATION
   Convert backend snake_case to frontend camelCase without inventing data.
   ──────────────────────────────────────────────────────────────────────────── */

export function normalizeCampaignSummary(raw: unknown): CampaignSummary | null {
  if (!isObject(raw)) return null;
  const r = raw as Record<string, unknown>;
  if (typeof r.campaign_id !== "string" || typeof r.name !== "string") return null;

  return {
    campaignId: r.campaign_id as string,
    name: r.name as string,
    goal: (r.goal as string | null) ?? null,
    status: String(r.status ?? "unknown"),
    createdAt: String(r.created_at ?? ""),
    updatedAt: (r.updated_at as string | null) ?? null,
    moveCount: typeof r.move_count === "number" ? r.move_count : undefined,
    taskCount: typeof r.task_count === "number" ? r.task_count : undefined,
    evaluationScore: typeof r.evaluation_score === "number" ? r.evaluation_score : null,
  };
}

export function normalizeCampaignEvaluation(raw: unknown): CampaignEvaluation | null {
  if (!isObject(raw)) return null;
  const r = raw as Record<string, unknown>;
  if (typeof r.overall_score !== "number") return null;

  return {
    overallScore: r.overall_score as number,
    summary: (r.summary as string | null) ?? null,
    strengths: isStringArray(r.strengths) ? r.strengths : [],
    weaknesses: isStringArray(r.weaknesses) ? r.weaknesses : [],
    opportunities: isStringArray(r.opportunities) ? r.opportunities : [],
    threats: isStringArray(r.threats) ? r.threats : [],
    recommendations: isStringArray(r.recommendations) ? r.recommendations : [],
    evaluatedAt: typeof r.evaluated_at === "string" ? r.evaluated_at : new Date().toISOString(),
  };
}

export function normalizeCampaignMove(raw: unknown): CampaignMove | null {
  if (!isObject(raw)) return null;
  const r = raw as Record<string, unknown>;
  if (
    typeof r.move_id !== "string" ||
    typeof r.campaign_id !== "string" ||
    typeof r.sequence_number !== "number"
  ) {
    return null;
  }

  return {
    moveId: r.move_id as string,
    campaignId: r.campaign_id as string,
    sequenceNumber: r.sequence_number as number,
    moveType: String(r.move_type ?? "unknown"),
    title: (r.title as string | null) ?? null,
    description: (r.description as string | null) ?? null,
    expectedImpact: (r.expected_impact as string | null) ?? null,
    confidence: typeof r.confidence === "number" ? r.confidence : null,
    status: String(r.status ?? "unknown"),
    createdAt: String(r.created_at ?? ""),
    updatedAt: (r.updated_at as string | null) ?? null,
  };
}

export function normalizeCampaignTask(raw: unknown): CampaignTask | null {
  if (!isObject(raw)) return null;
  const r = raw as Record<string, unknown>;
  if (
    typeof r.task_id !== "string" ||
    typeof r.campaign_id !== "string" ||
    typeof r.title !== "string"
  ) {
    return null;
  }

  const rawStatus = String(r.status ?? "pending");
  // Normalize backend status to canonical frontend status
  const statusMap: Record<string, TaskStatus> = {
    pending: "pending",
    in_progress: "in_progress",
    completed: "completed",
    complete: "completed",
    cancelled: "cancelled",
    canceled: "cancelled",
  };

  return {
    taskId: r.task_id as string,
    campaignId: r.campaign_id as string,
    moveId: (r.move_id as string | null) ?? null,
    title: r.title as string,
    description: (r.description as string | null) ?? null,
    status: statusMap[rawStatus] ?? "pending",
    owner: (r.owner as string | null) ?? null,
    dueAt: (r.due_at as string | null) ?? (r.scheduled_date as string | null) ?? null,
    artifactId: (r.artifact_id as string | null) ?? null,
    createdAt: String(r.created_at ?? ""),
    updatedAt: (r.updated_at as string | null) ?? null,
  };
}
