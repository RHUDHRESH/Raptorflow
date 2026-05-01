"use client";

import * as React from "react";
import { useEffect, useMemo, useRef } from "react";
import { gsap } from "gsap";
import {
  Cross2Icon,
  DotFilledIcon,
  ChatBubbleIcon,
  ArrowTopRightIcon,
} from "@radix-ui/react-icons";
import { AGENT_MAP, AGENTS, type AgentConfig } from "@/lib/agents";
import { AgentPortrait } from "@/components/ui/agent-portrait";
import { useOfficeStore } from "@/state/office-store";

/* ─── Stance Chip ─────────────────────────────────────────────── */
function StanceChip({ stance }: { stance: string }): React.ReactElement {
  const stanceMap: Record<string, { label: string; bg: string; color: string }> = {
    agreed: { label: "AGREED", bg: "var(--leaf-confirm-dim)", color: "var(--leaf-confirm)" },
    challenged: { label: "CHALLENGED", bg: "var(--signal-red-dim)", color: "var(--signal-red)" },
    updated: { label: "UPDATED", bg: "var(--amber-war-dim)", color: "var(--amber-war)" },
    thinking: { label: "THINKING", bg: "var(--indigo-muse-dim)", color: "var(--indigo-muse)" },
  };
  const s = stanceMap[stance.toLowerCase()] ?? stanceMap["thinking"];
  return (
    <span
      style={{
        background: s.bg,
        color: s.color,
        border: `1px solid ${s.color}`,
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 9,
        fontWeight: 700,
        textTransform: "uppercase" as const,
        letterSpacing: "0.08em",
        padding: "2px 6px",
      }}
    >
      {s.label}
    </span>
  );
}

/* ─── Agent Drawer Panel ──────────────────────────────────────── */
interface AgentPanelProps {
  agentKey: string;
  onClose: () => void;
}

