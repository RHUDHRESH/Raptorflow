"use client";

import type * as React from "react";
import { useState } from "react";
import { useOfficeStore } from "@/state/office-store";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const MOCK_ALERTS = [
  { id: "alert-001", type: "competitor_shift", label: "Competitor positioning shift", source: "Competitor intel", severity: "major", time: "2h ago", summary: "Competitor X has shifted messaging from 'affordable' to 'enterprise-grade'." },
  { id: "alert-002", type: "ranking_change", label: "SERP ranking drop", source: "SEO monitor", severity: "warning", time: "4h ago", summary: "Keyword 'marketing automation software' dropped from #3 to #7 in 48h." },
  { id: "alert-003", type: "ad_spending", label: "Competitor ad spend spike", source: "Ad library", severity: "warning", time: "6h ago", summary: "Competitor Y increased LinkedIn ad budget by 3x this week." },
  { id: "alert-004", type: "social_mention", label: "New social mention", source: "Social monitor", severity: "info", time: "1h ago", summary: "Target ICP discussing 'marketing ops' in 5 new posts on LinkedIn." },
];

const SEVERITY_ORDER = { major: 0, warning: 1, info: 2 };

export default function IntelAlertsPage(): React.ReactElement {
  const [filter, setFilter] = useState<"all" | "major" | "warning" | "info">("all");
  const eventLog = useOfficeStore((s) => s.eventLog);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const liveAlerts = eventLog.filter((e) => (e.type || e.eventType) === "intel_alert_received");

  const allAlerts = [...MOCK_ALERTS.filter((a) => !dismissed.has(a.id)), ...liveAlerts.map((e) => ({
    id: (e.type || "live-alert") + Date.now() + Math.random(),
    type: "live",
    label: "Intel alert received",
    source: "WebSocket",
    severity: (e.payload as { severity?: string })?.severity ?? "info",
    time: "Just now",
    summary: JSON.stringify(e.payload || {}).slice(0, 100),
  }))];

  const filtered = filter === "all" ? allAlerts : allAlerts.filter((a) => a.severity === filter);

  const sorted = filtered.sort((a, b) => (SEVERITY_ORDER[a.severity as keyof typeof SEVERITY_ORDER] ?? 2) - (SEVERITY_ORDER[b.severity as keyof typeof SEVERITY_ORDER] ?? 2));

  return (
    <RouteShell
      eyebrow="Intel"
      title="Alert stream"
      description="Real-time intelligence alerts sorted by severity. Major alerts require immediate action."
      tags={["intel", "alerts", "realtime"]}
      backHref={"/intel" as "/intel"}
      backLabel="Back to Intel"
    >
      {/* Filters */}
      <div className="flex items-center gap-2">
        {(["all", "major", "warning", "info"] as const).map((f) => (
          <Button
            key={f}
            size="sm"
            variant={filter === f ? "default" : "outline"}
            onClick={() => setFilter(f)}
            className="capitalize"
          >
            {f} {f !== "all" && `(${MOCK_ALERTS.filter((a) => a.severity === f && !dismissed.has(a.id)).length})`}
          </Button>
        ))}
      </div>

      {/* Alert list */}
      <div className="space-y-3">
        {sorted.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <p className="text-3xl">✅</p>
              <p className="mt-4 font-medium">No alerts at this severity level</p>
              <p className="mt-1 text-sm text-[var(--muted-foreground)]">All clear — check back later</p>
            </CardContent>
          </Card>
        )}

        {sorted.map((alert) => (
          <Card key={alert.id} className={
            alert.severity === "major"
              ? "border-red-300 bg-red-50/50"
              : alert.severity === "warning"
              ? "border-amber-300 bg-amber-50/50"
              : ""
          }>
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <span className={`mt-1 h-3 w-3 rounded-full flex-shrink-0 ${
                    alert.severity === "major" ? "bg-red-500 animate-pulse" :
                    alert.severity === "warning" ? "bg-amber-500" : "bg-blue-500"
                  }`} />
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-semibold">{alert.label}</p>
                      <Badge variant="outline" className="text-xs">{alert.source}</Badge>
                    </div>
                    <p className="mt-1 text-sm text-[var(--muted-foreground)]">{alert.summary}</p>
                    <p className="mt-1 text-xs text-[var(--muted-foreground)]">{alert.time}</p>
                  </div>
                </div>
                <div className="flex flex-col gap-1">
                  <Button size="sm" variant="secondary">Take action</Button>
                  <Button size="sm" variant="ghost" onClick={() => setDismissed((d) => new Set([...d, alert.id]))}>
                    Dismiss
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-amber-200 bg-amber-50/50">
        <CardHeader>
          <CardTitle className="text-base">📝 What to implement next</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-amber-800">
          <p><strong>Backend:</strong> Create <code>alertsApi.list(filter)</code> and <code>alertsApi.dismiss(id)</code> — alerts stored in DB with dismissed/snoozed state.</p>
          <p><strong>Real-time:</strong> Wire WebSocket <code>intel_alert_received</code> events to push new alerts into this list without refresh.</p>
          <p><strong>Snooze:</strong> "Snooze for 24h" should set a snooze flag in the DB, hiding the alert from the feed temporarily.</p>
          <p><strong>Take action:</strong> Each alert type should link to the relevant context — competitor shift → Intel overview, ranking drop → campaign performance.</p>
          <p><strong>Push notifications:</strong> Major alerts should trigger browser push notifications (requires service worker + Notification API).</p>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
