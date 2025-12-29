'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Ban,
  Building2,
  DollarSign,
  UserX,
  Wrench,
  AlertTriangle,
  Plus,
  X,
  Check,
  TrendingDown,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { NegativeICP, NegativeICPDisqualifier } from '@/lib/foundation';

interface NegativeICPBuilderProps {
  negativeICP: NegativeICP;
  onUpdate: (updates: Partial<NegativeICP>) => void;
  onAddDisqualifier: (
    disqualifier: Omit<NegativeICPDisqualifier, 'id'>
  ) => void;
  onRemoveDisqualifier: (id: string) => void;
  onUpdateDisqualifier: (
    id: string,
    updates: Partial<NegativeICPDisqualifier>
  ) => void;
}

const DISQUALIFIER_TYPES: Array<{
  type: NegativeICPDisqualifier['type'];
  label: string;
  icon: React.ElementType;
  color: string;
  examples: string[];
}> = [
  {
    type: 'industry',
    label: 'Industry',
    icon: Building2,
    color: '#E57373',
    examples: [
      'Government',
      'Heavy manufacturing',
      'Highly regulated healthcare',
    ],
  },
  {
    type: 'budget',
    label: 'Budget',
    icon: DollarSign,
    color: '#FFB74D',
    examples: ['Below $500/mo', 'No marketing budget', 'Price-first buyers'],
  },
  {
    type: 'behavior',
    label: 'Behavior',
    icon: UserX,
    color: '#9D9F9F',
    examples: [
      'DIY forever mindset',
      'Tool hoarders',
      'No decision-maker access',
    ],
  },
  {
    type: 'structure',
    label: 'Structure',
    icon: Wrench,
    color: '#64B5F6',
    examples: [
      'No marketing person',
      'Enterprise bureaucracy',
      'Committee paralysis',
    ],
  },
];

const DEFAULT_DISQUALIFIERS: Omit<NegativeICPDisqualifier, 'id'>[] = [
  {
    type: 'budget',
    description: 'Budget below $500/month',
    churnRiskScore: 85,
  },
  {
    type: 'behavior',
    description: 'DIY forever mindset - prefers building over buying',
    churnRiskScore: 90,
  },
  {
    type: 'structure',
    description: 'No champion or internal advocate',
    churnRiskScore: 75,
  },
  {
    type: 'industry',
    description: 'Heavily regulated industries (banking, healthcare)',
    churnRiskScore: 60,
  },
];

const DEFAULT_BEHAVIOR_SIGNALS = [
  'Asks for discounts before seeing demo',
  'Multiple tool evaluations in parallel',
  'No clear decision timeline',
  '"We can probably build this ourselves"',
];

function DisqualifierCard({
  disqualifier,
  typeConfig,
  onUpdate,
  onRemove,
}: {
  disqualifier: NegativeICPDisqualifier;
  typeConfig: (typeof DISQUALIFIER_TYPES)[0];
  onUpdate: (updates: Partial<NegativeICPDisqualifier>) => void;
  onRemove: () => void;
}) {
  const Icon = typeConfig.icon;
  const churnColor =
    disqualifier.churnRiskScore >= 80
      ? 'text-red-600'
      : disqualifier.churnRiskScore >= 60
        ? 'text-yellow-600'
        : 'text-green-600';

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-white border border-[#E5E6E3] rounded-xl overflow-hidden"
    >
      <div className="flex items-stretch">
        {/* Type indicator */}
        <div
          className="w-12 flex items-center justify-center"
          style={{ backgroundColor: typeConfig.color + '20' }}
        >
          <Icon className="w-5 h-5" style={{ color: typeConfig.color }} />
        </div>

        {/* Content */}
        <div className="flex-1 p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <span
                className="text-[9px] font-mono uppercase px-2 py-0.5 rounded"
                style={{
                  backgroundColor: typeConfig.color + '20',
                  color: typeConfig.color,
                }}
              >
                {typeConfig.label}
              </span>
              <p className="text-sm text-[#2D3538] mt-2">
                {disqualifier.description}
              </p>
            </div>
            <button
              onClick={onRemove}
              className="p-1 hover:bg-red-50 rounded-lg transition-colors"
            >
              <X className="w-4 h-4 text-[#9D9F9F] hover:text-red-500" />
            </button>
          </div>
        </div>

        {/* Churn Risk */}
        <div className="w-24 bg-[#FAFAF8] flex flex-col items-center justify-center border-l border-[#E5E6E3]">
          <TrendingDown className={`w-4 h-4 ${churnColor}`} />
          <span className={`text-lg font-mono font-bold ${churnColor}`}>
            {disqualifier.churnRiskScore}%
          </span>
          <span className="text-[9px] font-mono uppercase text-[#9D9F9F]">
            Churn Risk
          </span>
        </div>
      </div>
    </motion.div>
  );
}

