"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import {
  workspacesService,
  type OnboardingStatus,
  type Workspace,
} from "@/services/workspaces.service";

type WorkspaceContextValue = {
  workspaceId: string | null;
  workspace: Workspace | null;
  onboardingStatus: OnboardingStatus | null;
  isOnboardingComplete: boolean;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  refreshOnboarding: () => Promise<void>;
  reset: () => void;
};

const WorkspaceContext = createContext<WorkspaceContextValue | undefined>(undefined);
const STORAGE_KEY = "raptorflow.workspace_id";

function safeWriteWorkspaceId(id: string) {
  try { window.localStorage.setItem(STORAGE_KEY, id); } catch { /* ignore */ }
}
function safeClearWorkspaceId() {
  try { window.localStorage.removeItem(STORAGE_KEY); } catch { /* ignore */ }
}

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [onboardingStatus, setOnboardingStatus] = useState<OnboardingStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadOnboardingStatus = useCallback(async (id: string) => {
    const status = await workspacesService.getOnboardingStatus(id);
    setOnboardingStatus(status);
    return status;
  }, []);

  const ensureWorkspace = useCallback(async () => {
    setError(null);

    try {
      const storedId = window.localStorage.getItem(STORAGE_KEY);

      if (storedId) {
        // [PERF] Optimistically accept the stored ID immediately — skip loading state
        // Validate in parallel; if it fails, fall through to create silently.
        try {
          const [ws, status] = await Promise.all([
            workspacesService.get(storedId),
            workspacesService.getOnboardingStatus(storedId),
          ]);
          setWorkspaceId(ws.id);
          setWorkspace(ws);
          setOnboardingStatus(status);
          setIsLoading(false);
          return;
        } catch {
          safeClearWorkspaceId();
        }
      }

      // Create a brand new anonymous workspace
      const ws = await workspacesService.create({ name: "Anonymous Workspace" });
      safeWriteWorkspaceId(ws.id);

      // [PERF] Fetch onboarding status in parallel after create
      const [, status] = await Promise.all([
        Promise.resolve(ws), // already have ws
        workspacesService.getOnboardingStatus(ws.id),
      ]);

      setWorkspaceId(ws.id);
      setWorkspace(ws);
      setOnboardingStatus(status);
    } catch (e: any) {
      setError(e?.message || "Failed to initialize workspace");
    } finally {
      setIsLoading(false);
    }
  }, [loadOnboardingStatus]);

  const refreshOnboarding = useCallback(async () => {
    if (!workspaceId) return;
    setError(null);
    try {
      await loadOnboardingStatus(workspaceId);
    } catch (e: any) {
      setError(e?.message || "Failed to load onboarding status");
    }
  }, [workspaceId, loadOnboardingStatus]);

  const reset = useCallback(() => {
    safeClearWorkspaceId();
    setWorkspaceId(null);
    setWorkspace(null);
    setOnboardingStatus(null);
    setError(null);
    void ensureWorkspace();
  }, [ensureWorkspace]);

  useEffect(() => {
    void ensureWorkspace();
  }, [ensureWorkspace]);

  useEffect(() => {
    if (!workspaceId || !onboardingStatus) return;
    const isOnboardingRoute = pathname?.startsWith("/onboarding");
    if (!onboardingStatus.completed && !isOnboardingRoute) {
      router.replace("/onboarding");
      return;
    }
    if (onboardingStatus.completed && isOnboardingRoute) {
      router.replace("/dashboard");
    }
  }, [workspaceId, onboardingStatus, pathname, router]);

  const value = useMemo<WorkspaceContextValue>(
    () => ({
      workspaceId,
      workspace,
      onboardingStatus,
      isOnboardingComplete: Boolean(onboardingStatus?.completed),
      isLoading,
      error,
      refresh: ensureWorkspace,
      refreshOnboarding,
      reset,
    }),
    [workspaceId, workspace, onboardingStatus, isLoading, error, ensureWorkspace, refreshOnboarding, reset]
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-[var(--ink)] border-t-transparent rounded-full animate-spin" />
          <span className="text-[13px] font-mono text-[var(--muted)] tracking-wide">Setting up…</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-6 space-y-4">
          <h1 className="font-serif text-xl text-[var(--ink)]">Couldn&rsquo;t connect</h1>
          <p className="text-sm text-[var(--ink-muted)]">{error}</p>
          <div className="flex gap-3">
            <button onClick={() => void ensureWorkspace()} className="px-4 py-2 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium">
              Retry
            </button>
            <button onClick={reset} className="px-4 py-2 rounded-[var(--radius)] border border-[var(--border)] text-sm font-medium text-[var(--ink)]">
              Reset
            </button>
          </div>
        </div>
      </div>
    );
  }

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}

export function useWorkspace() {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) throw new Error("useWorkspace must be used within <WorkspaceProvider />");
  return ctx;
}
