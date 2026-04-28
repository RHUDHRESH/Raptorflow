/**
 * RaptorFlow Campaign Feature Hooks
 *
 * Unified TanStack Query hooks for campaigns, moves, and tasks.
 * All hooks use runtime guards. No `as any`. No fake data.
 */

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import {
  normalizeCampaignSummary,
  normalizeCampaignEvaluation,
  normalizeCampaignMove,
  normalizeCampaignTask,
} from "./types";
import type {
  CampaignSummary,
  CampaignEvaluation,
  CampaignMove,
  CampaignTask,
  CreateCampaignRequest,
} from "./types";

/* ─── Query Keys ──────────────────────────────────────────────────────────── */

export const campaignKeys = {
  all: ["campaigns"] as const,
  lists: () => [...campaignKeys.all, "list"] as const,
  list: (filters: string) => [...campaignKeys.lists(), { filters }] as const,
  details: () => [...campaignKeys.all, "detail"] as const,
  detail: (id: string) => [...campaignKeys.details(), id] as const,
  moves: (id: string) => [...campaignKeys.detail(id), "moves"] as const,
  tasks: (id: string) => [...campaignKeys.detail(id), "tasks"] as const,
  evaluations: (id: string) => [...campaignKeys.detail(id), "evaluation"] as const,
};

/* ─── List Campaigns ──────────────────────────────────────────────────────── */

async function fetchCampaigns(): Promise<CampaignSummary[]> {
  const res = await apiFetch<unknown>("/api/v1/campaigns", { auth: true });
  if (!res || typeof res !== "object") return [];
  const payload = res as Record<string, unknown>;
  const campaigns = Array.isArray(payload.campaigns)
    ? payload.campaigns
    : Array.isArray(res)
      ? res
      : [];
  return campaigns.map(normalizeCampaignSummary).filter((c): c is CampaignSummary => c !== null);
}

export function useCampaigns() {
  return useQuery({
    queryKey: campaignKeys.lists(),
    queryFn: fetchCampaigns,
  });
}

/* ─── Get Campaign Detail ─────────────────────────────────────────────────── */

async function fetchCampaignDetail(id: string): Promise<{
  campaign: CampaignSummary;
  moves: CampaignMove[];
  tasks: CampaignTask[];
  evaluation: CampaignEvaluation | null;
}> {
  const res = await apiFetch<unknown>(`/api/v1/campaigns/${id}`, { auth: true });
  if (!res || typeof res !== "object") {
    throw new Error("Campaign detail response is not an object");
  }
  const payload = res as Record<string, unknown>;

  const campaignRaw = payload.campaign ?? payload;
  const campaign = normalizeCampaignSummary(campaignRaw);
  if (!campaign) {
    throw new Error("Campaign detail missing valid campaign field");
  }

  const movesRaw = Array.isArray(payload.moves) ? payload.moves : [];
  const moves = movesRaw.map(normalizeCampaignMove).filter((m): m is CampaignMove => m !== null);

  const tasksRaw = Array.isArray(payload.tasks) ? payload.tasks : [];
  const tasks = tasksRaw.map(normalizeCampaignTask).filter((t): t is CampaignTask => t !== null);

  const evaluationRaw = payload.evaluation ?? payload.evaluation_result ?? null;
  const evaluation = evaluationRaw ? normalizeCampaignEvaluation(evaluationRaw) : null;

  return { campaign, moves, tasks, evaluation };
}

export function useCampaignDetail(id: string) {
  return useQuery({
    queryKey: campaignKeys.detail(id),
    queryFn: () => fetchCampaignDetail(id),
    enabled: !!id,
  });
}

/* ─── Create Campaign ─────────────────────────────────────────────────────── */

export function useCreateCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: CreateCampaignRequest) => {
      const res = await apiFetch<unknown>("/api/v1/campaigns", {
        method: "POST",
        body: { name: body.name, goal: body.goal ?? "Grow pipeline" },
        auth: true,
      });
      if (!res || typeof res !== "object") {
        throw new Error("Campaign create response is not an object");
      }
      const payload = res as Record<string, unknown>;
      const campaign = normalizeCampaignSummary(payload.campaign ?? payload);
      if (!campaign) {
        throw new Error("Campaign create response missing campaign");
      }
      return campaign;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: campaignKeys.lists() });
    },
  });
}

/* ─── Evaluate Campaign ───────────────────────────────────────────────────── */

