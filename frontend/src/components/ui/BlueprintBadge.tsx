import React from 'react';
import { cn } from '@/lib/utils';

interface BlueprintBadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md';
  className?: string;
}

export function BlueprintBadge({
  children,
  variant = 'default',
  size = 'md',
  className
}: BlueprintBadgeProps) {
  const baseClasses = 'inline-flex items-center justify-center rounded-full font-medium';

  const variantClasses = {
    default: 'bg-[var(--surface)] text-[var(--ink)] border border-[var(--border)]',
    success: 'bg-green-100 text-green-700 border border-green-200',
    warning: 'bg-amber-100 text-amber-700 border border-amber-200',
    error: 'bg-red-100 text-red-700 border border-red-200',
    info: 'bg-blue-100 text-blue-700 border border-blue-200'
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm'
  };

  return (
    <span className={cn(
      baseClasses,
      variantClasses[variant],
      sizeClasses[size],
      className
    )}>
      {children}
    </span>
  );
}
