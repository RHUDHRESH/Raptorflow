'use client';

import React from 'react';
import { RadarStatus } from './types';
import { Plus } from 'lucide-react';

interface RadarStatusWidgetProps {
  status: RadarStatus;
  onAddWatchlist?: () => void;
  onAddCompetitor?: () => void;
  onAddSource?: () => void;
}

export function RadarStatusWidget({
  status,
  onAddWatchlist,
  onAddCompetitor,
  onAddSource,
}: RadarStatusWidgetProps) {
  return (
    <aside className="bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="px-6 py-5 border-b border-[#E5E6E3]">
        <h3 className="text-[11px] font-semibold uppercase tracking-[0.15em] text-[#9D9F9F]">
          Radar Status
        </h3>
      </div>

      {/* Metrics */}
      <div className="p-6 space-y-5">
        <div className="flex items-center justify-between">
          <span className="text-[14px] text-[#5B5F61]">Active Watchlists</span>
          <span className="font-mono text-[18px] font-semibold text-[#2D3538]">
            {status.activeWatchlists}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-[14px] text-[#5B5F61]">New Alerts (24h)</span>
          <span className="font-mono text-[18px] font-semibold text-[#2D3538]">
            {status.newAlerts24h}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-[14px] text-[#5B5F61]">Next Scan</span>
          <span className="font-mono text-[14px] text-[#9D9F9F]">
            {status.nextScanIn}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-[14px] text-[#5B5F61]">Source Health</span>
          <div className="flex items-center gap-3">
            <div className="w-20 h-1.5 bg-[#E5E6E3] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#2D3538] rounded-full"
                style={{ width: `${status.sourceHealth}%` }}
              />
            </div>
            <span className="font-mono text-[12px] text-[#9D9F9F]">
              {status.sourceHealth}%
            </span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="px-6 py-5 border-t border-[#E5E6E3] bg-[#FAFBF9]">
        <h4 className="text-[10px] font-semibold uppercase tracking-[0.15em] text-[#9D9F9F] mb-4">
          Quick Actions
        </h4>
        <div className="space-y-1">
          <button
            onClick={onAddWatchlist}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white transition-colors text-[14px] text-[#5B5F61] hover:text-[#2D3538]"
          >
            <Plus className="w-4 h-4" />
            Create Watchlist
          </button>
          <button
            onClick={onAddCompetitor}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white transition-colors text-[14px] text-[#5B5F61] hover:text-[#2D3538]"
          >
            <Plus className="w-4 h-4" />
            Add Competitor
          </button>
          <button
            onClick={onAddSource}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white transition-colors text-[14px] text-[#5B5F61] hover:text-[#2D3538]"
          >
            <Plus className="w-4 h-4" />
            Add Source
          </button>
        </div>
      </div>
    </aside>
  );
}
