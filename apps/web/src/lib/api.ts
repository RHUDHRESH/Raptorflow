import { publicEnv } from "./env";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function getAuthToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;

  try {
    const clerk = (
      window as Window & {
        Clerk?: { session?: { getToken?: () => Promise<string | null> } };
      }
    ).Clerk;

    if (clerk?.session?.getToken) {
      const token = await clerk.session.getToken();
      if (token) return token;
    }
  } catch {
    // Clerk not loaded yet or session expired
  }

  // In development only, fall back to dev bearer token so the UI works without Clerk
  // In production, this returns null which causes API calls to fail with 401
  if (publicEnv.appEnv !== "prod") {
    return publicEnv.devBearerToken;
  }

  return null;
}

export function getApiBaseUrl(): string {
  const base = publicEnv.apiBaseUrl;
  return base.replace(/\/$/, "");
}

export function getWsBaseUrl(): string {
  const apiBase = getApiBaseUrl();
  return apiBase.replace(/^http/, "ws");
}

export async function apiFetch<T>(
  path: string,
  options: {
    token?: string | null;
    method?: string;
    body?: unknown;
    headers?: HeadersInit;
    auth?: boolean;
  } = {},
): Promise<T> {
  const base = getApiBaseUrl();

  const token = options.auth ? (options.token ?? (await getAuthToken())) : null;

  const res = await fetch(`${base}${path}`, {
    method: options.method ?? "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(res.status, text || `API request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}

function unwrapList<T>(payload: unknown, keys: string[], fallback: T[] = []): T[] {
  if (Array.isArray(payload)) return payload as T[];
  if (payload && typeof payload === "object") {
    for (const key of keys) {
      const value = (payload as Record<string, unknown>)[key];
      if (Array.isArray(value)) return value as T[];
    }
  }
  return fallback;
}

function unwrapItem<T>(payload: unknown, keys: string[]): T | null {
  if (payload && typeof payload === "object") {
    for (const key of keys) {
      const value = (payload as Record<string, unknown>)[key];
      if (value && typeof value === "object") {
        return value as T;
      }
    }
  }
  return (payload as T | null) ?? null;
}

// ─── API OBJECTS ──────────────────────────────────────────────────────────────

export const dailyWinsApi = {
  getToday: async () => {
    const res = await apiFetch<{ daily_win?: BackendDailyWin | null }>("/api/v1/daily-wins/today", {
      auth: true,
    });
    return res.daily_win ? normalizeDailyWin(res.daily_win) : null;
  },
  getArchive: async () => {
    const res = await apiFetch<unknown>("/api/v1/daily-wins", { auth: true });
    return unwrapList<BackendDailyWin>(res, ["daily_wins"]).map(normalizeDailyWin);
  },
  markAsRead: (id: string) =>
    apiFetch<void>(`/api/v1/daily-wins/${id}/viewed`, { method: "POST", auth: true }),
};

export const foundationApi = {
  get: () => apiFetch<FoundationResponse>("/api/v1/foundation", { auth: true }),
  updateSection: (section: string, data: unknown) =>
    apiFetch<void>(`/api/v1/foundation/section/${section}`, {
      method: "PATCH",
      body: { data },
      auth: true,
    }),
  listSnapshots: () =>
    apiFetch<FoundationSnapshot[]>("/api/v1/foundation/snapshots", { auth: true }),
  getSnapshot: (id: string) =>
    apiFetch<FoundationSnapshot>(`/api/v1/foundation/snapshots/${id}`, { auth: true }),
  createSnapshot: () =>
    apiFetch<FoundationSnapshot>("/api/v1/foundation/snapshots", { method: "POST", auth: true }),
  restoreSnapshot: (id: string) =>
    apiFetch<void>(`/api/v1/foundation/snapshots/${id}/restore`, { method: "POST", auth: true }),
  triggerScan: (url: string, _mode?: "quick" | "deep") =>
    apiFetch<ScanJob>("/api/v1/foundation/scan/start", {
      method: "POST",
      body: { url },
      auth: true,
    }),
  getScanStatus: () => apiFetch<ScanJob>("/api/v1/foundation/scan/status", { auth: true }),
  getFullStatus: () =>
    apiFetch<SnapshotFullResponse>("/api/v1/foundation/snapshot", { auth: true }),
};

export const campaignsApi = {
  list: async () => {
    const res = await apiFetch<unknown>("/api/v1/campaigns", { auth: true });
    return unwrapList<BackendCampaign>(res, ["campaigns"]).map(normalizeCampaign);
  },
  get: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/campaigns/${id}`, { auth: true });
    const campaign = unwrapItem<BackendCampaign>(res, ["campaign"]);
    if (!campaign) {
      throw new ApiError(500, "Campaign response missing campaign payload");
    }
    const moves = unwrapList<BackendMove>(res, ["moves"]).map(normalizeMove);
    const tasks = unwrapList<BackendTask>(res, ["tasks"]).map(normalizeTask);
    return normalizeCampaignDetail(campaign, moves, tasks);
  },
  create: async (body: CreateCampaignRequest) => {
    const res = await apiFetch<unknown>("/api/v1/campaigns", {
      method: "POST",
      body: { name: body.name, goal: body.goal ?? "Grow pipeline" },
      auth: true,
    });
    const campaign = unwrapItem<BackendCampaign>(res, ["campaign"]);
    if (!campaign) {
      throw new ApiError(500, "Campaign create response missing campaign payload");
    }
    return normalizeCampaign(campaign);
  },
  // Backend only supports PATCH /status — not PUT full update
  updateStatus: (id: string, status: Campaign["status"]) =>
    apiFetch<void>(`/api/v1/campaigns/${id}/status`, {
      method: "PATCH",
      body: { status },
      auth: true,
    }),
  getMoves: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/campaigns/${id}/moves`, { auth: true });
    return { moves: unwrapList<BackendMove>(res, ["moves"]).map(normalizeMove) };
  },
  createMove: async (id: string, body: CreateMoveRequest) => {
    const res = await apiFetch<{ move_id?: string }>(`/api/v1/campaigns/${id}/moves`, {
      method: "POST",
      body: {
        move_type: body.type,
        sequence_number:
          Number.parseInt(body.start_date?.replace(/\D/g, "").slice(-2) || "1", 10) || 1,
      },
      auth: true,
    });
    return {
      move_id: res.move_id ?? "",
      move_number: 0,
      name: body.name,
      type: body.type,
      sub_goal: body.sub_goal,
      start_date: body.start_date,
      end_date: body.end_date,
      status: "upcoming",
      tasks_completed: 0,
      tasks_total: 0,
    } satisfies Move;
  },
  updateMoveStatus: (id: string, moveId: string, status: string) =>
    apiFetch<void>(`/api/v1/campaigns/${id}/moves/${moveId}/status`, {
      method: "PATCH",
      body: { status },
      auth: true,
    }),
  getTasks: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/campaigns/${id}/tasks`, { auth: true });
    return { tasks: unwrapList<BackendTask>(res, ["tasks"]).map(normalizeTask) };
  },
  createTask: async (id: string, body: CreateTaskRequest) => {
    const res = await apiFetch<{ task_id?: string }>(`/api/v1/campaigns/${id}/tasks`, {
      method: "POST",
      body: {
        move_id: body.move_id ?? "",
        title: body.title,
        scheduled_date: body.scheduled_date,
      },
      auth: true,
    });
    return {
      task_id: res.task_id ?? "",
      title: body.title,
      task_type: body.task_type,
      channel: body.channel,
      status: "pending",
      content_ready: false,
      assigned_agent_key: body.assigned_agent_key ?? "strategist",
      assigned_agent_name: "Strategist",
      scheduled_date: body.scheduled_date,
      move_name: body.move_id ?? "Unassigned",
      priority: "normal",
    } satisfies Task;
  },
  updateTaskStatus: (id: string, taskId: string, status: string) =>
    apiFetch<void>(`/api/v1/campaigns/${id}/tasks/${taskId}/status`, {
      method: "PATCH",
      body: { status },
      auth: true,
    }),
  getBrief: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/campaigns/${id}/brief`, { auth: true });
    const brief = unwrapItem<BackendBrief>(res, ["brief"]);
    return brief ? normalizeBrief(brief) : null;
  },
  createBrief: async (id: string, body: CreateBriefRequest) => {
    const res = await apiFetch<{ brief_id?: string }>(`/api/v1/campaigns/${id}/brief`, {
      method: "POST",
      body: { original_text: body.content },
      auth: true,
    });
    return {
      brief_id: res.brief_id ?? "",
      campaign_id: id,
      content: body.content,
      status: "draft",
      created_at: new Date().toISOString(),
    } satisfies CampaignBrief;
  },
  updateBriefStatus: (id: string, status: string) =>
    apiFetch<void>(`/api/v1/campaigns/${id}/brief/status`, {
      method: "PATCH",
      body: { status },
      auth: true,
    }),
};

