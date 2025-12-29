import React from 'react';
import { Move } from '@/lib/campaigns-types';
import { cn } from '@/lib/utils';
import {
  CheckCircle2,
  Circle,
  PlayCircle,
  AlertCircle,
  MoreHorizontal,
} from 'lucide-react';

interface MoveMiniCardProps {
  move: Move;
  onClick?: () => void;
}

export function MoveMiniCard({ move, onClick }: MoveMiniCardProps) {
  // Status Icon Logic
  const StatusIcon = () => {
    if (move.status === 'completed')
      return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
    if (move.status === 'active')
      return <PlayCircle className="w-4 h-4 text-blue-500" />;
    if (move.rag === 'red')
      return <AlertCircle className="w-4 h-4 text-red-500" />;
    return <Circle className="w-4 h-4 text-muted-foreground" />;
  };

  // Calculate progress based on checklist if available
  const progress = React.useMemo(() => {
    if (!move.checklist || move.checklist.length === 0) return 0;
    const completed = move.checklist.filter((i) => i.completed).length;
    return Math.round((completed / move.checklist.length) * 100);
  }, [move.checklist]);

  return (
    <div
      onClick={onClick}
      className="group flex items-center justify-between p-3 rounded-lg border border-border bg-card/50 hover:bg-muted/50 transition-all cursor-pointer"
    >
      <div className="flex items-center gap-3">
        <StatusIcon />

        <div className="flex flex-col">
          <span
            className={cn(
              'text-sm font-medium text-foreground',
              move.status === 'completed' &&
                'line-through text-muted-foreground'
            )}
          >
            {move.name}
          </span>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-[10px] uppercase tracking-wider text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
              {move.channel}
            </span>
            {/* RAG Indicator */}
            {move.rag && (
              <span
                className={cn(
                  'w-1.5 h-1.5 rounded-full',
                  move.rag === 'green'
                    ? 'bg-emerald-500'
                    : move.rag === 'amber'
                      ? 'bg-amber-500'
                      : 'bg-red-500'
                )}
              />
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Progress Bar */}
        <div className="hidden sm:flex flex-col items-end w-24 gap-1">
          <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary/80 transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="text-[10px] text-muted-foreground">{progress}%</span>
        </div>

        <MoreHorizontal className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
    </div>
  );
}
