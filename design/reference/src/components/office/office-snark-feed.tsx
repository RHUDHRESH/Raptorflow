"use client";

import type * as React from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOfficeStore } from "@/state/office-store";

export function OfficeSnarkFeed(): React.ReactElement {
  const snarkLines = useOfficeStore((state) => state.snarkLines);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Snark Feed</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {snarkLines.map((line) => (
          <div key={line.id} className="rounded-[18px] border border-[var(--border)] bg-white/70 p-4">
            <div className="mb-2 flex items-center justify-between gap-3">
              <p className="font-semibold">{line.speaker}</p>
              <Badge>{line.tone}</Badge>
            </div>
            <p className="text-sm text-[var(--muted-foreground)]">{line.body}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
