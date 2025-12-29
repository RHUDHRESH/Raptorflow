'use client';

import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Info } from 'lucide-react';

interface SkipTooltipProps {
  show: boolean;
  onClose: () => void;
}

/**
 * Small tooltip that appears when user skips a question
 * Explains that RaptorFlow will infer from other answers
 */
export function SkipTooltip({ show, onClose }: SkipTooltipProps) {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  if (!show) return null;

  return (
    <div
      className={cn(
        'fixed bottom-6 left-1/2 -translate-x-1/2 z-50',
        'bg-card border border-border rounded-xl px-4 py-3 shadow-lg',
        'flex items-center gap-3',
        'animate-in slide-in-from-bottom-4 fade-in duration-300'
      )}
    >
      <div className="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0">
        <Info className="h-4 w-4" />
      </div>
      <div>
        <p className="text-sm font-medium text-foreground">
          Skipped — no problem!
        </p>
        <p className="text-xs text-muted-foreground">
          We'll infer this from your other answers.
        </p>
      </div>
    </div>
  );
}
