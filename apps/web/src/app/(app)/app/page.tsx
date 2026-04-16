"use client";

import * as React from "react";
import { useEffect, useState } from "react";
import Link from "next/link";
import type { Route } from "next";
import {
  ArrowTopRightIcon,
  DotFilledIcon,
  TimerIcon,
  BackpackIcon,
  AvatarIcon,
  TargetIcon,
  LightningBoltIcon,
} from "@radix-ui/react-icons";
import { useFoundation } from "@/hooks/use-foundation";
import { useCampaigns } from "@/hooks/use-campaigns";
import { useCouncilSessions } from "@/hooks/use-council";
import { useMuseConversations } from "@/hooks/use-muse";
import { useBillingStatus } from "@/hooks/use-billing";
import { AgentPortrait } from "@/components/ui/agent-portrait";
import { AGENTS } from "@/lib/agents";

/* ─── Section Label ───────────────────────────────────────────── */
function SectionLabel({ children }: { children: React.ReactNode }): React.ReactElement {
  return (
    <p
      style={{
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 9,
        fontWeight: 700,
        textTransform: "uppercase",
        letterSpacing: "0.2em",
        color: "var(--muted-foreground)",
        marginBottom: 16,
      }}
    >
      {children}
    </p>
  );
}

/* ─── System Indicator ────────────────────────────────────────── */
function SysIndicator({ label, value, live = false }: { label: string; value: string; live?: boolean }): React.ReactElement {
  return (
    <div className="flex items-center gap-2">
      {live && <span className="status-dot-live" />}
      <span
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 10,
          textTransform: "uppercase",
          letterSpacing: "0.12em",
          color: "var(--muted-foreground)",
        }}
      >
        {label}
      </span>
      <span
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 10,
          fontWeight: 700,
          color: "var(--foreground)",
        }}
      >
        {value}
      </span>
    </div>
  );
}

/* ─── Campaign Card ───────────────────────────────────────────── */
function CampaignCard({
  name,
  status,
  progress,
  moveName,
  daysLeft,
}: {
  name: string;
  status: string;
  progress: number;
  moveName?: string;
  daysLeft?: number;
}): React.ReactElement {
  const isActive = status === "active";
  return (
    <div
      className="shrink-0 border border-[var(--border)] hover:border-[var(--foreground)] transition-colors p-5 flex flex-col gap-3"
      style={{ width: 280, background: "var(--card)" }}
    >
      {/* Status row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isActive && <span className="status-dot-live" />}
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: isActive ? "var(--amber-war)" : "var(--muted-foreground)",
            }}
          >
            {status}
          </span>
        </div>
        {daysLeft !== undefined && (
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              color: "var(--muted-foreground)",
            }}
          >
            {daysLeft}d left
          </span>
        )}
      </div>

      {/* Campaign name */}
      <h3
        style={{
          fontFamily: "'DM Serif Display', serif",
          fontSize: 18,
          color: "var(--foreground)",
          margin: 0,
          lineHeight: 1.2,
        }}
      >
        {name}
      </h3>

      {/* Move */}
      {moveName && (
        <p
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 9,
            textTransform: "uppercase",
            letterSpacing: "0.12em",
            color: "var(--muted-foreground)",
            margin: 0,
          }}
        >
          Move: {moveName}
        </p>
      )}

      {/* Decay progress bar */}
      <div style={{ height: 3, background: "var(--muted)", width: "100%", overflow: "hidden" }}>
        <div
          style={{
            height: "100%",
            width: `${progress}%`,
            background: isActive ? "var(--amber-war)" : "var(--foreground)",
            transition: "width 0.8s ease",
          }}
        />
      </div>
    </div>
  );
}

/* ─── Agent Pulse Card ────────────────────────────────────────── */
function AgentPulseCard({
  agentKey,
  lastOutput,
}: {
  agentKey: string;
  lastOutput: string;
}): React.ReactElement {
  const config = AGENTS.find((a) => a.key === agentKey);
  if (!config) return <></>;

  return (
    <div
      className="flex flex-col gap-3 border border-[var(--border)] p-4 hover:border-[var(--foreground)] transition-colors cursor-pointer group"
      style={{ background: "var(--card)" }}
    >
      <div className="flex items-start justify-between">
        <AgentPortrait agent={config} size={36} showStatus status="idle" />
        <ArrowTopRightIcon className="h-3 w-3 text-[var(--muted-foreground)] opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
      <div>
        <p
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 11,
            fontWeight: 600,
            color: "var(--foreground)",
            marginBottom: 4,
          }}
        >
          {config.displayName}
        </p>
        <p
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: 11,
            color: "var(--muted-foreground)",
            lineHeight: 1.4,
          }}
        >
          {lastOutput}
        </p>
      </div>
    </div>
  );
}

/* ─── Clock ───────────────────────────────────────────────────── */
function LiveClock(): React.ReactElement {
  const [time, setTime] = useState("");
  useEffect(() => {
    const update = () =>
      setTime(
        new Date().toLocaleTimeString("en-IN", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false,
        })
      );
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <span
      style={{
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 11,
        color: "var(--muted-foreground)",
        letterSpacing: "0.05em",
      }}
    >
      {time} IST
    </span>
  );
}

