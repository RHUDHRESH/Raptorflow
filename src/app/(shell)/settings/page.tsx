"use client";

import { useEffect, useMemo, useState } from "react";
import { notify } from "@/lib/notifications";
import { useWorkspace } from "@/components/workspace/WorkspaceProvider";
import { workspacesService } from "@/services/workspaces.service";

export default function SettingsPage() {
  const { workspaceId, workspace, refresh } = useWorkspace();
  const [name, setName] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (workspace?.name) setName(workspace.name);
  }, [workspace?.name]);

  const hasChanges = useMemo(() => {
    if (!workspace) return false;
    return name.trim() !== "" && name.trim() !== workspace.name;
  }, [name, workspace]);

  async function saveWorkspace() {
    if (!workspaceId) return;
    if (!hasChanges) return;

    setIsSaving(true);
    setError(null);
    try {
      await workspacesService.update(workspaceId, { name: name.trim() });
      await refresh();
      notify.success("Workspace updated");
    } catch (e: any) {
      const message = e?.message || "Failed to save workspace";
      setError(message);
      notify.error(message);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-80px)] bg-[var(--canvas)]">
      <div className="max-w-3xl mx-auto px-8 py-10 space-y-8">
        <header className="space-y-1">
          <h1 className="font-serif text-3xl text-[var(--ink)]">Settings</h1>
          <p className="text-sm text-[var(--ink-muted)]">
            No login, no paywalls. Settings are scoped to your current workspace.
          </p>
        </header>

        <section className="bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius-lg)] p-6 space-y-4">
          <div className="space-y-1">
            <h2 className="font-serif text-lg text-[var(--ink)]">Workspace</h2>
            <p className="text-sm text-[var(--ink-muted)]">
              Workspace id is the tenant boundary. It is sent as{" "}
              <span className="font-mono text-[var(--ink)]">x-workspace-id</span>{" "}
              on API calls.
            </p>
          </div>

          <div className="grid gap-4">
            <label className="grid gap-2">
              <span className="text-sm font-medium text-[var(--ink)]">Name</span>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] text-[var(--ink)]"
                placeholder="Workspace name"
              />
            </label>

            <div className="grid gap-2">
              <span className="text-sm font-medium text-[var(--ink)]">ID</span>
              <div className="px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] font-mono text-xs text-[var(--ink)]">
                {workspaceId}
              </div>
            </div>

            {workspace?.slug ? (
              <div className="grid gap-2">
                <span className="text-sm font-medium text-[var(--ink)]">Slug</span>
                <div className="px-3 py-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--surface)] font-mono text-xs text-[var(--ink)]">
                  {workspace.slug}
                </div>
              </div>
            ) : null}
          </div>

          {error ? (
            <div className="text-sm text-[var(--error)]">{error}</div>
          ) : null}

          <div className="flex items-center gap-3">
            <button
              onClick={() => void saveWorkspace()}
              disabled={!hasChanges || isSaving}
              className="px-4 py-2 rounded-[var(--radius)] bg-[var(--ink)] text-white text-sm font-medium disabled:opacity-50"
            >
              {isSaving ? "Saving..." : "Save"}
            </button>
            {!hasChanges ? (
              <span className="text-xs text-[var(--ink-muted)]">No changes</span>
            ) : null}
          </div>
        </section>
      </div>
    </div>
  );
}

