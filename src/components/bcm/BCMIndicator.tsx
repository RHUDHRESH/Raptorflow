'use client';

import React from 'react';
import { useBcmSync } from '@/hooks/useBcmSync';
import { getFreshnessStatus } from '@/lib/bcm-client';
import { cn } from '@/lib/utils';

interface BCMIndicatorProps {
  workspaceId: string;
  className?: string;
  showDetails?: boolean;
  compact?: boolean;
}

export function BCMIndicator({
  workspaceId,
  className,
  showDetails = false,
  compact = false
}: BCMIndicatorProps) {
  const { manifest, status, lastFetchedAt, error } = useBcmSync(workspaceId);

  // Calculate freshness status
  const freshness = manifest?.generatedAt
    ? getFreshnessStatus(manifest.generatedAt)
    : { status: 'expired' as const, color: 'red' as const, daysOld: Infinity };

  // Get status color and icon
  const getStatusConfig = () => {
    if (status === 'loading') return { color: 'text-blue-600', bg: 'bg-blue-100', icon: '⏳' };
    if (status === 'error') return { color: 'text-red-600', bg: 'bg-red-100', icon: '❌' };
    if (status === 'stale') return { color: 'text-yellow-600', bg: 'bg-yellow-100', icon: '⚠️' };

    // Use freshness color for idle status
    const freshnessColors = {
      green: { color: 'text-green-600', bg: 'bg-green-100', icon: '✅' },
      yellow: { color: 'text-yellow-600', bg: 'bg-yellow-100', icon: '⚠️' },
      red: { color: 'text-red-600', bg: 'bg-red-100', icon: '❌' }
    };

    return freshnessColors[freshness.color];
  };

  const statusConfig = getStatusConfig();

  if (compact) {
    return (
      <div className={cn(
        'flex items-center gap-2 px-3 py-1 rounded-full text-sm',
        statusConfig.bg,
        statusConfig.color,
        className
      )}>
        <span className="text-xs">{statusConfig.icon}</span>
        <span className="font-medium">
          {status === 'loading' ? 'Loading...' :
           status === 'error' ? 'Error' :
           freshness.status.charAt(0).toUpperCase() + freshness.status.slice(1)}
        </span>
      </div>
    );
  }

  return (
    <div className={cn(
      'rounded-lg border p-4 space-y-3',
      'bg-white dark:bg-gray-800',
      'border-gray-200 dark:border-gray-700',
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={cn(
            'w-2 h-2 rounded-full',
            freshness.color === 'green' ? 'bg-green-500' :
            freshness.color === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'
          )} />
          <h3 className="font-semibold text-sm">Business Context</h3>
        </div>

        <div className={cn(
          'flex items-center gap-1 px-2 py-1 rounded text-xs font-medium',
          statusConfig.bg,
          statusConfig.color
        )}>
          <span>{statusConfig.icon}</span>
          <span>
            {status === 'loading' ? 'Loading' :
             status === 'error' ? 'Error' :
             freshness.status.charAt(0).toUpperCase() + freshness.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Status Details */}
      {showDetails && (
        <div className="space-y-2 text-xs">
          {manifest && (
            <>
              <div className="flex justify-between">
                <span className="text-gray-500">Version:</span>
                <span className="font-medium">{manifest.version || '1.0.0'}</span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-500">Generated:</span>
                <span className="font-medium">
                  {manifest.generatedAt ?
                    new Date(manifest.generatedAt).toLocaleString() : 'Unknown'}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-gray-500">Completion:</span>
                <span className="font-medium">
                  {Object.keys(manifest.rawStepData || {}).length}/23 steps
                </span>
              </div>


            </>
          )}

          {error && (
            <div className="text-red-600 bg-red-50 p-2 rounded">
                <span className="font-medium">Error:</span> {error}
              </div>
          )}

          {status === 'idle' && !manifest && (
            <div className="text-gray-500 italic">
              No Business Context Manifest available
            </div>
          )}
        </div>
      )}

      {/* Freshness Indicator */}
      {manifest && (
        <div className="flex items-center gap-2 text-xs">
          <div className={cn(
            'w-2 h-2 rounded-full',
            freshness.color === 'green' ? 'bg-green-500' :
            freshness.color === 'yellow' ? 'bg-yellow-500' : 'bg-red-500'
          )} />
          <span className="text-gray-600">
            {freshness.daysOld === 0 ? 'Generated today' :
             freshness.daysOld === 1 ? 'Generated yesterday' :
             `Generated ${freshness.daysOld} days ago`}
          </span>
        </div>
      )}
    </div>
  );
}
