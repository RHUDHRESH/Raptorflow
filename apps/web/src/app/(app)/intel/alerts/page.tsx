"use client";

import * as React from "react";
import { useMemo, useState } from "react";
import { useOfficeStore } from "@/state/office-store";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const SEVERITY_ORDER = { major: 0, warning: 1, info: 2 };

export default function IntelAlertsPage(): React.ReactElement {
  const [filter, setFilter] = useState<"all" | "major" | "warning" | "info">("all");
  const eventLog = useOfficeStore((s) => s.eventLog);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const liveAlerts = useMemo(
    () =>
      eventLog
        .filter((event) => (event.type || event.eventType) === "intel_alert_received")
        .map((event, index) => {
          const severity = (event.payload as { severity?: string })?.severity ?? "info";
          return {
            id: `${event.timestamp}-${index}`,
            type: "live",
            label: "Intel alert received",
            source: "WebSocket",
            severity,
            time: new Date(event.timestamp).toLocaleTimeString("en-IN", {
              hour: "numeric",
              minute: "2-digit",
            }),
            summary: JSON.stringify(event.payload || {}).slice(0, 120),
          };
        })
        .filter((alert) => !dismissed.has(alert.id)),
    [dismissed, eventLog],
  );

  const filtered =
    filter === "all" ? liveAlerts : liveAlerts.filter((alert) => alert.severity === filter);
  const sorted = [...filtered].sort(
    (a, b) =>
      (SEVERITY_ORDER[a.severity as keyof typeof SEVERITY_ORDER] ?? 2) -
      (SEVERITY_ORDER[b.severity as keyof typeof SEVERITY_ORDER] ?? 2),
  );

  return (
    <RouteShell
      eyebrow="Intel"
      title="Alert stream"
      description="Live intelligence alerts pushed through the office event stream."
      tags={["intel", "alerts", "realtime"]}
      backHref={"/intel" as "/intel"}
      backLabel="Back to Intel"
    >
      <div className="flex items-center gap-2">
        {(["all", "major", "warning", "info"] as const).map((f) => (
          <Button
            key={f}
            size="sm"
            variant={filter === f ? "default" : "outline"}
            onClick={() => setFilter(f)}
            className="capitalize"
          >
            {f} {f !== "all" && `(${liveAlerts.filter((alert) => alert.severity === f).length})`}
          </Button>
        ))}
      </div>

      <div className="space-y-3">
        {sorted.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <p className="text-3xl">✅</p>
              <p className="mt-4 font-medium">No live intel alerts yet</p>
              <p className="mt-1 text-sm text-[var(--muted-foreground)]">
                Alerts appear here when the backend emits intel events.
              </p>
            </CardContent>
          </Card>
        )}

        {sorted.map((alert) => (
          <Card
            key={alert.id}
            className={
              alert.severity === "major"
                ? "border-red-300 bg-red-50/50"
                : alert.severity === "warning"
                  ? "border-amber-300 bg-amber-50/50"
                  : ""
            }
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <span
                    className={`mt-1 h-3 w-3 rounded-full flex-shrink-0 ${
                      alert.severity === "major"
                        ? "bg-red-500 animate-pulse"
                        : alert.severity === "warning"
                          ? "bg-[#D97757]"
                          : "bg-blue-500"
                    }`}
                  />
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-semibold">{alert.label}</p>
                      <Badge variant="outline" className="text-xs">
                        {alert.source}
                      </Badge>
                    </div>
                    <p className="mt-1 text-sm text-[var(--muted-foreground)]">{alert.summary}</p>
                    <p className="mt-1 text-xs text-[var(--muted-foreground)]">{alert.time}</p>
                  </div>
                </div>
                <div className="flex flex-col gap-1">
                  <Button size="sm" variant="secondary">
                    Take action
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setDismissed((current) => new Set([...current, alert.id]))}
                  >
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
          <p>
            <strong>Backend:</strong> Persist alert events in the DB instead of only the client
            event log.
          </p>
          <p>
            <strong>Real-time:</strong> Keep wiring WebSocket <code>intel_alert_received</code>{" "}
            events so they show up here without refresh.
          </p>
          <p>
            <strong>Snooze:</strong> "Snooze for 24h" should be a DB-backed state instead of a local
            dismissal.
          </p>
          <p>
            <strong>Take action:</strong> Each alert type should link to the relevant backend
            context.
          </p>
          <p>
            <strong>Push notifications:</strong> Major alerts should trigger browser push
            notifications once the service worker exists.
          </p>
        </CardContent>
      </Card>
    </RouteShell>
  );
}
