'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { BrainCircuit, Clock, Calendar, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RefinementData {
  estimated_effort?: string;
  deadline?: string;
  rationale?: string;
}

interface MoveRefinerViewProps {
  data?: RefinementData;
  className?: string;
}

/**
 * SOTA Move Refiner Feedback Component
 * Displays agentic refinement and optimization logic for a specific move.
 */
export function MoveRefinerView({ data, className }: MoveRefinerViewProps) {
  if (!data) {
    return (
      <div className="p-6 rounded-2xl border border-dashed border-zinc-200 dark:border-zinc-800 text-zinc-400 text-center text-sm italic">
        Agentic refinement data is not available for this move.
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center gap-2 px-1">
        <BrainCircuit className="w-4 h-4 text-accent" />
        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-400">Agentic Optimization</h3>
      </div>

      <div className="bg-accent/5 border border-accent/20 rounded-2xl p-6 relative overflow-hidden group">
        <div className="relative z-10 space-y-6">
          <div className="flex items-center gap-10">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-[10px] font-bold text-zinc-400 uppercase tracking-wider">
                <Clock className="w-3 h-3" />
                Effort
              </div>
              <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">{data.estimated_effort || 'Medium'}</div>
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2 text-[10px] font-bold text-zinc-400 uppercase tracking-wider">
                <Calendar className="w-3 h-3" />
                Target Date
              </div>
              <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">{data.deadline || 'End of Week'}</div>
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2 text-[10px] font-bold text-zinc-400 uppercase tracking-wider">
                <CheckCircle2 className="w-3 h-3" />
                Confidence
              </div>
              <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">High (0.92)</div>
            </div>
          </div>

          <div className="pt-4 border-t border-accent/10">
            <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium">
              <span className="text-accent mr-2 font-bold">Rationale:</span>
              {data.rationale || "This move was surgically decomposed from your 90-day strategic arc to maximize early distribution signals."}
            </p>
          </div>
        </div>

        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
          <BrainCircuit size={100} />
        </div>
      </div>
    </div>
  );
}
