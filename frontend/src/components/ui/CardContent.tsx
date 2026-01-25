import React from 'react';
import { cn } from '@/lib/utils';

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export function CardContent({ children, className }: CardContentProps) {
  return (
    <div className={cn(
      'p-6 pt-4',
      className
    )}>
      {children}
    </div>
  );
}
