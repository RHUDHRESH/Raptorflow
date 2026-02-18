"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { HttpError } from "@/services/http";
import { useAuthStore } from "@/stores/authStore";
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
  try {
    window.localStorage.setItem(STORAGE_KEY, id);
  } catch {
    // If storage is blocked, we still keep it in-memory for this session.
  }
}

function safeClearWorkspaceId() {
  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    // noop
  }
}

export function WorkspaceProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { session, loading: authLoading, initialized: authInitialized } = useAuthStore();

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
    if (!authInitialized || authLoading) {
      return;
    }

    if (!session?.user) {
      setWorkspaceId(null);
      setWorkspace(null);
      setOnboardingStatus(null);
      setIsLoading(false);
      safeClearWorkspaceId();
      router.replace("/login");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const { workspace: ws } = await workspacesService.getDefaultForCurrentUser();
      await workspacesService.selectForCurrentUser({ workspace_id: ws.id });
      safeWriteWorkspaceId(ws.id);
      setWorkspaceId(ws.id);
      setWorkspace(ws);
      await loadOnboardingStatus(ws.id);
    } catch (e: any) {
      if (e instanceof HttpError && e.status === 401) {
        safeClearWorkspaceId();
        setWorkspaceId(null);
        setWorkspace(null);
        setOnboardingStatus(null);
        router.replace("/login");
        return;
      }
      setError(e?.message || "Failed to initialize workspace");
    } finally {
      setIsLoading(false);
    }
  }, [authInitialized, authLoading, loadOnboardingStatus, router, session?.user]);

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
    // Immediately attempt to create a fresh one.
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
    [
      workspaceId,
      workspace,
      onboardingStatus,
      isLoading,
      error,
      ensureWorkspace,
      refreshOnboarding,
      reset,
    ]
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-[var(--ink)] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-[var(--muted)]">Preparing workspace...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[var(--canvas)] flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-6 space-y-4">
          <div className="space-y-1">
            <h1 className="font-serif text-xl text-[var(--ink)]">Workspace initialization failed</h1>
            <p className="text-sm text-[var(--ink-muted)]">{error}</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => void ensureWorkspace()}
              className="px-4 py-2 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium"
            >
              Retry
            </button>
            <button
              onClick={reset}
              className="px-4 py-2 rounded-[var(--radius)] border border-[var(--border)] text-sm font-medium text-[var(--ink)]"
            >
              Reset Local Workspace
            </button>
          </div>
          <div className="text-xs text-[var(--ink-muted)] font-mono">
            Expected backend: <span className="text-[var(--ink)]">/api/proxy/workspaces</span>
          </div>
        </div>
      </div>
    );
  }

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}

export function useWorkspace() {
  const ctx = useContext(WorkspaceContext);
  if (!ctx) {
    throw new Error("useWorkspace must be used within <WorkspaceProvider />");
  }
  return ctx;
}
