"use client";

import type * as React from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOfficeStore } from "@/state/office-store";

export function OfficeFloorPlan(): React.ReactElement {
  const floorPlan = useOfficeStore((state) => state.floorPlan);
  const focusedZoneId = useOfficeStore((state) => state.focusedZoneId);
  const zoomLevel = useOfficeStore((state) => state.zoomLevel);
  const focusZone = useOfficeStore((state) => state.focusZone);

  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle>Floor Plan</CardTitle>
          <p className="text-sm text-[var(--muted-foreground)]">
            PixiJS will eventually render this as a live scene. For now it is a structured map of
            the office surface, pods, and debug zones.
          </p>
        </div>
        <Badge>Zoom {zoomLevel.toFixed(1)}x</Badge>
      </CardHeader>
      <CardContent className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {floorPlan.map((zone) => {
          const active = focusedZoneId === zone.id;
          return (
            <button
              key={zone.id}
              type="button"
              onClick={() => focusZone(zone.id)}
              className={[
                "rounded-[20px] border p-4 text-left transition-colors",
                active
                  ? "border-[var(--primary)] bg-[color:var(--primary)]/5"
                  : "border-[var(--border)] bg-white/70 hover:bg-white"
              ].join(" ")}
            >
              <div className="mb-3 flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-[var(--muted-foreground)]">
                    {zone.kind}
                  </p>
                  <p className="mt-1 text-base font-semibold">{zone.label}</p>
                </div>
                <Badge>{zone.status}</Badge>
              </div>
              <p className="text-sm text-[var(--muted-foreground)]">{zone.note}</p>
              <p className="mt-3 text-xs uppercase tracking-[0.18em] text-[var(--muted-foreground)]">
                Capacity: {zone.capacity}
              </p>
            </button>
          );
        })}
      </CardContent>
    </Card>
  );
}
