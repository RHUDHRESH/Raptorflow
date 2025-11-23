import { v4 as uuidv4 } from "uuid";
import { supabase } from "../supabase";
import type { PerformancePrediction } from "../../types/api";

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

export const performanceAPI = {
  predictEngagement: (content: string, icp_id: string, channel: string) =>
    http<PerformancePrediction>("/api/v1/analytics/predict/performance", {
      method: "POST",
      body: JSON.stringify({ content, icp_id, channel }),
    }),
};
