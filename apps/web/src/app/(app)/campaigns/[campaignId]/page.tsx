"use client";

import * as React from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import type { Route } from "next";
import {
  ChevronRightIcon,
  CheckCircledIcon,
  TargetIcon,
  ChatBubbleIcon,
  ArrowLeftIcon,
} from "@radix-ui/react-icons";
import { useQueryClient } from "@tanstack/react-query";
import {
  useCampaignDetail,
  useEvaluateCampaign,
  useGenerateMoves,
  useUpdateTaskStatus,
} from "@/features/campaigns";
import type { CampaignMove, CampaignTask } from "@/features/campaigns";
import { Button } from "@/components/ui/button";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { cn } from "@/lib/cn";

function ScoreBadge({ score }: { score: number }): React.ReactElement {
  const color =
    score >= 8 ? "var(--leaf-confirm)" : score >= 5 ? "var(--amber-war)" : "var(--destructive)";
  return (
    <div
      className="inline-flex flex-col items-center justify-center border px-4 py-2"
      style={{ borderColor: color, background: `${color}10` }}
    >
      <span className="text-3xl font-bold" style={{ color, fontFamily: "'DM Serif Display', serif" }}>
        {score}
      </span>
      <span className="text-[8px] font-mono uppercase tracking-[0.18em]" style={{ color }}>
        /10
      </span>
    </div>
  );
}

function ChannelBadge({ channel }: { channel: string }): React.ReactElement {
  const colors: Record<string, string> = {
    email: "bg-blue-500/10 text-blue-600 border-blue-500/30",
    social: "bg-pink-500/10 text-pink-600 border-pink-500/30",
    seo: "bg-green-500/10 text-green-600 border-green-500/30",
    paid: "bg-purple-500/10 text-purple-600 border-purple-500/30",
    content: "bg-amber-500/10 text-amber-600 border-amber-500/30",
    events: "bg-indigo-500/10 text-indigo-600 border-indigo-500/30",
  };
  const cls = colors[channel] ?? "bg-gray-500/10 text-gray-600 border-gray-500/30";
  return (
    <span
      className={cn("text-[8px] font-bold uppercase tracking-[0.14em] px-2 py-0.5 border font-mono", cls)}
      style={{ borderWidth: 1 }}
    >
      {channel}
    </span>
  );
}

