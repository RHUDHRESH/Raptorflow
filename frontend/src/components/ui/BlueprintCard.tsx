import React from 'react';
import { cn } from '@/lib/utils';

interface BlueprintCardProps {
  children: React.ReactNode;
  className?: string;
  showCorners?: boolean;
  padding?: 'sm' | 'md' | 'lg';
}

export function BlueprintCard({
  children,
  className,
  showCorners = false,
  padding = 'md'
}: BlueprintCardProps) {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  return (
    <div
      className={cn(
        'bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius)]',
        paddingClasses[padding],
        showCorners && 'relative',
        className
      )}
    >
      {showCorners && (
        <>
          <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-[var(--ink)]" />
          <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-[var(--ink)]" />
          <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-[var(--ink)]" />
          <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-[var(--ink)]" />
        </>
      )}
      {children}
    </div>
  );
}
