'use client';

import React from 'react';
import { Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Spinner } from '@/components/ui/spinner';

interface InferenceStatusIndicatorProps {
  status: 'idle' | 'generating' | 'complete' | 'error';
  className?: string;
}

/**
 * SOTA Status Indicator for Agentic Inference
 */
export function InferenceStatusIndicator({
  status,
  className,
}: InferenceStatusIndicatorProps) {
  if (status === 'idle') return null;

  return (
    <div
      className={cn(
        'flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium animate-in fade-in duration-300',
        status === 'generating' && 'bg-accent/5 border-accent/20 text-accent',
        status === 'complete' &&
          'bg-emerald-50 border-emerald-200 text-emerald-700 dark:bg-emerald-950/10 dark:border-emerald-900/20 dark:text-emerald-400',
        status === 'error' &&
          'bg-red-50 border-red-200 text-red-700 dark:bg-red-950/10 dark:border-red-900/20 dark:text-red-400',
        className
      )}
    >
      {status === 'generating' ? (
        <>
          <Spinner className="w-3 h-3" />
          <span>Agent thinking...</span>
        </>
      ) : status === 'complete' ? (
        <>
          <Sparkles className="w-3 h-3" />
          <span>Strategy Hardened</span>
        </>
      ) : (
        <span>Inference Interrupted</span>
      )}
    </div>
  );
}
