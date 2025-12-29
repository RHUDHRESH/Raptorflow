'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, Cpu, Code, Activity } from 'lucide-react';
import { getTelemetryByMove } from '@/lib/blackbox';
import { cn } from '@/lib/utils';

export interface TelemetryTrace {
  id: string;
  agent_id: string;
  trace: {
    status?: string;
    error?: string;
    action?: string;
  };
  latency: number;
  timestamp: string;
}

interface TelemetryFeedProps {
  moveId?: string;
  traces?: TelemetryTrace[];
  className?: string;
}

export function TelemetryFeed({
  moveId,
  traces: initialTraces,
  className,
}: TelemetryFeedProps) {
  const [traces, setTraces] = useState<TelemetryTrace[]>(initialTraces || []);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (moveId) {
      const fetchTelemetry = async () => {
        const data = await getTelemetryByMove(moveId);
        setTraces(data);
      };
      fetchTelemetry();

      // Polling for "Live" effect if move is active
      const interval = setInterval(fetchTelemetry, 5000);
      return () => clearInterval(interval);
    }
  }, [moveId]);

  // Sync with props if provided
  useEffect(() => {
    if (initialTraces) setTraces(initialTraces);
  }, [initialTraces]);

  return (
    <Card
      className={cn(
        'border border-border bg-card/50 backdrop-blur-sm rounded-2xl shadow-none overflow-hidden',
        className
      )}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-accent animate-pulse" />
            <CardTitle className="text-sm font-bold font-sans uppercase tracking-widest text-muted-foreground">
              Live Telemetry
            </CardTitle>
          </div>
          <Badge
            variant="outline"
            className="font-mono text-[9px] uppercase tracking-tighter bg-accent/10 text-accent border-accent/20 px-1.5 py-0"
          >
            Agent Stream
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {traces.length === 0 ? (
            <p className="text-xs text-muted-foreground italic py-4 text-center">
              No telemetry traces yet.
            </p>
          ) : (
            traces.map((trace) => {
              const isError =
                trace.trace?.status === 'failed' || !!trace.trace?.error;
              return (
                <div
                  key={trace.id}
                  className="flex items-center justify-between py-2 border-b border-border/50 last:border-0 group hover:bg-accent/5 transition-colors rounded-lg px-2 -mx-2"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        'h-7 w-7 rounded flex items-center justify-center shrink-0',
                        isError ? 'bg-red-500/10' : 'bg-muted'
                      )}
                    >
                      <Cpu
                        className={cn(
                          'h-3.5 w-3.5',
                          isError ? 'text-red-500' : 'text-muted-foreground'
                        )}
                      />
                    </div>
                    <div className="min-w-0">
                      <div className="text-xs font-semibold font-sans flex items-center gap-1.5">
                        <span className="truncate">{trace.agent_id}</span>
                        {trace.trace?.action && (
                          <span className="text-[10px] text-muted-foreground font-normal shrink-0">
                            → {trace.trace.action}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-3 mt-0.5">
                        <span className="flex items-center gap-1 text-[9px] text-muted-foreground/60 font-mono">
                          <Clock className="h-2.5 w-2.5" />{' '}
                          {new Date(trace.timestamp).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                        <span className="flex items-center gap-1 text-[9px] text-muted-foreground/60 font-mono">
                          <Code className="h-2.5 w-2.5" />{' '}
                          {trace.latency.toFixed(0)}ms
                        </span>
                      </div>
                    </div>
                  </div>
                  <div
                    className={cn(
                      'h-1.5 w-1.5 rounded-full shrink-0',
                      isError
                        ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'
                        : 'bg-emerald-500'
                    )}
                  />
                </div>
              );
            })
          )}
        </div>
      </CardContent>
    </Card>
  );
}
