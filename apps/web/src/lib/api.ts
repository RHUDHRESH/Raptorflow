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
        Clerk?: {
          loaded?: boolean;
          session?: {
            getToken?: (options?: { template?: string }) => Promise<string | null>;
          };
        };
      }
    ).Clerk;

    for (let attempt = 0; attempt < 100; attempt += 1) {
      if (clerk?.loaded && clerk.session?.getToken) {
        const token = await Promise.race([
          clerk.session.getToken({ template: "backend" } as never).catch(() => null),
          clerk.session.getToken().catch(() => null),
          new Promise<null>((resolve) => setTimeout(() => resolve(null), 1000)),
        ]);
        if (token) return token;
      }

      await new Promise((resolve) => setTimeout(resolve, 150));
    }
  } catch {
    // Clerk not loaded yet or session expired
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

export async function appFetch<T>(
  path: string,
  options: {
    token?: string | null;
    method?: string;
    body?: unknown;
    headers?: HeadersInit;
    auth?: boolean;
  } = {},
): Promise<T> {
  const token = options.auth ? (options.token ?? null) : null;

  const res = await fetch(path, {
    method: options.method ?? "GET",
    credentials: "include",
    cache: "no-store",
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

export const avatarsApi = {
  list: async () => {
    const res = await apiFetch<{ avatars: BackendAvatar[] }>("/api/v1/avatars", { auth: true });
    return res.avatars.map(normalizeAvatar);
  },
  get: async (id: string) => {
    const res = await apiFetch<{ avatar: BackendAvatar }>(`/api/v1/avatars/${id}`, { auth: true });
    return normalizeAvatar(res.avatar);
  },
  create: async (body: CreateAvatarRequest) => {
    const res = await apiFetch<{ avatar: BackendAvatar }>("/api/v1/avatars", {
      method: "POST",
      body,
      auth: true,
    });
    return normalizeAvatar(res.avatar);
  },
  update: async (id: string, patch: UpdateAvatarRequest) => {
    const res = await apiFetch<{ avatar: BackendAvatar }>(`/api/v1/avatars/${id}`, {
      method: "PATCH",
      body: patch,
      auth: true,
    });
    return normalizeAvatar(res.avatar);
  },
  deactivate: async (id: string) => {
    await apiFetch<{ deleted: boolean }>(`/api/v1/avatars/${id}`, {
      method: "DELETE",
      auth: true,
    });
  },
  ensureDefaults: async () => {
    const res = await apiFetch<{ avatars: BackendAvatar[] }>("/api/v1/avatars/defaults", {
      method: "POST",
      auth: true,
    });
    return res.avatars.map(normalizeAvatar);
  },
};

export const harnessApi = {
  listRuns: async () => {
    const res = await apiFetch<{ runs: BackendHarnessRun[] }>("/api/v1/harness/runs", {
      auth: true,
    });
    return res.runs.map(normalizeHarnessRun);
  },
  getRun: async (id: string) => {
    const res = await apiFetch<{ run: BackendHarnessRun }>(`/api/v1/harness/runs/${id}`, {
      auth: true,
    });
    return normalizeHarnessRun(res.run);
  },
  createRun: async (body: CreateHarnessRunRequest) => {
    const res = await apiFetch<{ run: BackendHarnessRun }>("/api/v1/harness/runs", {
      method: "POST",
      body,
      auth: true,
    });
    return normalizeHarnessRun(res.run);
  },
  cancelRun: async (id: string) => {
    const res = await apiFetch<{ run: BackendHarnessRun }>(`/api/v1/harness/runs/${id}/cancel`, {
      method: "POST",
      auth: true,
    });
    return normalizeHarnessRun(res.run);
  },
  listSteps: async (runId: string) => {
    const res = await apiFetch<{ steps: BackendHarnessStep[] }>(
      `/api/v1/harness/runs/${runId}/steps`,
      {
        auth: true,
      },
    );
    return res.steps.map(normalizeHarnessStep);
  },
};

export const capabilitiesApi = {
  list: async () => {
    const res = await apiFetch<unknown>("/api/v1/capabilities", { auth: true });
    return unwrapList<BackendCapabilityDefinition>(res, ["capabilities"]);
  },
  ensureDefaults: async () => {
    const res = await apiFetch<unknown>("/api/v1/capabilities/defaults", {
      method: "POST",
      auth: true,
    });
    return unwrapList<BackendCapabilityDefinition>(res, ["capabilities"]);
  },
  get: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/capabilities/${id}`, { auth: true });
    const cap = unwrapItem<BackendCapabilityDefinition>(res, ["capability"]);
    if (!cap) throw new ApiError(500, "Capability response missing capability payload");
    return cap;
  },
  getByKey: async (key: string) => {
    const res = await apiFetch<unknown>(`/api/v1/capabilities/key/${key}`, { auth: true });
    const cap = unwrapItem<BackendCapabilityDefinition>(res, ["capability"]);
    if (!cap) throw new ApiError(500, "Capability response missing capability payload");
    return cap;
  },
  listAvatarCapabilities: async (avatarId: string) => {
    const res = await apiFetch<unknown>(`/api/v1/avatars/${avatarId}/capabilities`, {
      auth: true,
    });
    return unwrapList<BackendCapabilityDefinition>(res, ["capabilities"]);
  },
  grantToAvatar: async (avatarId: string, body: GrantCapabilityRequest) => {
    const res = await apiFetch<{
      grant_id: string;
      avatar_id: string;
      capability_id: string;
      capability_key: string;
      grant_scope: string;
    }>(`/api/v1/avatars/${avatarId}/capabilities`, { method: "POST", body, auth: true });
    return res;
  },
  revokeFromAvatar: async (avatarId: string, capabilityId: string) => {
    await apiFetch<void>(`/api/v1/avatars/${avatarId}/capabilities/${capabilityId}`, {
      method: "DELETE",
      auth: true,
    });
  },
  createContextPack: async (body: CreateContextPackRequest) => {
    const res = await apiFetch<{
      context_pack_id: string;
      org_id: string;
      scope: string;
      token_budget: number;
      created_at: string;
    }>("/api/v1/harness/context-packs", { method: "POST", body, auth: true });
    return res;
  },
  getContextPack: async (id: string) => {
    const res = await apiFetch<{
      context_pack_id: string;
      org_id: string;
      run_id: string | null;
      capability_id: string | null;
      avatar_id: string | null;
      scope: string;
      token_budget: number;
      foundation_context: unknown;
      intel_context: unknown;
      campaign_context: unknown;
      office_context: unknown;
      ripple_context: unknown;
      compressed_context: unknown | null;
      created_at: string;
    }>(`/api/v1/harness/context-packs/${id}`, { auth: true });
    return res;
  },
  listRuns: async (limit = 50) => {
    const res = await apiFetch<unknown>(`/api/v1/capability-runs?limit=${limit}`, { auth: true });
    return unwrapList<BackendCapabilityRun>(res, ["capability_runs"]);
  },
  createRun: async (body: CreateCapabilityRunRequest) => {
    const res = await apiFetch<{
      capability_run_id: string;
      artifact_id: string | null;
      status: string;
      output: unknown;
      error: string | null;
      model_id: string | null;
      token_usage: unknown;
    }>("/api/v1/capability-runs", { method: "POST", body, auth: true });
    return res;
  },
  getRun: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/capability-runs/${id}`, { auth: true });
    const run = unwrapItem<BackendCapabilityRun>(res, ["capability_run"]);
    if (!run) throw new ApiError(500, "Run response missing run payload");
    return run;
  },
  listArtifacts: async (params?: { artifact_type?: string; status?: string; limit?: number }) => {
    const query = new URLSearchParams();
    if (params?.artifact_type) query.set("artifact_type", params.artifact_type);
    if (params?.status) query.set("status", params.status);
    if (params?.limit) query.set("limit", String(params.limit));
    const qs = query.toString();
    const res = await apiFetch<unknown>(`/api/v1/artifacts${qs ? `?${qs}` : ""}`, { auth: true });
    return unwrapList<BackendCapabilityArtifact>(res, ["artifacts"]);
  },
  getArtifact: async (id: string) => {
    const res = await apiFetch<unknown>(`/api/v1/artifacts/${id}`, { auth: true });
    const artifact = unwrapItem<BackendCapabilityArtifact>(res, ["artifact"]);
    if (!artifact) throw new ApiError(500, "Artifact response missing artifact payload");
    return artifact;
  },
  createArtifactVersion: async (artifactId: string, body: CreateArtifactVersionRequest) => {
    const res = await apiFetch<{ artifact: BackendCapabilityArtifact }>(
      `/api/v1/artifacts/${artifactId}/versions`,
      { method: "POST", body, auth: true },
    );
    return res.artifact;
  },
};

export const avatarSoulApi = {
  getSoul: async (avatarId: string) => {
    const res = await apiFetch<{ soul: BackendAvatarSoul }>(`/api/v1/avatars/${avatarId}/soul`, {
      auth: true,
    });
    return normalizeAvatarSoul(res.soul);
  },
  updateSoul: async (avatarId: string, body: UpdateAvatarSoulRequest) => {
    const res = await apiFetch<{ soul: BackendAvatarSoul }>(`/api/v1/avatars/${avatarId}/soul`, {
      method: "PUT",
      body,
      auth: true,
    });
    return normalizeAvatarSoul(res.soul);
  },
  listMemoryEdges: async (avatarId: string) => {
    const res = await apiFetch<{ memory_edges: BackendAvatarMemoryEdge[] }>(
      `/api/v1/avatars/${avatarId}/memory/edges`,
      { auth: true },
    );
    return res.memory_edges.map(normalizeAvatarMemoryEdge);
  },
  createMemoryEdge: async (avatarId: string, body: CreateMemoryEdgeRequest) => {
    const res = await apiFetch<{ memory_edge: BackendAvatarMemoryEdge }>(
      `/api/v1/avatars/${avatarId}/memory/edges`,
      { method: "POST", body, auth: true },
    );
    return normalizeAvatarMemoryEdge(res.memory_edge);
  },
  deleteMemoryEdge: async (avatarId: string, edgeId: string) => {
    await apiFetch<void>(`/api/v1/avatars/${avatarId}/memory/edges/${edgeId}`, {
      method: "DELETE",
      auth: true,
    });
  },
  createInstinctFrame: async (avatarId: string, body: CreateInstinctFrameRequest) => {
    const res = await apiFetch<{ instinct_frame_id: string; status: string }>(
      `/api/v1/avatars/${avatarId}/instinct-frame`,
      { method: "POST", body, auth: true },
    );
    return res;
  },
  listPresenceStates: async (runId: string) => {
    const res = await apiFetch<{ presence_states: BackendAvatarPresenceState[] }>(
      `/api/v1/harness/runs/${runId}/presence`,
      { auth: true },
    );
    return res.presence_states.map(normalizeAvatarPresenceState);
  },
  upsertPresenceState: async (runId: string, body: UpsertPresenceStateRequest) => {
    const res = await apiFetch<{ presence_id: string; status: string }>(
      `/api/v1/harness/runs/${runId}/presence`,
      { method: "POST", body, auth: true },
    );
    return res;
  },
  listDebateEvents: async (runId: string) => {
    const res = await apiFetch<{ debate_events: BackendAvatarDebateEvent[] }>(
      `/api/v1/harness/runs/${runId}/debate-events`,
      { auth: true },
    );
    return res.debate_events.map(normalizeAvatarDebateEvent);
  },
  createDebateEvent: async (runId: string, body: CreateDebateEventRequest) => {
    const res = await apiFetch<{ debate_event_id: string; status: string }>(
      `/api/v1/harness/runs/${runId}/debate-events`,
      { method: "POST", body, auth: true },
    );
    return res;
  },
  getArtifactTrail: async (avatarId: string) => {
    const res = await apiFetch<{ artifact_trail: BackendAvatarArtifactTrail[] }>(
      `/api/v1/avatars/${avatarId}/artifact-trail`,
      { auth: true },
    );
    return res.artifact_trail.map(normalizeAvatarArtifactTrail);
  },
};

export const strategistApi = {
  ensureDefault: async () => {
    const res = await apiFetch<StrategistSoulResponse>("/api/v1/avatars/strategist/default", {
      method: "POST",
      auth: true,
    });
    return res;
  },
  dryRun: async (body: StrategistDryRunRequest) => {
    const res = await apiFetch<StrategistDryRunResponse>("/api/v1/avatars/strategist/dry-run", {
      method: "POST",
      body,
      auth: true,
    });
    return res;
  },
};

export interface StrategistSoulResponse {
  avatar_id: string;
  soul_id: string;
  created: boolean;
  updated: boolean;
}

export interface StrategistDryRunRequest {
  task_summary: string;
  context_summary: string;
}

export interface StrategistDryRunResponse {
  avatar_id: string;
  soul_id: string;
  embodiment_pack: StrategistEmbodimentPack;
  role_lock_prompt: string;
  instinct_frame: StrategistInstinctFrame;
  presence_state: StrategistPresenceState | null;
  debate_event: StrategistDebateEvent | null;
}

export interface StrategistEmbodimentPack {
  avatar_id: string;
  soul_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  operating_principles: string[];
  debate_style: Record<string, unknown>;
  evaluation_bias: Record<string, unknown>;
  memory_edges: StrategistMemoryEdge[];
}

export interface StrategistMemoryEdge {
  memory_edge_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface StrategistInstinctFrame {
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: string[];
  recommended_posture: string;
  visible_summary: string;
}

export interface StrategistPresenceState {
  presence_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  visible_summary: string;
  confidence: number;
}

export interface StrategistDebateEvent {
  debate_event_id: string;
  event_type: string;
  stance: string;
  content: Record<string, unknown>;
  confidence: number;
}

export const researcherApi = {
  ensureDefault: async () => {
    const res = await apiFetch<ResearcherSoulResponse>("/api/v1/avatars/researcher/default", {
      method: "POST",
      auth: true,
    });
    return res;
  },
  dryRun: async (body: ResearcherDryRunRequest) => {
    const res = await apiFetch<ResearcherDryRunResponse>("/api/v1/avatars/researcher/dry-run", {
      method: "POST",
      body,
      auth: true,
    });
    return res;
  },
};

export interface ResearcherSoulResponse {
  avatar_id: string;
  soul_id: string;
  created: boolean;
  updated: boolean;
}

export interface ResearcherDryRunRequest {
  task_summary: string;
  context_summary: string;
}

export interface ResearcherDryRunResponse {
  avatar_id: string;
  soul_id: string;
  embodiment_pack: ResearcherEmbodimentPack;
  role_lock_prompt: string;
  instinct_frame: ResearcherInstinctFrame;
  presence_state: ResearcherPresenceState | null;
  debate_event: ResearcherDebateEvent | null;
  claim_audit: ResearcherClaimAudit | null;
}

export interface ResearcherEmbodimentPack {
  avatar_id: string;
  soul_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  operating_principles: string[];
  debate_style: Record<string, unknown>;
  evaluation_bias: Record<string, unknown>;
  memory_edges: ResearcherMemoryEdge[];
}

export interface ResearcherMemoryEdge {
  memory_edge_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface ResearcherInstinctFrame {
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: string[];
  recommended_posture: string;
  visible_summary: string;
}

export interface ResearcherPresenceState {
  presence_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  visible_summary: string;
  confidence: number;
}

export interface ResearcherDebateEvent {
  debate_event_id: string;
  event_type: string;
  stance: string;
  content: Record<string, unknown>;
  confidence: number;
}

export interface ResearcherClaimAudit {
  known_facts: string[];
  claims: ClaimAnalysis[];
  unsupported_claims: string[];
  assumptions: string[];
  needed_sources: string[];
  competitor_notes: string[];
  open_questions: string[];
}

export interface ClaimAnalysis {
  claim: string;
  evidence_level: string;
  source: string;
  risk: string;
  recommended_action: string;
  safer_rewrite: string;
}

export interface UpdateAvatarSoulRequest {
  identity_kernel?: Record<string, unknown>;
  worldview?: string[];
  obsessions?: string[];
  reflexes?: string[];
  taboos?: string[];
  debate_style?: Record<string, unknown>;
  embodiment_level?: string;
  operating_principles?: string[];
  evaluation_bias?: Record<string, unknown>;
  is_active?: boolean;
}

export interface CreateMemoryEdgeRequest {
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy?: string;
  use_when: string;
}

export interface CreateInstinctFrameRequest {
  avatar_id: string;
  harness_run_id?: string;
  capability_run_id?: string;
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: Record<string, unknown>;
  recommended_posture: string;
  visible_summary: string;
  private_notes?: Record<string, unknown>;
}

export interface UpsertPresenceStateRequest {
  avatar_id: string;
  state: string;
  current_focus: string;
  current_concern: string;
  confidence: number;
  visible_summary: string;
  last_event_id?: string;
}

export interface CreateDebateEventRequest {
  speaker_avatar_id?: string;
  target_avatar_id?: string;
  event_type: string;
  stance?: string;
  content: Record<string, unknown>;
  confidence: number;
}

export interface CreateContextPackRequest {
  avatar_id?: string;
  capability_id?: string;
  capability_key?: string;
  campaign_id?: string;
  token_budget?: number;
}

export interface CreateCapabilityRunRequest {
  avatar_id: string;
  capability_key: string;
  campaign_id?: string;
  input: Record<string, unknown>;
  mode?: "draft" | "dry_run";
}

export interface GrantCapabilityRequest {
  capability_id: string;
  grant_scope?: string;
  constraints?: Record<string, unknown>;
}

export interface CreateArtifactVersionRequest {
  body: Record<string, unknown>;
  change_reason?: string;
}

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
  status: "queued" | "running" | "completed" | "failed";
  progress?: number;
}

export interface QuickScanResult {
  strengths: string[];
  gaps: string[];
  recommendations: string[];
  positioning_score: number;
  summary: string;
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
export interface BackendCouncilPosition {
  position_id: string;
  avatar_key: string;
  round_number: number;
  content: string;
  extracted_ripple_data?: {
    key_risks?: string[];
    recommended_next_move?: string;
    ripple_candidates?: Array<{
      summary: string;
      salience: number;
      type: string;
    }>;
  };
  created_at: string;
}

export interface CouncilPollSessionResponse {
  session: BackendCouncilSession;
  positions?: BackendCouncilPosition[];
  status: string;
}

export interface CouncilPollMessagesResponse {
  session_id: string;
  positions: BackendCouncilPosition[];
  status: string;
}
export interface BackendCouncilSession {
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

export interface Avatar {
  avatarId: string;
  avatarKey: string;
  displayName: string;
  role: string;
  archetype: string;
  personality: Record<string, unknown>;
  systemPrompt: string;
  toolPermissions: Record<string, unknown>;
  memoryScope: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface BackendAvatar {
  avatar_id: string;
  avatar_key: string;
  display_name: string;
  role: string;
  archetype: string;
  personality: Record<string, unknown>;
  system_prompt: string;
  tool_permissions: Record<string, unknown>;
  memory_scope: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateAvatarRequest {
  avatar_key: string;
  display_name: string;
  role: string;
  archetype: string;
  personality?: Record<string, unknown>;
  system_prompt?: string;
  tool_permissions?: Record<string, unknown>;
  memory_scope?: string;
}

export interface UpdateAvatarRequest {
  display_name?: string;
  personality?: Record<string, unknown>;
  system_prompt?: string;
  tool_permissions?: Record<string, unknown>;
  is_active?: boolean;
}

export interface HarnessRun {
  runId: string;
  runType: string;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  errorMessage: string | null;
  createdBy: string | null;
  startedAt: string | null;
  completedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

interface BackendHarnessRun {
  run_id: string;
  run_type: string;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  error_message: string | null;
  created_by: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface HarnessStep {
  stepId: string;
  runId: string;
  avatarId: string | null;
  stepType: string;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  errorMessage: string | null;
  sequenceNumber: number;
  startedAt: string | null;
  completedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

interface BackendHarnessStep {
  step_id: string;
  run_id: string;
  avatar_id: string | null;
  step_type: string;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  error_message: string | null;
  sequence_number: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateHarnessRunRequest {
  run_type: string;
  input: Record<string, unknown>;
  avatar_keys?: string[];
  execute_now?: boolean;
}

export interface BackendCapabilityDefinition {
  capability_id: string;
  capability_key: string;
  name: string;
  domain: string;
  description: string;
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  required_context: Record<string, unknown>;
  allowed_tools: Record<string, unknown>;
  artifact_type: string;
  evaluator_key: string;
  ripple_policy: Record<string, unknown>;
  risk_level: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BackendCapabilityRun {
  capability_run_id: string;
  org_id: string;
  avatar_id: string | null;
  capability_id: string;
  capability_key: string | null;
  status: string;
  input: Record<string, unknown>;
  output: Record<string, unknown> | null;
  error_message: string | null;
  model_id: string | null;
  token_usage: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface BackendCapabilityArtifact {
  artifact_id: string;
  org_id: string;
  capability_run_id: string | null;
  avatar_id: string | null;
  capability_id: string | null;
  artifact_type: string;
  title: string;
  body: Record<string, unknown>;
  status: string;
  version: number;
  evaluation: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

function normalizeAvatar(a: BackendAvatar): Avatar {
  return {
    avatarId: a.avatar_id,
    avatarKey: a.avatar_key,
    displayName: a.display_name,
    role: a.role,
    archetype: a.archetype,
    personality: a.personality,
    systemPrompt: a.system_prompt,
    toolPermissions: a.tool_permissions,
    memoryScope: a.memory_scope,
    isActive: a.is_active,
    createdAt: a.created_at,
    updatedAt: a.updated_at,
  };
}

function normalizeHarnessRun(r: BackendHarnessRun): HarnessRun {
  return {
    runId: r.run_id,
    runType: r.run_type,
    status: r.status,
    input: r.input,
    output: r.output,
    errorMessage: r.error_message,
    createdBy: r.created_by,
    startedAt: r.started_at,
    completedAt: r.completed_at,
    createdAt: r.created_at,
    updatedAt: r.updated_at,
  };
}

function normalizeHarnessStep(s: BackendHarnessStep): HarnessStep {
  return {
    stepId: s.step_id,
    runId: s.run_id,
    avatarId: s.avatar_id,
    stepType: s.step_type,
    status: s.status,
    input: s.input,
    output: s.output,
    errorMessage: s.error_message,
    sequenceNumber: s.sequence_number,
    startedAt: s.started_at,
    completedAt: s.completed_at,
    createdAt: s.created_at,
    updatedAt: s.updated_at,
  };
}

export interface BackendAvatarSoul {
  soul_id: string;
  avatar_id: string;
  identity_kernel: Record<string, unknown>;
  worldview: unknown;
  obsessions: unknown;
  reflexes: unknown;
  taboos: unknown;
  debate_style: Record<string, unknown>;
  embodiment_level: string;
  operating_principles: unknown;
  evaluation_bias: Record<string, unknown>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BackendAvatarMemoryEdge {
  memory_edge_id: string;
  avatar_id: string;
  ripple_id: string;
  relationship_type: string;
  salience: number;
  decay_policy: string;
  use_when: string;
  last_used_at: string | null;
  created_at: string;
}

export interface BackendAvatarInstinctFrame {
  instinct_frame_id: string;
  avatar_id: string;
  harness_run_id: string | null;
  capability_run_id: string | null;
  trigger_kind: string;
  dominant_concern: string;
  risk_flags: Record<string, unknown>;
  recommended_posture: string;
  visible_summary: string;
  created_at: string;
}

export interface BackendAvatarPresenceState {
  presence_id: string;
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

export interface BackendAvatarDebateEvent {
  debate_event_id: string;
  harness_run_id: string;
  speaker_avatar_id: string | null;
  target_avatar_id: string | null;
  event_type: string;
  stance: string | null;
  content: Record<string, unknown>;
  confidence: number;
  created_at: string;
}

export interface BackendAvatarArtifactTrail {
  trail_id: string;
  avatar_id: string;
  artifact_id: string;
  harness_run_id: string | null;
  contribution_type: string;
  summary: string;
  created_at: string;
}

export interface AvatarSoul {
  soulId: string;
  avatarId: string;
  identityKernel: Record<string, unknown>;
  worldview: string[];
  obsessions: string[];
  reflexes: string[];
  taboos: string[];
  debateStyle: Record<string, unknown>;
  embodimentLevel: string;
  operatingPrinciples: string[];
  evaluationBias: Record<string, unknown>;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AvatarMemoryEdge {
  memoryEdgeId: string;
  avatarId: string;
  rippleId: string;
  relationshipType: string;
  salience: number;
  decayPolicy: string;
  useWhen: string;
  lastUsedAt: string | null;
  createdAt: string;
}

export interface AvatarPresenceState {
  presenceId: string;
  avatarId: string;
  harnessRunId: string | null;
  state: string;
  currentFocus: string;
  currentConcern: string;
  confidence: number;
  visibleSummary: string;
  lastEventId: string | null;
  updatedAt: string;
}

export interface AvatarDebateEvent {
  debateEventId: string;
  harnessRunId: string;
  speakerAvatarId: string | null;
  targetAvatarId: string | null;
  eventType: string;
  stance: string | null;
  content: Record<string, unknown>;
  confidence: number;
  createdAt: string;
}

export interface AvatarArtifactTrail {
  trailId: string;
  avatarId: string;
  artifactId: string;
  harnessRunId: string | null;
  contributionType: string;
  summary: string;
  createdAt: string;
}

function normalizeAvatarSoul(s: BackendAvatarSoul): AvatarSoul {
  return {
    soulId: s.soul_id,
    avatarId: s.avatar_id,
    identityKernel: s.identity_kernel,
    worldview: Array.isArray(s.worldview) ? (s.worldview as string[]) : [],
    obsessions: Array.isArray(s.obsessions) ? (s.obsessions as string[]) : [],
    reflexes: Array.isArray(s.reflexes) ? (s.reflexes as string[]) : [],
    taboos: Array.isArray(s.taboos) ? (s.taboos as string[]) : [],
    debateStyle: s.debate_style,
    embodimentLevel: s.embodiment_level,
    operatingPrinciples: Array.isArray(s.operating_principles)
      ? (s.operating_principles as string[])
      : [],
    evaluationBias: s.evaluation_bias,
    isActive: s.is_active,
    createdAt: s.created_at,
    updatedAt: s.updated_at,
  };
}

function normalizeAvatarMemoryEdge(e: BackendAvatarMemoryEdge): AvatarMemoryEdge {
  return {
    memoryEdgeId: e.memory_edge_id,
    avatarId: e.avatar_id,
    rippleId: e.ripple_id,
    relationshipType: e.relationship_type,
    salience: e.salience,
    decayPolicy: e.decay_policy,
    useWhen: e.use_when,
    lastUsedAt: e.last_used_at,
    createdAt: e.created_at,
  };
}

function normalizeAvatarPresenceState(p: BackendAvatarPresenceState): AvatarPresenceState {
  return {
    presenceId: p.presence_id,
    avatarId: p.avatar_id,
    harnessRunId: p.harness_run_id,
    state: p.state,
    currentFocus: p.current_focus,
    currentConcern: p.current_concern,
    confidence: p.confidence,
    visibleSummary: p.visible_summary,
    lastEventId: p.last_event_id,
    updatedAt: p.updated_at,
  };
}

function normalizeAvatarDebateEvent(e: BackendAvatarDebateEvent): AvatarDebateEvent {
  return {
    debateEventId: e.debate_event_id,
    harnessRunId: e.harness_run_id,
    speakerAvatarId: e.speaker_avatar_id,
    targetAvatarId: e.target_avatar_id,
    eventType: e.event_type,
    stance: e.stance,
    content: e.content,
    confidence: e.confidence,
    createdAt: e.created_at,
  };
}

function normalizeAvatarArtifactTrail(t: BackendAvatarArtifactTrail): AvatarArtifactTrail {
  return {
    trailId: t.trail_id,
    avatarId: t.avatar_id,
    artifactId: t.artifact_id,
    harnessRunId: t.harness_run_id,
    contributionType: t.contribution_type,
    summary: t.summary,
    createdAt: t.created_at,
  };
}
