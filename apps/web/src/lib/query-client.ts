"use client";

import { QueryClient } from "@tanstack/react-query";

let browserQueryClient: QueryClient | undefined;

export function getQueryClient(): QueryClient {
  if (typeof window === "undefined") {
    return new QueryClient();
  }

  browserQueryClient ??= new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        refetchOnWindowFocus: false,
      },
    },
  });

  return browserQueryClient;
}
