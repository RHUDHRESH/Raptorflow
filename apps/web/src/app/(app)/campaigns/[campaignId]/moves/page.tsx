"use client";

import * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { ArrowLeftIcon, CheckIcon, DotFilledIcon } from "@radix-ui/react-icons";
import { useCampaignMoves } from "@/hooks/use-campaigns";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

const TYPE_COLOR: Record<string, string> = {
  awareness: "var(--indigo-muse)",
  consideration: "var(--amber-war)",
  conversion: "var(--leaf-confirm)",
  retention: "var(--signal-red)",
  launch: "var(--foreground)",
};

export default function CampaignMovesPage({
  params,
}: {
  params: Promise<{ campaignId: string }>;
}): React.ReactElement {
  const { campaignId } = React.use(params);
  const { data, isLoading, error } = useCampaignMoves(campaignId);
  const moves = data?.moves ?? [];
  const totalBudget = moves.reduce((sum, move) => sum + ((move as { budget?: number }).budget ?? 0), 0);
  const completedBudget = moves
    .filter((move) => move.status === "completed")
    .reduce((sum, move) => sum + ((move as { budget?: number }).budget ?? 0), 0);
  const progress = totalBudget > 0 ? Math.round((completedBudget / totalBudget) * 100) : 0;

  return (
    <div className="flex flex-col gap-8 py-2">
      <Link
        href={`/campaigns/${campaignId}` as Route}
        className="flex w-fit items-center gap-2 hover:underline"
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 9,
          textTransform: "uppercase",
          letterSpacing: "0.16em",
          color: "var(--muted-foreground)",
        }}
      >
        <ArrowLeftIcon className="h-3 w-3" />
        Campaign Hub
      </Link>

      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
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
            Campaign Journey Map
          </p>
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 40, lineHeight: 1, margin: 0 }}>
            Move Sequence
          </h1>
        </div>

        <div className="text-right shrink-0">
          <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 28, color: "var(--foreground)", lineHeight: 1 }}>
            ₹{completedBudget.toLocaleString("en-IN")}
          </p>
          <p
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 8,
              textTransform: "uppercase",
              letterSpacing: "0.12em",
              color: "var(--muted-foreground)",
            }}
          >
            of ₹{totalBudget.toLocaleString("en-IN")} deployed
          </p>
          <div style={{ height: 2, background: "var(--muted)", marginTop: 6, width: 120 }}>
            <div style={{ height: "100%", width: `${progress}%`, background: "var(--amber-war)" }} />
          </div>
        </div>
      </header>

      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-28 w-full rounded-none" />
          <Skeleton className="h-28 w-full rounded-none" />
          <Skeleton className="h-28 w-full rounded-none" />
        </div>
      ) : error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-sm text-red-800">
          Failed to load campaign moves from the backend.
        </div>
      ) : moves.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--border)] p-10 text-center">
          <p className="font-semibold">No moves exist yet for this campaign.</p>
          <p className="mt-2 text-sm text-[var(--muted-foreground)]">
            Open the campaign hub to generate the move ladder from the backend.
          </p>
          <div className="mt-4">
            <Button asChild variant="secondary">
              <Link href={`/campaigns/${campaignId}` as Route}>Open campaign</Link>
            </Button>
          </div>
        </div>
      ) : (
        <div className="relative">
          <div
            className="absolute left-[17px] top-9 bottom-8"
            style={{ width: 2, background: "var(--border)", zIndex: 0 }}
          />

          <div className="space-y-0">
            {moves.map((move, index) => {
              const isCompleted = move.status === "completed";
              const isActive = move.status === "active";
              const typeColor = TYPE_COLOR[move.type] ?? "var(--muted-foreground)";
              const budget = (move as { budget?: number }).budget ?? 0;
              const isLast = index === moves.length - 1;

              return (
                <div key={move.move_id} className="flex gap-6">
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
                        <span
                          style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: 11,
                            fontWeight: 700,
                            color: "var(--muted-foreground)",
                          }}
                        >
                          {move.move_number}
                        </span>
                      )}
                    </div>
                  </div>

                  <Link
                    href={`/campaigns/${campaignId}/moves/${move.move_id}` as Route}
                    className={`group flex-1 mb-8 border transition-all hover:border-[var(--foreground)] ${isLast ? "mb-0" : ""}`}
                    style={{
                      background: "var(--card)",
                      borderLeft: `3px solid ${typeColor}`,
                      borderTop: `1px solid ${isActive ? typeColor : "var(--border)"}`,
                      borderRight: "1px solid var(--border)",
                      borderBottom: "1px solid var(--border)",
                    }}
                  >
                    <div className="p-5">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span
                            style={{
                              fontFamily: "'JetBrains Mono', monospace",
                              fontSize: 8,
                              fontWeight: 700,
                              textTransform: "uppercase",
                              letterSpacing: "0.14em",
                              border: `1px solid ${typeColor}`,
                              color: typeColor,
                              padding: "2px 6px",
                            }}
                          >
                            {move.type}
                          </span>
                          <span
                            style={{
                              fontFamily: "'JetBrains Mono', monospace",
                              fontSize: 8,
                              textTransform: "uppercase",
                              letterSpacing: "0.1em",
                              color: isActive ? "var(--amber-war)" : isCompleted ? "var(--leaf-confirm)" : "var(--muted-foreground)",
                            }}
                          >
                            {move.status}
                          </span>
                        </div>
                        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 9, color: "var(--muted-foreground)" }}>
                          ₹{budget.toLocaleString("en-IN")}
                        </span>
                      </div>

                      <h3
                        style={{
                          fontFamily: "'DM Serif Display', serif",
                          fontSize: 20,
                          lineHeight: 1.2,
                          color: "var(--foreground)",
                          margin: 0,
                          marginBottom: 8,
                        }}
                      >
                        {move.name}
                      </h3>
                      <p style={{ fontFamily: "'Inter', sans-serif", fontSize: 11, lineHeight: 1.6, color: "var(--muted-foreground)", margin: 0 }}>
                        {move.sub_goal}
                      </p>
                    </div>
                  </Link>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
