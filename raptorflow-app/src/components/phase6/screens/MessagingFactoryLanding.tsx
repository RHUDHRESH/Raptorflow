'use client';

import React from 'react';
import { Phase6Data, Phase5Data } from '@/lib/foundation';
import { Check, AlertCircle, Settings2 } from 'lucide-react';

interface Props {
  phase5: Phase5Data;
  phase6: Phase6Data;
  onToneChange: (tone: 'conservative' | 'balanced' | 'aggressive') => void;
  onConfirm: () => void;
}

export function MessagingFactoryLanding({
  phase5,
  phase6,
  onToneChange,
  onConfirm,
}: Props) {
  const primaryICP = phase5.icps[0];
  const toneRisk = phase6.toneRisk || 'balanced';

  // Calculate confidence scores
  const vocScore =
    (phase6.vocPhrases?.length || 0) >= 5
      ? 100
      : ((phase6.vocPhrases?.length || 0) / 5) * 100;
  const proofScore =
    phase6.proofSlots?.filter((p) => p.status === 'green').length || 0;
  const diffScore = phase6.qaReport?.differentiationScore || 60;

  const overallConfidence = Math.round(
    (vocScore + (proofScore / 7) * 100 + diffScore) / 3
  );

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="bg-[#2D3538] rounded-3xl p-10 text-white">
        <h2 className="font-serif text-[32px] mb-4">
          We're generating your Messaging Kit
        </h2>
        <p className="text-white/70 text-lg max-w-xl">
          10 deployable assets from your ICP + Positioning + Competitive Map.
          Paste-ready lines for homepage, LinkedIn, ads, emails, and decks.
        </p>
      </div>

      {/* Inputs Used Chips */}
      <div className="space-y-3">
        <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
          Inputs Used
        </span>
        <div className="flex flex-wrap gap-2">
          <div className="flex items-center gap-2 px-4 py-2 bg-white border border-[#E5E6E3] rounded-xl">
            <Check className="w-4 h-4 text-[#2D3538]" />
            <span className="text-sm text-[#2D3538]">
              Primary ICP: {primaryICP?.name || 'Not set'}
            </span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-white border border-[#E5E6E3] rounded-xl">
            <Check className="w-4 h-4 text-[#2D3538]" />
            <span className="text-sm text-[#2D3538]">
              Position:{' '}
              {phase6.blueprint?.controllingIdea?.slice(0, 50) ||
                'Marketing OS'}
              ...
            </span>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-white border border-[#E5E6E3] rounded-xl">
            <Check className="w-4 h-4 text-[#2D3538]" />
            <span className="text-sm text-[#2D3538]">
              {phase5.icps.length} ICP{phase5.icps.length !== 1 ? 's' : ''}{' '}
              configured
            </span>
          </div>
        </div>
      </div>

      {/* Confidence Meter */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
            Messaging Confidence
          </span>
          <span className="text-xl font-medium text-[#2D3538]">
            {overallConfidence}%
          </span>
        </div>

        {/* Progress bar */}
        <div className="h-3 bg-[#F3F4EE] rounded-full overflow-hidden mb-6">
          <div
            className="h-full bg-[#2D3538] rounded-full transition-all duration-700"
            style={{ width: `${overallConfidence}%` }}
          />
        </div>

        {/* Breakdown */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-medium text-[#2D3538] mb-1">
              {phase6.vocPhrases?.length || 0}/5
            </div>
            <div className="text-xs text-[#9D9F9F]">VoC Evidence</div>
          </div>
          <div className="text-center border-x border-[#E5E6E3]">
            <div className="text-2xl font-medium text-[#2D3538] mb-1">
              {proofScore}/7
            </div>
            <div className="text-xs text-[#9D9F9F]">Proof Available</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-medium text-[#2D3538] mb-1">
              {diffScore}%
            </div>
            <div className="text-xs text-[#9D9F9F]">Differentiation</div>
          </div>
        </div>
      </div>

      {/* Tone Toggle */}
      <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Settings2 className="w-5 h-5 text-[#5B5F61]" />
          <span className="text-sm font-medium text-[#2D3538]">
            Messaging Tone
          </span>
        </div>

        <div className="flex gap-2">
          {(['conservative', 'balanced', 'aggressive'] as const).map((tone) => (
            <button
              key={tone}
              onClick={() => onToneChange(tone)}
              className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all ${
                toneRisk === tone
                  ? 'bg-[#2D3538] text-white'
                  : 'bg-white border border-[#E5E6E3] text-[#5B5F61] hover:border-[#2D3538]'
              }`}
            >
              {tone.charAt(0).toUpperCase() + tone.slice(1)}
            </button>
          ))}
        </div>
        <p className="text-xs text-[#9D9F9F] mt-3">
          {toneRisk === 'conservative' &&
            'Play it safe. Focus on proof and specificity.'}
          {toneRisk === 'balanced' &&
            'Mix of confidence and caution. Recommended.'}
          {toneRisk === 'aggressive' &&
            'Bold claims. Make sure you have the proof.'}
        </p>
      </div>
    </div>
  );
}
