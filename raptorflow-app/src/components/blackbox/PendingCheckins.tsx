'use client';

import React from 'react';
import { Experiment } from '@/lib/blackbox-types';
import { Button } from '@/components/ui/button';
import { Rocket, Clock } from 'lucide-react';

interface PendingCheckinsProps {
  experiments: Experiment[];
  onReview: (experiment: Experiment) => void;
}

export function PendingCheckins({
  experiments,
  onReview,
}: PendingCheckinsProps) {
  if (experiments.length === 0) return null;

  return (
    <div className="flex flex-col gap-4">
      <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-400 mb-2">
        Pending Check-ins
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {experiments.map((exp) => (
          <div
            key={exp.id}
            className="flex items-center gap-4 p-4 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl"
          >
            <div className="w-10 h-10 rounded-lg bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 flex items-center justify-center shrink-0">
              <Rocket className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 truncate">
                {exp.title}
              </h4>
              <div className="flex items-center gap-1.5 text-[10px] text-zinc-500 font-medium">
                <Clock className="w-3 h-3" />
                Launched {new Date(exp.launched_at!).toLocaleDateString()}
              </div>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => onReview(exp)}
              className="rounded-lg text-xs font-bold"
            >
              Review Result
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
