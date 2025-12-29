'use client';

import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  MinusCircle,
  ThumbsUp,
  ChevronDown,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Experiment, Outcome, SelfReport, WhyChip } from '@/lib/blackbox-types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface CheckinCardProps {
  experiment: Experiment;
  onSubmit: (report: SelfReport) => void;
  onCancel: () => void;
}

const WHY_CHIPS: { id: WhyChip; label: string }[] = [
  { id: 'wrong_audience', label: 'Wrong Audience' },
  { id: 'weak_hook', label: 'Weak Hook' },
  { id: 'offer_unclear', label: 'Offer Unclear' },
  { id: 'too_spicy', label: 'Too Spicy' },
  { id: 'timing', label: 'Bad Timing' },
  { id: 'format_mismatch', label: 'Format Mismatch' },
];

const OUTCOMES = [
  { id: 'bombed', icon: XCircle, label: 'Bombed' },
  { id: 'meh', icon: MinusCircle, label: 'Meh' },
  { id: 'worked', icon: CheckCircle2, label: 'Worked' },
  { id: 'great', icon: ThumbsUp, label: 'Great' },
];

export function CheckinCard({
  experiment,
  onSubmit,
  onCancel,
}: CheckinCardProps) {
  const [outcome, setOutcome] = useState<Outcome | null>(null);
  const [metricValue, setMetricValue] = useState<string>('');
  const [runAgain, setRunAgain] = useState<boolean | null>(null);
  const [selectedChips, setSelectedChips] = useState<WhyChip[]>([]);
  const [showDetails, setShowDetails] = useState(false);

  const handleChipToggle = (chip: WhyChip) => {
    if (selectedChips.includes(chip)) {
      setSelectedChips(selectedChips.filter((c) => c !== chip));
    } else if (selectedChips.length < 2) {
      setSelectedChips([...selectedChips, chip]);
    }
  };

  const handleSubmit = () => {
    if (!outcome || runAgain === null) return;
    onSubmit({
      submitted_at: new Date().toISOString(),
      outcome,
      metric_name: experiment.goal,
      metric_value: parseInt(metricValue) || 0,
      run_again: runAgain,
      why_chips: selectedChips.length > 0 ? selectedChips : undefined,
    });
  };

  const isComplete = outcome !== null && runAgain !== null;

  return (
    <div className="bg-white dark:bg-zinc-950 rounded-2xl shadow-xl border border-zinc-200 dark:border-zinc-800 max-w-md mx-auto overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-zinc-100 dark:border-zinc-900">
        <p className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-1">
          Check-in
        </p>
        <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
          {experiment.title}
        </h3>
      </div>

      <div className="p-5 space-y-5">
        {/* Outcome */}
        <div>
          <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-2 block">
            How did it go?
          </label>
          <div className="grid grid-cols-4 gap-2">
            {OUTCOMES.map((item) => {
              const Icon = item.icon;
              const isActive = outcome === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setOutcome(item.id as Outcome)}
                  className={cn(
                    'flex flex-col items-center p-3 rounded-lg border transition-all',
                    isActive
                      ? 'bg-zinc-900 border-zinc-900 text-white dark:bg-white dark:border-white dark:text-zinc-900'
                      : 'bg-zinc-50 border-zinc-200 text-zinc-500 hover:border-zinc-300 dark:bg-zinc-900 dark:border-zinc-800'
                  )}
                >
                  <Icon className="w-4 h-4 mb-1" />
                  <span className="text-[9px] font-bold uppercase">
                    {item.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Metric */}
        <div>
          <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-2 block">
            {experiment.goal} count
          </label>
          <Input
            type="number"
            placeholder="0"
            value={metricValue}
            onChange={(e) => setMetricValue(e.target.value)}
            className="h-10 text-lg font-mono bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 rounded-lg"
          />
        </div>

        {/* Run Again */}
        <div>
          <label className="text-[10px] font-bold uppercase tracking-widest text-zinc-400 mb-2 block">
            Run again?
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setRunAgain(true)}
              className={cn(
                'py-2.5 rounded-lg font-medium text-sm transition-all border',
                runAgain === true
                  ? 'bg-zinc-900 border-zinc-900 text-white dark:bg-white dark:text-zinc-900'
                  : 'bg-zinc-50 border-zinc-200 text-zinc-600 dark:bg-zinc-900 dark:border-zinc-800'
              )}
            >
              Yes
            </button>
            <button
              onClick={() => setRunAgain(false)}
              className={cn(
                'py-2.5 rounded-lg font-medium text-sm transition-all border',
                runAgain === false
                  ? 'bg-zinc-900 border-zinc-900 text-white dark:bg-white dark:text-zinc-900'
                  : 'bg-zinc-50 border-zinc-200 text-zinc-600 dark:bg-zinc-900 dark:border-zinc-800'
              )}
            >
              No
            </button>
          </div>
        </div>

        {/* Optional Details */}
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="flex items-center gap-1 text-[10px] font-medium text-zinc-400 hover:text-zinc-600"
        >
          <ChevronDown
            className={cn(
              'w-3 h-3 transition-transform',
              showDetails && 'rotate-180'
            )}
          />
          Add context (optional)
        </button>

        {showDetails && (
          <div className="flex flex-wrap gap-1.5">
            {WHY_CHIPS.map((chip) => (
              <button
                key={chip.id}
                onClick={() => handleChipToggle(chip.id)}
                className={cn(
                  'px-2 py-1 rounded text-[10px] font-medium border transition-all',
                  selectedChips.includes(chip.id)
                    ? 'bg-zinc-900 border-zinc-900 text-white dark:bg-white dark:text-zinc-900'
                    : 'bg-zinc-50 border-zinc-200 text-zinc-500 dark:bg-zinc-900 dark:border-zinc-800'
                )}
              >
                {chip.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-5 border-t border-zinc-100 dark:border-zinc-900 flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={onCancel}
          className="rounded-lg text-zinc-500"
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={!isComplete}
          className="rounded-lg bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 px-5"
        >
          Submit
        </Button>
      </div>
    </div>
  );
}
