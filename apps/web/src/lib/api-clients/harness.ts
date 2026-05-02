import { ApiError, apiFetch, unwrapItem, unwrapList } from "../api-core";
import {
  normalizeAvatar,
  normalizeAvatarArtifactTrail,
  normalizeAvatarDebateEvent,
  normalizeAvatarMemoryEdge,
  normalizeAvatarPresenceState,
  normalizeAvatarSoul,
  normalizeHarnessRun,
  normalizeHarnessStep,
} from "../api-models";
import type {
  Avatar,
  AvatarArtifactTrail,
  AvatarDebateEvent,
  AvatarMemoryEdge,
  AvatarPresenceState,
  AvatarSoul,
  BackendAvatar,
  BackendAvatarArtifactTrail,
  BackendAvatarDebateEvent,
  BackendAvatarMemoryEdge,
  BackendAvatarPresenceState,
  BackendAvatarSoul,
  BackendCapabilityArtifact,
  BackendCapabilityDefinition,
  BackendCapabilityRun,
  BackendHarnessRun,
  BackendHarnessStep,
  CreateArtifactVersionRequest,
  CreateAvatarRequest,
  CreateCapabilityRunRequest,
  CreateContextPackRequest,
  CreateDebateEventRequest,
  CreateHarnessRunRequest,
  CreateInstinctFrameRequest,
  CreateMemoryEdgeRequest,
  GrantCapabilityRequest,
  HarnessRun,
  HarnessStep,
  UpdateAvatarRequest,
  UpdateAvatarSoulRequest,
  UpsertPresenceStateRequest,
} from "../api-models";

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
