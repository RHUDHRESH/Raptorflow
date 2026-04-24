"use client";

import * as React from "react";
import { useState, useEffect } from "react";
import { useRipples, useCreateRipple, useDeleteRipple, useRealizeRipple, useRunDecay } from "@/hooks/use-prl";
import { AGENTS } from "@/lib/agents";
import { AgentPill } from "@/components/ui/agent-portrait";
import {
  PlusIcon,
  Cross2Icon,
  LightningBoltIcon,
  TrashIcon,
  ReloadIcon,
} from "@radix-ui/react-icons";

/* ─── Protection band config ────────────────────────────────────── */
const BAND_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  protected:  { label: "PROTECTED",  color: "var(--indigo-muse)",      bg: "var(--indigo-muse-dim, rgba(99,102,241,0.08))" },
  important:  { label: "IMPORTANT",  color: "var(--amber-war)",         bg: "var(--amber-war-dim,  rgba(196,128,30,0.08))"  },
  normal:     { label: "NORMAL",     color: "var(--leaf-confirm)",      bg: "var(--leaf-confirm-dim, rgba(34,197,94,0.06))" },
  disposable: { label: "DISPOSABLE", color: "var(--signal-red)",        bg: "var(--signal-red-dim, rgba(220,38,38,0.07))"   },
};

