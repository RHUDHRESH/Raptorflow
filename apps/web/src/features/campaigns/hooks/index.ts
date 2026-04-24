"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";

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
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ campaignId, focus }: { campaignId: string; focus?: string }) => {
      return apiFetch<{
        campaign_id: string;
        evaluation: {
          overall_score: number;
          strengths: string[];
          weaknesses: string[];
          opportunities: string[];
          threats: string[];
          recommendations: string[];
        };
      }>(`/api/v1/campaigns/${campaignId}/evaluate`, {
        method: "POST",
        body: { focus },
        auth: true,
      });
    },
    onSuccess: (_, { campaignId }) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId] });
    },
  });
}

export function useGenerateMoves() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      campaignId,
      context,
      maxMoves,
    }: {
      campaignId: string;
      context?: string;
      maxMoves?: number;
    }) => {
      return apiFetch<{
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
      }>(`/api/v1/campaigns/${campaignId}/moves/generate`, {
        method: "POST",
        body: { context, max_moves: maxMoves },
        auth: true,
      });
    },
    onSuccess: (_, { campaignId }) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId] });
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId, "moves"] });
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
