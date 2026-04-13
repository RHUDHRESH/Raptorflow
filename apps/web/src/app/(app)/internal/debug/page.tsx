"use client";

import * as React from "react";
import { useOfficeStore } from "@/state/office-store";
import { useFoundation } from "@/hooks/use-foundation";
import { RouteShell } from "@/components/layout/route-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { publicEnv } from "@/lib/env";

export default function InternalDebugPage(): React.ReactElement {
  const eventLog = useOfficeStore((s) => s.eventLog);
  const connectionStatus = useOfficeStore((s) => s.connectionStatus);
  const { data: foundation } = useFoundation();

  if (publicEnv.appEnv === "prod") {
    return (
      <RouteShell
        eyebrow="Internal"
        title="Debug tools"
        description="This page is not available in production."
        tags={["debug", "internal"]}
      >
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-3xl">🔒</p>
            <p className="mt-4 font-medium">Not available in production</p>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">
              The debug tools page is only available in non-production environments.
            </p>
          </CardContent>
        </Card>
      </RouteShell>
    );
  }

  return (
    <RouteShell
      eyebrow="Internal"
      title="Debug tools"
      description="Transport diagnostics, cache state, and contract introspection. Non-production only."
      tags={["debug", "internal"]}
    >
      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">WebSocket connection</CardTitle>
              <Badge className={
                connectionStatus === "connected" ? "bg-green-100 text-green-700" :
                connectionStatus === "connecting" ? "bg-amber-100 text-amber-700" :
                "bg-red-100 text-red-700"
              }>
                {connectionStatus}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-[var(--muted-foreground)]">Status</span>
              <span className="font-medium capitalize">{connectionStatus}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[var(--muted-foreground)]">Event log size</span>
              <span className="font-medium">{eventLog.length}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[var(--muted-foreground)]">Max event log</span>
              <span className="font-medium">500 (capped)</span>
            </div>
            <Button size="sm" variant="destructive" className="w-full">
              Disconnect socket
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Foundation cache</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-[var(--muted-foreground)]">Version</span>
              <span className="font-mono text-xs">{foundation?.version ?? "—"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[var(--muted-foreground)]">Sections loaded</span>
              <span className="font-medium">{foundation?.sections ? Object.keys(foundation.sections).length : 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[var(--muted-foreground)]">Updated at</span>
              <span className="font-mono text-xs">{foundation?.updatedAt ? new Date(foundation.updatedAt).toLocaleString() : "—"}</span>
            </div>
            <Button size="sm" variant="secondary" className="w-full">
              Invalidate cache
            </Button>
          </CardContent>
        </Card>

        <Card className="xl:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Recent event log (last 10)</CardTitle>
              <Button size="sm" variant="ghost" onClick={() => useOfficeStore.getState().clearEvents()}>
                Clear log
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {eventLog.length === 0 ? (
              <p className="py-4 text-center text-sm text-[var(--muted-foreground)]">
                No events received yet — connect to the office WebSocket to see events
              </p>
            ) : (
              <div className="space-y-2">
                {eventLog.slice(-10).reverse().map((e, i) => (
                  <div key={i} className="flex items-start gap-3 rounded-lg border border-[var(--border)] px-3 py-2 text-xs">
                    <span className="flex-shrink-0 rounded bg-[var(--muted)] px-1.5 py-0.5 font-mono">
                      {e.eventType}
                    </span>
                    <span className="truncate text-[var(--muted-foreground)]">
                      {JSON.stringify(e.payload).slice(0, 100)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="border-red-200 bg-red-50/50">
        <CardHeader>
          <CardTitle className="text-base">⚠️ Production warning</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-red-800">
          This page exposes internal system state. It should only be accessible in non-production environments. Gate with <code>APP_ENV != "prod"</code> check at the route level before deployment.
        </CardContent>
      </Card>
    </RouteShell>
  );
}