/* ─── Confidence bar ────────────────────────────────────────────── */
function ConfidenceBar({ value }: { value: number }): React.ReactElement {
  const pct = Math.round(value * 100);
  const color = pct >= 75 ? "var(--leaf-confirm)" : pct >= 40 ? "var(--amber-war)" : "var(--signal-red)";
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.12em", color: "var(--muted-foreground)" }}>
          Confidence
        </span>
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, color }}>
          {pct}%
        </span>
      </div>
      <div style={{ height: 3, background: "var(--muted)", overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${pct}%`, background: color, transition: "width 0.6s ease" }} />
      </div>
    </div>
  );
}

/* ─── Ripple Card ───────────────────────────────────────────────── */
function RippleCard({ ripple, onRealize, onDelete }: {
  ripple: any;
  onRealize: () => void;
  onDelete: () => void;
}): React.ReactElement {
  const band = BAND_CONFIG[ripple.protectionBand] ?? BAND_CONFIG.normal;
  const sourceAgent = ripple.source ? AGENTS.find((a) => a.key === ripple.source || a.displayName === ripple.source) : undefined;
  const dateStr = new Date(ripple.createdAt).toLocaleDateString("en-IN", { day: "numeric", month: "short" });

  return (
    <div
      className="flex border border-[var(--border)] overflow-hidden"
      style={{ background: "var(--card)" }}
    >
      {/* Left band */}
      <div className="w-1 shrink-0" style={{ background: band.color }} />

      {/* Content */}
      <div className="flex-1 p-5">
        {/* Header row */}
        <div className="flex items-start justify-between mb-3 gap-3">
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 8,
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.14em",
              border: `1px solid ${band.color}`,
              color: band.color,
              padding: "2px 6px",
              background: band.bg,
              whiteSpace: "nowrap",
            }}
          >
            {band.label}
          </span>
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, color: "var(--muted-foreground)", whiteSpace: "nowrap" }}>
            {dateStr}
          </span>
        </div>

        {/* Core claim */}
        <h3
          style={{
            fontFamily: "'DM Serif Display', serif",
            fontSize: 17,
            lineHeight: 1.3,
            color: "var(--foreground)",
            margin: 0,
            marginBottom: 8,
          }}
        >
          {ripple.coreClaim}
        </h3>

        {/* Reasoning */}
        {ripple.keyReasoning && (
          <p
            className="mb-4 line-clamp-2"
            style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, lineHeight: 1.6, color: "var(--muted-foreground)" }}
          >
            {ripple.keyReasoning}
          </p>
        )}

        {/* Confidence bar */}
        <div className="mb-4">
          <ConfidenceBar value={ripple.confidence} />
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between">
          {sourceAgent ? (
            <AgentPill agent={sourceAgent} size={16} />
          ) : ripple.source ? (
            <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, color: "var(--muted-foreground)" }}>
              {ripple.source}
            </span>
          ) : (
            <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, color: "var(--muted-foreground)" }}>
              No source
            </span>
          )}
          <div className="flex gap-1">
            <button
              onClick={onRealize}
              className="flex h-7 w-7 items-center justify-center border border-[var(--border)] hover:border-[var(--amber-war)] hover:text-[var(--amber-war)] transition-all"
              title="Realize ripple"
            >
              <LightningBoltIcon className="h-3 w-3" />
            </button>
            <button
              onClick={onDelete}
              className="flex h-7 w-7 items-center justify-center border border-[var(--border)] hover:border-[var(--signal-red)] hover:text-[var(--signal-red)] transition-all"
              title="Delete ripple"
            >
              <TrashIcon className="h-3 w-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── New Ripple Slide-in Panel ─────────────────────────────────── */
function NewRipplePanel({ onClose, onCreate }: {
  onClose: () => void;
  onCreate: (data: { coreClaim: string; keyReasoning: string }) => void;
}): React.ReactElement {
  const [claim, setClaim] = useState("");
  const [reasoning, setReasoning] = useState("");

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  return (
    <>
      <div className="fixed inset-0 z-40" style={{ background: "rgba(16,14,15,0.2)" }} onClick={onClose} />
      <div
        className="fixed right-0 top-0 bottom-0 z-50 flex flex-col border-l-2 border-[var(--foreground)]"
        style={{ width: 400, background: "var(--background)" }}
      >
        <div className="flex items-center justify-between p-5 border-b-2 border-[var(--foreground)]">
          <h2 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24, margin: 0 }}>New Ripple</h2>
          <button onClick={onClose} className="p-1 hover:bg-[var(--accent)] transition-colors">
            <Cross2Icon className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          <div>
            <label style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)", display: "block", marginBottom: 8 }}>
              Core Claim *
            </label>
            <textarea
              className="w-full bg-transparent border border-[var(--border)] focus:border-[var(--foreground)] focus:outline-none p-3 resize-none"
              style={{ fontFamily: "'DM Serif Display', serif", fontSize: 16, color: "var(--foreground)", minHeight: 80 }}
              placeholder="State the strategic claim..."
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              rows={3}
            />
          </div>
          <div>
            <label style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)", display: "block", marginBottom: 8 }}>
              Key Reasoning
            </label>
            <textarea
              className="w-full bg-transparent border border-[var(--border)] focus:border-[var(--foreground)] focus:outline-none p-3 resize-none"
              style={{ fontFamily: "'Inter', sans-serif", fontSize: 13, color: "var(--foreground)", minHeight: 100 }}
              placeholder="Why does this claim matter? What evidence supports it?"
              value={reasoning}
              onChange={(e) => setReasoning(e.target.value)}
              rows={4}
            />
          </div>
        </div>

        <div className="p-5 border-t-2 border-[var(--foreground)] flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-3 border border-[var(--border)] hover:border-[var(--foreground)] transition-all"
            style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.14em" }}
          >
            Cancel
          </button>
          <button
            onClick={() => { if (claim.trim()) onCreate({ coreClaim: claim, keyReasoning: reasoning }); }}
            disabled={!claim.trim()}
            className="flex-1 py-3 hover:opacity-80 disabled:opacity-30 transition-all"
            style={{ background: "var(--foreground)", color: "var(--background)", fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.14em" }}
          >
            Create Ripple
          </button>
        </div>
      </div>
    </>
  );
}

/* ─── Main Ripples Page ─────────────────────────────────────────── */
type BandFilter = "all" | "protected" | "important" | "normal" | "disposable";

export default function RipplesPage(): React.ReactElement {
  const { data: ripples, isLoading, error } = useRipples();
  const createRipple  = useCreateRipple();
  const deleteRipple  = useDeleteRipple();
  const realizeRipple = useRealizeRipple();
  const runDecay      = useRunDecay();

  const [filter, setFilter] = useState<BandFilter>("all");
  const [showPanel, setShowPanel] = useState(false);

  const displayRipples = ripples ?? [];
  const filtered = displayRipples.filter((r: any) => filter === "all" || r.protectionBand === filter);

  const handleCreate = (data: { coreClaim: string; keyReasoning: string }) => {
    createRipple.mutate(data, { onSuccess: () => setShowPanel(false) });
  };

  return (
    <div className="flex flex-col gap-8 py-2">

      {/* ── Header ──────────────────────────────────────── */}
      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
        <div>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "var(--muted-foreground)", marginBottom: 8 }}>
            PRL — Propagated Rationality Log
          </p>
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
            Memory Ripples
          </h1>
          <p className="mt-2" style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, color: "var(--muted-foreground)", textTransform: "uppercase", letterSpacing: "0.14em" }}>
            {displayRipples.length} tracked claims
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => runDecay.mutate()}
            disabled={runDecay.isPending}
            className="flex h-10 items-center gap-2 px-4 border border-[var(--border)] hover:border-[var(--foreground)] transition-all"
            style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em", color: "var(--muted-foreground)" }}
          >
            <ReloadIcon className={`h-3 w-3 ${runDecay.isPending ? "animate-spin" : ""}`} />
            Run Decay
          </button>
          <button
            onClick={() => setShowPanel(true)}
            className="flex h-10 items-center gap-2 px-4 hover:opacity-80 transition-opacity"
            style={{ background: "var(--foreground)", color: "var(--background)", fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em" }}
          >
            <PlusIcon className="h-3.5 w-3.5" />
            New Ripple
          </button>
        </div>
      </header>

      {/* ── Band Filter ──────────────────────────────────── */}
      <div className="flex gap-0.5 flex-wrap">
        {(["all", "protected", "important", "normal", "disposable"] as BandFilter[]).map((b) => {
          const conf = b !== "all" ? BAND_CONFIG[b] : null;
          const isActive = filter === b;
          return (
            <button
              key={b}
              onClick={() => setFilter(b)}
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
              }}
            >
              {b}
            </button>
          );
        })}
      </div>

      {/* ── Grid ─────────────────────────────────────────── */}
      {isLoading && (
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-48 border border-[var(--border)] animate-pulse" style={{ background: "var(--card)" }} />
          ))}
        </div>
      )}

      {error && (
        <div className="border border-[var(--signal-red)] p-5" style={{ background: "var(--signal-red-dim, rgba(220,38,38,0.06))" }}>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10, color: "var(--signal-red)" }}>
            FAILED TO LOAD: {error.message}
          </p>
        </div>
      )}

      {!isLoading && filtered.length === 0 && !error && (
        <div className="flex flex-col items-center justify-center py-24 border-2 border-dashed border-[var(--border)]">
          <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24, color: "var(--foreground)", marginBottom: 8 }}>
            No ripples in this band
          </p>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)" }}>
            {filter === "all" ? "Create your first ripple to begin tracking" : `No ${filter} ripples`}
          </p>
        </div>
      )}

      {!isLoading && filtered.length > 0 && (
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((ripple: any) => (
            <RippleCard
              key={ripple.rippleId}
              ripple={ripple}
              onRealize={() => realizeRipple.mutate(ripple.rippleId)}
              onDelete={() => { if (confirm("Delete this ripple?")) deleteRipple.mutate(ripple.rippleId); }}
            />
          ))}
        </div>
      )}

      {/* ── Slide-in Panel ───────────────────────────────── */}
      {showPanel && (
        <NewRipplePanel
          onClose={() => setShowPanel(false)}
          onCreate={handleCreate}
        />
      )}
    </div>
  );
}
