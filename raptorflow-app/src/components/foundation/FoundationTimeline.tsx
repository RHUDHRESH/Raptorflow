'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Clock, CheckCircle2, User, Sparkles, Target } from 'lucide-react';

export interface TimelineEvent {
  id: string;
  date: string;
  type: 'voice' | 'positioning' | 'identity' | 'checkpoint';
  description: string;
  author: string;
}

interface FoundationTimelineProps {
  events: TimelineEvent[];
  className?: string;
}

export function FoundationTimeline({
  events,
  className,
}: FoundationTimelineProps) {
  const sortedEvents = [...events].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );

  const getIcon = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'voice':
        return <Sparkles className="h-3 w-3" />;
      case 'positioning':
        return <Target className="h-3 w-3" />;
      case 'checkpoint':
        return <CheckCircle2 className="h-3 w-3" />;
      default:
        return <User className="h-3 w-3" />;
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div
      className={cn(
        'p-8 rounded-[24px] bg-card border border-border flex flex-col transition-all duration-300',
        className
      )}
    >
      <div className="flex items-center gap-3 mb-8">
        <div className="h-8 w-8 rounded-lg bg-primary/5 flex items-center justify-center">
          <Clock className="h-4 w-4 text-primary/60" />
        </div>
        <h3 className="text-[11px] font-semibold uppercase tracking-[0.2em] text-muted-foreground/80 font-sans">
          Brand History
        </h3>
      </div>

      <div className="relative space-y-8">
        {/* Vertical Line */}
        <div className="absolute left-[15px] top-2 bottom-2 w-[1px] bg-border/40" />

        {sortedEvents.map((event, idx) => (
          <motion.div
            key={event.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1, duration: 0.5 }}
            className="relative pl-10 group"
          >
            {/* Dot / Icon */}
            <div className="absolute left-0 top-1 h-[31px] w-[31px] rounded-full bg-background border border-border flex items-center justify-center z-10 group-hover:border-primary/40 transition-colors">
              <div className="text-muted-foreground group-hover:text-primary transition-colors">
                {getIcon(event.type)}
              </div>
            </div>

            <div className="flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">
                  {formatDate(event.date)}
                </span>
                <span className="text-[9px] font-sans font-medium text-muted-foreground/60 bg-muted/30 px-2 py-0.5 rounded-full uppercase tracking-tight">
                  {event.author}
                </span>
              </div>
              <p className="text-sm font-sans text-foreground/90 leading-relaxed">
                {event.description}
              </p>
            </div>
          </motion.div>
        ))}

        {sortedEvents.length === 0 && (
          <div className="py-12 text-center">
            <p className="text-xs text-muted-foreground italic font-sans">
              No history recorded yet.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
