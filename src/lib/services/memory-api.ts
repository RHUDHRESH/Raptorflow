import { v4 as uuidv4 } from "uuid";
import { supabase } from "../supabase";
import type { MemoryContext } from "../../types/api";

const API_URL =
  (import.meta as any)?.env?.VITE_API_URL ||
  (import.meta as any)?.env?.NEXT_PUBLIC_API_URL ||
  "";

async function getAuthHeaders() {
  const {
    data: { session },
  } = await supabase.auth.getSession();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Correlation-ID": uuidv4(),
  };

  if (session?.access_token) {
    headers.Authorization = `Bearer ${session.access_token}`;
  }

  return headers;
}

async function http<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { ...headers, ...(options.headers as Record<string, string>) },
  });

  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || `Request failed: ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export const memoryAPI = {
  rememberContext: (
    workspace_id: string,
    key: string,
    value: unknown,
    metadata?: Record<string, unknown>,
  ) =>
    http<MemoryContext>("/api/v1/memory/remember", {
      method: "POST",
      body: JSON.stringify({ workspace_id, key, value, metadata }),
    }),

  recallContext: (workspace_id: string, key: string) =>
    http<MemoryContext>(`/api/v1/memory/recall/${workspace_id}/${key}`),

  searchMemory: (workspace_id: string, query: string, top_k?: number) => {
    const params = new URLSearchParams({ query });
    if (top_k) params.append("top_k", top_k.toString());
    return http<MemoryContext>(`/api/v1/memory/search/${workspace_id}?${params.toString()}`, {
      method: "POST",
    });
  },

  learnFromFeedback: (agent_name: string, feedback: unknown, workspace_id: string) =>
    http<{ status: string }>("/api/v1/memory/feedback", {
      method: "POST",
      body: JSON.stringify({ agent_name, feedback, workspace_id }),
    }),

  getContext: (workspace_id: string, task_type?: string) =>
    http<MemoryContext>("/api/v1/memory/context", {
      method: "POST",
      body: JSON.stringify({ workspace_id, task_type }),
    }),
};
