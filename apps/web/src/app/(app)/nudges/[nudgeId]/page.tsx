"use client";

import type * as React from "react";
import { use } from "react";
import type { Route } from "next";
import Link from "next/link";
import {
  ArrowLeftIcon,
  BellIcon,
  LightningBoltIcon,
  ChatBubbleIcon,
  EyeOpenIcon,
  ArchiveIcon,
} from "@radix-ui/react-icons";
import { useOfficeStore } from "@/state/office-store";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AGENT_MAP } from "@/lib/agents";
import { AgentPill } from "@/components/ui/agent-portrait";

const NUDGE_TYPES: Record<
  string,
  { label: string; description: string; severity: string; action: string }
> = {
  "major-competitor-shift": {
    label: "Strategic Directive",
    description:
      "A major competitor has shifted their positioning or launched a new campaign. This requires an immediate Council review of our Move 3 creative.",
    severity: "critical",
    action: "Review Council Rationale",
  },
  "budget-underutilization": {
    label: "Media Alert",
    description:
      "Campaign budget is underutilized by more than 20% this week. Performance Node suggests scaling LinkedIn spend.",
    severity: "warning",
    action: "Update Budget Allocation",
  },
  "opportunity-detected": {
    label: "Growth Signal",
    description:
      "New ICP segment identified based on recent conversion data. High salience match for our 'Identity' narrative.",
    severity: "info",
    action: "Draft Campaign Brief",
  },
};

