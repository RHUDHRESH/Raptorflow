"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiFetch } from "@/lib/api";

export interface MuseMessage {
  id: string;
  role: string;
  content: string;
  route: string | null;
  created_at: string;
}

export interface MuseConversation {
  id: string;
  title: string;
  updated_at: string;
  created_at: string;
  message_count: number;
  last_message: { role: string; content: string; route: string | null } | null;
}

export interface ChatResponse {
  response: string;
  route: string;
  conversationId: string;
  messageId: string;
  sessionId?: string;
}

async function fetchConversations(): Promise<MuseConversation[]> {
  return apiFetch<MuseConversation[]>("/api/v1/muse", { auth: true });
}

async function fetchConversation(
  id: string,
): Promise<MuseConversation & { messages: MuseMessage[] }> {
  return apiFetch<MuseConversation & { messages: MuseMessage[] }>(`/api/v1/muse/${id}`, {
    auth: true,
  });
}

export function useMuseConversations() {
  return useQuery({
    queryKey: ["museConversations"],
    queryFn: fetchConversations,
  });
}

export function useMuseConversation(id: string) {
  return useQuery({
    queryKey: ["museConversations", id],
    queryFn: () => fetchConversation(id),
    enabled: !!id,
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (title?: string) =>
      apiFetch<{ id: string; title: string }>("/api/v1/muse", {
        method: "POST",
        body: { title },
        auth: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["museConversations"] });
    },
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ conversationId, message }: { conversationId: string; message: string }) =>
      apiFetch<ChatResponse>(`/api/v1/muse/${conversationId}/messages`, {
        method: "POST",
        body: { message },
        auth: true,
      }),
    onSuccess: (_, { conversationId }) => {
      queryClient.invalidateQueries({ queryKey: ["museConversations", conversationId] });
      queryClient.invalidateQueries({ queryKey: ["museConversations"] });
    },
  });
}

export function usePatchConversation() {
  return useMutation({
    mutationFn: ({ id, title }: { id: string; title: string }) => {
      throw new ApiError(501, "muse_conversation_patch_not_implemented_in_rust");
    },
  });
}
