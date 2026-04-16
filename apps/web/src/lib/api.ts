import { publicEnv } from "./env";

export const isOffline = () => publicEnv.offlineMode;

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

let _authPromise: Promise<string | null> | null = null;

async function getAuthToken(): Promise<string | null> {
  if (typeof window === "undefined") return null;
  if (_authPromise) return _authPromise;
  _authPromise = (async () => {
    try {
      const { getToken } = await import("@clerk/nextjs/client");
      return await getToken();
    } catch {
      return null;
    }
  })();
  return _authPromise;
}

async function request<T>(path: string, options?: RequestInit & { auth?: boolean }): Promise<T> {
  if (isOffline()) {
    return offlineRequest<T>(path, options);
  }

  const token = options?.auth ? await getAuthToken() : null;

  const res = await fetch(`${publicEnv.apiBaseUrl}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });

  if (!res.ok) {
    throw new ApiError(res.status, await res.text());
  }

  return res.json() as Promise<T>;
}

async function offlineRequest<T>(
  path: string,
  options?: RequestInit & { auth?: boolean },
): Promise<T> {
  if (options?.method === "POST" || options?.method === "PUT" || options?.method === "DELETE") {
    await new Promise((r) => setTimeout(r, 100 + Math.random() * 200));
    const { getOfflineMutationResult } = await import("@/mocks/data");
    const result = getOfflineMutationResult(path, options.method);
    if (result === null) {
      throw new ApiError(501, `Offline mutation not implemented for ${options.method} ${path}`);
    }
    return result as T;
  }

  const { getOfflineData } = await import("@/mocks/data");
  const data = await getOfflineData(path);
  if (!data) {
    throw new ApiError(404, `Offline mock not defined for GET ${path}`);
  }
  return data as T;
}

function buildBody<T>(body: T) {
  return JSON.stringify(body);
}

// ─── Foundation ────────────────────────────────────────────────────────────────

export const foundationApi = {
  get: () => request<FoundationResponse>("/api/v1/foundation", { auth: true }),

  create: (body: CreateFoundationRequest) =>
    request<FoundationResponse>("/api/v1/foundation", {
      method: "POST",
      body: buildBody(body),
      auth: true,
    }),

  updateSection: (section: string, body: UpdateSectionRequest) =>
    request<void>(`/api/v1/foundation/sections/${section}`, {
      method: "PUT",
      body: buildBody(body),
      auth: true,
    }),

  listSnapshots: () =>
    request<FoundationSnapshot[]>("/api/v1/foundation/snapshots", { auth: true }),

  getSnapshot: (id: string) =>
    request<FoundationSnapshot>(`/api/v1/foundation/snapshots/${id}`, { auth: true }),

  createSnapshot: () =>
    request<FoundationSnapshot>("/api/v1/foundation/snapshots", {
      method: "POST",
      auth: true,
    }),

  restoreSnapshot: (id: string) =>
    request<void>(`/api/v1/foundation/snapshots/${id}/restore`, {
      method: "POST",
      auth: true,
    }),

  triggerScan: (mode: "quick" | "deep") =>
    request<ScanJob>("/api/v1/foundation/scan", {
      method: "POST",
      body: buildBody({ type: mode }),
      auth: true,
    }),

  getScanStatus: (jobId: string) =>
    request<ScanJob>(`/api/v1/foundation/scan/${jobId}`, { auth: true }),
};

// ─── Campaigns ────────────────────────────────────────────────────────────────

export const campaignsApi = {
  list: () => request<Campaign[]>("/api/v1/campaigns", { auth: true }),

  get: (id: string) => request<Campaign>(`/api/v1/campaigns/${id}`, { auth: true }),

  create: (body: CreateCampaignRequest) =>
    request<Campaign>("/api/v1/campaigns", {
      method: "POST",
      body: buildBody(body),
      auth: true,
    }),

  update: (id: string, body: UpdateCampaignRequest) =>
    request<Campaign>(`/api/v1/campaigns/${id}`, {
      method: "PUT",
      body: buildBody(body),
      auth: true,
    }),

  archive: (id: string) =>
    request<void>(`/api/v1/campaigns/${id}`, {
      method: "DELETE",
      auth: true,
    }),
};

// ─── Council ─────────────────────────────────────────────────────────────────

export const councilApi = {
  startSession: (body: StartCouncilRequest) =>
    request<CouncilSession>("/api/v1/council", {
      method: "POST",
      body: buildBody(body),
      auth: true,
    }),

  listSessions: () => request<CouncilSession[]>("/api/v1/council/history", { auth: true }),

  getSession: (id: string) => request<CouncilSession>(`/api/v1/council/${id}`, { auth: true }),

  getMessages: (id: string) =>
    request<CouncilMessage[]>(`/api/v1/council/${id}/messages`, { auth: true }),
};

// ─── Muse ─────────────────────────────────────────────────────────────────────

export const museApi = {
  submitPrompt: (body: MusePromptRequest) =>
    request<MuseResponse>("/api/v1/muse", {
      method: "POST",
      body: buildBody(body),
      auth: true,
    }),

  listConversations: () => request<MuseConversation[]>("/api/v1/muse/history", { auth: true }),

  getConversation: (id: string) => request<MuseConversation>(`/api/v1/muse/${id}`, { auth: true }),

  getMessages: (id: string) => request<Message[]>(`/api/v1/muse/${id}/messages`, { auth: true }),
};

// ─── PRL ──────────────────────────────────────────────────────────────────────

export const prlApi = {
  listRipples: () => request<Ripple[]>("/api/v1/ripples", { auth: true }),

  createRipple: (body: CreateRippleRequest) =>
    request<Ripple>("/api/v1/ripples", {
      method: "POST",
      body: buildBody(body),
      auth: true,
    }),

  getRipple: (id: string) => request<Ripple>(`/api/v1/ripples/${id}`, { auth: true }),

  updateRipple: (id: string, body: UpdateRippleRequest) =>
    request<Ripple>(`/api/v1/ripples/${id}`, {
      method: "PUT",
      body: buildBody(body),
      auth: true,
    }),

  deleteRipple: (id: string) =>
    request<void>(`/api/v1/ripples/${id}`, {
      method: "DELETE",
      auth: true,
    }),

  realizeRipple: (id: string) =>
    request<void>(`/api/v1/ripples/${id}/realize`, {
      method: "POST",
      auth: true,
    }),

  getRippleEdges: (id: string) => request<Edge[]>(`/api/v1/ripples/${id}/edges`, { auth: true }),

  createRippleEdge: (id: string, body: CreateEdgeRequest) =>
    request<Edge>(`/api/v1/ripples/${id}/edges`, {
      method: "POST",
      body: buildBody(body),
      auth: true,
    }),

  deleteRippleEdge: (edgeId: string) =>
    request<void>(`/api/v1/ripples/edges/${edgeId}`, {
      method: "DELETE",
      auth: true,
    }),

  listEssences: () => request<Essence[]>("/api/v1/essences", { auth: true }),

  createEssence: (body: CreateEssenceRequest) =>
    request<Essence>("/api/v1/essences", {
      method: "POST",
      body: buildBody(body),
      auth: true,
    }),

  getEssence: (id: string) => request<Essence>(`/api/v1/essences/${id}`, { auth: true }),

  updateEssence: (id: string, body: UpdateEssenceRequest) =>
    request<Essence>(`/api/v1/essences/${id}`, {
      method: "PUT",
      body: buildBody(body),
      auth: true,
    }),

  runDecay: () =>
    request<void>("/api/v1/prl/decay", {
      method: "POST",
      auth: true,
    }),
};

// ─── Uploads ─────────────────────────────────────────────────────────────────

export const uploadsApi = {
  generateUploadUrl: (body: UploadRequest) =>
    request<UploadUrlResponse>("/api/v1/uploads", {
      method: "POST",
      body: buildBody(body),
      auth: true,
    }),

  generateDownloadUrl: (key: string) =>
    request<DownloadUrlResponse>("/api/v1/uploads/download", {
      method: "POST",
      body: buildBody({ key }),
      auth: true,
    }),

  deleteUpload: (key: string) =>
    request<void>(`/api/v1/uploads/${encodeURIComponent(key)}`, {
      method: "DELETE",
      auth: true,
    }),

  generateScreenshotUploadUrl: (filename: string) =>
    request<UploadUrlResponse>("/api/v1/screenshots", {
      method: "POST",
      body: buildBody({ filename }),
      auth: true,
    }),

  generateExportUrl: (exportId: string) =>
    request<ExportUrlResponse>("/api/v1/exports", {
      method: "POST",
      body: buildBody({ exportId }),
      auth: true,
    }),

  generateExportDownloadUrl: (exportId: string) =>
    request<ExportUrlResponse>("/api/v1/exports/download", {
      method: "POST",
      body: buildBody({ exportId }),
      auth: true,
    }),
};

// ─── Billing ──────────────────────────────────────────────────────────────────

export const billingApi = {
  getStatus: () => request<BillingStatus>("/api/v1/billing", { auth: true }),

  createOrder: (body: CreateOrderRequest) =>
    request<Order>("/api/v1/billing/orders", {
      method: "POST",
      body: buildBody(body),
      auth: true,
    }),

  getSubscription: (id: string) =>
    request<Subscription>(`/api/v1/billing/subscriptions/${id}`, { auth: true }),

  cancelSubscription: (id: string) =>
    request<void>(`/api/v1/billing/subscriptions/${id}/cancel`, {
      method: "POST",
      auth: true,
    }),
};

// ─── Types ────────────────────────────────────────────────────────────────────

export interface FoundationResponse {
  orgId: string;
  version: number;
  sections: Record<string, unknown>;
  updatedAt: string;
}

export interface CreateFoundationRequest {
  url?: string;
}

export interface UpdateSectionRequest {
  value: unknown;
}

export interface FoundationSnapshot {
  id: string;
  orgId: string;
  foundationVersion: number;
  sections: Record<string, unknown>;
  createdAt: string;
}

export interface ScanJob {
  scanId: string;
  status: "queued" | "running" | "streaming" | "completed" | "failed";
  progress: number;
}

export interface Campaign {
  campaignId: string;
  orgId: string;
  name: string;
  status: "draft" | "pending_approval" | "active" | "paused" | "archived";
  goal?: string;
  timeline?: string;
  channels?: string[];
  createdAt: string;
  updatedAt: string;
}

export interface CreateCampaignRequest {
  name: string;
  goal?: string;
  timeline?: string;
  channels?: string[];
}

export interface UpdateCampaignRequest {
  name?: string;
  status?: Campaign["status"];
  goal?: string;
}

export interface StartCouncilRequest {
  campaignId: string;
  sessionType?: "tactical" | "operational" | "strategic" | "war_room" | "replanning";
}

export interface CouncilSession {
  sessionId: string;
  orgId: string;
  campaignId: string;
  sessionType: "tactical" | "operational" | "strategic" | "war_room" | "replanning";
  status: "queued" | "running" | "streaming" | "completed" | "failed";
  createdAt: string;
}

export interface CouncilMessage {
  messageId: string;
  sessionId: string;
  avatarKey: string;
  content: string;
  roundNumber: number;
  createdAt: string;
}

export interface MusePromptRequest {
  conversationId?: string;
  route: "strategic" | "content" | "tactical" | "foundation_update";
  message: string;
}

export interface MuseResponse {
  conversationId: string;
  message: Message;
  suggestedRoutes?: string[];
}

export interface MuseConversation {
  conversationId: string;
  orgId: string;
  route: "strategic" | "content" | "tactical" | "foundation_update";
  lastMessageAt: string;
  messageCount: number;
}

export interface Message {
  messageId: string;
  conversationId: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
}

export interface Ripple {
  rippleId: string;
  orgId: string;
  coreClaim: string;
  keyReasoning: string;
  prediction?: string;
  source: string;
  confidence: number;
  protectionBand: "protected" | "important" | "normal" | "disposable";
  createdAt: string;
}

export interface CreateRippleRequest {
  coreClaim: string;
  keyReasoning: string;
  prediction?: string;
  source?: string;
}

export interface UpdateRippleRequest {
  coreClaim?: string;
  keyReasoning?: string;
  protectionBand?: "protected" | "important" | "normal" | "disposable";
}

export interface Edge {
  edgeId: string;
  sourceRippleId: string;
  targetRippleId: string;
  relationship: string;
}

export interface CreateEdgeRequest {
  targetRippleId: string;
  relationship: string;
}

export interface Essence {
  essenceId: string;
  orgId: string;
  avatarKey: string;
  content: string;
  category: string;
  createdAt: string;
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

export interface UploadRequest {
  filename: string;
  contentType: string;
}

export interface UploadUrlResponse {
  uploadUrl: string;
  key: string;
  expiresAt: string;
}

export interface DownloadUrlResponse {
  downloadUrl: string;
  expiresAt: string;
}

export interface ExportUrlResponse {
  exportUrl: string;
  expiresAt: string;
}

export type PlanTier = "ascend" | "glide" | "soar" | "enterprise";

export interface PlanDetails {
  tier: PlanTier;
  name: string;
  price_inr_monthly: number | "talk_to_us";
  description: string;
  features: string[];
}

export type PlanTier = "ascend" | "glide" | "soar" | "enterprise";

export interface PlanDetails {
  tier: PlanTier;
  name: string;
  price_inr_monthly: number | "talk_to_us";
  description: string;
  features: string[];
}

export interface BillingStatus {
  provider: string;
  currency: string;
  grace_period_days: number;
  subscription_status: string | null;
  current_plan: PlanDetails | null;
  available_plans: PlanDetails[];
  org_id: string;
}

export interface CreateOrderRequest {
  campaignId: string;
  amount: number;
  currency?: string;
}

export interface Order {
  orderId: string;
  campaignId: string;
  amount: number;
  currency: string;
  status: "pending" | "paid" | "failed";
  razorpayOrderId: string;
  createdAt: string;
}

export interface Subscription {
  subscriptionId: string;
  plan: string;
  status: "active" | "past_due" | "canceled";
  currentPeriodEnd: string;
}
