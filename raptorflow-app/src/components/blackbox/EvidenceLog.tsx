'use client';

import React from 'react';
import {
  ExternalLink,
  FileText,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface EvidenceTrace {
  id: string;
  agent_id: string;
  trace: {
    input?: any;
    output?: any;
    error?: string;
    status?: string;
  };
  latency: number;
  timestamp: string;
}

interface EvidenceLogProps {
  traces: EvidenceTrace[];
  isLoading?: boolean;
}

export function EvidenceLog({ traces, isLoading }: EvidenceLogProps) {
  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-20 bg-muted rounded-xl" />
        ))}
      </div>
    );
  }

  if (traces.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-4 text-center border border-dashed rounded-2xl bg-muted/30">
        <FileText className="h-8 w-8 text-muted-foreground/50 mb-3" />
        <p className="text-sm font-sans text-muted-foreground">
          No evidence links found for this insight.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {traces.map((trace) => {
        const isError = trace.trace.status === 'failed' || !!trace.trace.error;

        return (
          <div
            key={trace.id}
            className={cn(
              'group p-4 rounded-xl border transition-all duration-200 hover:shadow-md',
              isError
                ? 'border-red-500/20 bg-red-500/5'
                : 'border-border bg-card hover:border-accent/30'
            )}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div
                  className={cn(
                    'mt-1 p-2 rounded-lg shrink-0',
                    isError
                      ? 'bg-red-500/10 text-red-500'
                      : 'bg-accent/10 text-accent'
                  )}
                >
                  {isError ? (
                    <AlertCircle size={16} />
                  ) : (
                    <CheckCircle2 size={16} />
                  )}
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground font-sans">
                      {trace.agent_id}
                    </span>
                    <span className="text-[10px] text-muted-foreground/60 font-mono">
                      {new Date(trace.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <h4 className="text-sm font-medium font-sans leading-snug">
                    {isError
                      ? 'Agent Execution Failed'
                      : `Evidence from ${trace.agent_id}`}
                  </h4>
                  {trace.trace.output &&
                    typeof trace.trace.output === 'object' &&
                    trace.trace.output.url && (
                      <a
                        href={trace.trace.output.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-xs text-accent hover:underline mt-1 font-sans"
                      >
                        <ExternalLink size={12} />
                        {new URL(trace.trace.output.url).hostname}
                      </a>
                    )}
                  {trace.trace.error && (
                    <p className="text-xs text-red-500/80 font-mono mt-1 line-clamp-2">
                      {trace.trace.error}
                    </p>
                  )}
                </div>
              </div>
              <div className="text-[10px] font-mono text-muted-foreground/40 whitespace-nowrap">
                {trace.latency.toFixed(2)}s
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
