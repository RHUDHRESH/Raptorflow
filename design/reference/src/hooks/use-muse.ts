"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { museApi } from "@/lib/api";
import type { MusePromptRequest } from "@/lib/api";

export function useMuseConversations() {
  return useQuery({
    queryKey: ["muse", "conversations"],
    queryFn: () => museApi.listConversations(),
  });
}

export function useMuseConversation(id: string) {
  return useQuery({
    queryKey: ["muse", "conversations", id],
    queryFn: () => museApi.getConversation(id),
    enabled: !!id,
  });
}

export function useMuseMessages(conversationId: string) {
  return useQuery({
    queryKey: ["muse", "conversations", conversationId, "messages"],
    queryFn: () => museApi.getMessages(conversationId),
    enabled: !!conversationId,
  });
}

export function useSubmitMusePrompt() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: MusePromptRequest) => museApi.submitPrompt(body),
    onSuccess: (_, { conversationId }) => {
      if (conversationId) {
        queryClient.invalidateQueries({
          queryKey: ["muse", "conversations", conversationId, "messages"],
        });
      }
      queryClient.invalidateQueries({ queryKey: ["muse", "conversations"] });
    },
  });
}
