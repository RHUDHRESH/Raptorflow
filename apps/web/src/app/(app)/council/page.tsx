"use client";

import * as React from "react";
import { useState } from "react";
import type { Route } from "next";
import Link from "next/link";
import {
  PlusIcon,
  ClockIcon,
  ArrowTopRightIcon,
  AvatarIcon,
  DotFilledIcon,
} from "@radix-ui/react-icons";
import { useCouncilSessions, useStartCouncilSession } from "@/hooks/use-council";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/cn";
import { Users } from "lucide-react";

/* ─── Session Type → Intensity Bars ──────────────────────────── */
const SESSION_TYPE_INTENSITY: Record<string, number> = {
  strategic_review:   2,
  creative_brief:     3,
  council_war_room:   5,
  campaign_kickoff:   3,
  performance_review: 2,
  replanning:         4,
};

function IntensityBars({ sessionType }: { sessionType: string }): React.ReactElement {
  const bars = SESSION_TYPE_INTENSITY[sessionType] ?? 2;
  return (
    <div className="flex items-end gap-[3px] h-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className={cn(
            "w-[3px] rounded-full transition-all duration-300",
            i < bars ? "bg-[var(--primary)]" : "bg-[var(--paper-300)]"
          )}
          style={{ height: `${4 + i * 2.5}px` }}
        />
      ))}
    </div>
  );
}

/* ─── Status Badge ────────────────────────────────────────────── */
function StatusBadge({ status }: { status: string }): React.ReactElement {
  const isLive = status === "running" || status === "streaming";
  return (
    <div className="flex items-center gap-1.5">
      {isLive && <span className="status-dot-live" />}
      <span className={cn(
        "mono-label",
        isLive ? "text-[var(--primary)]" : status === "completed" ? "text-[var(--leaf-confirm)]" : "text-[var(--ink-400)]"
      )}>
        {status}
      </span>
    </div>
  );
}

/* ─── Filter options ──────────────────────────────────────────── */
type Filter = "all" | "running" | "completed";

/* ─── Council Page ────────────────────────────────────────────── */
export default function CouncilPage(): React.ReactElement {
  const { data: sessions, isLoading, error } = useCouncilSessions();
  const startSession = useStartCouncilSession();
  const [filter, setFilter] = useState<Filter>("all");

  const filtered = sessions?.filter((s) => {
    if (filter === "all") return true;
    if (filter === "running") return s.status === "running" || s.status === "streaming";
    if (filter === "completed") return s.status === "completed";
    return true;
  });

  const displaySessions = filtered ?? [];

  return (
    <div className="flex flex-col gap-8 py-2">
      <GsapBridge stagger className="flex flex-col gap-8">

        {/* ── Header ──────────────────────────────────────── */}
        <header className="gsap-reveal flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-[var(--border)] pb-8">
          <div>
            <p className="eyebrow mb-2">Strategic Operations</p>
            <h1 className="display-md">Council Archive</h1>
            <p className="mono-label mt-2">
              {sessions?.length ?? 0} Historical Deliberations
            </p>
          </div>

          <button
            onClick={() =>
              startSession.mutate({
                campaignId: "campaign-001",
                sessionType: "strategic_review",
                question: "Review campaign-001 and recommend the next best strategic move.",
              })
            }
            disabled={startSession.isPending}
            className="btn-mono h-12 px-6 disabled:opacity-50"
          >
            {startSession.isPending ? (
              "Summoning..."
            ) : (
              <>
                <PlusIcon className="h-4 w-4" />
                Summon Council
              </>
            )}
          </button>
        </header>

        {/* ── Filter Bar ──────────────────────────────────── */}
        <div className="gsap-reveal flex items-center justify-between">
          <div className="flex gap-0 bg-[var(--paper-150)] rounded-[var(--radius)] p-0.5">
            {(["all", "running", "completed"] as Filter[]).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={cn(
                  "px-4 py-2 transition-all duration-200 mono-label rounded-[var(--radius-sm)]",
                  filter === f
                    ? "bg-[var(--ink-900)] text-white shadow-sm"
                    : "text-[var(--ink-500)] hover:text-[var(--ink-900)]"
                )}
              >
                {f}
              </button>
            ))}
          </div>
          <p className="mono-label">Sort: Newest</p>
        </div>

        {/* ── Loading ──────────────────────────────────────── */}
        {isLoading && (
          <div className="grid md:grid-cols-2 gap-5">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-48 card-elevated space-y-4 p-6">
                <div className="flex items-center gap-3">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-4 w-16" />
                </div>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            ))}
          </div>
        )}

        {/* ── Error ────────────────────────────────────────── */}
        {error && (
          <div className="card-elevated p-6 border-[var(--destructive)] bg-[var(--destructive-wash)]">
            <p className="mono-label text-[var(--destructive)]">
              Failed to load archives: {error.message}
            </p>
          </div>
        )}

        {/* ── Empty ────────────────────────────────────────── */}
        {!isLoading && !error && displaySessions.length === 0 && (
          <EmptyState
            icon={Users}
            title="No council sessions yet"
            description="Ask your council a strategic question to begin."
          />
        )}

        {/* ── Session Grid ─────────────────────────────────── */}
        {!isLoading && !error && displaySessions.length > 0 && (
          <div className="gsap-reveal grid md:grid-cols-2 gap-5">
            {displaySessions.map((session: any, index: number) => {
              const isLive = session.status === "running" || session.status === "streaming" || session.status === "active";
              const dateStr = new Date(session.createdAt).toLocaleDateString("en-IN", {
                day: "numeric", month: "short", year: "numeric",
              });

              return (
                <Link
                  key={session.sessionId}
                  href={`/council/${session.sessionId}` as Route}
                  className="group block card-elevated hover:border-[var(--ink-900)]/20 transition-all duration-300"
                  style={{ animationDelay: `${index * 80}ms` }}
                >
                  {/* Session header */}
                  <div className="p-6 border-b border-[var(--border)]">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <IntensityBars sessionType={session.sessionType} />
                        <StatusBadge status={session.status} />
                      </div>
                      <div className="h-9 w-9 border border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center group-hover:bg-[var(--ink-900)] group-hover:text-white group-hover:border-[var(--ink-900)] transition-all duration-300">
                        <ArrowTopRightIcon className="h-3.5 w-3.5" />
                      </div>
                    </div>

                    {/* Campaign / Session Name */}
                    <h3 className="h2">
                      {session.campaignId || "Unassigned Campaign"}
                    </h3>
                    <p className="mono-label mt-1">
                      {session.sessionType.replace(/_/g, " ")}
                    </p>
                    <p className="mono-label mt-2">
                      ID {session.sessionId}
                    </p>
                  </div>

                  {/* Meta footer */}
                  <div className="flex items-center justify-between px-6 py-3">
                    <div className="flex items-center gap-5">
                      <span className="flex items-center gap-1.5 mono-label">
                        <AvatarIcon className="h-3 w-3" />
                        {session.agentCount ?? 12} Agents
                      </span>
                      <span className={cn(
                        "flex items-center gap-1.5 mono-label",
                        isLive && "text-[var(--primary)]"
                      )}>
                        <ClockIcon className="h-3 w-3" />
                        {session.duration ?? "—"}
                      </span>
                    </div>
                    <span className="mono-label">{dateStr}</span>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </GsapBridge>
    </div>
  );
}
