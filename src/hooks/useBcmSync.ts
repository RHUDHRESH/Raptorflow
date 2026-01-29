"use client";

import { useCallback, useEffect, useRef } from "react";
import { useBcmStore } from "@/stores/bcmStore";

type FetchOptions = {
  tier?: "tier0" | "tier1" | "tier2";
};

export function useBcmSync(workspaceId?: string) {
  const inFlightRef = useRef(false);
  const {
    manifest,
    status,
    lastFetchedAt,
    staleReason,
    error,
    fetchLatest,
    ensureLatest,
    setActiveWorkspace,
    rebuild,
    markStale,
  } = useBcmStore();

  const refresh = useCallback(
    async (options?: FetchOptions) => {
      if (!workspaceId || inFlightRef.current) return;
      inFlightRef.current = true;
      try {
        await fetchLatest(workspaceId, options);
      } finally {
        inFlightRef.current = false;
      }
    },
    [workspaceId, fetchLatest]
  );

  useEffect(() => {
    setActiveWorkspace(workspaceId ?? null);
    if (!workspaceId) return;
    ensureLatest(workspaceId).catch(() => {
      // errors captured in store state
    });
  }, [workspaceId, ensureLatest, setActiveWorkspace]);

  const rebuildNow = useCallback(
    async (force = false) => {
      if (!workspaceId) {
        throw new Error("Workspace ID is required to rebuild BCM");
      }
      return rebuild(workspaceId, force);
    },
    [workspaceId, rebuild]
  );

  return {
    manifest,
    status,
    lastFetchedAt,
    staleReason,
    error,
    refresh,
    rebuild: rebuildNow,
    markStale,
    hasWorkspace: Boolean(workspaceId),
  };
}
