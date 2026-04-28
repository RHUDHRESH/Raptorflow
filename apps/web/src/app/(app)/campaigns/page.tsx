"use client";

import * as React from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import type { Route } from "next";
import {
  PlusIcon,
  TargetIcon,
  ChevronRightIcon,
  LightningBoltIcon,
  BackpackIcon,
} from "@radix-ui/react-icons";
import {
  useCampaigns,
  useCreateCampaign,
  useEvaluateCampaign,
} from "@/features/campaigns";
import type { CampaignSummary } from "@/features/campaigns";
import { Button } from "@/components/ui/button";
import { GsapBridge } from "@/components/ui/gsap-bridge";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/cn";
import { Rocket } from "lucide-react";

const STATUS_COLORS: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  draft: { bg: "bg-[var(--paper-150)]", text: "text-[var(--ink-400)]", border: "border-[var(--border)]", dot: "bg-[var(--ink-400)]" },
  evaluating: { bg: "bg-[var(--amber-wash)]", text: "text-[var(--primary)]", border: "border-[var(--amber-stroke)]/30", dot: "bg-[var(--primary)]" },
  active: { bg: "bg-[var(--leaf-wash)]", text: "text-[var(--leaf-confirm)]", border: "border-[var(--leaf-confirm)]/30", dot: "bg-[var(--leaf-confirm)]" },
  paused: { bg: "bg-[var(--indigo-wash)]", text: "text-[var(--indigo-muse)]", border: "border-[var(--indigo-muse)]/30", dot: "bg-[var(--indigo-muse)]" },
  completed: { bg: "bg-[var(--paper-150)]", text: "text-[var(--pod-creative)]", border: "border-[var(--pod-creative)]/30", dot: "bg-[var(--pod-creative)]" },
  complete: { bg: "bg-[var(--paper-150)]", text: "text-[var(--pod-creative)]", border: "border-[var(--pod-creative)]/30", dot: "bg-[var(--pod-creative)]" },
};

function StatusBadge({ status }: { status: string }): React.ReactElement {
  const colors = STATUS_COLORS[status] ?? STATUS_COLORS.draft;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 border px-3 py-1 text-[9px] font-bold uppercase tracking-[0.14em] font-mono rounded-full",
        colors.bg, colors.text, colors.border
      )}
      style={{ borderWidth: 1, borderStyle: "solid" }}
    >
      <span className={cn("w-1.5 h-1.5 rounded-full", colors.dot)} />
      {status}
    </span>
  );
}

