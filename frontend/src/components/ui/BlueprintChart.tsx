import React from 'react';
import { cn } from '@/lib/utils';

interface BlueprintChartProps {
  data?: any[];
  type?: 'line' | 'bar' | 'pie';
  className?: string;
}

export function BlueprintChart({ data = [], type = 'line', className }: BlueprintChartProps) {
  return (
    <div className={cn(
      'w-full h-64 bg-[var(--surface)] border border-[var(--border)] rounded-[var(--radius)] flex items-center justify-center text-[var(--muted)]',
      className
    )}>
      <div className="text-center">
        <div className="text-sm">Chart Component</div>
        <div className="text-xs mt-1">Type: {type}</div>
        <div className="text-xs">Data points: {data.length}</div>
      </div>
    </div>
  );
}
