"use client";

import * as React from "react";
import { use } from "react";
import type { Route } from "next";
import Link from "next/link";
import {
  ArrowLeftIcon,
  ChatBubbleIcon,
  DrawingPinIcon,
  MixerHorizontalIcon,
} from "@radix-ui/react-icons";
import { useCampaignMoves, useCampaignTasks } from "@/features/campaigns";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

function TaskStatusPill({ status }: { status: string }): React.ReactElement {
  const tone =
    status === "completed"
      ? "bg-green-500/10 text-green-600 border-green-500/20"
      : status === "in_progress"
        ? "bg-amber-500/10 text-amber-600 border-amber-500/20"
        : "bg-[#E5DED4] text-[#6B655E] border-[#E5DED4]";
  return (
    <Badge variant="outline" className={`text-[9px] uppercase ${tone}`}>
      {status.replaceAll("_", " ")}
    </Badge>
  );
}

export default function CampaignMoveDetailPage({
  params,
}: {
  params: Promise<{ campaignId: string; moveId: string }>;
}): React.ReactElement {
  const { campaignId, moveId } = use(params);
  const { data: moves, isLoading: movesLoading } = useCampaignMoves(campaignId);
  const { data: tasks, isLoading: tasksLoading } = useCampaignTasks(campaignId);

  const move = moves?.find((candidate) => candidate.moveId === moveId);
  const moveTasks = (tasks ?? []).filter((task) => task.moveId === moveId);
  const completedCount = moveTasks.filter((t) => t.status === "completed").length;
  const totalCount = moveTasks.length;

  if (movesLoading || tasksLoading) {
    return (
      <div className="py-8 text-sm text-[var(--muted-foreground)]">Loading move from backend…</div>
    );
  }

  if (!move) {
    return (
      <div className="py-12 text-center">
        <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24 }}>Move not found</p>
        <Link
          href={`/campaigns/${campaignId}/moves` as Route}
          className="mt-4 text-sm font-mono text-[#9A948C] hover:text-[#2A2622]"
        >
          ← Back to moves
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 py-2">
      <Link
        href={`/campaigns/${campaignId}/moves` as Route}
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
        Move Sequence
      </Link>

      <header className="flex items-end justify-between border-b-2 border-[var(--foreground)] pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <DrawingPinIcon className="h-4 w-4" style={{ color: "var(--amber-war)" }} />
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
              Move Detail // {move.moveId.slice(0, 8).toUpperCase()}
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
            {move.title ?? `${move.moveType} move`}
          </h1>
        </div>

        <div className="flex flex-col items-end gap-2 text-right">
          <Badge
            className={
              move.status === "active" || move.status === "in_progress"
                ? "bg-amber-500/10 text-amber-500 border-amber-500/20"
                : move.status === "completed"
                  ? "bg-green-500/10 text-green-500 border-green-500/20"
                  : "bg-[#E5DED4] text-[#6B655E]"
            }
          >
            {move.status}
          </Badge>
          <p
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 10,
              color: "var(--foreground)",
            }}
          >
            {move.sequenceNumber} of sequence
          </p>
        </div>
      </header>

      <div className="grid xl:grid-cols-[1fr_360px] gap-8 items-start">
        <div className="space-y-8">
          <section className="border-2 border-[var(--foreground)] bg-[var(--card)] p-8">
            <div className="flex items-start justify-between mb-8">
              <div className="space-y-4 max-w-xl">
                <h3 style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24 }}>
                  Move Narrative
                </h3>
                <p className="text-[#6B655E] font-light italic leading-relaxed">
                  {move.description ?? move.expectedImpact ?? move.moveType}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 pt-8 border-t border-[#E5DED4]">
              <div>
                <p className="font-mono text-[8px] text-[#9A948C] uppercase tracking-widest mb-1">
                  Type
                </p>
                <p className="text-sm font-medium">{move.moveType}</p>
              </div>
              <div>
                <p className="font-mono text-[8px] text-[#9A948C] uppercase tracking-widest mb-1">
                  Tasks
                </p>
                <p className="text-sm font-medium">
                  {completedCount}/{totalCount} completed
                </p>
              </div>
              <div>
                <p className="font-mono text-[8px] text-[#9A948C] uppercase tracking-widest mb-1">
                  Status
                </p>
                <p className="text-sm font-medium">{move.status}</p>
              </div>
              <div>
                <p className="font-mono text-[8px] text-[#9A948C] uppercase tracking-widest mb-1">
                  Sequence
                </p>
                <p className="text-sm font-medium">#{move.sequenceNumber}</p>
              </div>
            </div>
          </section>

          <section className="border border-[var(--border)] bg-[var(--card)]">
            <div className="px-6 py-4 border-b border-[var(--border)] flex items-center justify-between">
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
                Operational Ledger
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  className="h-7 px-2 text-[9px] font-mono text-[#9A948C] uppercase"
                  asChild
                >
                  <Link href={`/campaigns/${campaignId}` as Route}>Open campaign</Link>
                </Button>
              </div>
            </div>
            <div className="divide-y divide-[var(--border)]">
              {moveTasks.length === 0 ? (
                <div className="p-6 text-sm text-[var(--muted-foreground)]">
                  No tasks are attached to this move yet.
                </div>
              ) : (
                moveTasks.map((task) => (
                  <div
                    key={task.taskId}
                    className="p-6 flex items-center justify-between group hover:bg-white/[0.02] transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className={`h-2 w-2 rounded-full ${
                          task.status === "completed"
                            ? "bg-green-500"
                            : task.status === "in_progress"
                              ? "bg-amber-500 animate-pulse"
                              : "bg-[#E5DED4]"
                        }`}
                      />
                      <div>
                        <p className="text-sm text-[#2A2622] font-medium group-hover:text-amber-500 transition-colors uppercase tracking-tight">
                          {task.title}
                        </p>
                        <div className="flex items-center gap-3 mt-1">
                          <TaskStatusPill status={task.status} />
                          <span className="text-[#BAB0A0]">|</span>
                          <span className="text-[9px] font-mono text-[#6B655E] uppercase">
                            {task.owner ?? "Unassigned"}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>

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
                Available Actions
              </p>
            </div>
            <Link
              href={`/campaigns/${campaignId}` as Route}
              className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-all group"
            >
              <span
                style={{
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 10,
                  fontWeight: 700,
                  textTransform: "uppercase",
                }}
              >
                Open Campaign
              </span>
              <MixerHorizontalIcon className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
            </Link>
          </div>
        </aside>
      </div>
    </div>
  );
}
