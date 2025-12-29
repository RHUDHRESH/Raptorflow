'use client';

import React, { useState } from 'react';
import {
  Check,
  Plus,
  X,
  ChevronRight,
  Eye,
  Merge,
  AlertCircle,
  Building,
  Users,
  Zap,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Phase4Data,
  CompetitiveAlternative,
  CompetitorType,
} from '@/lib/foundation';
import { v4 as uuidv4 } from 'uuid';

interface CompetitionScreenProps {
  phase4: Phase4Data;
  onUpdate: (updates: Partial<Phase4Data>) => void;
  onShowEvidence: (alternativeId: string) => void;
  onContinue: () => void;
  onBack: () => void;
}

type TabType = 'statusQuo' | 'indirect' | 'direct';

const TAB_CONFIG: Record<
  TabType,
  { label: string; icon: React.ReactNode; description: string }
> = {
  statusQuo: {
    label: 'Status Quo',
    icon: <Building className="w-4 h-4" />,
    description: 'What they do when they buy nothing',
  },
  indirect: {
    label: 'Indirect',
    icon: <Users className="w-4 h-4" />,
    description: "If they didn't buy software, who would they hire?",
  },
  direct: {
    label: 'Direct',
    icon: <Zap className="w-4 h-4" />,
    description: "Tools they'll compare you to",
  },
};