export const councilApi = {
  startSession: async (body: StartCouncilRequest) => {
    const res = await apiFetch<unknown>("/api/v1/council", {
      method: "POST",
      body: {
        campaign_id: body.campaignId,
        session_type: body.sessionType,
        question: body.question ?? "Review this campaign and recommend the next best move.",
        agent_roster: body.agentRoster ?? [],
      },
      auth: true,
    });
    const session = unwrapItem<BackendCouncilSession>(res, ["session"]);
    if (!session) {
      throw new ApiError(500, "Council start response missing session payload");
    }
    return normalizeCouncilSession(session);
  },
  listSessions: async () => {
    const res = await apiFetch<unknown>("/api/v1/council", { auth: true });
    return unwrapList<BackendCouncilSession>(res, ["sessions"]).map(normalizeCouncilSession);
  },
  getSession: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/council/${id}`, { auth: true });
    const session = unwrapItem<BackendCouncilSession>(res, ["session"]);
    if (!session) {
      throw new ApiError(500, "Council session response missing session payload");
    }
    return normalizeCouncilSession(session);
  },
  getMessages: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/council/${id}/messages`, { auth: true });
    return unwrapList<BackendCouncilPosition>(res, ["positions"]).map(normalizeCouncilMessage);
  },
};

export const museApi = {
  submitPrompt: async (body: MusePromptRequest) => {
    const res = await apiFetch<{
      conversation_id: string;
      message_id: string;
      assistant_message_id: string;
    }>("/api/v1/muse", {
      method: "POST",
      body: {
        prompt: body.message,
        route: body.route,
        conversation_id: body.conversationId,
      },
      auth: true,
    });
    return {
      conversationId: res.conversation_id,
      message: {
        messageId: res.message_id,
        content: body.message,
      },
      assistantMessageId: res.assistant_message_id,
    };
  },
  listConversations: async () => {
    const res = await apiFetch<unknown>("/api/v1/muse", { auth: true });
    return unwrapList<BackendMuseConversation>(res, ["conversations"]).map(
      normalizeMuseConversation,
    );
  },
  getConversation: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/muse/${id}`, { auth: true });
    const conversation = unwrapItem<BackendMuseConversation>(res, ["conversation"]);
    if (!conversation) {
      throw new ApiError(500, "Muse conversation response missing conversation payload");
    }
    return normalizeMuseConversation(conversation);
  },
  getMessages: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/muse/${id}/messages`, { auth: true });
    return unwrapList<BackendMuseMessage>(res, ["messages"]).map(normalizeMuseMessage);
  },
};

