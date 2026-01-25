import React from 'react';
import { cn } from '@/lib/utils';

interface PageHeaderProps {
  title: string;
  descriptor?: string;
  moduleCode?: string;
  actions?: React.ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  descriptor,
  moduleCode,
  actions,
  className
}: PageHeaderProps) {
  return (
    <div className={cn(
      'mb-6 pb-6 border-b border-[var(--border)]',
      className
    )}>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">{title}</h1>
          {descriptor && (
            <p className="text-sm text-[var(--muted)] mt-1">{descriptor}</p>
          )}
          {moduleCode && (
            <code className="text-xs bg-[var(--surface)] px-2 py-1 rounded text-[var(--muted)] mt-2 inline-block">
              {moduleCode}
            </code>
          )}
        </div>
        {actions && (
          <div className="flex items-center gap-2">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
