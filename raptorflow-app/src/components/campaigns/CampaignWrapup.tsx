'use client';

import React, { useState } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Campaign, CampaignWrapup } from '@/lib/campaigns-types';
import { updateCampaign } from '@/lib/campaigns';
import { toast } from 'sonner';

interface CampaignWrapupProps {
  campaign: Campaign;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onComplete: () => void;
}

export function CampaignWrapupModal({
  campaign,
  open,
  onOpenChange,
  onComplete,
}: CampaignWrapupProps) {
  const [whatWorked, setWhatWorked] = useState('');
  const [whatDidnt, setWhatDidnt] = useState('');
  const [biggestInsight, setBiggestInsight] = useState('');
  const [nextRec, setNextRec] = useState('');

  const handleSubmit = () => {
    const wrapup: CampaignWrapup = {
      whatWorked,
      whatDidnt,
      biggestInsight,
      nextRecommendation: nextRec,
      submittedAt: new Date().toISOString(),
    };

    const updated: Campaign = {
      ...campaign,
      status: 'archived',
      completedAt: new Date().toISOString(),
      wrapup,
    };

    updateCampaign(updated);
    toast.success('Campaign archived successfully');
    onComplete();
  };

  const handleSkip = () => {
    if (
      !confirm(
        'Are you sure you want to skip the review? Learnings will be lost.'
      )
    )
      return;

    const updated: Campaign = {
      ...campaign,
      status: 'archived',
      completedAt: new Date().toISOString(),
    };

    updateCampaign(updated);
    toast.success('Campaign archived details');
    onComplete();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl bg-zinc-50 dark:bg-zinc-950 p-0 overflow-hidden">
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
          <h2 className="font-display text-xl font-semibold mb-1">
            Campaign Wrap-up
          </h2>
          <p className="text-sm text-zinc-500">
            Capture learnings before archiving {campaign.name}.
          </p>
        </div>

        <div className="p-6 space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
              What worked well?
            </label>
            <textarea
              value={whatWorked}
              onChange={(e) => setWhatWorked(e.target.value)}
              className="w-full h-24 p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-900 dark:focus:ring-zinc-100 placeholder:text-zinc-400"
              placeholder="e.g. The cold DM script had a 15% reply rate..."
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
              What didn't work?
            </label>
            <textarea
              value={whatDidnt}
              onChange={(e) => setWhatDidnt(e.target.value)}
              className="w-full h-24 p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-900 dark:focus:ring-zinc-100 placeholder:text-zinc-400"
              placeholder="e.g. LinkedIn posts got zero engagement..."
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
              Biggest Insight
            </label>
            <input
              type="text"
              value={biggestInsight}
              onChange={(e) => setBiggestInsight(e.target.value)}
              className="w-full p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-900 dark:focus:ring-zinc-100 placeholder:text-zinc-400"
              placeholder="One sentence takeaway"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
              Recommended Next Step
            </label>
            <input
              type="text"
              value={nextRec}
              onChange={(e) => setNextRec(e.target.value)}
              className="w-full p-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-900 dark:focus:ring-zinc-100 placeholder:text-zinc-400"
              placeholder="e.g. Run a Convert campaign for the new leads"
            />
          </div>
        </div>

        <div className="p-6 border-t border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 flex justify-between items-center">
          <button
            onClick={handleSkip}
            className="text-sm text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300"
          >
            Skip review & archive
          </button>
          <Button
            onClick={handleSubmit}
            disabled={!whatWorked || !biggestInsight}
            className="bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900"
          >
            Complete & Archive
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