/* ─── Main Dashboard ──────────────────────────────────────────── */
export default function AppHomePage(): React.ReactElement {
  const { data: foundation }        = useFoundation();
  const { data: campaigns }         = useCampaigns();
  const { data: councilSessions }   = useCouncilSessions();
  const { data: museConversations } = useMuseConversations();
  const { data: billing }           = useBillingStatus();

  const today = new Date().toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const activeCampaigns   = campaigns?.filter((c) => c.status === "active") ?? [];
  const allCampaigns      = campaigns ?? [];
  const runningSessions   = councilSessions?.filter((s) => s.status === "running" || s.status === "streaming").length ?? 0;
  const foundationFilled  = foundation ? Object.values(foundation.sections).filter(Boolean).length : 0;

  /* Mock campaign data for UI display */
  const displayCampaigns = allCampaigns.length > 0
    ? allCampaigns
    : [
        { campaignId: "c1", name: "Diya Organics Launch", status: "active", progress: 72, moveName: "Move 3: Reels Blitz", daysLeft: 14 },
        { campaignId: "c2", name: "Monsoon Expansion",    status: "paused", progress: 34, moveName: "Move 1: Positioning", daysLeft: 30 },
        { campaignId: "c3", name: "Q2 Brand Awareness",   status: "draft",  progress: 8,  moveName: undefined,             daysLeft: 60 },
      ];

  return (
    <div className="flex flex-col gap-10 py-2">

      {/* ── Strip 1: Morning Lead ────────────────────────── */}
      <section>
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-3">
            <LightningBoltIcon className="h-4 w-4 text-[var(--amber-war)]" />
            <SectionLabel>Morning Brief</SectionLabel>
          </div>
          <LiveClock />
        </div>

        <div className="border-l-4 border-[var(--foreground)] pl-6 mb-4">
          <p
            style={{
              fontFamily: "'DM Serif Display', serif",
              fontSize: 28,
              lineHeight: 1.25,
              color: "var(--foreground)",
              margin: 0,
            }}
          >
            {activeCampaigns.length > 0
              ? `${activeCampaigns.length} campaign${activeCampaigns.length > 1 ? "s" : ""} running — the office is live.`
              : "No active campaigns yet. Your agents are ready and waiting."}
          </p>
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
            {today} · Briefing generated at 04:00 IST
          </p>
        </div>

        {/* Recommended Action */}
        <div
          className="p-5 flex items-start justify-between gap-4"
          style={{ background: "var(--foreground)", color: "var(--background)" }}
        >
          <div>
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.16em",
                opacity: 0.5,
                marginBottom: 8,
              }}
            >
              Today&apos;s Recommended Action
            </p>
            <p
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: 14,
                lineHeight: 1.5,
              }}
            >
              {activeCampaigns.length > 0
                ? `Review the Council synthesis from yesterday and approve the next Move for ${activeCampaigns[0].name ?? "your active campaign"}.`
                : "Complete your Foundation profile so the Strategist can design your first campaign."}
            </p>
          </div>
          <Link
            href={(activeCampaigns.length > 0 ? "/council" : "/foundation") as Route}
            className="shrink-0 flex items-center gap-2 px-4 py-2.5 border border-[var(--background)] hover:bg-[var(--background)] hover:text-[var(--foreground)] transition-all"
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
            }}
          >
            Open <ArrowTopRightIcon className="h-3 w-3" />
          </Link>
        </div>
      </section>

      {/* ── Strip 2: Campaign Ticker ─────────────────────── */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <SectionLabel>
            <BackpackIcon className="inline h-3 w-3 mr-1.5" />
            Active Campaigns
          </SectionLabel>
          <Link
            href="/campaigns"
            className="flex items-center gap-1 hover:underline"
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 9,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              color: "var(--muted-foreground)",
            }}
          >
            All campaigns <ArrowTopRightIcon className="h-3 w-3" />
          </Link>
        </div>

        <div className="flex gap-4 overflow-x-auto pb-2">
          {displayCampaigns.map((c: any) => (
            <CampaignCard
              key={c.campaignId}
              name={c.name}
              status={c.status}
              progress={c.progress ?? 50}
              moveName={c.moveName}
              daysLeft={c.daysLeft}
            />
          ))}
        </div>
      </section>

      {/* ── Strip 3: Agent Pulse ─────────────────────────── */}
      <section>
        <SectionLabel>
          <AvatarIcon className="inline h-3 w-3 mr-1.5" />
          Agent Pulse
        </SectionLabel>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <AgentPulseCard agentKey="ogilvy"     lastOutput="Reviewed headline variants for Diya Organics." />
          <AgentPulseCard agentKey="vaynerchuk" lastOutput="Recommends 3x Reels frequency this week." />
          <AgentPulseCard agentKey="strategist" lastOutput="Awaiting campaign brief approval from you." />
          <AgentPulseCard agentKey="patel"      lastOutput="Instagram engagement up 38% vs. last week." />
        </div>
      </section>

      {/* ── Strip 4: System Footer ───────────────────────── */}
      <section
        className="border-t border-[var(--border)] pt-5 flex flex-wrap items-center gap-6"
      >
        <SysIndicator label="Intel" value="47 items" live />
        <div className="h-3 w-px bg-[var(--border)]" />
        <SysIndicator label="Council" value={`${runningSessions} running`} live={runningSessions > 0} />
        <div className="h-3 w-px bg-[var(--border)]" />
        <SysIndicator label="Memory" value="1,284 ripples" />
        <div className="h-3 w-px bg-[var(--border)]" />
        <SysIndicator
          label="Plan"
          value={billing?.current_plan?.name ? billing.current_plan.name.toUpperCase() : "—"}
        />
        <div className="h-3 w-px bg-[var(--border)]" />
        <SysIndicator
          label="Foundation"
          value={`${foundationFilled}/21`}
        />
        <div className="h-3 w-px bg-[var(--border)]" />
        <div className="flex items-center gap-2">
          <TargetIcon className="h-3 w-3 text-[var(--muted-foreground)]" />
          <SysIndicator label="Agents" value={`${AGENTS.length} ready`} />
        </div>
      </section>
    </div>
  );
}
