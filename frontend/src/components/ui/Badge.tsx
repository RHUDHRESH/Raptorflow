import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  className?: string;
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  const variantClasses = {
    default: 'bg-[var(--surface)] text-[var(--ink)] border border-[var(--border)]',
    success: 'bg-green-100 text-green-700 border border-green-200',
    warning: 'bg-amber-100 text-amber-700 border border-amber-200',
    error: 'bg-red-100 text-red-700 border border-red-200',
    info: 'bg-blue-100 text-blue-700 border border-blue-200'
  };

  return (
    <span className={cn(
      'inline-flex items-center justify-center rounded-full px-2.5 py-1 text-xs font-medium',
      variantClasses[variant],
      className
    )}>
      {children}
    </span>
  );
}
