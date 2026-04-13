"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { useCampaigns } from "@/hooks/use-campaigns";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CampaignsPage(): React.ReactElement {
  const { data: campaigns, isLoading, error } = useCampaigns();

  return (
    <RouteShell
      eyebrow="Campaigns"
      title="Campaigns"
      description="Campaign management gets its own shell, with nested detail, move, task, replanning, and performance routes."
      tags={["briefs", "moves", "tasks", "performance"]}
      rail={
        <Card>
          <CardHeader>
            <CardTitle>Quick links</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <Link href="/campaigns/campaign-001/tasks" className="block text-[var(--foreground)]">
              View tasks board
            </Link>
            <Link href="/campaigns/campaign-001/performance" className="block text-[var(--foreground)]">
              View performance
            </Link>
            <Link href="/campaigns/campaign-001/replanning" className="block text-[var(--foreground)]">
              View replanning
            </Link>
          </CardContent>
        </Card>
      }
    >
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">All campaigns</h2>
          <p className="text-sm text-[var(--muted-foreground)]">
            {campaigns?.length ?? 0} total
          </p>
        </div>
        <Button size="sm">+ New campaign</Button>
      </div>

      {isLoading && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <div className="h-4 w-32 animate-pulse rounded bg-[var(--muted)]" />
                <div className="mt-3 h-3 w-full animate-pulse rounded bg-[var(--muted)]" />
                <div className="mt-2 h-3 w-3/4 animate-pulse rounded bg-[var(--muted)]" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4 text-sm text-red-700">
            Failed to load campaigns: {error.message}
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && campaigns?.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-3xl">📋</p>
            <p className="mt-4 font-medium">No campaigns yet</p>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">
              Create your first campaign to get started
            </p>
            <Button className="mt-4" size="sm">+ Create campaign</Button>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && campaigns && campaigns.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {campaigns.map((campaign) => {
            const statusVariant =
              campaign.status === "active" ? "default" :
              campaign.status === "paused" ? "secondary" :
              campaign.status === "archived" ? "destructive" : "outline";
            return (
              <Card key={campaign.campaignId} className="transition-shadow hover:shadow-md">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <Link href={`/campaigns/${campaign.campaignId}` as Route} className="font-semibold hover:underline">
                        {campaign.name}
                      </Link>
                      {campaign.goal && (
                        <p className="mt-1 truncate text-sm text-[var(--muted-foreground)]">
                          {campaign.goal}
                        </p>
                      )}
                      {campaign.timeline && (
                        <p className="mt-0.5 text-xs text-[var(--muted-foreground)]">
                          {campaign.timeline}
                        </p>
                      )}
                    </div>
                    <Badge variant={statusVariant} className="flex-shrink-0">
                      {campaign.status.replace("_", " ")}
                    </Badge>
                  </div>
                  {campaign.channels && campaign.channels.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {campaign.channels.map((ch) => (
                        <span
                          key={ch}
                          className="rounded-full bg-[var(--muted)] px-2 py-0.5 text-xs text-[var(--muted-foreground)]"
                        >
                          {ch}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="mt-4 flex gap-2">
                    <Button asChild size="sm" variant="secondary" className="flex-1">
                      <Link href={`/campaigns/${campaign.campaignId}/tasks` as Route}>Tasks</Link>
                    </Button>
                    <Button asChild size="sm" variant="secondary" className="flex-1">
                      <Link href={`/campaigns/${campaign.campaignId}/performance` as Route}>Analytics</Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </RouteShell>
  );
}
