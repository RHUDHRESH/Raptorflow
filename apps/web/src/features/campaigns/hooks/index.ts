"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiFetch } from "@/lib/api";

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
  return apiFetch<CampaignListItem[]>("/api/v1/campaigns", { auth: true });
}

async function fetchCampaign(id: string): Promise<CampaignDetail> {
  return apiFetch<CampaignDetail>(`/api/v1/campaigns/${id}`, { auth: true });
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
      return apiFetch<{ id: string }>("/api/v1/campaigns", {
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
  return useMutation({
    mutationFn: (_campaignId: string) => {
      throw new ApiError(501, "campaign_evaluate_not_implemented_in_rust");
    },
  });
}

export function useGenerateMoves() {
  return useMutation({
    mutationFn: (_campaignId: string) => {
      throw new ApiError(501, "campaign_generate_moves_not_implemented_in_rust");
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      campaignId,
      taskId,
      status,
    }: {
      campaignId: string;
      taskId: string;
      status: string;
      moveId?: string;
    }) =>
      apiFetch<{ id: string; status: string }>(
        `/api/v1/campaigns/${campaignId}/tasks/${taskId}/status`,
        {
          method: "PATCH",
          body: { status },
          auth: true,
        },
      ),
    onSuccess: (_, { campaignId }) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId] });
    },
  });
}

export function usePatchCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      apiFetch<Record<string, unknown>>(`/api/v1/campaigns/${id}/status`, {
        method: "PATCH",
        body: { status },
        auth: true,
      }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", id] });
    },
  });
}
