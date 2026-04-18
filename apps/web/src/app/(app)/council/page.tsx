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
    <div className="session-bars" style={{ height: 16 }}>
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className={`session-bar${i < bars ? " active" : ""}`}
          style={{ height: 4 + i * 2.5 }}
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
      <span
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 9,
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: "0.12em",
          color: isLive ? "var(--amber-war)" : status === "completed" ? "var(--leaf-confirm)" : "var(--muted-foreground)",
        }}
      >
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
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                color: "var(--muted-foreground)",
                marginBottom: 8,
              }}
            >
              Strategic Operations
            </p>
            <h1
              style={{
                fontFamily: "'DM Serif Display', serif",
                fontSize: 40,
                lineHeight: 1,
                margin: 0,
              }}
            >
              Council Archive
            </h1>
            <p
              className="mt-3"
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 10,
                textTransform: "uppercase",
                letterSpacing: "0.14em",
                color: "var(--muted-foreground)",
              }}
            >
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
            className="flex h-12 w-fit items-center whitespace-nowrap gap-2 px-6 transition-all hover:opacity-80 disabled:opacity-50"
            style={{
              background: "var(--foreground)",
              color: "var(--background)",
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 10,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.16em",
            }}
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
          <div className="flex gap-0">
            {(["all", "running", "completed"] as Filter[]).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className="px-4 py-2 transition-all"
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 9,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.14em",
                  background: filter === f ? "var(--foreground)" : "transparent",
                  color: filter === f ? "var(--background)" : "var(--muted-foreground)",
                  border: "1px solid var(--border)",
                  borderLeft: f === "all" ? "1px solid var(--border)" : "none",
                }}
              >
                {f}
              </button>
            ))}
          </div>
          <p
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: "var(--muted-foreground)",
            }}
          >
            Sort: Newest
          </p>
        </div>

        {/* ── Loading ──────────────────────────────────────── */}
        {isLoading && (
          <div className="grid md:grid-cols-2 gap-5">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-48 border border-[var(--border)] animate-pulse bg-[var(--card)] opacity-40" />
            ))}
          </div>
        )}

        {/* ── Error ────────────────────────────────────────── */}
        {error && (
          <div className="border border-[var(--destructive)] p-6 font-mono text-sm text-[var(--destructive)]" style={{ background: "var(--signal-red-dim)" }}>
            Failed to load archives: {error.message}
          </div>
        )}

        {/* ── Session Grid ─────────────────────────────────── */}
        <div className="gsap-reveal grid md:grid-cols-2 gap-5">
          {displaySessions.map((session: any) => {
            const isLive = session.status === "running" || session.status === "streaming" || session.status === "active";
            const dateStr = new Date(session.createdAt).toLocaleDateString("en-IN", {
              day: "numeric", month: "short", year: "numeric",
            });

            return (
              <Link
                key={session.sessionId}
                href={`/council/${session.sessionId}` as Route}
                className="group block border border-[var(--border)] hover:border-[var(--foreground)] transition-all"
                style={{ background: "var(--card)" }}
              >
                {/* Session header */}
                <div className="p-6 border-b border-[var(--border)]">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <IntensityBars sessionType={session.sessionType} />
                      <StatusBadge status={session.status} />
                    </div>
                    <div
                      className="h-9 w-9 border border-[var(--border)] flex items-center justify-center group-hover:bg-[var(--foreground)] group-hover:text-[var(--background)] group-hover:border-[var(--foreground)] transition-all"
                    >
                      <ArrowTopRightIcon className="h-3.5 w-3.5" />
                    </div>
                  </div>

                  {/* Campaign / Session Name */}
                  <h3
                    style={{
                      fontFamily: "'DM Serif Display', serif",
                      fontSize: 22,
                      lineHeight: 1.2,
                      color: "var(--foreground)",
                      margin: 0,
                    }}
                  >
                    {session.campaignId || "Unassigned Campaign"}
                  </h3>
                  <p
                    className="mt-1"
                    style={{
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: 9,
                      textTransform: "uppercase",
                      letterSpacing: "0.12em",
                      color: "var(--muted-foreground)",
                    }}
                  >
                    {session.sessionType.replace(/_/g, " ")}
                  </p>
                </div>

                {/* Meta footer */}
                <div className="flex items-center justify-between px-6 py-3">
                  <div className="flex items-center gap-5">
                    <span
                      className="flex items-center gap-1.5"
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 9,
                        textTransform: "uppercase",
                        letterSpacing: "0.1em",
                        color: "var(--muted-foreground)",
                      }}
                    >
                      <AvatarIcon className="h-3 w-3" />
                      {session.agentCount ?? 12} Agents
                    </span>
                    <span
                      className="flex items-center gap-1.5"
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 9,
                        textTransform: "uppercase",
                        letterSpacing: "0.1em",
                        color: isLive ? "var(--amber-war)" : "var(--muted-foreground)",
                      }}
                    >
                      <ClockIcon className="h-3 w-3" />
                      {session.duration ?? "—"}
                    </span>
                  </div>
                  <span
                    style={{
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: 9,
                      color: "var(--muted-foreground)",
                    }}
                  >
                    {dateStr}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>

        {/* ── Empty State ──────────────────────────────────── */}
        {!isLoading && !error && displaySessions.length === 0 && (
          <div
            className="flex flex-col items-center justify-center py-24 border border-dashed border-[var(--border)]"
          >
            <AvatarIcon className="h-10 w-10 text-[var(--muted-foreground)] mb-6 opacity-30" />
            <p
              style={{
                fontFamily: "'DM Serif Display', serif",
                fontSize: 24,
                color: "var(--foreground)",
                marginBottom: 8,
              }}
            >
              The Chamber is Empty
            </p>
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                textTransform: "uppercase",
                letterSpacing: "0.16em",
                color: "var(--muted-foreground)",
              }}
            >
              Summon a session to begin deliberation.
            </p>
          </div>
        )}

      </GsapBridge>
    </div>
  );
}
