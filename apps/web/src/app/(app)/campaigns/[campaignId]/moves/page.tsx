"use client";

import * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { ArrowLeftIcon, CheckIcon, DotFilledIcon, PlusIcon } from "@radix-ui/react-icons";

const MOVE_TYPES = ["awareness", "consideration", "conversion", "retention", "launch"] as const;

const MOCK_MOVES = [
  { id: "m1", slug: "awareness",     phase: 1, name: "Brand Awareness Push",  type: "awareness",     status: "completed", budget: 4000,  description: "Initial brand visibility on LinkedIn and Instagram. Ogilvy leads creative brief." },
  { id: "m2", slug: "consideration", phase: 2, name: "Content Nurture Sprint", type: "consideration", status: "active",    budget: 8000,  description: "3 blog posts + LinkedIn playbook targeting mid-funnel ICP. Godin leads narrative." },
  { id: "m3", slug: "conversion",    phase: 3, name: "ICP Webinar",            type: "conversion",    status: "planned",   budget: 12000, description: "Live event targeting high-intent prospects. Cialdini's social proof strategy." },
  { id: "m4", slug: "retention",     phase: 4, name: "Email Nurture Sequence", type: "retention",     status: "planned",   budget: 3000,  description: "Welcome + onboarding email flow. Wunderman direct-response architecture." },
  { id: "m5", slug: "launch",        phase: 5, name: "Full Launch Blast",      type: "launch",        status: "planned",   budget: 18000, description: "Multi-channel launch: Search + Reels + PR. Vaynerchuk leads digital execution." },
] as const;

const TYPE_COLOR: Record<string, string> = {
  awareness:     "var(--indigo-muse)",
  consideration: "var(--amber-war)",
  conversion:    "var(--leaf-confirm)",
  retention:     "var(--signal-red)",
  launch:        "var(--foreground)",
};

export default async function CampaignMovesPage({
  params,
}: {
  params: Promise<{ campaignId: string }>;
}): Promise<React.ReactElement> {
  const { campaignId } = await params;

  const totalBudget = MOCK_MOVES.reduce((s, m) => s + m.budget, 0);
  const completedBudget = MOCK_MOVES.filter((m) => m.status === "completed").reduce((s, m) => s + m.budget, 0);

  return (
    <div className="flex flex-col gap-8 py-2">

      {/* Back */}
      <Link
        href={`/campaigns/${campaignId}` as Route}
        className="flex w-fit items-center gap-2 hover:underline"
        style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--muted-foreground)" }}
      >
        <ArrowLeftIcon className="h-3 w-3" />
        Campaign Hub
      </Link>

      {/* Header */}
      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
        <div>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.2em", color: "var(--muted-foreground)", marginBottom: 8 }}>
            Campaign Journey Map
          </p>
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
            Move Sequence
          </h1>
        </div>

        {/* Budget summary */}
        <div className="text-right shrink-0">
          <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 28, color: "var(--foreground)", lineHeight: 1 }}>
            ₹{completedBudget.toLocaleString("en-IN")}
          </p>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.12em", color: "var(--muted-foreground)" }}>
            of ₹{totalBudget.toLocaleString("en-IN")} deployed
          </p>
          <div style={{ height: 2, background: "var(--muted)", marginTop: 6, width: 120 }}>
            <div style={{ height: "100%", width: `${Math.round(completedBudget / totalBudget * 100)}%`, background: "var(--amber-war)" }} />
          </div>
        </div>
      </header>

      {/* Journey chain */}
      <div className="relative">
        {/* Vertical axis label */}
        <div
          className="absolute left-[17px] top-9 bottom-8"
          style={{ width: 2, background: "var(--border)", zIndex: 0 }}
        />

        <div className="space-y-0">
          {MOCK_MOVES.map((move, i) => {
            const isCompleted = move.status === "completed";
            const isActive    = move.status === "active";
            const typeColor   = TYPE_COLOR[move.type] ?? "var(--muted-foreground)";
            const isLast      = i === MOCK_MOVES.length - 1;

            return (
              <div key={move.id} className="flex gap-6">
                {/* Node column */}
                <div className="flex flex-col items-center shrink-0" style={{ zIndex: 1 }}>
                  <div
                    className="flex h-9 w-9 items-center justify-center border-2 shrink-0"
                    style={{
                      background: isCompleted ? "var(--foreground)" : isActive ? typeColor : "var(--card)",
                      borderColor: isCompleted ? "var(--foreground)" : isActive ? typeColor : "var(--border)",
                    }}
                  >
                    {isCompleted ? (
                      <CheckIcon className="h-4 w-4 text-[var(--background)]" />
                    ) : isActive ? (
                      <DotFilledIcon className="h-4 w-4 animate-pulse" style={{ color: "var(--background)" }} />
                    ) : (
                      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, fontWeight: 700, color: "var(--muted-foreground)" }}>
                        {move.phase}
                      </span>
                    )}
                  </div>
                </div>

                {/* Card column */}
                <Link
                  href={`/campaigns/${campaignId}/moves/${move.slug}` as Route}
                  className={`group flex-1 mb-8 border transition-all hover:border-[var(--foreground)] ${isLast ? "mb-0" : ""}`}
                  style={{
                    background: isActive ? "var(--card)" : "var(--card)",
                    borderLeft: `3px solid ${typeColor}`,
                    borderTop: `1px solid ${isActive ? typeColor : "var(--border)"}`,
                    borderRight: "1px solid var(--border)",
                    borderBottom: "1px solid var(--border)",
                  }}
                >
                  <div className="p-5">
                    {/* Meta row */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.14em", border: `1px solid ${typeColor}`, color: typeColor, padding: "2px 6px" }}>
                          {move.type}
                        </span>
                        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 8, textTransform: "uppercase", letterSpacing: "0.1em", color: isActive ? "var(--amber-war)" : isCompleted ? "var(--leaf-confirm)" : "var(--muted-foreground)" }}>
                          {move.status}
                        </span>
                      </div>
                      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, color: "var(--muted-foreground)" }}>
                        ₹{move.budget.toLocaleString("en-IN")}
                      </span>
                    </div>

                    <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 20, lineHeight: 1.2, color: "var(--foreground)", margin: 0, marginBottom: 8 }}>
                      {move.name}
                    </h3>
                    <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, lineHeight: 1.6, color: "var(--muted-foreground)", margin: 0 }}>
                      {move.description}
                    </p>
                  </div>
                </Link>
              </div>
            );
          })}

          {/* Add Move */}
          <div className="flex gap-6">
            <div className="flex flex-col items-center shrink-0" style={{ zIndex: 1 }}>
              <div
                className="flex h-9 w-9 items-center justify-center border-2 border-dashed"
                style={{ borderColor: "var(--border)", background: "var(--card)" }}
              >
                <PlusIcon className="h-4 w-4 text-[var(--muted-foreground)]" />
              </div>
            </div>
            <button
              className="flex-1 border-2 border-dashed border-[var(--border)] p-4 hover:border-[var(--foreground)] transition-all flex items-center gap-3"
              style={{ color: "var(--muted-foreground)", background: "transparent" }}
            >
              <PlusIcon className="h-4 w-4" />
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.14em" }}>
                Add Move
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
