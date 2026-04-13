"use client";

import type * as React from "react";
import { useEffect, useState } from "react";
import { useUser } from "@clerk/nextjs";
import { OfficeCanvas } from "@/components/office/office-canvas";
import { OfficeHud } from "@/components/office/office-hud";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { useOfficeSocket, type OfficeSocketStatus } from "@/lib/socket";

export function OfficeShell(): React.ReactElement {
  const { user } = useUser();
  const orgId = user?.publicMetadata?.orgId as string | undefined;
  const [wsStatus, setWsStatus] = useState<OfficeSocketStatus>("disconnected");

  const { socket, addStatusListener, disconnect } = useOfficeSocket(orgId ?? "");

  useEffect(() => {
    if (!orgId) return;

    socket.connect();
    const unsubscribe = addStatusListener(setWsStatus);

    return () => {
      unsubscribe();
      disconnect();
    };
  }, [orgId, socket, addStatusListener, disconnect]);

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.55fr)_minmax(360px,0.45fr)]">
      <div className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <p className="text-sm uppercase tracking-[0.22em] text-[var(--muted-foreground)]">
              The Office
            </p>
            <div className="flex items-center gap-2">
              <div
                className={`h-2 w-2 rounded-full ${
                  wsStatus === "connected"
                    ? "bg-green-500"
                    : wsStatus === "connecting"
                      ? "bg-amber-500 animate-pulse"
                      : "bg-red-400"
                }`}
              />
              <span className="text-xs text-[var(--muted-foreground)] capitalize">{wsStatus}</span>
            </div>
          </div>
          <h1 className="font-[family-name:var(--font-display)] text-4xl">
            Event-driven canvas and ops scaffold
          </h1>
          <div className="flex flex-wrap gap-2">
            <Badge>Floor plan</Badge>
            <Badge>Zoom and pan</Badge>
            <Badge>Snark</Badge>
            <Badge>Roster</Badge>
            <Badge>Debug surfaces</Badge>
            {orgId && <Badge variant="outline">org: {orgId.slice(0, 8)}…</Badge>}
          </div>
          <p className="max-w-2xl text-sm text-[var(--muted-foreground)]">
            The office canvas connects via WebSocket to receive real-time agent activity, speech
            bubbles, zone state changes, and council events. Agents render as colored avatars on the
            floor plan.
          </p>
        </div>

        {!orgId && (
          <Card className="border-amber-300 bg-amber-50/50">
            <CardContent className="p-4 text-sm text-amber-700">
              Sign in with an organization to connect to the live office WebSocket.
            </CardContent>
          </Card>
        )}

        <OfficeCanvas />
      </div>

      <OfficeHud />
    </div>
  );
}
