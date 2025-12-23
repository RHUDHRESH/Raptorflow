"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useMatrixOverview } from "@/hooks/useMatrixOverview";
import { Terminal, Database, Cpu } from "lucide-react";
import { MatrixListSkeleton } from "./LoadingSkeletons";
import { TelemetryEmptyState } from "./EmptyStates";

export function InferenceLogExplorer() {
  const { data, loading } = useMatrixOverview("verify_ws");
  
  if (loading) return <MatrixListSkeleton />;

  // SOTA: Mock data for explorer if API doesn't provide enough yet
  const events = data?.recent_events || [
    {
      event_id: "ev_1",
      timestamp: new Date().toISOString(),
      event_type: "inference_end",
      source: "MoveGenerator",
      metadata: { model: "gemini-1.5-ultra", latency_ms: 1240, tokens: 850 }
    },
    {
      event_id: "ev_2",
      timestamp: new Date(Date.now() - 5000).toISOString(),
      event_type: "tool_end",
      source: "WebSearch",
      metadata: { tool: "tavily", status: "success" }
    },
    {
      event_id: "ev_3",
      timestamp: new Date(Date.now() - 15000).toISOString(),
      event_type: "inference_end",
      source: "StrategyAligner",
      metadata: { model: "gemini-1.5-flash", latency_ms: 450, tokens: 320 }
    }
  ];

  return (
    <Card className="rounded-2xl border-border bg-card/50 shadow-sm overflow-hidden h-full font-mono">
      <CardHeader className="border-b border-border/50 bg-muted/5 font-sans">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="font-display text-xl">Inference Log</CardTitle>
            <CardDescription className="text-xs">Real-time metadata from the cognitive spine.</CardDescription>
          </div>
          <Terminal className="h-4 w-4 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[400px]">
          <div className="text-[11px] leading-relaxed">
            {events.length === 0 ? (
              <TelemetryEmptyState />
            ) : (
              events.map((event) => (
              <div key={event.event_id} className="p-3 border-b border-border/30 hover:bg-muted/10 transition-colors group">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-muted-foreground">[{new Date(event.timestamp).toLocaleTimeString()}]</span>
                    <span className="font-bold text-primary uppercase">{event.source}</span>
                  </div>
                  <Badge variant="outline" className="text-[9px] h-4 rounded-sm font-mono opacity-70 group-hover:opacity-100">
                    {event.event_type}
                  </Badge>
                </div>
                
                <div className="grid grid-cols-3 gap-2 mt-2 text-muted-foreground">
                  {event.metadata.model && (
                    <div className="flex items-center">
                      <Cpu className="mr-1 h-3 w-3" />
                      {event.metadata.model}
                    </div>
                  )}
                  {event.metadata.latency_ms && (
                    <div className="flex items-center">
                      <Terminal className="mr-1 h-3 w-3" />
                      {event.metadata.latency_ms}ms
                    </div>
                  )}
                  {event.metadata.tokens && (
                    <div className="flex items-center">
                      <Database className="mr-1 h-3 w-3" />
                      {event.metadata.tokens} tokens
                    </div>
                  )}
                </div>
                
                {/* Expandable JSON detail could go here */}
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
