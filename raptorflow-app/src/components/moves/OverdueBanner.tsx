'use client';

import React from 'react';
import { AlertTriangle, Clock, Play, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface OverdueBannerProps {
  daysOverdue: number;
  onComplete: () => void;
  onExtend: () => void;
  onAbandon: () => void;
}

export function OverdueBanner({
  daysOverdue,
  onComplete,
  onExtend,
  onAbandon,
}: OverdueBannerProps) {
  if (daysOverdue <= 0) return null;

  return (
    <div className="bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-800/50 flex items-center justify-center text-amber-600 dark:text-amber-400 shrink-0">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-semibold text-amber-900 dark:text-amber-100">
            Move Overdue by {daysOverdue} Day{daysOverdue > 1 ? 's' : ''}
          </h3>
          <p className="text-sm text-amber-700 dark:text-amber-300">
            Don't let this drag on. Close it out or renegotiate the deadline.
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 w-full md:w-auto">
        <Button
          variant="outline"
          className="border-amber-300 text-amber-900 hover:bg-amber-100 dark:border-amber-700 dark:text-amber-100 dark:hover:bg-amber-800"
          onClick={onAbandon}
          title="Abandon Move"
        >
          <Trash2 className="w-4 h-4" />
        </Button>
        <Button
          variant="outline"
          className="border-amber-300 text-amber-900 hover:bg-amber-100 dark:border-amber-700 dark:text-amber-100 dark:hover:bg-amber-800"
          onClick={onExtend}
        >
          <Clock className="w-4 h-4 mr-2" />
          Extend 3 Days
        </Button>
        <Button
          className="bg-amber-600 hover:bg-amber-700 text-white border-0"
          onClick={onComplete}
        >
          <Play className="w-4 h-4 mr-2" />
          Complete Move
        </Button>
      </div>
    </div>
  );
}
