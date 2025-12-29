import React, { useState } from 'react';
import { Icp } from '@/types/icp-types';
import { Copy, Check, Share2 } from 'lucide-react';
import { ShareExportModal } from '@/components/ui/ShareExportModal';

interface StepReviewProps {
  data: Partial<Icp>;
  onChange: (updates: Partial<Icp>) => void;
  onJumpToStep?: (stepId: string) => void;
}

export default function StepReview({
  data,
  onChange,
  onJumpToStep,
}: StepReviewProps) {
  const [name, setName] = useState(data.name || 'My Ideal Customer Profile');
  const [copied, setCopied] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);

  const handleJump = (stepId: string) => {
    if (onJumpToStep) onJumpToStep(stepId);
  };

  const handleCopy = () => {
    const text = JSON.stringify(data, null, 2);
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-12">
      <div className="text-center space-y-4 relative group">
        <h1 className="font-serif text-4xl text-[#2D3538] leading-tight flex items-center justify-center gap-3">
          <span
            contentEditable
            suppressContentEditableWarning
            onBlur={(e) => {
              const newName = e.currentTarget.textContent || '';
              if (newName !== name) {
                setName(newName);
                onChange({ name: newName });
              }
            }}
            onKeyDown={(e) => e.key === 'Enter' && e.currentTarget.blur()}
            className="hover:bg-[#E5E7E1] px-2 rounded cursor-text outline-none focus:bg-white focus:ring-2 focus:ring-[#2D3538] border border-transparent focus:border-[#C0C1BE] transition-all min-w-[200px]"
            title="Click to rename"
          >
            {name}
          </span>
          <button
            onClick={handleCopy}
            className="p-2 rounded-full bg-[#F3F4EE] hover:bg-[#E5E7E1] text-[#5B5F61] transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100"
            title="Copy JSON to clipboard"
          >
            {copied ? (
              <Check className="w-5 h-5 text-green-600" />
            ) : (
              <Copy className="w-5 h-5" />
            )}
          </button>
          <button
            onClick={() => setShowShareModal(true)}
            className="p-2 rounded-full bg-[#F3F4EE] hover:bg-[#E5E7E1] text-[#5B5F61] transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100"
            title="Share / Export"
          >
            <Share2 className="w-5 h-5" />
          </button>
        </h1>
        <p className="text-[#5B5F61] text-lg max-w-md mx-auto relative">
          Sanity check. Does this look like a real market segment?
          <span className="absolute left-1/2 -translate-x-1/2 -bottom-6 text-xs text-[#9D9F9F] opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            Tip: Click title to rename
          </span>
        </p>
      </div>

      <div className="bg-white rounded-3xl border border-[#C0C1BE]/50 p-8 shadow-sm space-y-8">
        {/* Name Input */}
        <div className="space-y-2">
          <label className="text-xs uppercase font-bold tracking-widest text-[#9D9F9F]">
            ICP Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              onChange({ name: e.target.value });
            }}
            className="w-full text-2xl font-serif text-[#2D3538] border-b border-[#C0C1BE] pb-2 focus:outline-none focus:border-[#2D3538] bg-transparent"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Context */}
          <div
            onClick={() => handleJump('business_model')}
            className="space-y-3 cursor-pointer group hover:bg-[#F3F4EE] p-4 -m-4 rounded-xl transition-colors"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase text-[#9D9F9F]">
                Context
              </h3>
              <span className="text-xs text-[#2D3538] opacity-0 group-hover:opacity-100 transition-opacity">
                Edit
              </span>
            </div>
            <ul className="space-y-1 text-sm text-[#2D3538]">
              {data.firmographics?.companyType.length ? (
                data.firmographics.companyType.map((t) => (
                  <li key={t}>• {t}</li>
                ))
              ) : (
                <li className="text-gray-400 italic">None selected</li>
              )}
              {data.firmographics?.salesMotion.length
                ? data.firmographics.salesMotion.map((t) => (
                    <li key={t}>• {t}</li>
                  ))
                : null}
              {data.firmographics?.budgetComfort.length
                ? data.firmographics.budgetComfort.map((b) => (
                    <li key={b}>• Budget: {b}</li>
                  ))
                : null}
            </ul>
          </div>

          {/* Pain */}
          <div
            onClick={() => handleJump('primary_pains')}
            className="space-y-3 cursor-pointer group hover:bg-[#F3F4EE] p-4 -m-4 rounded-xl transition-colors"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase text-[#9D9F9F]">
                Core Pain
              </h3>
              <span className="text-xs text-[#2D3538] opacity-0 group-hover:opacity-100 transition-opacity">
                Edit
              </span>
            </div>
            <ul className="space-y-1 text-sm text-[#2D3538]">
              {data.painMap?.primaryPains.length ? (
                data.painMap.primaryPains.map((p) => <li key={p}>• {p}</li>)
              ) : (
                <li className="text-gray-400 italic">None selected</li>
              )}
              {data.painMap?.urgencyLevel && (
                <li>
                  • Urgency:{' '}
                  <span className="font-medium capitalize">
                    {data.painMap.urgencyLevel}
                  </span>
                </li>
              )}
            </ul>
          </div>

          {/* Language */}
          <div
            onClick={() => handleJump('tone')}
            className="space-y-3 cursor-pointer group hover:bg-[#F3F4EE] p-4 -m-4 rounded-xl transition-colors"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase text-[#9D9F9F]">
                Language
              </h3>
              <span className="text-xs text-[#2D3538] opacity-0 group-hover:opacity-100 transition-opacity">
                Edit
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {data.psycholinguistics?.tonePreference.map((t) => (
                <span
                  key={t}
                  className="px-2 py-1 bg-[#F3F4EE] rounded text-xs"
                >
                  {t}
                </span>
              ))}
              {data.psycholinguistics?.mindsetTraits.map((t) => (
                <span
                  key={t}
                  className="px-2 py-1 bg-[#F3F4EE] rounded text-xs"
                >
                  {t}
                </span>
              ))}
            </div>
          </div>

          {/* Exclusions */}
          {data.disqualifiers && (
            <div
              onClick={() => handleJump('excluded_types')}
              className="space-y-3 cursor-pointer group hover:bg-red-50 p-4 -m-4 rounded-xl transition-colors"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold uppercase text-red-800/60">
                  Disqualifiers
                </h3>
                <span className="text-xs text-red-800 opacity-0 group-hover:opacity-100 transition-opacity">
                  Edit
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {data.disqualifiers.excludedCompanyTypes.map((t) => (
                  <span
                    key={t}
                    className="px-2 py-1 bg-red-50 text-red-900 rounded text-xs border border-red-100"
                  >
                    {t}
                  </span>
                ))}
                {data.disqualifiers.excludedBehaviors.map((t) => (
                  <span
                    key={t}
                    className="px-2 py-1 bg-red-50 text-red-900 rounded text-xs border border-red-100"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <ShareExportModal
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
        data={data}
      />
    </div>
  );
}
