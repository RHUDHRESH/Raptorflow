/**
 * Loading State Components
 * Reusable loading indicators and skeleton screens
 */

import { cn } from '../utils/cn';

// Simple Spinner
export function LoadingSpinner({ size = 'md', className = '' }) {
  const sizes = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-16 h-16 border-4',
  };

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <div
        className={cn(
          'border-neutral-200 border-t-neutral-900 rounded-full animate-spin',
          sizes[size]
        )}
      />
    </div>
  );
}

// Full Page Loading
export function PageLoading({ message = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <LoadingSpinner size="lg" className="mb-4" />
        <p className="text-neutral-600">{message}</p>
      </div>
    </div>
  );
}

// Card Skeleton
export function CardSkeleton({ count = 1 }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="runway-card p-6 animate-pulse">
          <div className="flex items-start gap-4 mb-4">
            <div className="w-12 h-12 bg-neutral-200 rounded-lg" />
            <div className="flex-1">
              <div className="h-4 bg-neutral-200 rounded w-3/4 mb-2" />
              <div className="h-3 bg-neutral-200 rounded w-1/2" />
            </div>
          </div>
          <div className="space-y-2">
            <div className="h-3 bg-neutral-200 rounded" />
            <div className="h-3 bg-neutral-200 rounded w-5/6" />
          </div>
        </div>
      ))}
    </>
  );
}

// List Skeleton
export function ListSkeleton({ rows = 5 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-4 p-4 bg-white rounded-lg border border-neutral-200 animate-pulse">
          <div className="w-10 h-10 bg-neutral-200 rounded-full" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-neutral-200 rounded w-3/4" />
            <div className="h-3 bg-neutral-200 rounded w-1/2" />
          </div>
        </div>
      ))}
    </div>
  );
}

// Table Skeleton
export function TableSkeleton({ rows = 5, cols = 4 }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-neutral-200">
            {Array.from({ length: cols }).map((_, i) => (
              <th key={i} className="p-3 text-left">
                <div className="h-4 bg-neutral-200 rounded w-20 animate-pulse" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, rowIdx) => (
            <tr key={rowIdx} className="border-b border-neutral-100">
              {Array.from({ length: cols }).map((_, colIdx) => (
                <td key={colIdx} className="p-3">
                  <div className="h-4 bg-neutral-200 rounded animate-pulse" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Inline Loading (for buttons)
export function InlineLoading({ text = 'Loading...' }) {
  return (
    <span className="flex items-center gap-2">
      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
      {text}
    </span>
  );
}

// Grid Skeleton
export function GridSkeleton({ cols = 3, rows = 2 }) {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-${cols} gap-6`}>
      {Array.from({ length: cols * rows }).map((_, i) => (
        <div key={i} className="runway-card p-6 animate-pulse">
          <div className="aspect-video bg-neutral-200 rounded-lg mb-4" />
          <div className="h-4 bg-neutral-200 rounded w-3/4 mb-2" />
          <div className="h-3 bg-neutral-200 rounded w-1/2" />
        </div>
      ))}
    </div>
  );
}

// Stat Skeleton
export function StatSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="runway-card p-4 animate-pulse">
          <div className="h-8 bg-neutral-200 rounded w-16 mb-2" />
          <div className="h-3 bg-neutral-200 rounded w-24" />
        </div>
      ))}
    </div>
  );
}


