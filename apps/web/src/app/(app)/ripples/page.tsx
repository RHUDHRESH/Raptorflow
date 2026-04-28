"use client";

import * as React from "react";
import { useState } from "react";
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
import { Activity } from "lucide-react";
import { AppPageFrame } from "@/components/layout/AppPageFrame";
import { AppPageSection } from "@/components/layout/AppPageSection";
import { AppEmptyState } from "@/components/layout/AppEmptyState";
import { AppLoadingState } from "@/components/layout/AppLoadingState";
import { AppErrorState } from "@/components/layout/AppErrorState";
import { AppPageToolbar } from "@/components/layout/AppPageToolbar";
import { StatusPill } from "@/components/windows/StatusPill";
import { SignalDot } from "@/components/windows/SignalDot";
import { cn } from "@/lib/cn";

/* ─── Protection band config ────────────────────────────────────── */
const BAND_CONFIG: Record<string, { label: string; tone: "neutral" | "success" | "warning" | "danger" | "amber" | "muse" }> = {
  protected:  { label: "PROTECTED",  tone: "muse" },
  important:  { label: "IMPORTANT",  tone: "amber" },
  normal:     { label: "NORMAL",     tone: "success" },
  disposable: { label: "DISPOSABLE", tone: "danger" },
};

/* ─── Confidence bar ────────────────────────────────────────────── */
function ConfidenceBar({ value }: { value: number }): React.ReactElement {
  const pct = Math.round(value * 100);
  const color = pct >= 75 ? "var(--leaf-confirm)" : pct >= 40 ? "var(--primary)" : "var(--destructive)";
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="mono-label">Confidence</span>
        <span className="font-mono text-[9px] font-bold" style={{ color }}>{pct}%</span>
      </div>
      <div className="h-[3px] bg-[var(--paper-200)] overflow-hidden rounded-full">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, background: color }}
        />
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
  const band = BAND_CONFIG[ripple.importanceBand] ?? BAND_CONFIG.normal;
  const sourceAgent = ripple.sourceAgent ? AGENTS.find((a) => a.key === ripple.sourceAgent || a.displayName === ripple.sourceAgent) : undefined;
  const dateStr = new Date(ripple.createdAt).toLocaleDateString("en-IN", { day: "numeric", month: "short" });

  return (
    <AppPageSection
      eyebrow={`LEVEL ${ripple.hierarchyLevel || 1}`}
      title={ripple.summaryText}
      actions={<StatusPill status={band.label} tone={band.tone} />}
      variant="quiet"
    >
      <div className="space-y-4">
        {ripple.rawText && (
          <p className="text-xs text-[var(--ink-500)] line-clamp-2">{ripple.rawText}</p>
        )}

        <ConfidenceBar value={ripple.confidence} />

        <div className="flex items-center justify-between pt-3 border-t border-[var(--border)]">
          {sourceAgent ? (
            <AgentPill agent={sourceAgent} size={16} />
          ) : (
            <span className="mono-label">{ripple.sourceAgent || "System Generated"}</span>
          )}
          <div className="flex items-center gap-2">
            <span className="mono-label">{dateStr}</span>
            <div className="flex gap-1">
              <button
                onClick={onRealize}
                className="flex h-7 w-7 items-center justify-center rounded-[var(--radius)] border border-[var(--border)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-all"
                title="Realize ripple"
              >
                <LightningBoltIcon className="h-3 w-3" />
              </button>
              <button
                onClick={onDelete}
                className="flex h-7 w-7 items-center justify-center rounded-[var(--radius)] border border-[var(--border)] hover:border-[var(--destructive)] hover:text-[var(--destructive)] transition-all"
                title="Delete ripple"
              >
                <TrashIcon className="h-3 w-3" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </AppPageSection>
  );
}