function NewCampaignModal({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: (id: string) => void;
}): React.ReactElement {
  const [name, setName] = useState("");
  const [goal, setGoal] = useState("");
  const create = useCreateCampaign();
  const evaluate = useEvaluateCampaign();

  const isValid = name.trim().length > 0;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isValid) return;
    try {
      const result = await create.mutateAsync({ name: name.trim(), goal: goal || null });
      await evaluate.mutateAsync({ campaignId: result.campaignId });
      onCreated(result.campaignId);
    } catch (err) {
      console.error("Failed to create campaign:", err);
    }
  }

  if (!open) return <></>;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-[var(--ink-900)]/40 backdrop-blur-sm" onClick={onClose} />
      <div className="relative z-10 w-full max-w-lg card-elevated p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="display-sm">New Campaign</h2>
          <button onClick={onClose} className="text-[var(--ink-400)] hover:text-[var(--ink-900)] transition-colors p-1 rounded-[var(--radius)] hover:bg-[var(--paper-150)]">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="eyebrow mb-2 block">Campaign Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Q4 Pipeline Push"
              className="w-full border border-[var(--border)] bg-white px-4 py-3 text-sm text-[var(--ink-900)] placeholder:text-[var(--ink-300)] rounded-[var(--radius)] focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--primary)]/20 transition-all"
            />
          </div>

          <div>
            <label className="eyebrow mb-2 block">Goal</label>
            <input
              type="text"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g. Drive 500 qualified leads"
              className="w-full border border-[var(--border)] bg-white px-4 py-3 text-sm text-[var(--ink-900)] placeholder:text-[var(--ink-300)] rounded-[var(--radius)] focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--primary)]/20 transition-all"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <Button
              type="submit"
              className="flex-1 h-12"
              disabled={!isValid || create.isPending || evaluate.isPending}
            >
              {evaluate.isPending ? "Evaluating…" : create.isPending ? "Creating…" : "Create & Evaluate"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="h-12"
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function CampaignsPage(): React.ReactElement {
  const router = useRouter();
  const [modalOpen, setModalOpen] = useState(false);
  const { data: campaigns, isLoading } = useCampaigns();

  const campaignList: CampaignSummary[] = campaigns ?? [];
  const activeCount = campaignList.filter((c) => c.status === "active").length;
  const completedCount = campaignList.filter((c) => c.status === "completed" || c.status === "complete").length;

  function handleCreated(campaignId: string) {
    setModalOpen(false);
    router.push(`/campaigns/${campaignId}` as Route);
  }

  return (
    <div className="flex flex-col gap-12 py-2">
      <GsapBridge stagger>

        <header className="gsap-reveal flex items-end justify-between border-b border-[var(--border)] pb-8">
          <div className="space-y-2">
            <p className="eyebrow">Strategy Ledger</p>
            <h1 className="display-md">Campaigns</h1>
          </div>
          <Button
            className="h-12 px-8"
            onClick={() => setModalOpen(true)}
          >
            <PlusIcon className="w-4 h-4 mr-2" />
            New Campaign
          </Button>
        </header>

        <div className="gsap-reveal grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card-elevated p-6">
            <p className="mono-label mb-3">Active Fronts</p>
            <div className="text-4xl text-[var(--ink-900)] font-display">
              {isLoading ? "..." : activeCount}
            </div>
          </div>
          <div className="card-elevated p-6">
            <p className="mono-label mb-3">Completed Initiatives</p>
            <div className="text-4xl text-[var(--ink-900)] font-display">
              {isLoading ? "..." : completedCount}
            </div>
          </div>
          <div className="card-elevated p-6">
            <p className="mono-label mb-3">Total Briefs</p>
            <div className="text-4xl text-[var(--ink-900)] font-display">
              {isLoading ? "..." : campaignList.length}
            </div>
          </div>
        </div>

        <div className="gsap-reveal space-y-6 mt-12">
          <div className="flex items-center justify-between">
            <p className="eyebrow">Campaign Log</p>
          </div>

          <div className="card-elevated divide-y divide-[var(--border)] overflow-hidden">
            {isLoading ? (
              <div className="divide-y divide-[var(--border)]">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="p-6 space-y-3">
                    <div className="flex items-center gap-5">
                      <Skeleton className="h-10 w-10 rounded-[var(--radius)]" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-5 w-48" />
                        <Skeleton className="h-3 w-32" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : campaignList.length === 0 ? (
              <EmptyState
                icon={Rocket}
                title="No campaigns yet"
                description="Create your first campaign and let the council evaluate it."
                action={
                  <Button onClick={() => setModalOpen(true)}>
                    <PlusIcon className="w-4 h-4 mr-2" />
                    New Campaign
                  </Button>
                }
              />
            ) : (
              campaignList.map((c, index) => (
                <Link
                  key={c.campaignId}
                  href={`/campaigns/${c.campaignId}` as Route}
                  className="flex flex-col md:flex-row md:items-center justify-between p-6 group hover:bg-[var(--paper-150)]/50 transition-all duration-200 gap-6"
                  style={{ animationDelay: `${index * 60}ms` }}
                >
                  <div className="flex items-center gap-5">
                    <div className="w-10 h-10 border border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center group-hover:bg-[var(--primary)] group-hover:border-[var(--primary)] transition-all duration-300">
                      <BackpackIcon className="w-4 h-4 text-[var(--ink-400)] group-hover:text-white transition-colors duration-300" />
                    </div>
                    <div>
                      <h3 className="h2 group-hover:text-[var(--primary)] transition-colors duration-200">
                        {c.name}
                      </h3>
                      <div className="flex items-center gap-3 mt-1.5">
                        <StatusBadge status={c.status} />
                        {c.goal && (
                          <>
                            <span className="h-1 w-1 rounded-full bg-[var(--border)]" />
                            <span className="mono-label">
                              {c.goal}
                            </span>
                          </>
                        )}
                        {c.moveCount != null && c.moveCount > 0 && (
                          <>
                            <span className="h-1 w-1 rounded-full bg-[var(--border)]" />
                            <span className="mono-label">
                              {c.moveCount} moves
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-8">
                    {c.evaluationScore != null && (
                      <div className="hidden lg:flex flex-col items-center">
                        <span
                          className="text-2xl font-bold font-display"
                          style={{
                            color:
                              c.evaluationScore >= 8
                                ? "var(--leaf-confirm)"
                                : c.evaluationScore >= 5
                                ? "var(--primary)"
                                : "var(--destructive)",
                          }}
                        >
                          {c.evaluationScore}
                        </span>
                        <span className="mono-label">/10</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <span className="mono-label">
                        {new Date(c.createdAt).toLocaleDateString("en-IN", {
                          day: "numeric",
                          month: "short",
                        })}
                      </span>
                      <ChevronRightIcon className="w-5 h-5 text-[var(--ink-300)] group-hover:text-[var(--ink-900)] transition-colors duration-200" />
                    </div>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        <footer className="gsap-reveal mt-20 card-elevated p-8 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-[var(--radius)] bg-[var(--amber-wash)] flex items-center justify-center">
              <LightningBoltIcon className="w-5 h-5 text-[var(--primary)]" />
            </div>
            <div>
              <p className="text-sm font-bold text-[var(--ink-900)] uppercase tracking-tight">
                Ready for deployment?
              </p>
              <p className="mono-label">
                Create a campaign to begin the evaluation pipeline.
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            className="h-12 px-8"
            onClick={() => setModalOpen(true)}
          >
            New Campaign
          </Button>
        </footer>

      </GsapBridge>

      <NewCampaignModal open={modalOpen} onClose={() => setModalOpen(false)} onCreated={handleCreated} />
    </div>
  );
}
