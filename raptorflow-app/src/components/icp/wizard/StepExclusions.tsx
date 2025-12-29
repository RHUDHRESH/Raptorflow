import React from 'react';
import { IcpDisqualifiers } from '@/types/icp-types';
import { Ban } from 'lucide-react';

interface StepExclusionsProps {
  data: IcpDisqualifiers;
  onChange: (data: Partial<IcpDisqualifiers>) => void;
}

const EXCLUDED_TYPES = [
  'Enterprise',
  'Agencies',
  'Price shoppers',
  'Early hobbyists',
  'Non-English markets',
  'Consultants',
];

const EXCLUDED_BEHAVIORS = [
  'Requires heavy customization',
  'Long procurement process',
  'Expects 24/7 support',
  'Looking for free trials',
  'Agency hoppers',
];

export default function StepExclusions({
  data,
  onChange,
}: StepExclusionsProps) {
  const toggleList = (
    current: string[],
    item: string,
    field: keyof IcpDisqualifiers
  ) => {
    const newVal = current.includes(item)
      ? current.filter((i) => i !== item)
      : [...current, item];
    onChange({ [field]: newVal });
  };

  return (
    <div className="space-y-12">
      <div className="text-center space-y-4">
        <h1 className="font-serif text-4xl text-[#2D3538] leading-tight flex items-center justify-center gap-3">
          Who to <span className="text-red-700 font-serif italic">Ignore</span>.
        </h1>
        <p className="text-[#5B5F61] text-lg max-w-md mx-auto">
          Disqualifiers matter more than qualifiers. Who wastes your time?
        </p>
      </div>

      <div className="bg-red-50/50 border border-red-100 rounded-3xl p-8 space-y-8">
        {/* Excluded Types */}
        <div className="space-y-4">
          <label className="block text-sm font-semibold uppercase tracking-wider text-red-900/60 flex items-center gap-2">
            <Ban className="w-4 h-4" /> Never Target
          </label>
          <div className="flex flex-wrap gap-3">
            {EXCLUDED_TYPES.map((type) => (
              <button
                key={type}
                onClick={() =>
                  toggleList(
                    data.excludedCompanyTypes,
                    type,
                    'excludedCompanyTypes'
                  )
                }
                className={`px-4 py-2 rounded-lg border transition-all text-sm font-medium
                  ${
                    data.excludedCompanyTypes.includes(type)
                      ? 'bg-red-100 text-red-800 border-red-300'
                      : 'bg-white text-[#5B5F61] border-[#C0C1BE]/50 hover:border-red-200 hover:text-red-700'
                  }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Excluded Behaviors */}
        <div className="space-y-4">
          <label className="block text-sm font-semibold uppercase tracking-wider text-red-900/60 flex items-center gap-2">
            <Ban className="w-4 h-4" /> Red Flags
          </label>
          <div className="flex flex-wrap gap-3">
            {EXCLUDED_BEHAVIORS.map((behavior) => (
              <button
                key={behavior}
                onClick={() =>
                  toggleList(
                    data.excludedBehaviors,
                    behavior,
                    'excludedBehaviors'
                  )
                }
                className={`px-4 py-2 rounded-lg border transition-all text-sm font-medium
                  ${
                    data.excludedBehaviors.includes(behavior)
                      ? 'bg-red-100 text-red-800 border-red-300'
                      : 'bg-white text-[#5B5F61] border-[#C0C1BE]/50 hover:border-red-200 hover:text-red-700'
                  }`}
              >
                {behavior}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
