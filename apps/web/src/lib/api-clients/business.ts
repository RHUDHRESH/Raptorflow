import { ApiError, apiFetch, appFetch, unwrapItem, unwrapList } from "../api-core";
import {
  normalizeBrief,
  normalizeCampaign,
  normalizeCampaignDetail,
  normalizeCouncilMessage,
  normalizeCouncilSession,
  normalizeDailyWin,
  normalizeGeneratedContent,
  normalizeMove,
  normalizeMuseConversation,
  normalizeMuseMessage,
  normalizeTask,
} from "../api-models";
import type {
  BackendBrief,
  BackendCampaign,
  BackendCouncilPosition,
  BackendCouncilSession,
  BackendDailyWin,
  BackendGeneratedContent,
  BackendMove,
  BackendMuseConversation,
  BackendMuseMessage,
  BackendTask,
  Campaign,
  CampaignBrief,
  Competitor,
  CreateBriefRequest,
  CreateCampaignRequest,
  CreateEdgeRequest,
  CreateEssenceRequest,
  CreateMoveRequest,
  CreateRippleRequest,
  CreateTaskRequest,
  CouncilPollMessagesResponse,
  CouncilPollSessionResponse,
  DailyWin,
  Essence,
  FoundationResponse,
  FoundationSnapshot,
  GeneratedContentRecord,
  IntelDocument,
  IntelOverview,
  IntelSignal,
  IntelStats,
  Move,
  MuseConversation,
  MusePromptRequest,
  MuseResponse,
  OfficeStateSnapshot,
  QuickScanResult,
  Ripple,
  ResearchRun,
  ScanJob,
  SnapshotFullResponse,
  StartCouncilRequest,
  Task,
  UpdateEssenceRequest,
  UpdateRippleRequest,
} from "../api-models";

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
  savePartial: (fields: Record<string, unknown>, method: "POST" | "PATCH" = "PATCH") =>
    apiFetch<{ id: string }>("/api/v1/foundation", {
      method,
      body: fields,
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
  triggerScan: (url: string, mode?: "quick" | "deep") => {
    const path =
      mode === "deep"
        ? "/api/v1/foundation/scan/deep"
        : mode === "quick"
          ? "/api/v1/foundation/scan/quick"
          : "/api/v1/foundation/scan/start";
    return apiFetch<ScanJob>(path, {
      method: "POST",
      body: { url },
      auth: true,
    });
  },
  getScanStatus: () => apiFetch<ScanJob>("/api/v1/foundation/scan/status", { auth: true }),
  getFullStatus: () =>
    apiFetch<SnapshotFullResponse>("/api/v1/foundation/snapshot", { auth: true }),
  triggerQuickScan: async (url?: string): Promise<{ scan: QuickScanResult; scannedAt: string }> => {
    const res = await apiFetch<{ scan: QuickScanResult; scannedAt: string }>(
      "/api/v1/foundation/scan/quick",
      {
        method: "POST",
        body: url ? { url } : {},
        auth: true,
      },
    );
    return res;
  },
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
  evaluate: async (id: string, focus?: string) => {
    const res = await apiFetch<{
      campaign_id: string;
      evaluation: {
        overall_score: number;
        strengths: string[];
        weaknesses: string[];
        opportunities: string[];
        threats: string[];
        recommendations: string[];
      };
    }>(`/api/v1/campaigns/${id}/evaluate`, {
      method: "POST",
      body: { focus },
      auth: true,
    });
    return {
      campaign_id: res.campaign_id,
      evaluation: res.evaluation,
      evaluated_at: new Date().toISOString(),
    };
  },
  generateMoves: async (id: string, context?: string, maxMoves?: number) => {
    const res = await apiFetch<{
      campaign_id: string;
      generated_moves: Array<{
        move_id: string;
        move_type: string;
        description: string;
        expected_impact: string;
        confidence: number;
        sequence_number: number;
      }>;
      total: number;
    }>(`/api/v1/campaigns/${id}/moves/generate`, {
      method: "POST",
      body: { context, max_moves: maxMoves },
      auth: true,
    });
    return res;
  },
};

export const councilApi = {
  startSession: async (body: StartCouncilRequest) => {
    const res = await apiFetch<{
      session: BackendCouncilSession;
    }>("/api/v1/council", {
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
  startCouncilGeneration: async (sessionId: string, agentRoster?: string[], maxAgents?: number) => {
    const res = await apiFetch<{
      session_id: string;
      status: string;
      positions: BackendCouncilPosition[];
    }>(`/api/v1/council/${sessionId}/start`, {
      method: "POST",
      body: {
        agent_roster: agentRoster ?? [],
        max_agents: maxAgents ?? 5,
      },
      auth: true,
    });
    return res;
  },
  synthesizeSession: async (sessionId: string, focus?: string) => {
    const res = await apiFetch<{
      session_id: string;
      status: string;
      synthesis: {
        decision: string;
        rationale: string;
        risks: string[];
        next_actions: string[];
        participating_agents: string[];
      };
    }>(`/api/v1/council/${sessionId}/synthesize`, {
      method: "POST",
      body: { focus },
      auth: true,
    });
    return res;
  },
  pollSession: async (sessionId: string) => {
    return councilApi.getSession(sessionId);
  },
  pollMessages: async (sessionId: string) => {
    return councilApi.getMessages(sessionId);
  },
  pollSessionRaw: async (sessionId: string): Promise<CouncilPollSessionResponse> =>
    apiFetch<CouncilPollSessionResponse>(`/api/v1/council/${sessionId}`, { auth: true }),
  pollMessagesRaw: async (sessionId: string): Promise<CouncilPollMessagesResponse> =>
    apiFetch<CouncilPollMessagesResponse>(`/api/v1/council/${sessionId}/messages`, { auth: true }),
};

export const councilOrchestrationApi = {
  create: async (
    body: CreateCouncilOrchestrationRequest,
  ): Promise<CouncilOrchestrationResponse> => {
    return apiFetch<CouncilOrchestrationResponse>("/api/v1/council/orchestrations", {
      method: "POST",
      body,
      auth: true,
    });
  },
  list: async (limit?: number): Promise<CouncilOrchestrationRun[]> => {
    return apiFetch<CouncilOrchestrationRun[]>(
      `/api/v1/council/orchestrations${limit ? `?limit=${limit}` : ""}`,
      { auth: true },
    );
  },
  get: async (id: string): Promise<CouncilOrchestrationRun> => {
    return apiFetch<CouncilOrchestrationRun>(`/api/v1/council/orchestrations/${id}`, {
      auth: true,
    });
  },
  listTurns: async (id: string): Promise<CouncilAvatarTurn[]> => {
    return apiFetch<CouncilAvatarTurn[]>(`/api/v1/council/orchestrations/${id}/turns`, {
      auth: true,
    });
  },
  listPresence: async (id: string): Promise<CouncilPresenceState[]> => {
    return apiFetch<CouncilPresenceState[]>(`/api/v1/council/orchestrations/${id}/presence`, {
      auth: true,
    });
  },
  listDebateEvents: async (id: string): Promise<CouncilDebateEvent[]> => {
    return apiFetch<CouncilDebateEvent[]>(`/api/v1/council/orchestrations/${id}/debate-events`, {
      auth: true,
    });
  },
};

export interface CreateCouncilOrchestrationRequest {
  request_summary: string;
  context_summary: string;
  mode?: string;
  requested_avatar_keys?: string[];
  max_challenge_rounds?: number;
}

export interface CouncilOrchestrationResponse {
  council_run_id: string;
  harness_run_id: string | null;
  status: string;
  avatar_roster: string[];
  presence_states: unknown[];
  debate_events: unknown[];
  synthesis: unknown;
  turns: unknown[];
}

export interface CouncilPresenceState {
  presence_id: string;
  org_id: string;
  avatar_id: string;
  harness_run_id: string | null;
  state: string;
  current_focus: string;
  current_concern: string;
  confidence: number;
  visible_summary: string;
  last_event_id: string | null;
  updated_at: string;
}

export interface CouncilDebateEvent {
  debate_event_id: string;
  org_id: string;
  harness_run_id: string;
  speaker_avatar_id: string | null;
  target_avatar_id: string | null;
  event_type: string;
  stance: string | null;
  content: unknown;
  confidence: number;
  created_at: string;
}

export interface CouncilSynthesis {
  known_facts: string[];
  assumptions: string[];
  risks: string[];
  next_actions: string[];
  open_questions: string[];
  strategic_recommendation: string;
  synthesized_by: string;
}

export interface CouncilChallengeContent {
  challenge_reason?: string;
  dominant_concern?: string;
  strategic_concern?: string;
  evidence_concern?: string;
  language_concern?: string;
  execution_concern?: string;
  measurement_concern?: string;
  creative_concern?: string;
  proof_concern?: string;
  text?: string;
  summary?: string;
  topic?: string;
}

export interface CouncilPositionContent {
  text?: string;
  dominant_concern?: string;
  [key: string]: unknown;
}

export interface CouncilInstinctContent {
  trigger_kind?: string;
  dominant_concern?: string;
  risk_flags?: string[];
  recommended_posture?: string;
  visible_summary?: string;
}

export interface CouncilOrchestrationRun {
  council_run_id: string;
  org_id: string;
  harness_run_id: string | null;
  request_summary: string;
  mode: string;
  status: string;
  avatar_roster: unknown;
  context_summary: string;
  synthesis: unknown;
  final_artifact_id: string | null;
  error_message: string | null;
  created_by: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CouncilAvatarTurn {
  turn_id: string;
  org_id: string;
  council_run_id: string;
  harness_run_id: string | null;
  avatar_id: string;
  avatar_key: string;
  turn_type: string;
  sequence_number: number;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  debate_event_id: string | null;
  instinct_frame_id: string | null;
  presence_id: string | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

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
  getSignals: async (params?: { category?: string }): Promise<IntelSignal[]> => {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.set("type", params.category);
    const query = queryParams.toString();
    const res = await apiFetch<{ signals: IntelSignal[] }>(
      `/api/v1/intel/signals${query ? `?${query}` : ""}`,
      { auth: true },
    );
    return res.signals ?? [];
  },
  getCompetitors: async (): Promise<Competitor[]> => {
    const res = await apiFetch<{
      competitor_snapshots: { id: string; competitor_name: string; website: string | null }[];
    }>("/api/v1/intel/competitors", { auth: true });
    return (res.competitor_snapshots ?? []).map((s) => ({
      id: s.id,
      name: s.competitor_name,
      websiteUrl: s.website ?? undefined,
      monitors: [],
      lastSeenAt: "",
    }));
  },
  getSignalStats: async (): Promise<IntelStats> => {
    const overview = await intelApi.getOverview();
    return {
      monitoredCount: overview.monitored_count ?? 0,
      signalsTwentyFourHours: overview.signals_24h ?? 0,
      highPriorityCount: overview.high_priority_count ?? 0,
      categoryBreakdown: {},
    };
  },
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

export const uploadsApi = {
  generateUploadUrl: (_body: { filename: string; contentType: string }) => {
    throw new ApiError(501, "uploads_api_not_implemented");
  },
  generateDownloadUrl: (_key: string) => {
    throw new ApiError(501, "uploads_api_not_implemented");
  },
  deleteUpload: (_key: string) => {
    throw new ApiError(501, "uploads_api_not_implemented");
  },
  generateScreenshotUploadUrl: (_filename: string) => {
    throw new ApiError(501, "uploads_api_not_implemented");
  },
  generateExportUrl: (_exportId: string) => {
    throw new ApiError(501, "uploads_api_not_implemented");
  },
  generateExportDownloadUrl: (_exportId: string) => {
    throw new ApiError(501, "uploads_api_not_implemented");
  },
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
    const summary = (payload.summary ?? payload) as Record<string, unknown>;
    return {
      activeCampaigns: Number(summary.active_campaigns ?? payload.active_campaigns ?? 0),
      activeCouncilSessions: Number(
        summary.active_council_sessions ?? payload.active_council_sessions ?? 0,
      ),
      openNudges: Number(summary.open_nudges ?? payload.open_nudges ?? 0),
      recentMuseConversations: Number(
        summary.recent_muse_conversations ?? payload.recent_muse_conversations ?? 0,
      ),
      eventTypes: Array.isArray(payload.event_types) ? (payload.event_types as string[]) : [],
    };
  },
};