export function OfficeAgentPanel({ agentKey, onClose }: AgentPanelProps): React.ReactElement {
  const panelRef = useRef<HTMLDivElement>(null);
  const config = AGENT_MAP.get(agentKey);
  const eventLog = useOfficeStore((state) => state.eventLog);
  const ripples = useMemo(() => {
    return eventLog
      .filter((event) => {
        const payload = event.payload as Record<string, unknown> | undefined;
        return (
          event.agentKey === agentKey ||
          payload?.agentKey === agentKey ||
          payload?.sourceAgent === agentKey ||
          (typeof event.type === "string" && event.type.includes(agentKey))
        );
      })
      .slice(-6)
      .reverse()
      .map((event) => {
        const payload = event.payload as Record<string, unknown> | undefined;
        const text =
          (typeof payload?.summary === "string" && payload.summary) ||
          (typeof payload?.message === "string" && payload.message) ||
          (typeof payload?.text === "string" && payload.text) ||
          (typeof payload?.content === "string" && payload.content) ||
          event.type.replaceAll("_", " ");
        return {
          date: new Date(event.timestamp).toLocaleDateString("en-IN", {
            day: "2-digit",
            month: "short",
          }),
          text,
        };
      });
  }, [agentKey, eventLog]);

  // Animate in
  useEffect(() => {
    if (panelRef.current) {
      gsap.fromTo(
        panelRef.current,
        { x: 40, opacity: 0 },
        { x: 0, opacity: 1, duration: 0.28, ease: "power2.out" },
      );
    }
  }, [agentKey]);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  if (!config) {
    return (
      <div className="agent-drawer flex items-center justify-center">
        <p className="font-mono text-xs text-[var(--muted-foreground)]">Agent not found.</p>
      </div>
    );
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-90"
        onClick={onClose}
        style={{ background: "rgba(16,14,15,0.15)" }}
      />

      {/* Drawer */}
      <div ref={panelRef} className="agent-drawer" style={{ zIndex: 100 }}>
        {/* ── Header ─────────────────────────────────────────── */}
        <div
          className="flex items-start justify-between p-5 border-b-2"
          style={{ borderColor: config.color }}
        >
          <div className="flex items-start gap-4">
            <AgentPortrait agent={config} size={56} showStatus status="idle" />
            <div>
              <p
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 9,
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.16em",
                  color: "var(--muted-foreground)",
                  marginBottom: 4,
                }}
              >
                {config.pod.toUpperCase()} POD
              </p>
              <h2
                style={{
                  fontFamily: "'DM Serif Display', serif",
                  fontSize: 22,
                  color: "var(--foreground)",
                  lineHeight: 1.1,
                  margin: 0,
                }}
              >
                {config.displayName}
              </h2>
              <p
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 10,
                  color: "var(--muted-foreground)",
                  marginTop: 4,
                }}
              >
                {config.role}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 hover:bg-[var(--accent)] transition-colors"
            aria-label="Close panel"
          >
            <Cross2Icon className="h-4 w-4 text-[var(--muted-foreground)]" />
          </button>
        </div>

        {/* ── Scrollable Body ─────────────────────────────────── */}
        <div className="flex-1 overflow-y-auto">
          {/* Essence Core */}
          <div className="p-5 border-b border-[var(--border)]">
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.16em",
                color: "var(--muted-foreground)",
                marginBottom: 10,
              }}
            >
              Essence Core
            </p>
            <blockquote
              style={{
                fontFamily: "'DM Serif Display', serif",
                fontSize: 15,
                fontStyle: "italic",
                color: "var(--foreground)",
                borderLeft: `3px solid ${config.color}`,
                paddingLeft: 12,
                margin: 0,
              }}
            >
              &ldquo;{config.essenceCore}&rdquo;
            </blockquote>
          </div>

          {/* Current Status */}
          <div className="p-5 border-b border-[var(--border)]">
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.16em",
                color: "var(--muted-foreground)",
                marginBottom: 10,
              }}
            >
              Current Status
            </p>
            <div className="flex items-center gap-3">
              <DotFilledIcon className="h-5 w-5 shrink-0" style={{ color: config.color }} />
              <div>
                <p
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: 13,
                    fontWeight: 500,
                    color: "var(--foreground)",
                    margin: 0,
                  }}
                >
                  Reviewing campaign brief
                </p>
                <p
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 9,
                    color: "var(--muted-foreground)",
                    marginTop: 2,
                  }}
                >
                  Zone: {config.zone} · Last active 3m ago
                </p>
              </div>
            </div>
          </div>

          {/* PRL Ripples */}
          <div className="p-5 border-b border-[var(--border)]">
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.16em",
                color: "var(--muted-foreground)",
                marginBottom: 12,
              }}
            >
              Recent Memory Ripples
            </p>

            {ripples.length === 0 ? (
              <p
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 10,
                  color: "var(--muted-foreground)",
                }}
              >
                No ripples yet for this agent.
              </p>
            ) : (
              <div className="space-y-4">
                {ripples.map((r, i) => (
                  <div key={i} className="flex gap-3">
                    <div
                      className="shrink-0 mt-1"
                      style={{
                        width: 3,
                        alignSelf: "stretch",
                        background: i === 0 ? config.color : "var(--border)",
                      }}
                    />
                    <div>
                      <p
                        style={{
                          fontFamily: "'JetBrains Mono', monospace",
                          fontSize: 9,
                          textTransform: "uppercase",
                          letterSpacing: "0.12em",
                          color: "var(--muted-foreground)",
                          marginBottom: 4,
                        }}
                      >
                        {r.date}
                      </p>
                      <p
                        style={{
                          fontFamily: "'Inter', sans-serif",
                          fontSize: 12,
                          color: "var(--foreground)",
                          margin: 0,
                        }}
                      >
                        {r.text}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* All Agents in Pod row */}
          <div className="p-5">
            <p
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.16em",
                color: "var(--muted-foreground)",
                marginBottom: 12,
              }}
            >
              {config.pod.toUpperCase()} POD — ALL MEMBERS
            </p>
            <div className="flex flex-wrap gap-3">
              {AGENTS.filter((a) => a.pod === config.pod).map((a) => (
                <AgentPortrait
                  key={a.key}
                  agent={a}
                  size={32}
                  showName
                  className={
                    a.key === agentKey
                      ? "opacity-100"
                      : "opacity-60 hover:opacity-100 transition-opacity"
                  }
                />
              ))}
            </div>
          </div>
        </div>

        {/* ── Footer CTAs ──────────────────────────────────────── */}
        <div className="border-t-2 border-[var(--foreground)] p-4 flex gap-3">
          <button className="flex items-center gap-2 flex-1 justify-center py-2.5 text-xs font-mono uppercase tracking-widest border border-[var(--foreground)] hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all">
            <ChatBubbleIcon className="h-3 w-3" />
            Ask in Muse
          </button>
          <button className="flex items-center gap-2 flex-1 justify-center py-2.5 text-xs font-mono uppercase tracking-widest bg-[var(--foreground)] text-[var(--background)] hover:opacity-80 transition-opacity">
            <ArrowTopRightIcon className="h-3 w-3" />
            Full Profile
          </button>
        </div>
      </div>
    </>
  );
}