export default function NudgeDetailPage({
  params,
}: {
  params: Promise<{ nudgeId: string }>;
}): React.ReactElement {
  const { nudgeId } = use(params);
  const typeKey =
    Object.keys(NUDGE_TYPES).find((k) => nudgeId.includes(k)) || "opportunity-detected";
  const nudge = NUDGE_TYPES[typeKey];
  const eventLog = useOfficeStore((s) => s.eventLog);
  const strategist = AGENT_MAP.get("strategist");

  const relatedEvents = eventLog
    .filter(
      (e) =>
        (e.type || e.eventType) === "intel_alert_received" ||
        (e.type || e.eventType) === "task_missed_notification",
    )
    .slice(0, 5);

  return (
    <div className="flex flex-col gap-8 py-2">
      {/* ── Back nav ──────────────────────────────────── */}
      <Link
        href="/nudges"
        className="flex items-center gap-2 mb-2 hover:underline w-fit"
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 9,
          textTransform: "uppercase",
          letterSpacing: "0.16em",
          color: "var(--muted-foreground)",
        }}
      >
        <ArrowLeftIcon className="h-3 w-3" />
        Nudge Center
      </Link>

      {/* ── Header ────────────────────────────────────────── */}
      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <BellIcon className="h-4 w-4" style={{ color: "var(--amber-war)" }} />
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                color: "var(--muted-foreground)",
              }}
            >
              Nudge Reference: {nudgeId.toUpperCase()}
            </p>
          </div>
          <h1
            style={{
              fontFamily: "'DM Serif Display', serif",
              fontSize: 40,
              lineHeight: 1,
              margin: 0,
            }}
          >
            {nudge.label}
          </h1>
        </div>

        <div className="flex flex-col items-end gap-2 text-right">
          <Badge
            className={
              nudge.severity === "critical"
                ? "bg-red-500/10 text-red-500 border-red-500/20"
                : nudge.severity === "warning"
                  ? "bg-amber-500/10 text-amber-500 border-amber-500/20"
                  : "bg-blue-500/10 text-blue-500 border-blue-500/20"
            }
          >
            {nudge.severity} priority
          </Badge>
          <p
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 8,
              textTransform: "uppercase",
              letterSpacing: "0.12em",
              color: "var(--muted-foreground)",
            }}
          >
            Trigger: System Intelligence
          </p>
        </div>
      </header>

      {/* ── Main content ──────────────────────────────────── */}
      <div className="grid xl:grid-cols-[1fr_360px] gap-8 items-start">
        <div className="space-y-8">
          {/* Nudge Content */}
          <section className="border-2 border-[var(--foreground)] bg-[var(--card)] p-10 relative">
            <div className="absolute left-0 top-10 bottom-10 w-1.5 bg-[var(--amber-war)] shadow-[0_0_15px_rgba(245,158,11,0.3)]" />

            <div className="flex items-center gap-4 mb-8">
              {strategist && <AgentPill agent={strategist} size={32} />}
              <div>
                <p
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 9,
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.18em",
                    color: "var(--muted-foreground)",
                  }}
                >
                  Strategist Direction
                </p>
                <p className="text-[#2A2622] font-medium text-sm mt-0.5">
                  {strategist?.displayName}
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <p className="text-[#2A2622] text-2xl font-light leading-relaxed font-serif italic">
                &ldquo;{nudge.description}&rdquo;
              </p>

              <div className="pt-10 flex gap-4">
                <Button className="h-14 px-10 bg-[var(--amber-war)] text-black font-bold uppercase tracking-widest text-[11px] rounded-none shadow-[0_10px_30px_rgba(245,158,11,0.1)]">
                  {nudge.action}
                </Button>
                <Button
                  variant="outline"
                  className="h-14 px-8 border-[var(--border)] text-[#2A2622] font-bold uppercase tracking-widest text-[11px] rounded-none bg-transparent hover:bg-[#E5DED4]"
                >
                  Consult Muse
                </Button>
              </div>
            </div>
          </section>

          {/* Context Log */}
          <section className="border border-[var(--border)] bg-[var(--card)]">
            <div className="px-6 py-4 border-b border-[var(--border)] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <LightningBoltIcon className="w-4 h-4 text-[#6B655E]" />
                <p
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 9,
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.18em",
                    color: "var(--muted-foreground)",
                  }}
                >
                  Related Telemetry
                </p>
              </div>
              <Badge className="bg-[#E5DED4] text-[#2A2622] px-2 py-0.5 text-xs">
                {relatedEvents.length}
              </Badge>
            </div>
            <div className="divide-y divide-[var(--border)]">
              {relatedEvents.length === 0 ? (
                <div className="p-12 text-center">
                  <p className="text-[#9A948C] font-mono text-[10px] uppercase tracking-widest">
                    No matching telemetry signals found in current session buffer
                  </p>
                </div>
              ) : (
                relatedEvents.map((e, i) => (
                  <div
                    key={i}
                    className="px-6 py-4 flex flex-col gap-1 hover:bg-white/[0.02] transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[#2A2622] font-mono text-[10px] uppercase tracking-wider">
                        {e.type || e.eventType}
                      </span>
                      <span className="text-[#9A948C] font-mono text-[8px] uppercase tracking-[0.2em]">
                        Live Stream
                      </span>
                    </div>
                    <p className="text-[#6B655E] text-[11px] truncate font-light italic">
                      {JSON.stringify(e.payload || {}).slice(0, 100)}...
                    </p>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>

        {/* ── Sidebar Actions ───────────────────────────────── */}
        <aside className="space-y-6 sticky top-6">
          <div className="border border-[var(--border)] bg-[var(--card)] divide-y divide-[var(--border)]">
            <div className="px-5 py-4">
              <p
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 9,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.14em",
                  color: "var(--muted-foreground)",
                }}
              >
                Management
              </p>
            </div>
            <button className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all group">
              <span
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 10,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                }}
              >
                View in Context
              </span>
              <EyeOpenIcon className="w-4 h-4 group-hover:scale-110 transition-transform" />
            </button>
            <button className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all group">
              <span
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 10,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                }}
              >
                Snooze 24h
              </span>
              <ChatBubbleIcon className="w-4 h-4 opacity-50 transition-transform" />
            </button>
            <button className="w-full flex items-center justify-between px-5 py-4 hover:bg-[#F5F0E8] border-t border-[#E5DED4] transition-all group text-red-500/70 hover:text-red-500">
              <span
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 10,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                }}
              >
                Dismiss Nudge
              </span>
              <ArchiveIcon className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
            </button>
          </div>

          <div className="p-6 border border-[#E5DED4] bg-[#FBF8F2] space-y-4">
            <p className="text-[10px] uppercase font-bold tracking-widest text-[#6B655E]">
              Nudge Logic
            </p>
            <p className="text-xs text-[#6B655E] leading-relaxed font-light italic">
              Strategists issue nudges when live market signals cross a threshold of{" "}
              <span className="text-[#2A2622]">7.5/10 salience</span> relative to current campaign
              moves.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
