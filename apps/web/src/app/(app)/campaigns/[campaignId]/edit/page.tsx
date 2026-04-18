"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import type { Route } from "next";
import { useCampaign, useUpdateCampaignStatus } from "@/hooks/use-campaigns";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/cn";

import { billingApi, type Campaign } from "@/lib/api";

const STATUS_OPTIONS: Campaign["status"][] = [
  "draft", "pending_approval", "active", "paused", "completed", "archived"
];

export default function EditCampaignPage({
  params,
}: {
  params: Promise<{ campaignId: string }>;
}): React.ReactElement {
  const router = useRouter();
  const resolvedParams = React.use(params);
  const { campaignId } = resolvedParams;

  const { data: campaign, isLoading } = useCampaign(campaignId);
  const updateCampaignStatus = useUpdateCampaignStatus();

  const [name, setName] = React.useState("");
  const [goal, setGoal] = React.useState("");
  const [status, setStatus] = React.useState<Campaign["status"]>("draft");

  React.useEffect(() => {
    if (campaign) {
      setName(campaign.name);
      setGoal(campaign.goal ?? "");
      setStatus(campaign.status);
    }
  }, [campaign]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Backend only supports status updates via PATCH /status
    // Name/goal changes are not yet persisted (no PUT route)
    updateCampaignStatus.mutate(
      { id: campaignId, status },
      {
        onSuccess: () => {
          router.push(`/campaigns/${campaignId}` as Route);
        },
      }
    );
  };

  if (isLoading) {
    return (
      <RouteShell
        eyebrow="Campaigns"
        title="Edit campaign"
        description="Update campaign details, goal, and status."
        tags={["campaigns", "edit"]}
        backHref={`/campaigns/${campaignId}` as Route}
        backLabel="Back to Campaign"
      >
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="h-4 w-48 animate-pulse rounded bg-[var(--muted)]" />
              <div className="h-4 w-full animate-pulse rounded bg-[var(--muted)]" />
              <div className="h-4 w-3/4 animate-pulse rounded bg-[var(--muted)]" />
            </div>
          </CardContent>
        </Card>
      </RouteShell>
    );
  }

  return (
    <RouteShell
      eyebrow="Campaigns"
      title={`Edit: ${campaign?.name ?? campaignId}`}
      description="Update campaign details, goal, and status."
      tags={["campaigns", "edit"]}
      backHref={`/campaigns/${campaignId}` as Route}
      backLabel="Back to Campaign"
    >
      <Card>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="text-sm font-medium">Campaign name *</label>
              <input
                type="text"
                className="mt-1 w-full rounded border border-[var(--border)] bg-white px-3 py-2 text-sm"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium">Primary goal</label>
              <input
                type="text"
                className="mt-1 w-full rounded border border-[var(--border)] bg-white px-3 py-2 text-sm"
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
              />
            </div>

            <div>
              <label className="text-sm font-medium">Status</label>
              <div className="mt-2 flex flex-wrap gap-2">
                {STATUS_OPTIONS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setStatus(s)}
                    className={cn(
                      "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                      status === s
                        ? "border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)]"
                        : "border-[var(--border)] bg-white text-[var(--foreground)] hover:bg-[var(--muted)]"
                    )}
                  >
                    {s.replace("_", " ")}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <Button type="submit" disabled={updateCampaignStatus.isPending}>
                {updateCampaignStatus.isPending ? "Saving..." : "Save status"}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => router.back()}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