export function CompetitionScreen({
  phase4,
  onUpdate,
  onShowEvidence,
  onContinue,
  onBack,
}: CompetitionScreenProps) {
  const [activeTab, setActiveTab] = useState<TabType>('statusQuo');
  const [newAlternativeName, setNewAlternativeName] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);

  const getAlternatives = (type: TabType): CompetitiveAlternative[] => {
    return phase4.competitiveAlternatives?.[type] || [];
  };

  const getDefaultAlternatives = (type: TabType): CompetitiveAlternative[] => {
    if (type === 'statusQuo') {
      return [
        {
          id: uuidv4(),
          name: 'Spreadsheets & Docs',
          whatUsedFor: 'Tracking campaigns, content calendars',
          whatBreaks: 'No automation, manual errors',
          whyTolerated: 'Free, familiar',
          evidence: [],
          isConfirmed: false,
        },
        {
          id: uuidv4(),
          name: 'WhatsApp / Slack chaos',
          whatUsedFor: 'Team coordination',
          whatBreaks: 'No audit trail, context lost',
          whyTolerated: "Everyone's there",
          evidence: [],
          isConfirmed: false,
        },
        {
          id: uuidv4(),
          name: 'Founder does it all',
          whatUsedFor: 'Everything marketing',
          whatBreaks: 'Burnout, bottleneck',
          whyTolerated: 'No budget for tools',
          evidence: [],
          isConfirmed: false,
        },
      ];
    } else if (type === 'indirect') {
      return [
        {
          id: uuidv4(),
          name: 'Marketing Agency',
          whatUsedFor: 'Strategy + execution',
          whatBreaks: 'Expensive, slow, misaligned',
          whyTolerated: 'Expertise outsourced',
          evidence: [],
          isConfirmed: false,
        },
        {
          id: uuidv4(),
          name: 'Freelancer / Contractor',
          whatUsedFor: 'Specific tasks',
          whatBreaks: 'Inconsistent, needs management',
          whyTolerated: 'Flexible, cheaper',
          evidence: [],
          isConfirmed: false,
        },
        {
          id: uuidv4(),
          name: 'Full-time Marketing Hire',
          whatUsedFor: 'In-house capability',
          whatBreaks: 'Expensive, single point of failure',
          whyTolerated: 'Dedicated attention',
          evidence: [],
          isConfirmed: false,
        },
      ];
    } else {
      return [
        {
          id: uuidv4(),
          name: 'HubSpot',
          whatUsedFor: 'All-in-one marketing',
          whatBreaks: 'Complex, expensive at scale',
          whyTolerated: 'Market leader',
          evidence: [],
          isConfirmed: false,
        },
        {
          id: uuidv4(),
          name: 'Mailchimp',
          whatUsedFor: 'Email marketing',
          whatBreaks: 'Limited beyond email',
          whyTolerated: 'Easy to start',
          evidence: [],
          isConfirmed: false,
        },
      ];
    }
  };

  const alternatives =
    getAlternatives(activeTab).length > 0
      ? getAlternatives(activeTab)
      : getDefaultAlternatives(activeTab);

  const handleConfirmAlternative = (id: string) => {
    const updated = alternatives.map((a) =>
      a.id === id ? { ...a, isConfirmed: true } : a
    );
    onUpdate({
      competitiveAlternatives: {
        ...phase4.competitiveAlternatives,
        [activeTab]: updated,
      },
    });
  };

  const handleRemoveAlternative = (id: string) => {
    const updated = alternatives.filter((a) => a.id !== id);
    onUpdate({
      competitiveAlternatives: {
        ...phase4.competitiveAlternatives,
        [activeTab]: updated,
      },
    });
  };

  const handleAddAlternative = () => {
    if (!newAlternativeName.trim()) return;
    const newAlt: CompetitiveAlternative = {
      id: uuidv4(),
      name: newAlternativeName.trim(),
      whatUsedFor: '',
      whatBreaks: '',
      whyTolerated: '',
      evidence: [],
      isConfirmed: true,
    };
    onUpdate({
      competitiveAlternatives: {
        ...phase4.competitiveAlternatives,
        [activeTab]: [...alternatives, newAlt],
      },
    });
    setNewAlternativeName('');
  };

  const handleUpdateAlternative = (
    id: string,
    field: keyof CompetitiveAlternative,
    value: string
  ) => {
    const updated = alternatives.map((a) =>
      a.id === id ? { ...a, [field]: value } : a
    );
    onUpdate({
      competitiveAlternatives: {
        ...phase4.competitiveAlternatives,
        [activeTab]: updated,
      },
    });
  };

  const confirmedCount = alternatives.filter((a) => a.isConfirmed).length;
  const totalCount = alternatives.length;
  const confidence =
    totalCount > 0 ? Math.round((confirmedCount / totalCount) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="flex gap-2 p-1 bg-[#F3F4EE] rounded-xl">
        {(
          Object.entries(TAB_CONFIG) as [
            TabType,
            (typeof TAB_CONFIG)[TabType],
          ][]
        ).map(([key, config]) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg transition-all ${
              activeTab === key
                ? 'bg-white text-[#2D3538] shadow-sm'
                : 'text-[#5B5F61] hover:text-[#2D3538]'
            }`}
          >
            {config.icon}
            <span className="text-sm font-medium">{config.label}</span>
            <span
              className={`text-xs px-1.5 py-0.5 rounded ${
                activeTab === key
                  ? 'bg-[#2D3538] text-white'
                  : 'bg-[#E5E6E3] text-[#5B5F61]'
              }`}
            >
              {getAlternatives(key).length ||
                getDefaultAlternatives(key).length}
            </span>
          </button>
        ))}
      </div>

      {/* Tab Description */}
      <div className="bg-[#F3F4EE] rounded-xl p-4 border border-[#E5E6E3]">
        <p className="text-sm text-[#5B5F61]">
          <strong>{TAB_CONFIG[activeTab].label}:</strong>{' '}
          {TAB_CONFIG[activeTab].description}
        </p>
      </div>

      {/* Confidence Indicator */}
      <div className="flex items-center gap-4">
        <div className="flex-1 h-2 bg-[#E5E6E3] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#2D3538] rounded-full transition-all duration-500"
            style={{ width: `${confidence}%` }}
          />
        </div>
        <span className="text-sm text-[#5B5F61]">
          {confirmedCount}/{totalCount} confirmed
        </span>
      </div>

      {/* Alternatives List */}
      <div className="space-y-4">
        {alternatives.map((alt) => (
          <div
            key={alt.id}
            className={`bg-white border rounded-2xl p-5 transition-all ${
              alt.isConfirmed ? 'border-[#2D3538]' : 'border-[#E5E6E3]'
            }`}
          >
            <div className="flex items-start gap-4">
              {/* Confirm checkbox */}
              <button
                onClick={() => handleConfirmAlternative(alt.id)}
                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-1 ${
                  alt.isConfirmed
                    ? 'bg-[#2D3538] border-[#2D3538] text-white'
                    : 'border-[#C0C1BE] hover:border-[#2D3538]'
                }`}
              >
                {alt.isConfirmed && <Check className="w-3.5 h-3.5" />}
              </button>

              <div className="flex-1">
                {/* Name */}
                <div className="flex items-center gap-3 mb-3">
                  <input
                    type="text"
                    value={alt.name}
                    onChange={(e) =>
                      handleUpdateAlternative(alt.id, 'name', e.target.value)
                    }
                    className="font-medium text-[#2D3538] bg-transparent border-none focus:outline-none focus:underline"
                  />
                  {alt.evidence.length > 0 && (
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#F3F4EE] text-[#5B5F61]">
                      {alt.evidence.length} sources
                    </span>
                  )}
                </div>

                {/* Details Grid */}
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <label className="text-[10px] font-mono uppercase tracking-wider text-[#9D9F9F] block mb-1">
                      What it's used for
                    </label>
                    <input
                      type="text"
                      value={alt.whatUsedFor}
                      onChange={(e) =>
                        handleUpdateAlternative(
                          alt.id,
                          'whatUsedFor',
                          e.target.value
                        )
                      }
                      placeholder="Main use case..."
                      className="w-full text-[#2D3538] bg-[#F3F4EE] px-3 py-2 rounded-lg border-none focus:outline-none focus:ring-1 focus:ring-[#2D3538]"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] font-mono uppercase tracking-wider text-[#9D9F9F] block mb-1">
                      What breaks
                    </label>
                    <input
                      type="text"
                      value={alt.whatBreaks}
                      onChange={(e) =>
                        handleUpdateAlternative(
                          alt.id,
                          'whatBreaks',
                          e.target.value
                        )
                      }
                      placeholder="Pain points..."
                      className="w-full text-[#2D3538] bg-[#F3F4EE] px-3 py-2 rounded-lg border-none focus:outline-none focus:ring-1 focus:ring-[#2D3538]"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] font-mono uppercase tracking-wider text-[#9D9F9F] block mb-1">
                      Why tolerated
                    </label>
                    <input
                      type="text"
                      value={alt.whyTolerated}
                      onChange={(e) =>
                        handleUpdateAlternative(
                          alt.id,
                          'whyTolerated',
                          e.target.value
                        )
                      }
                      placeholder="Reason they stick..."
                      className="w-full text-[#2D3538] bg-[#F3F4EE] px-3 py-2 rounded-lg border-none focus:outline-none focus:ring-1 focus:ring-[#2D3538]"
                    />
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onShowEvidence(alt.id)}
                  className="p-2 hover:bg-[#F3F4EE] rounded-lg transition-colors"
                  title="Show evidence"
                >
                  <Eye className="w-4 h-4 text-[#5B5F61]" />
                </button>
                <button
                  onClick={() => handleRemoveAlternative(alt.id)}
                  className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                  title="Remove"
                >
                  <X className="w-4 h-4 text-[#5B5F61] hover:text-red-500" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Add New */}
      <div className="flex gap-2">
        <input
          type="text"
          value={newAlternativeName}
          onChange={(e) => setNewAlternativeName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAddAlternative()}
          placeholder={`Add ${TAB_CONFIG[activeTab].label.toLowerCase()} alternative...`}
          className="flex-1 px-4 py-3 bg-white border border-[#E5E6E3] rounded-xl text-sm focus:outline-none focus:border-[#2D3538]"
        />
        <Button
          onClick={handleAddAlternative}
          variant="outline"
          className="border-[#2D3538] text-[#2D3538]"
        >
          <Plus className="w-4 h-4 mr-1" /> Add
        </Button>
      </div>

      {/* Direct Competitors: Collision Score */}
      {activeTab === 'direct' && alternatives.length > 0 && (
        <div className="bg-[#F3F4EE] rounded-2xl p-6 border border-[#E5E6E3]">
          <h4 className="font-medium text-[#2D3538] mb-4">
            Collision Likelihood
          </h4>
          <div className="space-y-3">
            {alternatives.slice(0, 3).map((alt) => {
              const score = Math.floor(Math.random() * 40) + 60; // Mock score 60-100%
              return (
                <div key={alt.id} className="flex items-center gap-4">
                  <span className="text-sm text-[#2D3538] w-32 truncate">
                    {alt.name}
                  </span>
                  <div className="flex-1 h-2 bg-[#E5E6E3] rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        score > 80
                          ? 'bg-red-500'
                          : score > 60
                            ? 'bg-amber-500'
                            : 'bg-green-500'
                      }`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                  <span
                    className={`text-xs font-mono ${
                      score > 80
                        ? 'text-red-600'
                        : score > 60
                          ? 'text-amber-600'
                          : 'text-green-600'
                    }`}
                  >
                    {score}%
                  </span>
                </div>
              );
            })}
          </div>
          <p className="text-xs text-[#5B5F61] mt-4">
            Based on: same buyer + same budget + same job
          </p>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t border-[#E5E6E3]">
        <Button variant="ghost" onClick={onBack} className="text-[#5B5F61]">
          Back
        </Button>
        <Button
          onClick={onContinue}
          className="bg-[#2D3538] hover:bg-[#1A1D1E] text-white px-8"
        >
          Continue <ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      </div>
    </div>
  );
}
