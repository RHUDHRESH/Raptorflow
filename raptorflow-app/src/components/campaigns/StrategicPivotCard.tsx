'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles, ArrowUpRight, ShieldAlert, History } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StrategicPivot {
  id: string;
  title: string;
  description: string;
  rationale: string;
  severity: 'low' | 'medium' | 'high';
}

interface StrategicPivotCardProps {
  pivot: StrategicPivot;
  onApply: (id: string) => void;
  onIgnore: (id: string) => void;
}

/**
 * SOTA Strategic Pivot Card (Task 21)
 * Presents agent-recommended strategic shifts with actionable buttons.
 */
export function StrategicPivotCard({ pivot, onApply, onIgnore }: StrategicPivotCardProps) {
  return (
    <Card className="p-6 border border-accent/20 bg-accent/5 backdrop-blur-sm relative overflow-hidden group rounded-[2rem]">
      <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
        <Sparkles size={80} />
      </div>

      <div className="flex items-start gap-5">
        <div className={cn(
          "h-12 w-12 rounded-2xl flex items-center justify-center shrink-0 shadow-lg shadow-accent/10",
          pivot.severity === 'high' ? "bg-red-500 text-white" : "bg-accent text-accent-foreground"
        )}>
          {pivot.severity === 'high' ? <ShieldAlert size={24} /> : <ArrowUpRight size={24} />}
        </div>

        <div className="space-y-2 flex-1">
          <div className="flex items-center justify-between">
            <h3 className="font-display font-semibold text-xl text-zinc-900 dark:text-zinc-100">{pivot.title}</h3>
            <span className={cn(
              "text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border",
              pivot.severity === 'high' ? "bg-red-50 border-red-200 text-red-700" : "bg-accent/10 border-accent/20 text-accent"
            )}>
              {pivot.severity} PRIORITY
            </span>
          </div>

          <p className="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed font-medium">
            {pivot.description}
          </p>

          <div className="bg-white/50 dark:bg-zinc-900/50 p-4 rounded-xl border border-zinc-100 dark:border-zinc-800 flex gap-3 items-start mt-4">
            <History size={16} className="text-zinc-400 mt-0.5" />
            <p className="text-xs text-zinc-500 italic leading-snug">
              Rationale: {pivot.rationale}
            </p>
          </div>

          <div className="pt-6 flex items-center gap-3">
            <Button
              onClick={() => onApply(pivot.id)}
              className="rounded-xl h-10 bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 px-6 font-medium shadow-xl hover:-translate-y-0.5 transition-transform"
            >
              Apply Strategy Shift
            </Button>
            <Button
              variant="ghost"
              onClick={() => onIgnore(pivot.id)}
              className="text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
            >
              Archive Recommendation
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
}