export function useEvaluateCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ campaignId, focus }: { campaignId: string; focus?: string }) => {
      const res = await apiFetch<unknown>(`/api/v1/campaigns/${campaignId}/evaluate`, {
        method: "POST",
        body: { focus },
        auth: true,
      });
      if (!res || typeof res !== "object") {
        throw new Error("Evaluation response is not an object");
      }
      const payload = res as Record<string, unknown>;
      const evaluation = normalizeCampaignEvaluation(payload.evaluation ?? payload);
      if (!evaluation) {
        throw new Error("Evaluation response missing evaluation field");
      }
      return evaluation;
    },
    onSuccess: (_, { campaignId }) => {
      queryClient.invalidateQueries({ queryKey: campaignKeys.detail(campaignId) });
      queryClient.invalidateQueries({ queryKey: campaignKeys.evaluations(campaignId) });
    },
  });
}

/* ─── Generate Moves ──────────────────────────────────────────────────────── */

export function useGenerateMoves() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      campaignId,
      context,
      maxMoves,
    }: {
      campaignId: string;
      context?: string;
      maxMoves?: number;
    }) => {
      const res = await apiFetch<unknown>(`/api/v1/campaigns/${campaignId}/moves/generate`, {
        method: "POST",
        body: { context, max_moves: maxMoves },
        auth: true,
      });
      if (!res || typeof res !== "object") {
        throw new Error("Generate moves response is not an object");
      }
      const payload = res as Record<string, unknown>;
      const generatedMoves = Array.isArray(payload.generated_moves) ? payload.generated_moves : [];
      const moves = generatedMoves
        .map(normalizeCampaignMove)
        .filter((m): m is CampaignMove => m !== null);
      return { campaignId, moves, total: moves.length };
    },
    onSuccess: (_, { campaignId }) => {
      queryClient.invalidateQueries({ queryKey: campaignKeys.moves(campaignId) });
      queryClient.invalidateQueries({ queryKey: campaignKeys.detail(campaignId) });
    },
  });
}

/* ─── Campaign Moves ──────────────────────────────────────────────────────── */

async function fetchCampaignMoves(id: string): Promise<CampaignMove[]> {
  const res = await apiFetch<unknown>(`/api/v1/campaigns/${id}/moves`, { auth: true });
  if (!res || typeof res !== "object") return [];
  const payload = res as Record<string, unknown>;
  const movesRaw = Array.isArray(payload.moves) ? payload.moves : [];
  return movesRaw.map(normalizeCampaignMove).filter((m): m is CampaignMove => m !== null);
}

export function useCampaignMoves(id: string) {
  return useQuery({
    queryKey: campaignKeys.moves(id),
    queryFn: () => fetchCampaignMoves(id),
    enabled: !!id,
  });
}

/* ─── Campaign Tasks ──────────────────────────────────────────────────────── */

async function fetchCampaignTasks(id: string): Promise<CampaignTask[]> {
  const res = await apiFetch<unknown>(`/api/v1/campaigns/${id}/tasks`, { auth: true });
  if (!res || typeof res !== "object") return [];
  const payload = res as Record<string, unknown>;
  const tasksRaw = Array.isArray(payload.tasks) ? payload.tasks : [];
  return tasksRaw.map(normalizeCampaignTask).filter((t): t is CampaignTask => t !== null);
}

export function useCampaignTasks(id: string) {
  return useQuery({
    queryKey: campaignKeys.tasks(id),
    queryFn: () => fetchCampaignTasks(id),
    enabled: !!id,
  });
}

/* ─── Update Task Status ──────────────────────────────────────────────────── */

export function useUpdateTaskStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      campaignId,
      taskId,
      status,
    }: {
      campaignId: string;
      taskId: string;
      status: string;
    }) => {
      await apiFetch<unknown>(`/api/v1/campaigns/${campaignId}/tasks/${taskId}/status`, {
        method: "PATCH",
        body: { status },
        auth: true,
      });
      return { campaignId, taskId, status };
    },
    onSuccess: (_, { campaignId }) => {
      queryClient.invalidateQueries({ queryKey: campaignKeys.tasks(campaignId) });
      queryClient.invalidateQueries({ queryKey: campaignKeys.detail(campaignId) });
    },
  });
}

/* ─── Update Campaign Status ──────────────────────────────────────────────── */

export function useUpdateCampaignStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      await apiFetch<unknown>(`/api/v1/campaigns/${id}/status`, {
        method: "PATCH",
        body: { status },
        auth: true,
      });
      return { id, status };
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: campaignKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: campaignKeys.lists() });
    },
  });
}