export const prlApi = {
  listRipples: () => apiFetch<Ripple[]>("/api/v1/prl/ripples", { auth: true }),
  getRipple: (id: string) => apiFetch<Ripple>(`/api/v1/prl/ripples/${id}`, { auth: true }),
  getRippleEdges: (id: string) =>
    apiFetch<any[]>(`/api/v1/prl/ripples/${id}/edges`, { auth: true }),
  createRipple: (body: CreateRippleRequest) =>
    apiFetch<Ripple>("/api/v1/prl/ripples", { method: "POST", body, auth: true }),
  updateRipple: (id: string, body: UpdateRippleRequest) =>
    apiFetch<Ripple>(`/api/v1/prl/ripples/${id}`, { method: "PUT", body, auth: true }),
  deleteRipple: (id: string) =>
    apiFetch<void>(`/api/v1/prl/ripples/${id}`, { method: "DELETE", auth: true }),
  realizeRipple: (id: string) =>
    apiFetch<void>(`/api/v1/prl/ripples/${id}/realize`, { method: "POST", auth: true }),
  createRippleEdge: (id: string, body: CreateEdgeRequest) =>
    apiFetch<void>(`/api/v1/prl/ripples/${id}/edges`, { method: "POST", body, auth: true }),
  deleteRippleEdge: (edgeId: string) =>
    apiFetch<void>(`/api/v1/prl/ripples/edges/${edgeId}`, { method: "DELETE", auth: true }),
  listEssences: () => apiFetch<Essence[]>("/api/v1/prl/essences", { auth: true }),
  getEssence: (id: string) => apiFetch<Essence>(`/api/v1/prl/essences/${id}`, { auth: true }),
  createEssence: (body: CreateEssenceRequest) =>
    apiFetch<Essence>("/api/v1/prl/essences", { method: "POST", body, auth: true }),
  updateEssence: (id: string, body: UpdateEssenceRequest) =>
    apiFetch<Essence>(`/api/v1/prl/essences/${id}`, { method: "PUT", body, auth: true }),
  runDecay: () => apiFetch<void>("/api/v1/prl/decay", { method: "POST", auth: true }),
};

