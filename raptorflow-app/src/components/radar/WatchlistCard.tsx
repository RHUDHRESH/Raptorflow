'use client';

import React from 'react';
import { Watchlist } from './types';
import { ArrowRight } from 'lucide-react';

interface WatchlistCardProps {
  watchlist: Watchlist;
  onView?: (id: string) => void;
  onEdit?: (id: string) => void;
  onRunRecon?: (id: string) => void;
}

function formatLastScan(date?: Date): string {
  if (!date) return 'Never';
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return 'Just now';
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function WatchlistCard({
  watchlist,
  onView,
  onEdit,
  onRunRecon,
}: WatchlistCardProps) {
  return (
    <article className="bg-white border border-[#E5E6E3] rounded-2xl transition-all duration-300 hover:shadow-[0_8px_24px_rgba(0,0,0,0.04)]">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-6 mb-5">
          <div>
            <h3 className="font-serif text-xl text-[#2D3538] mb-1">
              {watchlist.name}
            </h3>
            {watchlist.description && (
              <p className="text-[14px] text-[#5B5F61]">
                {watchlist.description}
              </p>
            )}
          </div>
          <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[#9D9F9F]">
            {watchlist.status}
          </span>
        </div>

        {/* Stats Row */}
        <div className="flex items-center gap-8 text-[13px] text-[#5B5F61] mb-5">
          <div>
            <span className="text-[#9D9F9F]">Targets:</span>{' '}
            <span className="text-[#2D3538] font-medium">
              {watchlist.competitors.length}
            </span>
          </div>
          <div>
            <span className="text-[#9D9F9F]">Signals:</span>{' '}
            <span className="text-[#2D3538] font-medium">
              {watchlist.signalTypes.join(', ')}
            </span>
          </div>
          <div>
            <span className="text-[#9D9F9F]">Frequency:</span>{' '}
            <span className="text-[#2D3538] font-medium capitalize">
              {watchlist.scanFrequency}
            </span>
          </div>
          <div>
            <span className="text-[#9D9F9F]">Last Scan:</span>{' '}
            <span className="text-[#2D3538] font-medium">
              {formatLastScan(watchlist.lastScan)}
            </span>
          </div>
        </div>

        {/* Competitors */}
        {watchlist.competitors.length > 0 && (
          <div className="flex items-center gap-2 mb-6">
            {watchlist.competitors.slice(0, 4).map((comp) => (
              <span
                key={comp.id}
                className="px-3 py-1.5 bg-[#F8F9F7] border border-[#E5E6E3] rounded-lg text-[13px] font-medium text-[#2D3538]"
              >
                {comp.name}
              </span>
            ))}
            {watchlist.competitors.length > 4 && (
              <span className="text-[13px] text-[#9D9F9F]">
                +{watchlist.competitors.length - 4} more
              </span>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-4 pt-5 border-t border-[#E5E6E3]">
          <button
            onClick={() => onView?.(watchlist.id)}
            className="text-[13px] font-medium text-[#5B5F61] hover:text-[#2D3538] transition-colors"
          >
            View Alerts
          </button>
          <button
            onClick={() => onEdit?.(watchlist.id)}
            className="text-[13px] font-medium text-[#5B5F61] hover:text-[#2D3538] transition-colors"
          >
            Edit
          </button>
          <button
            onClick={() => onRunRecon?.(watchlist.id)}
            className="ml-auto inline-flex items-center gap-2 h-10 px-5 bg-[#1A1D1E] text-white rounded-xl text-[13px] font-medium transition-all hover:bg-black"
          >
            Run Recon
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </article>
  );
}
