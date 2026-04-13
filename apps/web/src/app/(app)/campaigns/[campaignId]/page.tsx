"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { use } from "react";
import { useCampaign, useArchiveCampaign } from "@/hooks/use-campaigns";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-[var(--muted)] text-[var(--muted-foreground)]",
  pending_approval: "bg-amber-100 text-amber-700 border-amber-200",
  active: "bg-green-100 text-green-700 border-green-200",
  paused: "bg-blue-100 text-blue-700 border-blue-200",
  archived: "bg-[var(--muted)] text-[var(--muted-foreground)]",
};

export default function CampaignDetailPage({
  params
}: {
  params: Promise<{ campaignId: string }>;
}): React.ReactElement {
  const { campaignId } = use(params);
  const { data: campaign, isLoading, error } = useCampaign(campaignId);
  const archiveCampaign = useArchiveCampaign();

  const statusColor = campaign ? STATUS_COLORS[campaign.status] ?? STATUS_COLORS.draft : STATUS_COLORS.draft;

  return (
    <RouteShell
      eyebrow="Campaign"
      title={isLoading ? "Loading..." : campaign?.name ?? campaignId}
      description={campaign?.goal ?? `Campaign ${campaignId}`}
      tags={["campaign", "detail"]}
      backHref={"/campaigns" as Route}
      backLabel="Back to Campaigns"
    >
      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="h-4 w-48 animate-pulse rounded bg-[var(--muted)]" />
                <div className="mt-3 h-3 w-full animate-pulse rounded bg-[var(--muted)]" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4 text-sm text-red-700">
            Failed to load campaign: {error.message}
          </CardContent>
        </Card>
      )}

      {campaign && (
        <>
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-1">
              <Badge className={statusColor}>{campaign.status.replace("_", " ")}</Badge>
              {campaign.timeline && (
                <p className="text-sm text-[var(--muted-foreground)]">{campaign.timeline}</p>
              )}
            </div>
            <div className="flex gap-2">
              {campaign.status === "active" && (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => archiveCampaign.mutate(campaignId)}
                  disabled={archiveCampaign.isPending}
                >
                  {archiveCampaign.isPending ? "Archiving..." : "Archive"}
                </Button>
              )}
              <Button asChild size="sm" variant="secondary">
                <Link href={`/campaigns/${campaignId}/replanning` as Route}>Replan</Link>
              </Button>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Channels</CardTitle>
            </CardHeader>
            <CardContent>
              {campaign.channels && campaign.channels.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {campaign.channels.map((ch) => (
                    <Badge key={ch} variant="outline">{ch}</Badge>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-[var(--muted-foreground)]">No channels assigned yet.</p>
              )}
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[
              { label: "Moves", href: `/campaigns/${campaignId}/moves`, desc: "View move sequence" },
              { label: "Tasks", href: `/campaigns/${campaignId}/tasks`, desc: "View task board" },
              { label: "Performance", href: `/campaigns/${campaignId}/performance`, desc: "Analytics & metrics" },
              { label: "Replanning", href: `/campaigns/${campaignId}/replanning`, desc: "Review proposed changes" },
            ].map((link) => (
              <Card key={link.label} className="transition-shadow hover:shadow-md">
                <CardContent className="flex flex-col items-center justify-center p-6 text-center">
                  <p className="text-xl font-semibold">{link.label}</p>
                  <p className="mt-1 text-xs text-[var(--muted-foreground)]">{link.desc}</p>
                  <Button asChild size="sm" variant="ghost" className="mt-3">
                    <Link href={link.href as Route}>Open →</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}

      <Card className="border-amber-200 bg-amber-50/50">
        <CardHeader>
          <CardTitle className="text-base">📝 What to implement next</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-amber-800">
          <p><strong>Campaign overview tab:</strong> Show key metrics (budget spent, tasks completed, moves in progress) with sparklines.</p>
          <p><strong>Quick actions bar:</strong> "Add move", "Create task", "Start council session" — inline from the campaign detail shell.</p>
          <p><strong>Timeline view:</strong> Gantt-style view of moves mapped to a timeline, using the campaign timeline field.</p>
          <p><strong>Campaign brief:</strong> Expandable brief section showing the Foundation context this campaign was built from.</p>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
