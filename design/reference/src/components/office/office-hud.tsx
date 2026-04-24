"use client";

import type * as React from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOfficeStore } from "@/state/office-store";
import { OfficeDebugPanel } from "@/components/office/office-debug-panel";
import { OfficeRoster } from "@/components/office/office-roster";
import { OfficeSnarkFeed } from "@/components/office/office-snark-feed";
import { OfficeViewControls } from "@/components/office/office-view-controls";

export function OfficeHud(): React.ReactElement {
  const mode = useOfficeStore((state) => state.mode);
  const surface = useOfficeStore((state) => state.surface);
  const zoomLevel = useOfficeStore((state) => state.zoomLevel);
  const focusedZoneId = useOfficeStore((state) => state.focusedZoneId);
  const clearEvents = useOfficeStore((state) => state.clearEvents);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Office HUD</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-[var(--muted-foreground)]">
          <div className="flex flex-wrap gap-2">
            <Badge>Mode {mode}</Badge>
            <Badge>Surface {surface}</Badge>
            <Badge>Zoom {zoomLevel.toFixed(1)}x</Badge>
          </div>
          <p>Focused zone: {focusedZoneId}</p>
          <p>
            Speech bubbles, snark, roster state, and debug surfaces are scaffolded here as
            independent panels instead of a single empty placeholder.
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>View Controls</CardTitle>
        </CardHeader>
        <CardContent>
          <OfficeViewControls />
        </CardContent>
      </Card>
      <OfficeRoster />
      <OfficeSnarkFeed />
      <OfficeDebugPanel />
      <Card>
        <CardHeader>
          <CardTitle>Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <Button type="button" variant="secondary" onClick={() => clearEvents()}>
            Clear event log
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
