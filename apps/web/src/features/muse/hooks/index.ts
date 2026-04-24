"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ApiError, appFetch } from "@/lib/api";

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
  return appFetch<MuseConversation[]>("/api/muse/conversations", { auth: true });
}

async function fetchConversation(
  id: string,
): Promise<MuseConversation & { messages: MuseMessage[] }> {
  return appFetch<MuseConversation & { messages: MuseMessage[] }>(`/api/muse/conversations/${id}`, { auth: true });
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
      appFetch<{ id: string; title: string }>("/api/muse/conversations", {
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
      appFetch<ChatResponse>(`/api/muse/conversations/${conversationId}/chat`, {
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
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, title }: { id: string; title: string }) =>
      appFetch<Record<string, unknown>>(`/api/muse/conversations/${id}`, {
        method: "PATCH",
        body: { title },
        auth: true,
      }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["museConversations", id] });
    },
  });
}
