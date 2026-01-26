import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={cn(
      'bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius)] shadow-sm',
      className
    )}>
      {children}
    </div>
  );
}
