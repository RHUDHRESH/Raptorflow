'use client';

import React from 'react';
import { MetricDelta } from './MetricDelta';

interface BoardroomStats {
  totalMoves: number;
  movesDelta: number;
  momentumScore: number;
  momentumDelta: number;
  activeCampaigns: number;
  campaignsDelta: number;
  averageRoi: number;
  roiDelta: number;
}

const DEFAULT_STATS: BoardroomStats = {
  totalMoves: 124,
  movesDelta: 12,
  momentumScore: 88.4,
  momentumDelta: 2.5,
  activeCampaigns: 3,
  campaignsDelta: 0,
  averageRoi: 340,
  roiDelta: 15.2,
};

export function BoardroomView({
  stats = DEFAULT_STATS,
}: {
  stats?: BoardroomStats;
}) {
  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
      <MetricDelta
        label="Momentum"
        value={stats.momentumScore}
        delta={stats.momentumDelta}
      />

      <MetricDelta
        label="Avg. ROI"
        value={stats.averageRoi}
        delta={stats.roiDelta}
        unit="%"
      />

      <MetricDelta
        label="Active Campaigns"
        value={stats.activeCampaigns}
        delta={stats.campaignsDelta}
      />

      <MetricDelta
        label="Total Moves"
        value={stats.totalMoves}
        delta={stats.movesDelta}
      />
    </div>
  );
}
