"use client";

import * as React from "react";
import { useState, useEffect, useRef } from "react";
import {
  ExclamationTriangleIcon,
  InfoCircledIcon,
  CheckCircledIcon,
  CrossCircledIcon,
  Cross2Icon,
  ReloadIcon,
  LightningBoltIcon,
  ActivityLogIcon,
} from "@radix-ui/react-icons";
import { useNudges } from "@/hooks/use-nudges";
import { useOfficeStore } from "@/state/office-store";
import { AGENTS } from "@/lib/agents";
import { AgentPill } from "@/components/ui/agent-portrait";
import Link from "next/link";

/* ─── Alert severity config ─────────────────────────────────────── */
const SEVERITY_CONFIG = {
  high:   { label: "HIGH",   color: "var(--signal-red)",   bg: "var(--signal-red-dim,   rgba(220,38,38,0.05))",  icon: CrossCircledIcon,        border: "var(--signal-red)"   },
  medium: { label: "MED",    color: "var(--amber-war)",    bg: "var(--amber-war-dim,    rgba(196,128,30,0.06))", icon: ExclamationTriangleIcon, border: "var(--amber-war)"    },
  low:    { label: "LOW",    color: "var(--leaf-confirm)", bg: "var(--leaf-confirm-dim, rgba(34,197,94,0.05))",  icon: InfoCircledIcon,         border: "var(--leaf-confirm)" },
  system: { label: "SYS",   color: "var(--indigo-muse)",  bg: "rgba(99,102,241,0.05)",                          icon: CheckCircledIcon,        border: "var(--indigo-muse)"  },
} as const;

type Severity = "high" | "medium" | "low" | "system";

/* ─── Radar sweep animation (CSS) ──────────────────────────────── */
function RadarEmpty(): React.ReactElement {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-6">
      <div className="relative h-20 w-20">
        {/* Concentric rings */}
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="absolute rounded-full border"
            style={{
              inset: `${i * 12}%`,
              borderColor: "var(--border)",
              opacity: 0.5 - i * 0.1,
            }}
          />
        ))}
        {/* Sweep line */}
        <div
          className="absolute inset-0 flex items-center justify-center origin-center"
          style={{
            animation: "spin 3s linear infinite",
          }}
        >
          <div
            className="absolute h-px origin-left"
            style={{
              width: "50%",
              left: "50%",
              top: "50%",
              background: "linear-gradient(to right, transparent, var(--leaf-confirm))",
            }}
          />
        </div>
        {/* Center dot */}
        <div className="absolute inset-[48%] rounded-full" style={{ background: "var(--leaf-confirm)" }} />
      </div>
      <div className="text-center">
        <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 22, color: "var(--foreground)", marginBottom: 6 }}>
          System Nominal
        </p>
        <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.18em", color: "var(--muted-foreground)" }}>
          No active alerts · All clear
        </p>
      </div>
    </div>
  );
}

/* ─── Alert Card ────────────────────────────────────────────────── */
function AlertCard({ nudge, onDismiss }: { nudge: any; onDismiss: () => void }): React.ReactElement {
  const sevKey = (nudge.priority?.toLowerCase() as Severity) || "system";
  const sev  = SEVERITY_CONFIG[sevKey] || SEVERITY_CONFIG.system;
  const Icon = sev.icon;
  const typeLabel = (nudge.nudge_type || "SYSTEM").toUpperCase();
  const agentKey = nudge.action_data?.agent_key;
  const agent = AGENTS.find((a) => a.key === agentKey);

  const elapsed = Date.now() - new Date(nudge.created_at).getTime();
  const elapsedStr = elapsed < 60000
    ? "just now"
    : elapsed < 3600000
    ? `${Math.floor(elapsed / 60000)}m ago`
    : `${Math.floor(elapsed / 3600000)}h ago`;

  return (
    <div
      className="flex border transition-all hover:border-[var(--foreground)]"
      style={{ background: sev.bg, borderLeft: `3px solid ${sev.color}`, borderTop: `1px solid var(--border)`, borderRight: `1px solid var(--border)`, borderBottom: `1px solid var(--border)` }}
    >
      {/* Severity icon */}
      <div className="flex items-start px-4 pt-4 shrink-0">
        <Icon className="h-4 w-4" style={{ color: sev.color }} />
      </div>

      {/* Content */}
      <div className="flex-1 py-4 pr-3 min-w-0">
        <div className="flex items-start justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 8,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.14em",
                border: `1px solid ${sev.color}`,
                color: sev.color,
                padding: "1px 5px",
              }}
            >
              {sev.label}
            </span>
            <span
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 8,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.12em",
                color: "var(--muted-foreground)",
              }}
            >
              {typeLabel}
            </span>
          </div>
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, color: "var(--muted-foreground)", whiteSpace: "nowrap", flexShrink: 0 }}>
            {elapsedStr}
          </span>
        </div>

        <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 12, fontWeight: 600, color: "var(--foreground)", marginBottom: 4 }}>
          {nudge.title}
        </p>
        <p className="line-clamp-2" style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, lineHeight: 1.5, color: "var(--muted-foreground)" }}>
          {nudge.body}
        </p>

        {/* Footer */}
        <div className="flex items-center justify-between mt-3">
          {agent ? (
            <AgentPill agent={agent} size={14} />
          ) : (
            <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, color: "var(--muted-foreground)" }}>System</span>
          )}
          <div className="flex gap-1">
            <Link
              href={nudge.nudge_type === "intel" ? "/intel" : nudge.nudge_type === "performance" ? "/campaigns" : "/muse"}
              className="flex items-center gap-1 px-2 py-1 border border-[var(--border)] hover:border-[var(--foreground)] transition-all"
              style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 7, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--muted-foreground)" }}
            >
              <LightningBoltIcon className="h-2.5 w-2.5" />
              Act
            </Link>
            <button
              onClick={onDismiss}
              className="flex h-6 w-6 items-center justify-center border border-[var(--border)] hover:border-[var(--foreground)] transition-colors"
            >
              <Cross2Icon className="h-2.5 w-2.5 text-[var(--muted-foreground)]" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── Main Nudges Page ───────────────────────────────────────────── */