/* ─── New Ripple Slide-in Panel ─────────────────────────────────── */
function NewRipplePanel({ onClose, onCreate }: {
  onClose: () => void;
  onCreate: (data: { coreClaim: string; keyReasoning: string }) => void;
}): React.ReactElement {
  const [claim, setClaim] = useState("");
  const [reasoning, setReasoning] = useState("");

  React.useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  return (
    <>
      <div className="fixed inset-0 z-40 bg-[var(--ink-900)]/20" onClick={onClose} />
      <div className="fixed right-0 top-0 bottom-0 z-50 flex flex-col border-l border-[var(--border)] bg-[var(--background)] w-full max-w-md">
        <div className="flex items-center justify-between p-5 border-b border-[var(--border)]">
          <h2 className="h2">New Ripple</h2>
          <button onClick={onClose} className="p-1 hover:bg-[var(--paper-150)] rounded-[var(--radius)] transition-colors">
            <Cross2Icon className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          <div>
            <label className="mono-label block mb-2">Core Claim *</label>
            <textarea
              className="w-full bg-transparent border border-[var(--border)] focus:border-[var(--primary)] focus:outline-none p-3 resize-none rounded-[var(--radius)] font-display text-base"
              placeholder="State the strategic claim..."
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              rows={3}
            />
          </div>
          <div>
            <label className="mono-label block mb-2">Key Reasoning</label>
            <textarea
              className="w-full bg-transparent border border-[var(--border)] focus:border-[var(--primary)] focus:outline-none p-3 resize-none rounded-[var(--radius)] text-sm"
              placeholder="Why does this claim matter? What evidence supports it?"
              value={reasoning}
              onChange={(e) => setReasoning(e.target.value)}
              rows={4}
            />
          </div>
        </div>

        <div className="p-5 border-t border-[var(--border)] flex gap-3">
          <button onClick={onClose} className="btn-secondary flex-1">
            Cancel
          </button>
          <button
            onClick={() => { if (claim.trim()) onCreate({ coreClaim: claim, keyReasoning: reasoning }); }}
            disabled={!claim.trim()}
            className="btn-primary flex-1 disabled:opacity-30"
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
  const filtered = displayRipples.filter((r: any) => filter === "all" || r.importanceBand === filter);

  const handleCreate = (data: { coreClaim: string; keyReasoning: string }) => {
    createRipple.mutate({
      summaryText: data.coreClaim,
      rawText: data.keyReasoning,
      confidence: 0.8,
      importanceBand: "normal",
      sourceAgent: "System"
    }, { onSuccess: () => setShowPanel(false) });
  };

  if (isLoading) {
    return (
      <AppPageFrame eyebrow="PRL" title="Memory Ripples">
        <AppLoadingState label="Loading ripples..." />
      </AppPageFrame>
    );
  }

  if (error) {
    return (
      <AppPageFrame eyebrow="PRL" title="Memory Ripples">
        <AppErrorState
          title="Failed to load ripples"
          description={error.message}
        />
      </AppPageFrame>
    );
  }

  return (
    <AppPageFrame
      eyebrow="PRL — Propagated Rationality Log"
      title="Memory Ripples"
      description={`${displayRipples.length} tracked claims`}
      actions={
        <>
          <button
            onClick={() => runDecay.mutate()}
            disabled={runDecay.isPending}
            className="btn-secondary"
          >
            <ReloadIcon className={cn("h-3 w-3", runDecay.isPending && "animate-spin")} />
            Run Decay
          </button>
          <button onClick={() => setShowPanel(true)} className="btn-primary">
            <PlusIcon className="h-3.5 w-3.5" />
            New Ripple
          </button>
        </>
      }
    >
      <AppPageToolbar>
        {(["all", "protected", "important", "normal", "disposable"] as BandFilter[]).map((b) => {
          const isActive = filter === b;
          return (
            <button
              key={b}
              onClick={() => setFilter(b)}
              className={cn(
                "px-4 py-2 rounded-[var(--radius)] text-[11px] font-mono uppercase tracking-widest transition-all border",
                isActive
                  ? "bg-[var(--ink-900)] text-white border-[var(--ink-900)]"
                  : "bg-transparent text-[var(--ink-500)] border-[var(--border)] hover:border-[var(--ink-400)]",
              )}
            >
              {b}
            </button>
          );
        })}
      </AppPageToolbar>

      {!isLoading && filtered.length === 0 && !error && (
        <AppEmptyState
          icon={<Activity className="w-6 h-6 text-[var(--ink-400)]" />}
          title={filter === "all" ? "No ripples yet" : `No ${filter} ripples`}
          description={filter === "all" ? "Create your first ripple to begin tracking." : `No ripples in the ${filter} band.`}
        />
      )}

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

      {showPanel && (
        <NewRipplePanel
          onClose={() => setShowPanel(false)}
          onCreate={handleCreate}
        />
      )}
    </AppPageFrame>
  );
}
