import React from 'react';
import { cn } from '@/lib/utils';

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={cn(
      'p-6 pb-4 border-b border-[var(--border)]',
      className
    )}>
      {children}
    </div>
  );
}
