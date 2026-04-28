"use client";

import Link from "next/link";
import type { Route } from "next";
import { CouncilOrchestrationRun } from "@/lib/api";

interface Props {
  runs: CouncilOrchestrationRun[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  isLoading: boolean;
}

function statusColor(status: string): string {
  if (status === "completed") return "var(--leaf-confirm)";
  if (status === "failed") return "var(--destructive)";
  if (
    status === "queued" ||
    status === "building_context" ||
    status === "forming_positions" ||
    status === "debating" ||
    status === "synthesizing"
  )
    return "var(--amber)";
  return "var(--ink-400)";
}

function statusDot(status: string): string {
  if (
    status === "completed" ||
    status === "queued" ||
    status === "building_context" ||
    status === "forming_positions" ||
    status === "debating" ||
    status === "synthesizing"
  )
    return "●";
  if (status === "failed") return "●";
  return "●";
}

export function CouncilRunList({ runs, selectedId, onSelect, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-16 card-elevated p-4 animate-pulse bg-[var(--paper-150)]" />
        ))}
      </div>
    );
  }

  if (runs.length === 0) {
    return (
      <div className="card-elevated p-6 text-center">
        <p className="mono-label text-[var(--ink-400)]">No council runs yet</p>
        <p className="mono-label text-[var(--ink-300)] mt-1">Create your first run above</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {runs.map((run) => {
        const roster: string[] = Array.isArray(run.avatar_roster)
          ? run.avatar_roster
          : typeof run.avatar_roster === "object" && run.avatar_roster !== null
            ? Object.keys(run.avatar_roster)
            : [];
        const isSelected = run.council_run_id === selectedId;
        const date = new Date(run.created_at).toLocaleDateString("en-IN", {
          day: "numeric",
          month: "short",
          hour: "2-digit",
          minute: "2-digit",
        });

        return (
          <button
            key={run.council_run_id}
            onClick={() => onSelect(run.council_run_id)}
            className="w-full text-left card-elevated p-4 border transition-all duration-200 hover:border-[var(--primary)]/30"
            style={{
              borderColor: isSelected ? "var(--primary)" : "var(--border)",
              background: isSelected ? "var(--primary)" : undefined,
            }}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span style={{ color: statusColor(run.status) }}>{statusDot(run.status)}</span>
                <span className="mono-label" style={{ color: statusColor(run.status) }}>
                  {run.status}
                </span>
              </div>
              <span className="mono-label text-[var(--ink-400)]">{date}</span>
            </div>
            <p className="text-sm font-medium truncate">{run.request_summary}</p>
            <div className="flex items-center gap-2 mt-1">
              <span className="mono-label text-[var(--ink-400)] text-[10px]">
                {roster.length} avatars
              </span>
              {run.error_message && (
                <span className="mono-label text-[var(--destructive)] text-[10px]">
                  Error: {run.error_message}
                </span>
              )}
            </div>
          </button>
        );
      })}
      <div className="pt-2 text-center">
        <Link
          href="/council"
          className="mono-label text-[var(--ink-400)] hover:text-[var(--ink-900)] text-[10px]"
        >
          View all council sessions →
        </Link>
      </div>
    </div>
  );
}
