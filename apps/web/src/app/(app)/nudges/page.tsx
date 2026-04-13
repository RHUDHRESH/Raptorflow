"use client";

import type * as React from "react";
import type { Route } from "next";
import Link from "next/link";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const nudgeTypes = [
  "Intel nudge",
  "Performance nudge",
  "Opportunity nudge"
];

export default function NudgesPage(): React.ReactElement {
  return (
    <RouteShell
      eyebrow="Nudges"
      title="Nudges"
      description="Immediate, in-app alerts driven by the office WebSocket. Nudges surface from intelligence, campaign performance, and council events in real-time."
      tags={["alerts", "priority", "in-app", "websocket"]}
      rail={
        <Card>
          <CardHeader>
            <CardTitle>How nudges work</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="text-[var(--muted-foreground)]">
              Nudges are not REST API-driven. They are pushed to the browser via the office WebSocket connection as events occur.
            </p>
            <div className="space-y-2">
              <p className="font-medium">Event types that trigger nudges:</p>
              <ul className="list-inside list-disc space-y-1 text-[var(--muted-foreground)]">
                <li><code className="text-xs bg-[var(--muted)] px-1 rounded">intel_alert_received</code> — competitor intel detected</li>
                <li><code className="text-xs bg-[var(--muted)] px-1 rounded">task_missed_notification</code> — SLA breach on campaign task</li>
                <li><code className="text-xs bg-[var(--muted)] px-1 rounded">campaign_task_ready</code> — content move completed</li>
                <li><code className="text-xs bg-[var(--muted)] px-1 rounded">morning_meeting_start</code> — daily briefing available</li>
              </ul>
            </div>
            <p className="text-[var(--muted-foreground)]">
              The nudge store in <code>office-store.ts</code> accumulates these events. Individual nudge detail pages (<code>/nudges/[nudgeId]</code>) will fetch full context from the API.
            </p>
          </CardContent>
        </Card>
      }
    >
      <Card>
        <CardHeader>
          <CardTitle>Scaffolded alert classes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-[var(--muted-foreground)]">
            The route exists so the future implementation can attach prioritization, source links, and action buttons without changing navigation.
          </p>
          <div className="flex flex-wrap gap-2">
            {nudgeTypes.map((type) => (
              <span key={type} className="rounded-full border border-[var(--border)] bg-white/80 px-3 py-1 text-xs">
                {type}
              </span>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Live nudge feed</CardTitle>
            <Badge variant="outline" className="text-xs">
              Connect to office WebSocket to receive live nudges
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <p className="text-3xl">🔔</p>
            <p className="mt-4 font-medium">No live nudges</p>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">
              Nudges appear here in real-time when you are connected to the office WebSocket.
              Navigate to the <Link href="/office" className="underline">Office</Link> page to connect.
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        {nudgeTypes.map((type) => (
          <Card key={type}>
            <CardContent className="p-4">
              <p className="font-medium">{type}</p>
              <p className="mt-1 text-sm text-[var(--muted-foreground)]">
                Triggered by WebSocket events from the office canvas
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </RouteShell>
  );
}
