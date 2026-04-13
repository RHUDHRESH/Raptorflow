"use client";

import type * as React from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useOfficeStore } from "@/state/office-store";

const surfaces = [
  { id: "floor_plan", label: "Floor Plan" },
  { id: "conference_room", label: "Conference Room" },
  { id: "snark", label: "Snark" },
  { id: "roster", label: "Roster" },
  { id: "debug", label: "Debug" }
] as const;

export function OfficeViewControls(): React.ReactElement {
  const mode = useOfficeStore((state) => state.mode);
  const surface = useOfficeStore((state) => state.surface);
  const zoomLevel = useOfficeStore((state) => state.zoomLevel);
  const setMode = useOfficeStore((state) => state.setMode);
  const setSurface = useOfficeStore((state) => state.setSurface);
  const setZoomLevel = useOfficeStore((state) => state.setZoomLevel);
  const zoomIn = useOfficeStore((state) => state.zoomIn);
  const zoomOut = useOfficeStore((state) => state.zoomOut);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge>Mode: {mode}</Badge>
        <Badge>Surface: {surface}</Badge>
        <Badge>Zoom: {zoomLevel.toFixed(1)}x</Badge>
      </div>
      <div className="grid gap-2 sm:grid-cols-3">
        <Button type="button" variant="secondary" onClick={() => setMode("passive")}>
          Passive
        </Button>
        <Button type="button" variant="default" onClick={() => setMode("active")}>
          Active
        </Button>
        <Button type="button" variant="secondary" onClick={() => setMode("debug")}>
          Debug
        </Button>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        <Button type="button" variant="secondary" onClick={() => zoomOut()}>
          Zoom out
        </Button>
        <Button type="button" variant="secondary" onClick={() => zoomIn()}>
          Zoom in
        </Button>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        <Button type="button" variant="secondary" onClick={() => setZoomLevel(1)}>
          Reset zoom
        </Button>
        <Button type="button" variant="secondary" onClick={() => setSurface("floor_plan")}>
          Focus floor plan
        </Button>
      </div>
      <div className="grid gap-2 md:grid-cols-2">
        {surfaces.map((item) => (
          <Button
            key={item.id}
            type="button"
            variant={surface === item.id ? "default" : "secondary"}
            onClick={() => setSurface(item.id)}
          >
            {item.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
