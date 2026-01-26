import React from 'react';
import { cn } from '@/lib/utils';

interface CardTitleProps {
  children: React.ReactNode;
  className?: string;
}

export function CardTitle({ children, className }: CardTitleProps) {
  return (
    <h3 className={cn(
      'text-lg font-semibold text-[var(--ink)]',
      className
    )}>
      {children}
    </h3>
  );
}
