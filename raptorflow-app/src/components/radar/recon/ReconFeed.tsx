'use client';

import React from 'react';
import { Signal } from '../types';
import { SignalCard } from './SignalCard';
import { Sparkles } from 'lucide-react';

interface ReconFeedProps {
  signals: Signal[];
}

export function ReconFeed({ signals }: ReconFeedProps) {
  if (signals.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center border border-dashed border-border/60 rounded-xl bg-card/30">
        <Sparkles className="h-8 w-8 text-muted-foreground/30 mb-4" />
        <p className="text-muted-foreground font-medium">No signals found.</p>
        <p className="text-sm text-muted-foreground/60 mt-1">
          Try widening your filters.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      {signals.map((signal) => (
        <SignalCard key={signal.id} signal={signal} />
      ))}

      <div className="py-8 text-center text-xs text-muted-foreground/40 uppercase tracking-widest font-medium">
        All caught up
      </div>
    </div>
  );
}
