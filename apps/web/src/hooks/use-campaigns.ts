"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { campaignsApi } from "@/lib/api";
import type { Campaign, CreateCampaignRequest, CreateMoveRequest, CreateTaskRequest, CreateBriefRequest } from "@/lib/api";

export function useCampaigns() {
  return useQuery({
    queryKey: ["campaigns"],
    queryFn: () => campaignsApi.list(),
  });
}

export function useCampaign(id: string) {
  return useQuery({
    queryKey: ["campaigns", id],
    queryFn: () => campaignsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateCampaign() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateCampaignRequest) => campaignsApi.create(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
    },
  });
}

export function useUpdateCampaignStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: Campaign["status"] }) =>
      campaignsApi.updateStatus(id, status),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
      queryClient.invalidateQueries({ queryKey: ["campaigns", id] });
    },
  });
}

export function useCampaignMoves(id: string) {
  return useQuery({
    queryKey: ["campaigns", id, "moves"],
    queryFn: () => campaignsApi.getMoves(id),
    enabled: !!id,
  });
}

export function useCreateMove() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ campaignId, body }: { campaignId: string; body: CreateMoveRequest }) =>
      campaignsApi.createMove(campaignId, body),
    onSuccess: (_, { campaignId }) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId, "moves"] });
    },
  });
}

export function useCampaignTasks(id: string) {
  return useQuery({
    queryKey: ["campaigns", id, "tasks"],
    queryFn: () => campaignsApi.getTasks(id),
    enabled: !!id,
  });
}

export function useUpdateTaskStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ campaignId, taskId, status }: { campaignId: string; taskId: string; status: string }) =>
      campaignsApi.updateTaskStatus(campaignId, taskId, status),
    onSuccess: (_, { campaignId }) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId, "tasks"] });
    },
  });
}

export function useCampaignBrief(id: string) {
  return useQuery({
    queryKey: ["campaigns", id, "brief"],
    queryFn: () => campaignsApi.getBrief(id),
    enabled: !!id,
  });
}

export function useCreateBrief() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ campaignId, body }: { campaignId: string; body: CreateBriefRequest }) =>
      campaignsApi.createBrief(campaignId, body),
    onSuccess: (_, { campaignId }) => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId, "brief"] });
    },
  });
}
