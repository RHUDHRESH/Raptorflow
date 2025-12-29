'use client';

import React, { useMemo } from 'react';
import { FoundationData } from '@/lib/foundation';
import { cn } from '@/lib/utils';
import { Sparkles } from 'lucide-react';

interface PositioningPreviewProps {
  data: FoundationData;
  className?: string;
}

/**
 * Live-updating positioning statement preview
 * Shows the positioning formula as user fills in data
 */
export function PositioningPreview({
  data,
  className,
}: PositioningPreviewProps) {
  const { category, targetAudience, psychologicalOutcome } =
    data.positioning || {};

  const hasAnyValue = category || targetAudience || psychologicalOutcome;

  // Determine completeness for styling
  const completeness = useMemo(() => {
    let filled = 0;
    if (category) filled++;
    if (targetAudience) filled++;
    if (psychologicalOutcome) filled++;
    return filled;
  }, [category, targetAudience, psychologicalOutcome]);

  if (!hasAnyValue) return null;

  return (
    <div
      className={cn(
        'bg-gradient-to-br from-card to-muted/30 border border-border rounded-2xl p-6 relative overflow-hidden',
        className
      )}
    >
      {/* Sparkle decoration */}
      <div className="absolute top-4 right-4 text-primary/20">
        <Sparkles className="h-6 w-6" />
      </div>

      <div className="mb-3">
        <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
          Your Positioning
        </span>
      </div>

      <p className="font-serif text-lg leading-relaxed text-foreground">
        We are the{' '}
        <span
          className={cn(
            'font-semibold transition-all duration-300',
            category ? 'text-foreground' : 'text-muted-foreground/50'
          )}
        >
          {category || '_____'}
        </span>{' '}
        for{' '}
        <span
          className={cn(
            'font-semibold transition-all duration-300',
            targetAudience ? 'text-foreground' : 'text-muted-foreground/50'
          )}
        >
          {targetAudience || '_____'}
        </span>{' '}
        who want{' '}
        <span
          className={cn(
            'font-semibold transition-all duration-300',
            psychologicalOutcome
              ? 'text-foreground'
              : 'text-muted-foreground/50'
          )}
        >
          {psychologicalOutcome || '_____'}
        </span>
        .
      </p>

      {/* Progress indicator */}
      <div className="mt-4 flex items-center gap-2">
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={cn(
                'h-1.5 w-6 rounded-full transition-colors duration-300',
                i < completeness ? 'bg-primary' : 'bg-border'
              )}
            />
          ))}
        </div>
        <span className="text-xs text-muted-foreground">
          {completeness === 3 ? 'Complete!' : `${completeness}/3 filled`}
        </span>
      </div>
    </div>
  );
}
