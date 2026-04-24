"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import type { HealthResponse } from "@raptorflow/contracts";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiFetch<HealthResponse>("/api/v1/health", { auth: true }),
    staleTime: 30_000,
    retry: false,
  });
}