export function NegativeICPBuilder({
  negativeICP,
  onUpdate,
  onAddDisqualifier,
  onRemoveDisqualifier,
  onUpdateDisqualifier,
}: NegativeICPBuilderProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newDisqualifier, setNewDisqualifier] = useState<
    Omit<NegativeICPDisqualifier, 'id'>
  >({
    type: 'behavior',
    description: '',
    churnRiskScore: 70,
  });
  const [newIndustry, setNewIndustry] = useState('');
  const [newSignal, setNewSignal] = useState('');

  // Use defaults if empty
  const displayDisqualifiers =
    (negativeICP.disqualifiers?.length || 0) > 0
      ? negativeICP.disqualifiers
      : DEFAULT_DISQUALIFIERS.map((d, i) => ({ ...d, id: `default-${i}` }));

  const displaySignals =
    (negativeICP.behaviorSignals?.length || 0) > 0
      ? negativeICP.behaviorSignals
      : DEFAULT_BEHAVIOR_SIGNALS;

  const handleAddDisqualifier = () => {
    if (newDisqualifier.description.trim()) {
      onAddDisqualifier(newDisqualifier);
      setNewDisqualifier({
        type: 'behavior',
        description: '',
        churnRiskScore: 70,
      });
      setShowAddForm(false);
    }
  };

  const handleAddIndustry = () => {
    if (
      newIndustry.trim() &&
      !negativeICP.industries?.includes(newIndustry.trim())
    ) {
      onUpdate({
        industries: [...(negativeICP.industries || []), newIndustry.trim()],
      });
      setNewIndustry('');
    }
  };

  const handleRemoveIndustry = (industry: string) => {
    onUpdate({
      industries: negativeICP.industries?.filter((i) => i !== industry) || [],
    });
  };

  const handleAddSignal = () => {
    if (
      newSignal.trim() &&
      !negativeICP.behaviorSignals?.includes(newSignal.trim())
    ) {
      onUpdate({
        behaviorSignals: [
          ...(negativeICP.behaviorSignals || displaySignals || []),
          newSignal.trim(),
        ],
      });
      setNewSignal('');
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
        <Ban className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm text-red-800">
            <strong>Negative ICP</strong> — These are accounts to avoid. They
            churn, take too long, or have fundamentally misaligned expectations.
          </p>
          <p className="text-xs text-red-600 mt-1">
            Defining who NOT to sell to is as important as who to sell to.
          </p>
        </div>
      </div>

      {/* Industries to Avoid */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <Building2 className="w-5 h-5 text-red-500" />
          <h3 className="font-medium text-[#2D3538]">Industries to Avoid</h3>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          {(negativeICP.industries || []).map((industry) => (
            <div
              key={industry}
              className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-xl px-3 py-2"
            >
              <span className="text-sm text-red-800">{industry}</span>
              <button onClick={() => handleRemoveIndustry(industry)}>
                <X className="w-3 h-3 text-red-400 hover:text-red-600" />
              </button>
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={newIndustry}
            onChange={(e) => setNewIndustry(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddIndustry()}
            placeholder="Add industry to avoid..."
            className="flex-1 border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-red-300"
          />
          <Button
            onClick={handleAddIndustry}
            disabled={!newIndustry.trim()}
            variant="outline"
            className="rounded-xl border-red-200 text-red-600 hover:bg-red-50"
          >
            <Plus className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Minimum Budget */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <DollarSign className="w-5 h-5 text-[#9D9F9F]" />
          <h3 className="font-medium text-[#2D3538]">
            Minimum Budget Threshold
          </h3>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-[#9D9F9F]">$</span>
          <input
            type="number"
            value={negativeICP.minBudgetThreshold || 0}
            onChange={(e) =>
              onUpdate({ minBudgetThreshold: parseInt(e.target.value) || 0 })
            }
            className="w-40 border border-[#E5E6E3] rounded-xl px-4 py-2 text-lg focus:outline-none focus:border-[#2D3538]"
            placeholder="500"
          />
          <span className="text-sm text-[#5B5F61]">per month minimum</span>
        </div>
        <p className="text-xs text-[#9D9F9F] mt-2">
          Accounts below this threshold typically churn or require
          disproportionate support.
        </p>
      </div>

      {/* Disqualifiers */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <div>
              <h3 className="font-medium text-[#2D3538]">Disqualifiers</h3>
              <p className="text-xs text-[#5B5F61]">
                Red flags that signal poor fit
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAddForm(!showAddForm)}
            className="rounded-xl"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add
          </Button>
        </div>

        {showAddForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-xl p-4 mb-4 space-y-4"
          >
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="text-xs text-[#5B5F61] mb-2 block">
                  Type
                </label>
                <select
                  value={newDisqualifier.type}
                  onChange={(e) =>
                    setNewDisqualifier({
                      ...newDisqualifier,
                      type: e.target.value as NegativeICPDisqualifier['type'],
                    })
                  }
                  className="w-full border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none"
                >
                  {DISQUALIFIER_TYPES.map((t) => (
                    <option key={t.type} value={t.type}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="w-32">
                <label className="text-xs text-[#5B5F61] mb-2 block">
                  Churn Risk %
                </label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={newDisqualifier.churnRiskScore}
                  onChange={(e) =>
                    setNewDisqualifier({
                      ...newDisqualifier,
                      churnRiskScore: parseInt(e.target.value) || 70,
                    })
                  }
                  className="w-full border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none"
                />
              </div>
            </div>
            <div>
              <label className="text-xs text-[#5B5F61] mb-2 block">
                Description
              </label>
              <input
                type="text"
                value={newDisqualifier.description}
                onChange={(e) =>
                  setNewDisqualifier({
                    ...newDisqualifier,
                    description: e.target.value,
                  })
                }
                placeholder="Describe this disqualifying factor..."
                className="w-full border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setShowAddForm(false)}
                className="rounded-xl"
              >
                Cancel
              </Button>
              <Button
                onClick={handleAddDisqualifier}
                disabled={!newDisqualifier.description.trim()}
                className="bg-[#2D3538] text-white rounded-xl"
              >
                Add Disqualifier
              </Button>
            </div>
          </motion.div>
        )}

        <div className="space-y-3">
          {(displayDisqualifiers || []).map((disqualifier) => {
            const typeConfig =
              DISQUALIFIER_TYPES.find((t) => t.type === disqualifier.type) ||
              DISQUALIFIER_TYPES[2];
            return (
              <DisqualifierCard
                key={disqualifier.id}
                disqualifier={disqualifier}
                typeConfig={typeConfig}
                onUpdate={(updates) => onUpdateDisqualifier(disqualifier.id, updates)}
                onRemove={() => onRemoveDisqualifier(disqualifier.id)}
              />
            );
          })}
        </div>
      </div>

      {/* Behavior Signals */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <UserX className="w-5 h-5 text-[#9D9F9F]" />
          <h3 className="font-medium text-[#2D3538]">
            Red Flag Behavior Signals
          </h3>
        </div>

        <div className="space-y-2 mb-4">
          {(displaySignals || []).map((signal, index) => (
            <div
              key={index}
              className="flex items-center gap-3 bg-[#FAFAF8] rounded-xl px-4 py-3"
            >
              <AlertTriangle className="w-4 h-4 text-yellow-600 flex-shrink-0" />
              <span className="text-sm text-[#2D3538]">"{signal}"</span>
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={newSignal}
            onChange={(e) => setNewSignal(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddSignal()}
            placeholder="Add behavior signal..."
            className="flex-1 border border-[#E5E6E3] rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-[#2D3538]"
          />
          <Button
            onClick={handleAddSignal}
            disabled={!newSignal.trim()}
            variant="outline"
            className="rounded-xl"
          >
            <Plus className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
