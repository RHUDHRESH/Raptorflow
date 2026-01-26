import React from 'react';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface BlueprintKPIProps {
  title: string;
  value: string;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
  };
  className?: string;
}

export function BlueprintKPI({
  title,
  value,
  subtitle,
  icon,
  trend,
  className
}: BlueprintKPIProps) {
  const getTrendIcon = (direction: 'up' | 'down' | 'neutral') => {
    switch (direction) {
      case 'up': return <TrendingUp className="w-4 h-4" />;
      case 'down': return <TrendingDown className="w-4 h-4" />;
      case 'neutral': return <Minus className="w-4 h-4" />;
    }
  };

  const getTrendColor = (direction: 'up' | 'down' | 'neutral') => {
    switch (direction) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      case 'neutral': return 'text-gray-600';
    }
  };

  return (
    <div className={cn(
      'bg-[var(--paper)] border border-[var(--border)] rounded-[var(--radius)] p-4',
      className
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-[var(--muted)]">{title}</p>
          <p className="text-2xl font-bold text-[var(--ink)] mt-1">{value}</p>
          {subtitle && (
            <p className="text-xs text-[var(--muted)] mt-1">{subtitle}</p>
          )}
        </div>

        <div className="flex flex-col items-end gap-2">
          {icon && (
            <div className="text-[var(--muted)]">
              {icon}
            </div>
          )}

          {trend && (
            <div className={cn(
              'flex items-center gap-1 text-xs font-medium',
              getTrendColor(trend.direction)
            )}>
              {getTrendIcon(trend.direction)}
              <span>{Math.abs(trend.value)}%</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
