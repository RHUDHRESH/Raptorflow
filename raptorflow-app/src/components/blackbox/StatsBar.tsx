'use client';

import React from 'react';
import { Beaker, Rocket, CheckCircle2, TrendingUp, Target } from 'lucide-react';
import { Experiment } from '@/lib/blackbox-types';

interface StatsBarProps {
  experiments: Experiment[];
}

export function StatsBar({ experiments }: StatsBarProps) {
  const total = experiments.length;
  const drafted = experiments.filter((e) => e.status === 'draft').length;
  const launched = experiments.filter((e) => e.status === 'launched').length;
  const completed = experiments.filter((e) => e.status === 'checked_in').length;

  const successfulExperiments = experiments.filter(
    (e) =>
      e.self_report?.outcome === 'great' || e.self_report?.outcome === 'worked'
  );
  const winRate =
    completed > 0
      ? Math.round((successfulExperiments.length / completed) * 100)
      : 0;

  if (total === 0) return null;

  const stats = [
    { label: 'Total', value: total, icon: Beaker },
    { label: 'Ready', value: drafted, icon: Target },
    { label: 'Live', value: launched, icon: Rocket },
    { label: 'Done', value: completed, icon: CheckCircle2 },
    { label: 'Win %', value: `${winRate}`, icon: TrendingUp },
  ];

  return (
    <div className="flex items-center gap-6 py-3 px-4 bg-zinc-50 dark:bg-zinc-900/50 rounded-xl border border-zinc-100 dark:border-zinc-800">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <div key={stat.label} className="flex items-center gap-2">
            <Icon className="w-4 h-4 text-zinc-400" />
            <span className="text-lg font-bold font-mono text-zinc-900 dark:text-zinc-100">
              {stat.value}
            </span>
            <span className="text-[10px] uppercase tracking-wider text-zinc-400 font-sans">
              {stat.label}
            </span>
            {idx < stats.length - 1 && (
              <div className="ml-4 w-px h-4 bg-zinc-200 dark:bg-zinc-700" />
            )}
          </div>
        );
      })}
    </div>
  );
}
