'use client';

import React from 'react';
import {
  MessageCircle,
  UserPlus,
  Calendar,
  MousePointer,
  Users,
  DollarSign,
  Star,
  TrendingUp,
  Eye,
  Heart,
  Share2,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { GoalType, GoalSelection } from '@/lib/blackbox-types';

interface GoalSelectorProps {
  selectedGoals: GoalSelection | null;
  onSelect: (goals: GoalSelection) => void;
}

const GOALS: { id: GoalType; label: string; icon: React.ElementType }[] = [
  { id: 'replies', label: 'Replies', icon: MessageCircle },
  { id: 'leads', label: 'Leads', icon: UserPlus },
  { id: 'calls', label: 'Demos', icon: Calendar },
  { id: 'clicks', label: 'Clicks', icon: MousePointer },
  { id: 'followers', label: 'Followers', icon: Users },
  { id: 'sales', label: 'Sales', icon: DollarSign },
];

export function GoalSelector({ selectedGoals, onSelect }: GoalSelectorProps) {
  const handleGoalClick = (goalId: GoalType) => {
    if (!selectedGoals) {
      // First click becomes primary
      onSelect({ primary: goalId, secondary: [] });
      return;
    }

    if (selectedGoals.primary === goalId) {
      // Clicking primary again - do nothing (can't deselect primary)
      return;
    }

    if (selectedGoals.secondary.includes(goalId)) {
      // Remove from secondary
      onSelect({
        primary: selectedGoals.primary,
        secondary: selectedGoals.secondary.filter((g) => g !== goalId),
      });
      return;
    }

    // At this point: clicking a goal that's neither primary nor secondary
    // Hold shift to add as secondary, otherwise replace primary
    if (selectedGoals.secondary.length < 2) {
      // Add to secondary
      onSelect({
        primary: selectedGoals.primary,
        secondary: [...selectedGoals.secondary, goalId],
      });
    } else {
      // Already have 2 secondary - replace primary instead
      onSelect({
        primary: goalId,
        secondary: selectedGoals.secondary,
      });
    }
  };

  const handleSetAsPrimary = (goalId: GoalType, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!selectedGoals) return;

    // Move current primary to secondary (if room), set new primary
    const newSecondary = selectedGoals.secondary.filter((g) => g !== goalId);
    if (selectedGoals.primary && newSecondary.length < 2) {
      newSecondary.unshift(selectedGoals.primary);
    }
    onSelect({
      primary: goalId,
      secondary: newSecondary.slice(0, 2),
    });
  };

  const getGoalState = (goalId: GoalType): 'primary' | 'secondary' | 'none' => {
    if (!selectedGoals) return 'none';
    if (selectedGoals.primary === goalId) return 'primary';
    if (selectedGoals.secondary.includes(goalId)) return 'secondary';
    return 'none';
  };

  return (
    <div className="w-full space-y-5 text-center">
      <div>
        <h2 className="text-xl font-semibold mb-1 font-sans">
          What's your goal?
        </h2>
        <p className="text-sm text-zinc-500 font-sans">
          Pick{' '}
          <span className="font-medium text-zinc-700 dark:text-zinc-300">
            1 primary
          </span>{' '}
          and up to{' '}
          <span className="font-medium text-zinc-700 dark:text-zinc-300">
            2 secondary
          </span>{' '}
          goals.
        </p>
        {selectedGoals && (
          <p className="text-xs text-zinc-400 mt-1 font-sans">
            Double-click a secondary goal to make it primary
          </p>
        )}
      </div>

      <div className="grid grid-cols-3 gap-2 max-w-sm mx-auto">
        {GOALS.map((g) => {
          const Icon = g.icon;
          const state = getGoalState(g.id);
          const isPrimary = state === 'primary';
          const isSecondary = state === 'secondary';

          return (
            <button
              key={g.id}
              onClick={() => handleGoalClick(g.id)}
              onDoubleClick={(e) =>
                isSecondary ? handleSetAsPrimary(g.id, e) : undefined
              }
              className={cn(
                'relative flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all',
                isPrimary &&
                  'bg-zinc-900 border-zinc-900 text-white dark:bg-white dark:border-white dark:text-zinc-900',
                isSecondary &&
                  'bg-zinc-100 border-zinc-400 text-zinc-900 dark:bg-zinc-800 dark:border-zinc-600 dark:text-zinc-100 cursor-pointer',
                !isPrimary &&
                  !isSecondary &&
                  'border-zinc-200 text-zinc-600 hover:border-zinc-400 dark:border-zinc-800 dark:text-zinc-400'
              )}
            >
              {/* Primary/Secondary badge */}
              {isPrimary && (
                <span className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-amber-500 text-white text-[10px] font-bold flex items-center justify-center">
                  1
                </span>
              )}
              {isSecondary && (
                <span className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-zinc-500 text-white text-[10px] font-bold flex items-center justify-center">
                  2
                </span>
              )}
              <Icon className="w-5 h-5 mb-1.5" />
              <span className="text-xs font-medium font-sans">{g.label}</span>
            </button>
          );
        })}
      </div>

      {/* Selection summary */}
      {selectedGoals && (
        <div className="text-xs text-zinc-500 font-sans">
          <span className="font-medium text-zinc-700 dark:text-zinc-300">
            {selectedGoals.primary}
          </span>
          {selectedGoals.secondary.length > 0 && (
            <span> + {selectedGoals.secondary.join(', ')}</span>
          )}
        </div>
      )}
    </div>
  );
}
