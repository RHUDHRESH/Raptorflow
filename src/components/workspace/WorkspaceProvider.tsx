"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { HttpError } from "@/services/http";
import { workspacesService, type Workspace } from "@/services/workspaces.service";

type WorkspaceContextValue = {
  workspaceId: string | null;
  workspace: Workspace | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  reset: () => void;
};

const WorkspaceContext = createContext<WorkspaceContextValue | undefined>(undefined);

const STORAGE_KEY = "raptorflow.workspace_id";

function safeReadWorkspaceId(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    return value && value.trim().length > 0 ? value : null;
  } catch {
    return null;
  }
}

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
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const ensureWorkspace = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const storedId = safeReadWorkspaceId();
    if (storedId) {
      try {
        const ws = await workspacesService.get(storedId);
        setWorkspaceId(ws.id);
        setWorkspace(ws);
        setIsLoading(false);
        return;
      } catch (e) {
        // Only clear the stored ID if it is actually invalid.
        // If the backend is down/unreachable, surfacing the error is the correct behavior.
        if (e instanceof HttpError && (e.status === 400 || e.status === 404)) {
          safeClearWorkspaceId();
          setWorkspaceId(null);
          setWorkspace(null);
        } else {
          setError((e as any)?.message || "Failed to load workspace");
          setIsLoading(false);
          return;
        }
      }
    }

    try {
      const suffix = new Date().toISOString().slice(0, 10);
      const ws = await workspacesService.create({ name: `Workspace ${suffix}` });
      safeWriteWorkspaceId(ws.id);
      setWorkspaceId(ws.id);
      setWorkspace(ws);
    } catch (e: any) {
      setError(e?.message || "Failed to initialize workspace");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    safeClearWorkspaceId();
    setWorkspaceId(null);
    setWorkspace(null);
    setError(null);
    // Immediately attempt to create a fresh one.
    void ensureWorkspace();
  }, [ensureWorkspace]);

  useEffect(() => {
    void ensureWorkspace();
  }, [ensureWorkspace]);

  const value = useMemo<WorkspaceContextValue>(
    () => ({
      workspaceId,
      workspace,
      isLoading,
      error,
      refresh: ensureWorkspace,
      reset,
    }),
    [workspaceId, workspace, isLoading, error, ensureWorkspace, reset]
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
            Expected backend: <span className="text-[var(--ink)]">/api/proxy/v1/workspaces</span>
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
