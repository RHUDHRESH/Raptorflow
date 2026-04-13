"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { use } from "react";
import { useOfficeStore } from "@/state/office-store";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const NUDGE_TYPES: Record<string, { label: string; description: string; severity: string }> = {
  "major-competitor-shift": { label: "Intel nudge", description: "A major competitor has shifted their positioning or launched a new campaign.", severity: "major" },
  "budget-underutilization": { label: "Performance nudge", description: "Campaign budget is underutilized by more than 20% this week.", severity: "warning" },
  "task-sla-breach": { label: "Performance nudge", description: "A campaign task has exceeded its SLA by 2 days.", severity: "warning" },
  "opportunity-detected": { label: "Opportunity nudge", description: "New ICP segment identified based on recent conversion data.", severity: "info" },
};

export default function NudgeDetailPage({
  params
}: {
  params: Promise<{ nudgeId: string }>;
}): React.ReactElement {
  const { nudgeId } = use(params);
  const nudge = NUDGE_TYPES[nudgeId] ?? Object.values(NUDGE_TYPES)[0];
  const eventLog = useOfficeStore((s) => s.eventLog);

  const relatedEvents = eventLog.filter(
    (e) => e.eventType === "intel_alert_received" || e.eventType === "task_missed_notification"
  ).slice(0, 5);

  return (
    <RouteShell
      eyebrow="Nudge detail"
      title={nudge.label}
      description={nudge.description}
      tags={[nudge.severity, "nudge"]}
      backHref={"/nudges" as Route}
      backLabel="Back to Nudges"
    >
      <div className="grid gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">{nudge.label}</CardTitle>
                <Badge className={
                  nudge.severity === "major" ? "bg-red-100 text-red-700 border-red-200" :
                  nudge.severity === "warning" ? "bg-amber-100 text-amber-700 border-amber-200" :
                  "bg-blue-100 text-blue-700 border-blue-200"
                }>
                  {nudge.severity}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-[var(--muted-foreground)]">{nudge.description}</p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-[var(--muted-foreground)]">Nudge ID</p>
                  <p className="font-mono text-xs">{nudgeId}</p>
                </div>
                <div>
                  <p className="text-[var(--muted-foreground)]">Triggered</p>
                  <p className="font-medium">Recently (via WebSocket)</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Take action</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full" size="sm">View in context</Button>
              <Button className="w-full" size="sm" variant="secondary">Start council session</Button>
              <Button className="w-full" size="sm" variant="secondary">Dismiss nudge</Button>
              <Button className="w-full" size="sm" variant="ghost">Snooze for 24h</Button>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Related WebSocket events</CardTitle>
            </CardHeader>
            <CardContent>
              {relatedEvents.length === 0 ? (
                <p className="py-4 text-center text-sm text-[var(--muted-foreground)]">
                  Connect to office WebSocket to see live events
                </p>
              ) : (
                <div className="space-y-2">
                  {relatedEvents.map((e, i) => (
                    <div key={i} className="rounded-lg border border-[var(--border)] px-3 py-2 text-xs">
                      <p className="font-medium">{e.eventType}</p>
                      <p className="text-[var(--muted-foreground)]">{JSON.stringify(e.payload).slice(0, 80)}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-amber-200 bg-amber-50/50">
            <CardHeader>
              <CardTitle className="text-base">📝 What to implement next</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-amber-800">
              <p><strong>Nudge store:</strong> Wire <code>useOfficeStore</code> nudges to a dedicated nudge slice with read/unread/dismissed/snoozed states.</p>
              <p><strong>Nudge API:</strong> Create <code>nudgesApi.get(id)</code> and <code>nudgesApi.dismiss(id)</code> for server-side nudge management.</p>
              <p><strong>Action buttons:</strong> "View in context" should deep-link to the relevant campaign, task, or intel artifact.</p>
              <p><strong>Snooze:</strong> Implement snooze with a Dragonfly-backed snooze timer — re-surface nudge after the snooze period.</p>
              <p><strong>Priority queue:</strong> Sort nudge feed by severity and recency. Allow bulk dismiss.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </RouteShell>
  );
}
