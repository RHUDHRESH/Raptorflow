"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ApiError, appFetch } from "@/lib/api";

export interface CampaignListItem {
  id: string;
  title: string;
  brief: string;
  status: string;
  goal: string | null;
  budget: string | null;
  timeframe: string | null;
  evaluation_result: Record<string, unknown> | null;
  evaluated_at: string | null;
  move_count: number;
  created_at: string;
}

export interface CampaignMoveTask {
  id: string;
  title: string;
  description: string | null;
  status: string;
  due_date: string | null;
}

export interface CampaignMove {
  id: string;
  title: string;
  description: string;
  channel: string;
  priority: number;
  status: string;
  tasks: CampaignMoveTask[];
}

export interface CampaignDetail extends CampaignListItem {
  updated_at: string;
  moves: CampaignMove[];
}

export interface EvaluateResponse {
  evaluation: {
    score: number;
    summary: string;
    strengths: string[];
    weaknesses: string[];
    icp_fit: string;
    suggested_goal: string;
    recommended_channels: string[];
    budget_assessment: string;
  };
  evaluatedAt: string;
}

async function fetchCampaigns(): Promise<CampaignListItem[]> {
  return appFetch<CampaignListItem[]>("/api/campaigns", { auth: true });
}

async function fetchCampaign(id: string): Promise<CampaignDetail> {
  return appFetch<CampaignDetail>(`/api/campaigns/${id}`, { auth: true });
}

export function useCampaigns() {
  return useQuery({
    queryKey: ["campaigns"],
    queryFn: fetchCampaigns,
  });
}

export function useCampaign(id: string) {
  return useQuery({
    queryKey: ["campaigns", id],
    queryFn: () => fetchCampaign(id),
    enabled: !!id,
  });
}

export function useCreateCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: {
      title: string;
      brief: string;
      goal?: string;
      budget?: string;
      timeframe?: string;
    }) => {
      return appFetch<{ id: string }>("/api/campaigns", {
        method: "POST",
        body,
        auth: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
    },
  });
}

export function useEvaluateCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (campaignId: string) =>
      appFetch<EvaluateResponse>(`/api/campaigns/${campaignId}/evaluate`, {
        method: "POST",
        auth: true,
      }),
    onSuccess: (_, campaignId) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId] });
    },
  });
}

export function useGenerateMoves() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (campaignId: string) =>
      appFetch<{ moves: CampaignMove[] }>(`/api/campaigns/${campaignId}/moves/generate`, {
        method: "POST",
        auth: true,
      }),
    onSuccess: (_, campaignId) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId] });
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      campaignId,
      moveId,
      taskId,
      status,
    }: {
      campaignId: string;
      moveId: string;
      taskId: string;
      status: string;
    }) =>
      appFetch<{ id: string; status: string }>(`/api/campaigns/${campaignId}/moves/${moveId}/tasks/${taskId}`, {
        method: "PATCH",
        body: { status },
        auth: true,
      }),
    onSuccess: (_, { campaignId }) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId] });
    },
  });
}

export function usePatchCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      ...body
    }: {
      id: string;
      title?: string;
      brief?: string;
      status?: string;
      goal?: string;
      budget?: string;
      timeframe?: string;
    }) =>
      appFetch<Record<string, unknown>>(`/api/campaigns/${id}`, {
        method: "PATCH",
        body,
        auth: true,
      }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", id] });
    },
  });
}
