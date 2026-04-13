"use client";

import type * as React from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOfficeStore } from "@/state/office-store";
import { officeEventTypes } from "@/state/office-types";

export function OfficeDebugPanel(): React.ReactElement {
  const debugSurfaces = useOfficeStore((state) => state.debugSurfaces);
  const eventLog = useOfficeStore((state) => state.eventLog);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Debug Surfaces</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3">
          {debugSurfaces.map((surface) => (
            <div
              key={surface.id}
              className="rounded-[18px] border border-[var(--border)] bg-white/70 p-4"
            >
              <div className="mb-2 flex items-center justify-between gap-3">
                <p className="font-semibold">{surface.label}</p>
                <Badge>{surface.id}</Badge>
              </div>
              <p className="text-sm text-[var(--muted-foreground)]">{surface.value}</p>
              <p className="mt-2 text-xs text-[var(--muted-foreground)]">{surface.hint}</p>
            </div>
          ))}
        </div>
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted-foreground)]">
            Event types reserved
          </p>
          <div className="flex flex-wrap gap-2">
            {officeEventTypes.map((eventType) => (
              <Badge key={eventType}>{eventType}</Badge>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted-foreground)]">
            Event log
          </p>
          {eventLog.slice(-4).map((event) => (
            <div
              key={`${event.type}-${event.eventType}`}
              className="rounded-[18px] border border-[var(--border)] bg-white/70 p-3 text-sm"
            >
              <p className="font-medium">{event.eventType}</p>
              <p className="text-[var(--muted-foreground)]">
                {event.payload ? JSON.stringify(event.payload) : "No payload"}
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