export const intelApi = {
  getSignals: async (_params?: {
    category?: string;
    competitorId?: string;
  }): Promise<IntelSignal[]> => [],
  getCompetitors: async (): Promise<Competitor[]> => [],
  getSignalStats: async (): Promise<IntelStats> => ({
    monitoredCount: 0,
    signalsTwentyFourHours: 0,
    highPriorityCount: 0,
    categoryBreakdown: {},
  }),
  getOverview: () => apiFetch<IntelOverview>("/api/v1/intel", { auth: true }),
  listRuns: async () => {
    const res = await apiFetch<unknown>("/api/v1/intel/runs", { auth: true });
    return unwrapList<ResearchRun>(res, ["runs", "research_runs"]);
  },
  listDocuments: async () => {
    const res = await apiFetch<unknown>("/api/v1/intel/documents", { auth: true });
    return unwrapList<IntelDocument>(res, ["documents", "research_documents"]);
  },
};

export const billingApi = {
  getStatus: () => apiFetch<BillingStatus>("/api/v1/billing", { auth: true }),
  createOrder: (body: CreateOrderRequest) =>
    apiFetch<any>("/api/v1/billing/orders", { method: "POST", body, auth: true }),
  getSubscription: (id: string) =>
    apiFetch<any>(`/api/v1/billing/subscriptions/${id}`, { auth: true }),
  cancelSubscription: (id: string) =>
    apiFetch<void>(`/api/v1/billing/subscriptions/${id}/cancel`, { method: "POST", auth: true }),
};

export const uploadsApi = {
  generateUploadUrl: (body: { filename: string; contentType: string }) =>
    apiFetch<{ uploadUrl: string; key: string }>("/api/v1/uploads", {
      method: "POST",
      body,
      auth: true,
    }),
  generateDownloadUrl: (key: string) =>
    apiFetch<{ downloadUrl: string }>(`/api/v1/uploads/download?key=${key}`, { auth: true }),
  deleteUpload: (key: string) =>
    apiFetch<void>(`/api/v1/uploads/${key}`, { method: "DELETE", auth: true }),
  generateScreenshotUploadUrl: (filename: string) =>
    apiFetch<{ uploadUrl: string; key: string }>("/api/v1/screenshots", {
      method: "POST",
      body: { filename },
      auth: true,
    }),
  generateExportUrl: (exportId: string) =>
    apiFetch<{ uploadUrl: string; key: string }>("/api/v1/exports", {
      method: "POST",
      body: { exportId },
      auth: true,
    }),
  generateExportDownloadUrl: (exportId: string) =>
    apiFetch<{ downloadUrl: string }>(`/api/v1/exports/download?exportId=${exportId}`, {
      auth: true,
    }),
};