function MoveCard({
  move,
  campaignId,
  tasks,
  onToggleTask,
}: {
  move: CampaignMove;
  campaignId: string;
  tasks: CampaignTask[];
  onToggleTask: (taskId: string, currentStatus: string) => void;
}): React.ReactElement {
  const moveTasks = tasks.filter((t) => t.moveId === move.moveId);
  const completedCount = moveTasks.filter((t) => t.status === "completed").length;
  const total = moveTasks.length;
  const pct = total > 0 ? (completedCount / total) * 100 : 0;

  return (
    <div className="border border-[#E5DED4] bg-white">
      <div className="p-6 border-b border-[#E5DED4] flex items-start justify-between gap-4">
        <div className="flex items-start gap-4">
          <div
            className="w-8 h-8 border border-[#E5DED4] flex items-center justify-center font-mono text-xs font-bold text-[#9A948C] flex-shrink-0"
            style={{ fontFamily: "'JetBrains Mono', monospace" }}
          >
            {move.sequenceNumber}
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h4
                className="text-base font-bold uppercase tracking-tight text-[#2A2622]"
                style={{ fontFamily: "'DM Serif Display', serif" }}
              >
                {move.title ?? `${move.moveType} move`}
              </h4>
              <ChannelBadge channel={move.moveType} />
            </div>
            <p className="text-sm text-[#6B655E] leading-relaxed">
              {move.description ?? move.expectedImpact ?? move.moveType}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1 flex-shrink-0">
          <span
            className="text-[9px] font-mono uppercase tracking-[0.14em]"
            style={{
              color: pct === 100 ? "var(--leaf-confirm)" : pct > 0 ? "var(--amber-war)" : "#9A948C",
            }}
          >
            {completedCount}/{total}
          </span>
          <div className="w-20 h-1 bg-[#E5DED4] overflow-hidden">
            <div
              className="h-full transition-all"
              style={{
                width: `${pct}%`,
                background: pct === 100 ? "var(--leaf-confirm)" : "var(--amber-war)",
              }}
            />
          </div>
        </div>
      </div>

      {moveTasks.length > 0 && (
        <div className="divide-y divide-[#F0EBE3]">
          {moveTasks.map((task) => (
            <div
              key={task.taskId}
              className="flex items-center gap-4 px-6 py-3 hover:bg-[#F5F0E8]/50 transition-colors cursor-pointer"
              onClick={() => onToggleTask(task.taskId, task.status)}
            >
              <div
                className="w-5 h-5 border flex items-center justify-center flex-shrink-0 transition-all"
                style={{
                  borderColor: task.status === "completed" ? "var(--leaf-confirm)" : "#D5CBC0",
                  background: task.status === "completed" ? "var(--leaf-confirm)" : "transparent",
                }}
              >
                {task.status === "completed" && (
                  <CheckCircledIcon className="w-3 h-3 text-white" />
                )}
              </div>
              <span
                className="text-sm flex-1"
                style={{
                  color: task.status === "completed" ? "#9A948C" : "#2A2622",
                  textDecoration: task.status === "completed" ? "line-through" : "none",
                }}
              >
                {task.title}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function CampaignDetailPage(): React.ReactElement {
  const params = useParams();
  const router = useRouter();
  const campaignId = params.campaignId as string;

  const { data, isLoading } = useCampaignDetail(campaignId);
  const evaluate = useEvaluateCampaign();
  const generateMoves = useGenerateMoves();
  const updateTask = useUpdateTaskStatus();

  const [confirmRegenerate, setConfirmRegenerate] = React.useState(false);
  const queryClient = useQueryClient();

  const campaign = data?.campaign;
  const moves = data?.moves ?? [];
  const tasks = data?.tasks ?? [];
  const evaluation = data?.evaluation;

  function handleToggleTask(taskId: string, currentStatus: string) {
    const next = currentStatus === "completed" ? "pending" : "completed";
    updateTask.mutate({ campaignId, taskId, status: next });
  }

  async function handleRegenerateMoves() {
    if (!confirmRegenerate) {
      setConfirmRegenerate(true);
      return;
    }
    setConfirmRegenerate(false);
    await generateMoves.mutateAsync({ campaignId });
  }

  async function handleEvaluate() {
    await evaluate.mutateAsync({ campaignId });
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-4 p-8">
        <div className="h-12 w-48 animate-pulse bg-[#E5DED4]" />
        <div className="h-64 animate-pulse bg-[#F5F0E8]" />
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="p-12 text-center">
        <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 24 }}>Campaign not found</p>
        <Link href="/campaigns" className="mt-4 text-sm font-mono text-[#9A948C] hover:text-[#2A2622]">
          ← Back to campaigns
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 py-2">
      <GsapBridge>

        <Link
          href="/campaigns"
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
          Campaign Ledger
        </Link>

        <div className="border-2 border-[var(--foreground)] bg-white p-8 md:p-10 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/5 rotate-45 translate-x-16 -translate-y-16 border-b border-l border-amber-500/10" />

          <div className="relative z-10">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
              <div>
                <h1
                  style={{ fontFamily: "'DM Serif Display', serif", fontSize: 48, lineHeight: 1, margin: 0 }}
                  className="text-[#2A2622] mb-4"
                >
                  {campaign.name}
                </h1>
                <div className="flex items-center gap-4 flex-wrap">
                  <span
                    className="text-[10px] font-mono font-bold uppercase tracking-[0.14em] px-3 py-1 border"
                    style={{
                      color:
                        campaign.status === "active"
                          ? "var(--leaf-confirm)"
                          : campaign.status === "evaluating"
                          ? "var(--amber-war)"
                          : "#9A948C",
                      borderColor:
                        campaign.status === "active"
                          ? "var(--leaf-confirm)"
                          : campaign.status === "evaluating"
                          ? "var(--amber-war)"
                          : "#E5DED4",
                      background:
                        campaign.status === "active"
                          ? "rgba(34,197,94,0.08)"
                          : campaign.status === "evaluating"
                          ? "rgba(255,180,0,0.08)"
                          : "transparent",
                    }}
                  >
                    {campaign.status}
                  </span>
                  {campaign.goal && (
                    <span className="text-[10px] font-mono text-[#6B655E] uppercase tracking-widest">
                      {campaign.goal}
                    </span>
                  )}
                  {evaluation && (
                    <div className="flex items-center gap-1.5">
                      <ScoreBadge score={evaluation.overallScore} />
                    </div>
                  )}
                </div>
              </div>
              <div className="flex gap-3 flex-wrap">
                {campaign.status === "draft" && (
                  <Button
                    className="h-10 px-6 bg-[#D97757] text-white font-bold uppercase tracking-[0.14em] text-[10px] rounded-none hover:bg-[#c4684a] disabled:opacity-50"
                    onClick={handleEvaluate}
                    disabled={evaluate.isPending}
                  >
                    {evaluate.isPending ? "Evaluating…" : "Evaluate Brief"}
                  </Button>
                )}
                <Link
                  href="/muse"
                  className="flex h-10 items-center gap-2 px-6 border border-[#E5DED4] text-[10px] font-mono font-bold uppercase tracking-[0.14em] text-[#6B655E] hover:bg-[#F5F0E8] transition-colors"
                >
                  <ChatBubbleIcon className="w-4 h-4" />
                  Ask Muse
                </Link>
              </div>
            </div>

            {evaluation && (
              <div className="border-t border-[#D5CBC0] pt-8 mt-6">
                <p
                  className="text-[9px] font-mono font-bold uppercase tracking-[0.18em] text-[#9A948C] mb-4"
                >
                  Strategic Evaluation
                </p>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    {evaluation.summary && (
                      <p
                        className="text-base leading-relaxed text-[#2A2622] italic"
                        style={{ fontFamily: "'DM Serif Display', serif", fontSize: 16 }}
                      >
                        "{evaluation.summary}"
                      </p>
                    )}
                    <div>
                      <p className="text-[9px] font-mono text-[#9A948C] uppercase tracking-[0.14em] mb-2">
                        Suggested Actions
                      </p>
                      <ul className="space-y-2">
                        {evaluation.recommendations.slice(0, 5).map((rec, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-[var(--primary)] font-mono text-sm">→</span>
                            <span className="text-sm text-[#2A2622]">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <p className="text-[9px] font-mono text-[var(--leaf-confirm)] uppercase tracking-[0.14em] mb-3">
                        Strengths ({evaluation.strengths.length})
                      </p>
                      <ul className="space-y-2">
                        {evaluation.strengths.map((s, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-[var(--leaf-confirm)] font-mono text-sm">→</span>
                            <span className="text-sm text-[#2A2622]">{s}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="text-[9px] font-mono text-[var(--amber-war)] uppercase tracking-[0.14em] mb-3">
                        Weaknesses ({evaluation.weaknesses.length})
                      </p>
                      <ul className="space-y-2">
                        {evaluation.weaknesses.map((w, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-[var(--amber-war)] font-mono text-sm">!</span>
                            <span className="text-sm text-[#2A2622]">{w}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2
              className="text-[10px] font-mono font-bold uppercase tracking-[0.18em] text-[#9A948C]"
            >
              Move Ladder
            </h2>
            {moves.length > 0 && (
              <Button
                className="h-9 px-5 text-[9px] font-mono font-bold uppercase tracking-[0.14em] rounded-none border border-[#E5DED4] text-[#9A948C] hover:border-[#D97757] hover:text-[#D97757] bg-transparent disabled:opacity-50"
                onClick={handleRegenerateMoves}
                disabled={generateMoves.isPending}
              >
                {confirmRegenerate ? "Confirm — this will replace all moves" : "Regenerate Moves"}
              </Button>
            )}
          </div>

          {moves.length === 0 ? (
            <div className="border border-dashed border-[#E5DED4] p-16 text-center space-y-4">
              <TargetIcon className="w-10 h-10 text-[#E5DED4] mx-auto" />
              <p style={{ fontFamily: "'DM Serif Display', serif", fontSize: 20 }} className="text-[#2A2622]">
                No moves generated yet
              </p>
              <p className="text-[10px] font-mono text-[#9A948C] uppercase tracking-widest">
                Generate the move ladder to see actionable steps
              </p>
              <Button
                className="h-11 px-8 bg-[#D97757] text-white font-bold uppercase tracking-[0.14em] text-[10px] rounded-none hover:bg-[#c4684a] disabled:opacity-50"
                onClick={() => generateMoves.mutate({ campaignId })}
                disabled={!evaluation || generateMoves.isPending}
              >
                {generateMoves.isPending ? "Generating…" : "Generate Move Ladder"}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {moves.map((move) => (
                <MoveCard
                  key={move.moveId}
                  move={move}
                  campaignId={campaignId}
                  tasks={tasks}
                  onToggleTask={handleToggleTask}
                />
              ))}
              <div className="text-center pt-4">
                <Button
                  className="h-9 px-5 text-[9px] font-mono font-bold uppercase tracking-[0.14em] rounded-none border border-[#E5DED4] text-[#9A948C] hover:border-[#D97757] hover:text-[#D97757] bg-transparent disabled:opacity-50"
                  onClick={handleRegenerateMoves}
                  disabled={generateMoves.isPending || confirmRegenerate}
                >
                  {confirmRegenerate ? "Click again to confirm" : "Regenerate Move Ladder"}
                </Button>
              </div>
            </div>
          )}
        </div>

      </GsapBridge>
    </div>
  );
}
