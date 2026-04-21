"use client";

import type * as React from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { getQueryClient } from "@/lib/query-client";
import { ToastProvider } from "@/components/ui/toast";
import { ReactLenis } from "lenis/react";

export function AppProviders({ children }: { children: React.ReactNode }): React.ReactElement {
  const queryClient = getQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <ReactLenis root options={{ duration: 1.1, smoothWheel: true }}>
          {children}
        </ReactLenis>
      </ToastProvider>
    </QueryClientProvider>
  );
}