type SevFilter = "all" | Severity;

export default function NudgesPage(): React.ReactElement {
  const eventLog = useOfficeStore((s) => s.eventLog);
  const wsStatus = useOfficeStore((s) => s.connectionStatus);
  const { data: realNudges, isLoading, error } = useNudges();
  const [sevFilter, setSevFilter] = useState<SevFilter>("all");

  const alerts = realNudges || [];
  const handleDismiss = (id: string) => {
    // Backend missing dismiss route, skipping for now to be TRUTHFUL
    console.log("Dismiss not implemented on backend", id);
  };

  const wsSeverityColor = wsStatus === "connected" ? "var(--leaf-confirm)" : wsStatus === "connecting" ? "var(--amber-war)" : "var(--signal-red)";
  const filtered = alerts.filter((a) => sevFilter === "all" || a.priority?.toLowerCase() === sevFilter);

  const highCount   = alerts.filter((a) => a.priority?.toLowerCase() === "high").length;
  const medCount    = alerts.filter((a) => a.priority?.toLowerCase() === "medium").length;
  const lowCount    = alerts.filter((a) => a.priority?.toLowerCase() === "low").length;
  const sysCount    = alerts.filter((a) => a.priority?.toLowerCase() === "system").length;

  return (
    <div className="flex flex-col gap-8 py-2">

      {/* ── Header ────────────────────────────────────────── */}
      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <ActivityLogIcon className="h-4 w-4" style={{ color: "var(--amber-war)" }} />
            <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "var(--muted-foreground)" }}>
              Alert Command Center
            </p>
            <div className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full" style={{ background: wsSeverityColor }} />
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--muted-foreground)" }}>
                WS: {wsStatus}
              </span>
            </div>
          </div>
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
            Nudges
          </h1>
        </div>

        {/* Severity summary */}
        <div className="flex items-center gap-6 shrink-0">
          <div className="text-right">
            <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 28, color: "var(--signal-red)", lineHeight: 1 }}>{highCount}</p>
            <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.12em", color: "var(--muted-foreground)" }}>HIGH</p>
          </div>
          <div className="text-right">
            <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 28, color: "var(--amber-war)", lineHeight: 1 }}>{medCount}</p>
            <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.12em", color: "var(--muted-foreground)" }}>MED</p>
          </div>
          <div className="text-right">
            <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 28, color: "var(--leaf-confirm)", lineHeight: 1 }}>{lowCount}</p>
            <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.12em", color: "var(--muted-foreground)" }}>LOW</p>
          </div>
        </div>
      </header>

      {/* ── Filter ─────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div className="flex gap-0">
          {(["all", "high", "medium", "low", "system"] as SevFilter[]).map((s) => {
            const conf = s !== "all" ? SEVERITY_CONFIG[s as Severity] : null;
            const isActive = sevFilter === s;
            return (
              <button
                key={s}
                onClick={() => setSevFilter(s)}
                className="px-4 py-2 border transition-all"
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 9,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.12em",
                  background: isActive ? (conf?.color ?? "var(--foreground)") : "transparent",
                  color: isActive ? "var(--background)" : conf?.color ?? "var(--muted-foreground)",
                  borderColor: isActive ? (conf?.color ?? "var(--foreground)") : "var(--border)",
                  borderLeft: s === "all" ? "1px solid var(--border)" : "none",
                }}
              >
                {s}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Alert List ─────────────────────────────────────── */}
      {isLoading ? (
        <div className="flex flex-col gap-2">
           {[1,2,3].map(i => <div key={i} className="h-24 border border-[var(--border)] animate-pulse bg-[#F5F0E8]/10" />)}
        </div>
      ) : error ? (
        <div className="p-12 border border-[var(--signal-red)] bg-[#F5F0E8]/10 text-center">
           <p className="font-mono text-xs text-[var(--signal-red)] uppercase tracking-widest">Telemetry Error: Failed to fetch nudges from command core.</p>
        </div>
      ) : filtered.length === 0 ? (
        <RadarEmpty />
      ) : (
        <div className="flex flex-col gap-0 border border-[var(--border)]">
          {filtered.map((nudge) => (
            <AlertCard key={nudge.nudge_id} nudge={nudge} onDismiss={() => handleDismiss(nudge.nudge_id)} />
          ))}
        </div>
      )}

      {/* ── WS Event Log ───────────────────────────────────── */}
      {eventLog.length > 0 && (
        <div>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.18em", color: "var(--muted-foreground)", marginBottom: 12 }}>
            Live WebSocket Events
          </p>
          <div className="border border-[var(--border)]" style={{ background: "var(--card)" }}>
            {[...eventLog].reverse().slice(0, 10).map((ev, i) => (
              <div key={i} className="flex items-start gap-3 px-4 py-3 border-b border-[var(--border)] last:border-0">
                <span className="h-1.5 w-1.5 rounded-full mt-1.5 shrink-0" style={{ background: "var(--amber-war)" }} />
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--foreground)" }}>
                  {ev.type || ev.eventType}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
