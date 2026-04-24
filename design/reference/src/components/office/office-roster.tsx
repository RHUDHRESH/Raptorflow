"use client";

import type * as React from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOfficeStore } from "@/state/office-store";

export function OfficeRoster(): React.ReactElement {
  const roster = useOfficeStore((state) => state.roster);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Roster</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {roster.map((agent) => (
          <div
            key={agent.agentKey}
            className="flex items-start justify-between gap-4 rounded-[18px] border border-[var(--border)] bg-white/70 p-4"
          >
            <div className="space-y-1">
              <p className="font-semibold">{agent.displayName}</p>
              <p className="text-sm text-[var(--muted-foreground)]">{agent.role}</p>
              <p className="text-xs text-[var(--muted-foreground)]">{agent.posture}</p>
            </div>
            <div className="space-y-2 text-right">
              <Badge>{agent.status}</Badge>
              <p className="text-xs text-[var(--muted-foreground)]">{agent.zoneId}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
