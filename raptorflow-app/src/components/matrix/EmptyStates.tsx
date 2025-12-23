"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Ghost, Terminal } from "lucide-react";

export function MatrixEmptyState({ title, message }: { title: string; message: string }) {
  return (
    <Card className="rounded-2xl border-border border-dashed bg-muted/5 shadow-none h-full min-h-[200px] flex items-center justify-center">
      <CardContent className="p-6 flex flex-col items-center text-center space-y-3">
        <div className="p-3 rounded-full bg-muted/10">
          <Ghost className="h-6 w-6 text-muted-foreground/50" />
        </div>
        <div>
          <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">{title}</h3>
          <p className="text-xs text-muted-foreground/70 mt-1 max-w-[200px] leading-relaxed italic">
            {message}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

export function TelemetryEmptyState() {
  return (
    <div className="h-full flex flex-col items-center justify-center p-12 text-center space-y-4">
      <div className="p-4 rounded-2xl bg-primary/5 border border-primary/10">
        <Terminal className="h-8 w-8 text-primary/40" />
      </div>
      <div>
        <h3 className="font-display text-lg text-primary/60">Silence in the Spine</h3>
        <p className="text-sm text-muted-foreground max-w-[250px] mx-auto mt-2">
          No agentic activity detected in the last 24 hours. The ecosystem is currently dormant.
        </p>
      </div>
    </div>
  );
}
