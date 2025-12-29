import React from 'react';
import { IcpPainMap } from '@/types/icp-types';
import { AlertTriangle } from 'lucide-react';

interface StepProblemProps {
  data: IcpPainMap;
  onChange: (data: Partial<IcpPainMap>) => void;
}

const COMMON_PROBLEMS = [
  'Leads are inconsistent',
  'No positioning clarity',
  "Content doesn't convert",
  'Founder doing marketing themselves',
  'Pipeline unpredictable',
  'High churn rate',
  'Long sales cycles',
  'Competitors winning on price',
];

const TRIGGER_EVENTS = [
  'New funding round',
  'New executive hire',
  'Product launch',
  'Fiscal year end',
  'Compliance audit',
  'Tech stack migration',
  'Team expansion',
  'Missed quarterly target',
];

export default function StepProblem({ data, onChange }: StepProblemProps) {
  const togglePain = (problem: string) => {
    let current = [...data.primaryPains];

    if (current.includes(problem)) {
      current = current.filter((p) => p !== problem);
    } else {
      if (current.length >= 2) return; // Strict Max 2
      current.push(problem);
    }

    onChange({ primaryPains: current });
  };

  const toggleTrigger = (trigger: string) => {
    const current = [...data.triggerEvents];
    const newTriggers = current.includes(trigger)
      ? current.filter((t) => t !== trigger)
      : [...current, trigger]; // No hard limit on triggers, maybe soft limit UX?

    onChange({ triggerEvents: newTriggers });
  };

  return (
    <div className="space-y-12">
      <div className="text-center space-y-4">
        <h1 className="font-serif text-4xl text-[#2D3538] leading-tight">
          Problem Gravity.
        </h1>
        <p className="text-[#5B5F61] text-lg max-w-md mx-auto">
          What is the{' '}
          <span className="font-semibold text-[#2D3538]">bleeding neck</span>{' '}
          problem? Select max 2. If everything is a problem, nothing is.
        </p>
      </div>

      {/* PAINS */}
      <div className="space-y-4">
        <div className="flex justify-between items-center text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">
          <span>Core Pain ({data.primaryPains.length}/2)</span>
          {data.primaryPains.length === 2 && (
            <span className="text-amber-600 flex items-center gap-1 text-xs normal-case">
              <AlertTriangle className="w-3 h-3" /> Max limits focus
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          {COMMON_PROBLEMS.map((problem) => {
            const isSelected = data.primaryPains.includes(problem);
            const isDisabled = !isSelected && data.primaryPains.length >= 2;

            return (
              <button
                key={problem}
                onClick={() => togglePain(problem)}
                disabled={isDisabled}
                className={`flex items-center p-5 rounded-2xl border transition-all text-left group
                  ${
                    isSelected
                      ? 'border-[#2D3538] bg-white ring-1 ring-[#2D3538] shadow-sm'
                      : isDisabled
                        ? 'opacity-50 cursor-not-allowed border-[#C0C1BE]/30 bg-[#F3F4EE]'
                        : 'border-[#C0C1BE]/50 bg-transparent hover:border-[#2D3538]/50 hover:bg-white/50'
                  }`}
              >
                <div
                  className={`w-5 h-5 rounded-full border mr-4 flex items-center justify-center transition-colors
                  ${isSelected ? 'border-[#2D3538] bg-[#2D3538]' : 'border-[#9D9F9F]'}`}
                >
                  {isSelected && (
                    <div className="w-1.5 h-1.5 rounded-full bg-white" />
                  )}
                </div>
                <span
                  className={`font-medium text-lg ${isSelected ? 'text-[#2D3538]' : 'text-[#5B5F61]'}`}
                >
                  {problem}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* TRIGGERS */}
      <div className="space-y-4 pt-8 border-t border-[#C0C1BE]/30">
        <label className="block text-sm font-semibold uppercase tracking-wider text-[#9D9F9F]">
          Trigger Events (Optional)
        </label>
        <p className="text-sm text-[#5B5F61] mb-4">
          What happens right before they buy?
        </p>
        <div className="flex flex-wrap gap-3">
          {TRIGGER_EVENTS.map((trigger) => (
            <button
              key={trigger}
              onClick={() => toggleTrigger(trigger)}
              className={`px-4 py-2 rounded-full border text-sm font-medium transition-all
                ${
                  data.triggerEvents.includes(trigger)
                    ? 'bg-[#2D3538] text-white border-[#2D3538]'
                    : 'bg-white border-[#C0C1BE] text-[#5B5F61] hover:border-[#5B5F61]'
                }`}
            >
              {trigger}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
