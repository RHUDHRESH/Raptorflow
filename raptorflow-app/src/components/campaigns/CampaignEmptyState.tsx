'use client';

import React from 'react';
import { Plus, Target } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface EmptyStateProps {
  onCreateCampaign: () => void;
}

export function CampaignEmptyState({ onCreateCampaign }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-8">
      <div className="w-14 h-14 rounded-2xl bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center mb-6">
        <Target className="w-7 h-7 text-zinc-400 dark:text-zinc-500" />
      </div>

      <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-2 text-center">
        No campaigns yet.
      </h2>
      <p className="text-zinc-500 dark:text-zinc-400 text-center max-w-sm mb-8">
        Stop random acts of marketing. Build a 90-day war plan.
      </p>

      <Button
        onClick={onCreateCampaign}
        className="rounded-xl bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-100 h-11 px-6"
      >
        <Plus className="w-4 h-4 mr-2" />
        Create your first campaign
      </Button>

      <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-4">
        Most founders start with an Acquire campaign.
      </p>
    </div>
  );
}