export const contentApi = {
  list: async () => {
    const res = await apiFetch<unknown>("/api/v1/content", { auth: true });
    return unwrapList<BackendGeneratedContent>(res, ["content"]).map(normalizeGeneratedContent);
  },
  get: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/content/${id}`, { auth: true });
    const content = unwrapItem<BackendGeneratedContent>(res, ["content"]);
    if (!content) {
      throw new ApiError(500, "Content response missing content payload");
    }
    return normalizeGeneratedContent(content);
  },
};

export const officeApi = {
  getState: async () => {
    const res = await apiFetch<unknown>("/api/v1/office", { auth: true });
    const payload = (res ?? {}) as Record<string, unknown>;
    return {
      activeCampaigns: Number(payload.active_campaigns ?? 0),
      activeCouncilSessions: Number(payload.active_council_sessions ?? 0),
      openNudges: Number(payload.open_nudges ?? 0),
      recentMuseConversations: Number(payload.recent_muse_conversations ?? 0),
      eventTypes: Array.isArray(payload.event_types) ? (payload.event_types as string[]) : [],
    };
  },
};

// ─── TYPES ───────────────────────────────────────────────────────────────────

export interface DailyWin {
  win_id: string;
  generated_at: string;
  strategist_name: string;
  lead: { text: string; significance: string };
  context: Array<{ text: string; source: string }>;
  todays_focus: {
    action: string;
    rationale: string;
    action_type: "approve_content" | "review_campaign" | "respond_to_intel" | "strategic_review";
    action_data: { task_id?: string; campaign_id?: string };
  };
  viewed_at: string | null;
  status?: "not_started";
  message?: string;
}
interface BackendDailyWin {
  briefing_id: string;
  briefing_date: string;
  generated_at: string;
  lead_summary: string;
  full_briefing: string;
  recommended_action: string;
  recommended_action_type: string;
  recommended_action_data: Record<string, unknown>;
  viewed_at: string | null;
  acted_on_at?: string | null;
  action_outcome?: string | null;
}

export interface FoundationResponse {
  orgId: string;
  version: number;
  sections: Record<string, any>;
  updatedAt: string;
}

export interface FoundationSnapshot {
  id: string;
  orgId: string;
  foundationVersion: number;
  sections: Record<string, any>;
  createdAt: string;
}

export interface SnapshotFullResponse {
  status: "not_started" | "in_progress" | "complete";
  completed_sections: string[];
  missing_sections: string[];
  last_updated_section?: string;
  version: number;
  sections: Record<string, any>;
}

export interface ScanJob {
  scan_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress?: number;
}

export interface Campaign {
  campaignId: string;
  campaign_id?: string; // Legacy/API compatibility
  orgId: string;
  name: string;
  status: "draft" | "pending_approval" | "active" | "paused" | "completed" | "archived";
  goal?: string;
  timeline?: string;
  channels?: string[];
  createdAt: string;
  updatedAt: string;
  goal_type: "awareness" | "leads" | "conversion" | "retention" | "re_engagement" | any;
  tasks_due_today?: number;
  tasks_completed?: number;
  tasks_total?: number;
  progress_pct: number;
  current_move_name?: string;
  start_date: string;
  end_date: string;
}

export interface CampaignDetail extends Campaign {
  council_rationale: { synthesis: string; participating_agents: string[] };
  outcome_projection: string;
  current_move?: {
    move_id: string;
    name: string;
    type: string;
    sub_goal: string;
    day_number: number;
    total_days: number;
    tasks_completed: number;
    tasks_total: number;
  };
}

export interface Move {
  move_id: string;
  move_number: number;
  name: string;
  type: string;
  sub_goal: string;
  start_date: string;
  end_date: string;
  status: "upcoming" | "active" | "completed" | "overdue";
  tasks_completed: number;
  tasks_total: number;
}

export interface Task {
  task_id: string;
  title: string;
  task_type:
    | "publish_content"
    | "review_performance"
    | "execute_ad"
    | "approve_content"
    | "research"
    | "setup";
  channel: string;
  status:
    | "pending"
    | "due"
    | "ready_for_review"
    | "approved"
    | "completed"
    | "missed"
    | "processing";
  content_ready: boolean;
  assigned_agent_key: string;
  assigned_agent_name: string;
  scheduled_date: string;
  move_name: string;
  priority?: "normal" | "high" | "critical";
}

export interface TaskDetail extends Task {
  description: string;
  campaign_name: string;
  content: {
    content_id: string;
    body: string;
    headline: string | null;
    hashtags: string[] | null;
    image_direction: string | null;
    posting_time: string | null;
    format: "social_post" | "email" | "ad_copy" | "long_form";
  } | null;
  performance_summary?: {
    metrics: Array<{
      label: string;
      value: string;
      vs_target: "above" | "on" | "below";
      trend: string;
    }>;
    recommendation: string;
  };
  ad_instruction?: string;
  ad_reasoning?: string;
}

export interface CreateCampaignRequest {
  name: string;
  goal?: string;
  timeline?: string;
  channels?: string[];
  goal_type?: string;
  start_date?: string;
  end_date?: string;
}
export interface CreateMoveRequest {
  name: string;
  type: string;
  sub_goal: string;
  start_date: string;
  end_date: string;
}
export interface CreateTaskRequest {
  title: string;
  task_type: Task["task_type"];
  channel: string;
  scheduled_date: string;
  assigned_agent_key?: string;
  move_id?: string;
}
export interface CreateBriefRequest {
  content: string;
  goal?: string;
}
export interface CampaignBrief {
  brief_id: string;
  campaign_id: string;
  content: string;
  status: "draft" | "approved" | "rejected";
  created_at: string;
}

export interface StartCouncilRequest {
  campaignId?: string;
  sessionType?: string;
  question?: string;
  agentRoster?: string[];
}
export interface CouncilSession {
  sessionId: string;
  orgId: string;
  campaignId: string;
  sessionType: string;
  status: string;
  createdAt: string;
  agentCount?: number;
  duration?: string;
}

export interface CouncilMessage {
  messageId: string;
  sessionId: string;
  content: string;
  createdAt: string;
}
interface BackendCouncilPosition {
  position_id: string;
  avatar_key: string;
  round_number: number;
  content: string;
  created_at: string;
}
interface BackendCouncilSession {
  session_id: string;
  org_id: string;
  campaign_id?: string | null;
  session_type: string;
  status: string;
  question?: string;
  total_cost_usd?: number;
  created_at: string;
}

export interface MuseConversation {
  conversationId: string;
  orgId: string;
  route: string;
  lastMessageAt: string;
  messageCount: number;
  preview?: string;
  id?: string; // Some parts of the code use .id
  updated_at?: string;
}

export interface MusePromptRequest {
  conversationId?: string;
  route: string;
  message: string;
}
export interface MuseResponse {
  conversationId: string;
  message: { messageId: string; content: string };
  assistantMessageId?: string;
}
interface BackendMuseConversation {
  conversation_id: string;
  route: string;
  created_at: string;
}
interface BackendMuseMessage {
  message_id: string;
  role: string;
  body: string;
  created_at: string;
}

export interface Ripple {
  rippleId: string;
  orgId: string;
  agentId?: string;
  summaryText: string;
  rawText?: string;
  triggerText?: string;
  prediction?: string;
  sourceAgent?: string;
  confidence: number;
  salience?: number;
  hierarchyLevel: 1 | 2 | 3 | 4;
  importanceBand: "critical" | "strong" | "normal" | "disposable";
  retentionBand?: "hot" | "warm" | "cold" | "archived";
  memoryClass?: "episodic" | "semantic" | "procedural" | "identity" | "affective" | "preference";
  eventType?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface IntelSignal {
  signalId: string;
  competitorId: string;
  competitorName: string;
  category: "website" | "social" | "ads" | "seo" | "system" | string;
  title: string;
  description: string;
  extractedAt: string;
  significance: "low" | "medium" | "high" | "critical";
  implication?: string;
}

export interface IntelOverview {
  monitored_count: number;
  signals_24h: number;
  high_priority_count: number;
  latest_signals: IntelSignal[];
}

export interface ResearchRun {
  run_id: string;
  title: string;
  status: "running" | "completed" | "failed";
  progress: number;
  created_at: string;
}

export interface IntelDocument {
  document_id: string;
  title: string;
  source_type: string;
  content_preview: string;
  created_at: string;
}

export interface Competitor {
  id: string;
  name: string;
  websiteUrl?: string;
  monitors: string[];
  lastSeenAt: string;
}

export interface IntelStats {
  monitoredCount: number;
  signalsTwentyFourHours: number;
  highPriorityCount: number;
  categoryBreakdown: Record<string, number>;
}

export interface Essence {
  essenceId: string;
  orgId: string;
  avatarKey: string;
  content: string;
  category: string;
  createdAt: string;
}

export interface BillingPlan {
  tier: string;
  name: string;
  description: string;
  price_inr_monthly: number | string;
  features: string[];
}

export interface BillingStatus {
  subscription_status: "active" | "past_due" | "canceled" | "unpaid" | "none";
  current_plan: BillingPlan | null;
  available_plans: BillingPlan[];
  plan: string;
  status: string;
  currentPeriodEnd: string;
  invoiceCount: number;
}

export interface CreateRippleRequest {
  summaryText: string;
  rawText: string;
  sourceAgent?: string;
  confidence: number;
  importanceBand: Ripple["importanceBand"];
}
export interface UpdateRippleRequest {
  summaryText?: string;
  rawText?: string;
  importanceBand?: Ripple["importanceBand"];
}
export interface CreateEdgeRequest {
  targetId: string;
  edgeType: string;
}
export interface CreateEssenceRequest {
  avatarKey: string;
  content: string;
  category: string;
}
export interface UpdateEssenceRequest {
  content?: string;
  category?: string;
}
export interface CreateOrderRequest {
  amount: number;
  currency: string;
  planId?: string;
}

export interface GeneratedContentRecord {
  contentId: string;
  orgId: string;
  campaignId?: string;
  taskId?: string;
  contentType: string;
  status: string;
  body: Record<string, unknown>;
  createdAt: string;
}

export interface OfficeStateSnapshot {
  activeCampaigns: number;
  activeCouncilSessions: number;
  openNudges: number;
  recentMuseConversations: number;
  eventTypes: string[];
}

interface BackendCampaign {
  campaign_id: string;
  org_id: string;
  name: string;
  goal: string;
  status: string;
  active_move_id?: string | null;
  created_at: string;
  updated_at: string;
}

interface BackendMove {
  move_id: string;
  campaign_id: string;
  move_type: string;
  sequence_number: number;
  status: string;
  created_at: string;
}

interface BackendTask {
  task_id: string;
  move_id: string;
  campaign_id: string;
  title: string;
  status: string;
  scheduled_date?: string | null;
  created_at: string;
}

interface BackendBrief {
  brief_id: string;
  campaign_id?: string | null;
  status: "draft" | "submitted" | "approved" | "rejected";
  original_text: string;
  created_at: string;
}

interface BackendGeneratedContent {
  content_id: string;
  org_id: string;
  campaign_id?: string | null;
  task_id?: string | null;
  content_type: string;
  status: string;
  body: Record<string, unknown>;
  created_at: string;
}

function normalizeDailyWin(win: BackendDailyWin): DailyWin {
  return {
    win_id: win.briefing_id,
    generated_at: win.generated_at,
    strategist_name: "Strategist",
    lead: {
      text: win.lead_summary,
      significance: "Grounded in the latest available product state.",
    },
    context: win.full_briefing ? [{ text: win.full_briefing, source: "daily_briefing" }] : [],
    todays_focus: {
      action: win.recommended_action,
      rationale: "Recommended from the current daily briefing.",
      action_type:
        (win.recommended_action_type as DailyWin["todays_focus"]["action_type"]) ??
        "strategic_review",
      action_data:
        (win.recommended_action_data as { task_id?: string; campaign_id?: string }) ?? {},
    },
    viewed_at: win.viewed_at,
  };
}

function normalizeCampaign(campaign: BackendCampaign): Campaign {
  return {
    campaignId: campaign.campaign_id,
    campaign_id: campaign.campaign_id,
    orgId: campaign.org_id,
    name: campaign.name,
    status: campaign.status as Campaign["status"],
    goal: campaign.goal,
    goal_type: "awareness",
    progress_pct: 0,
    start_date: campaign.created_at,
    end_date: campaign.updated_at,
    createdAt: campaign.created_at,
    updatedAt: campaign.updated_at,
    timeline: `${campaign.created_at} → ${campaign.updated_at}`,
    channels: [],
    current_move_name: campaign.active_move_id ?? undefined,
    tasks_completed: 0,
    tasks_due_today: 0,
    tasks_total: 0,
  };
}

function normalizeMove(move: BackendMove): Move {
  return {
    move_id: move.move_id,
    move_number: move.sequence_number,
    name: `${move.move_type} move`,
    type: move.move_type,
    sub_goal: move.move_type,
    start_date: move.created_at,
    end_date: move.created_at,
    status: move.status === "planned" ? "upcoming" : (move.status as Move["status"]),
    tasks_completed: 0,
    tasks_total: 0,
  };
}

function normalizeTask(task: BackendTask): Task {
  return {
    task_id: task.task_id,
    title: task.title,
    task_type: "setup",
    channel: "general",
    status: task.status as Task["status"],
    content_ready: false,
    assigned_agent_key: "strategist",
    assigned_agent_name: "Strategist",
    scheduled_date: task.scheduled_date ?? task.created_at,
    move_name: task.move_id,
  };
}

function normalizeCampaignDetail(
  campaign: BackendCampaign,
  moves: Move[],
  tasks: Task[],
): CampaignDetail {
  const currentMove = moves[0];
  return {
    ...normalizeCampaign(campaign),
    council_rationale: {
      synthesis: "Campaign detail is grounded in persisted backend campaign state.",
      participating_agents: [],
    },
    outcome_projection: "Projection will become richer as campaign performance data is populated.",
    current_move: currentMove
      ? {
          move_id: currentMove.move_id,
          name: currentMove.name,
          type: currentMove.type,
          sub_goal: currentMove.sub_goal,
          day_number: currentMove.move_number,
          total_days: moves.length,
          tasks_completed: tasks.filter((task) => task.status === "completed").length,
          tasks_total: tasks.length,
        }
      : undefined,
  };
}

function normalizeBrief(brief: BackendBrief): CampaignBrief {
  return {
    brief_id: brief.brief_id,
    campaign_id: brief.campaign_id ?? "",
    content: brief.original_text,
    status: brief.status === "submitted" ? "draft" : (brief.status as CampaignBrief["status"]),
    created_at: brief.created_at,
  };
}

function normalizeCouncilSession(session: BackendCouncilSession): CouncilSession {
  return {
    sessionId: session.session_id,
    orgId: session.org_id,
    campaignId: session.campaign_id ?? "",
    sessionType: session.session_type,
    status: session.status,
    createdAt: session.created_at,
    agentCount: 0,
  };
}

function normalizeCouncilMessage(position: BackendCouncilPosition): CouncilMessage {
  return {
    messageId: position.position_id,
    sessionId: "",
    content: position.content,
    createdAt: position.created_at,
  };
}

function normalizeMuseConversation(conversation: BackendMuseConversation): MuseConversation {
  return {
    conversationId: conversation.conversation_id,
    orgId: "",
    route: conversation.route,
    lastMessageAt: conversation.created_at,
    messageCount: 0,
    id: conversation.conversation_id,
    preview: conversation.route,
    updated_at: conversation.created_at,
  };
}

function normalizeMuseMessage(message: BackendMuseMessage) {
  return {
    id: message.message_id,
    role: message.role,
    content: message.body,
    createdAt: message.created_at,
  };
}

function normalizeGeneratedContent(content: BackendGeneratedContent): GeneratedContentRecord {
  return {
    contentId: content.content_id,
    orgId: content.org_id,
    campaignId: content.campaign_id ?? undefined,
    taskId: content.task_id ?? undefined,
    contentType: content.content_type,
    status: content.status,
    body: content.body,
    createdAt: content.created_at,
  };
}
