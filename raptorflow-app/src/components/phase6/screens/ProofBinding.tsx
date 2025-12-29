'use client';

import React, { useState } from 'react';
import {
  ProofSlot,
  Signal7Soundbite,
  RiskReversalType,
} from '@/lib/foundation';
import {
  Shield,
  BarChart3,
  Users,
  Cog,
  AlertTriangle,
  Check,
  ChevronDown,
} from 'lucide-react';

interface Props {
  proofSlots: ProofSlot[];
  soundbites: Signal7Soundbite[];
  onUpdate: (slots: ProofSlot[]) => void;
}

const RISK_REVERSAL_OPTIONS: {
  type: RiskReversalType;
  label: string;
  description: string;
}[] = [
  {
    type: 'pilot',
    label: 'Pilot Program',
    description: 'Try before you commit',
  },
  {
    type: 'guarantee',
    label: 'Guarantee',
    description: 'Money-back if not satisfied',
  },
  {
    type: 'cancel-anytime',
    label: 'Cancel Anytime',
    description: 'No lock-in contracts',
  },
  {
    type: 'pay-on-results',
    label: 'Pay on Results',
    description: 'Performance-based pricing',
  },
];

export function ProofBinding({ proofSlots, soundbites, onUpdate }: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const updateSlot = (soundbiteId: string, updates: Partial<ProofSlot>) => {
    const updated = proofSlots.map((slot) =>
      slot.soundbiteId === soundbiteId ? { ...slot, ...updates } : slot
    );
    onUpdate(updated);
  };

  const getSoundbite = (id: string) => soundbites.find((s) => s.id === id);

  const getStatusBadge = (status: ProofSlot['status']) => {
    switch (status) {
      case 'green':
        return { bg: 'bg-green-100', text: 'text-green-700', label: 'Proven' };
      case 'yellow':
        return { bg: 'bg-amber-100', text: 'text-amber-700', label: 'Partial' };
      case 'red':
        return { bg: 'bg-red-100', text: 'text-red-700', label: 'Unproven' };
    }
  };

  const calculateStatus = (slot: ProofSlot): ProofSlot['status'] => {
    const hasAny =
      slot.metricProof ||
      slot.socialProof ||
      slot.mechanismProof ||
      slot.riskReversal;
    const hasMultiple =
      [slot.metricProof, slot.socialProof, slot.mechanismProof].filter(Boolean)
        .length >= 2;
    if (hasMultiple || (hasAny && slot.riskReversal)) return 'green';
    if (hasAny) return 'yellow';
    return 'red';
  };

  const redCount = proofSlots.filter((s) => s.status === 'red').length;
  const yellowCount = proofSlots.filter((s) => s.status === 'yellow').length;
  const greenCount = proofSlots.filter((s) => s.status === 'green').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[#FAFAF8] border border-[#E5E6E3] rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-5 h-5 text-[#2D3538]" />
          <h3 className="font-medium text-[#2D3538]">Proof Binding</h3>
        </div>
        <p className="text-sm text-[#5B5F61] mb-4">
          No proof = weak message. Each soundbite needs evidence or it will
          sound like BS.
        </p>

        {/* Status Summary */}
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-sm text-[#5B5F61]">{greenCount} proven</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-amber-500" />
            <span className="text-sm text-[#5B5F61]">
              {yellowCount} partial
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-sm text-[#5B5F61]">{redCount} unproven</span>
          </div>
        </div>
      </div>

      {/* Proof Slots */}
      {proofSlots.map((slot) => {
        const soundbite = getSoundbite(slot.soundbiteId);
        if (!soundbite) return null;

        const status = calculateStatus(slot);
        const statusBadge = getStatusBadge(status);
        const isExpanded = expandedId === slot.soundbiteId;

        return (
          <div
            key={slot.soundbiteId}
            className="bg-white border border-[#E5E6E3] rounded-2xl overflow-hidden"
          >
            {/* Header */}
            <button
              onClick={() =>
                setExpandedId(isExpanded ? null : slot.soundbiteId)
              }
              className="w-full flex items-center justify-between p-4 hover:bg-[#FAFAF8] transition-colors"
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-3 h-3 rounded-full ${
                    status === 'green'
                      ? 'bg-green-500'
                      : status === 'yellow'
                        ? 'bg-amber-500'
                        : 'bg-red-500'
                  }`}
                />
                <span className="text-sm text-[#2D3538] text-left">
                  {soundbite.type.replace(/-/g, ' ')}
                </span>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] ${statusBadge.bg} ${statusBadge.text}`}
                >
                  {statusBadge.label}
                </span>
              </div>
              <ChevronDown
                className={`w-4 h-4 text-[#9D9F9F] transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              />
            </button>

            {/* Expanded Content */}
            {isExpanded && (
              <div className="p-4 border-t border-[#E5E6E3] bg-[#FAFAF8] space-y-4">
                {/* Soundbite Preview */}
                <div className="bg-[#2D3538] rounded-xl p-4">
                  <span className="text-[10px] font-mono uppercase text-white/50 block mb-1">
                    Soundbite
                  </span>
                  <p className="text-white text-sm">"{soundbite.text}"</p>
                </div>

                {/* Proof Types */}
                <div className="grid grid-cols-2 gap-3">
                  {/* Metric Proof */}
                  <div className="bg-white rounded-xl p-4 border border-[#E5E6E3]">
                    <div className="flex items-center gap-2 mb-2">
                      <BarChart3 className="w-4 h-4 text-[#9D9F9F]" />
                      <span className="text-xs font-mono uppercase text-[#9D9F9F]">
                        Metric
                      </span>
                      {slot.metricProof && (
                        <Check className="w-3 h-3 text-green-500" />
                      )}
                    </div>
                    <input
                      type="text"
                      value={slot.metricProof || ''}
                      onChange={(e) =>
                        updateSlot(slot.soundbiteId, {
                          metricProof: e.target.value,
                        })
                      }
                      placeholder="e.g., 10+ hours saved/week"
                      className="w-full px-3 py-2 bg-[#FAFAF8] border border-[#E5E6E3] rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-[#2D3538]/20"
                    />
                  </div>

                  {/* Social Proof */}
                  <div className="bg-white rounded-xl p-4 border border-[#E5E6E3]">
                    <div className="flex items-center gap-2 mb-2">
                      <Users className="w-4 h-4 text-[#9D9F9F]" />
                      <span className="text-xs font-mono uppercase text-[#9D9F9F]">
                        Social
                      </span>
                      {slot.socialProof && (
                        <Check className="w-3 h-3 text-green-500" />
                      )}
                    </div>
                    <input
                      type="text"
                      value={slot.socialProof || ''}
                      onChange={(e) =>
                        updateSlot(slot.soundbiteId, {
                          socialProof: e.target.value,
                        })
                      }
                      placeholder="e.g., Trusted by 500+ founders"
                      className="w-full px-3 py-2 bg-[#FAFAF8] border border-[#E5E6E3] rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-[#2D3538]/20"
                    />
                  </div>

                  {/* Mechanism Proof */}
                  <div className="bg-white rounded-xl p-4 border border-[#E5E6E3]">
                    <div className="flex items-center gap-2 mb-2">
                      <Cog className="w-4 h-4 text-[#9D9F9F]" />
                      <span className="text-xs font-mono uppercase text-[#9D9F9F]">
                        Mechanism
                      </span>
                      {slot.mechanismProof && (
                        <Check className="w-3 h-3 text-green-500" />
                      )}
                    </div>
                    <input
                      type="text"
                      value={slot.mechanismProof || ''}
                      onChange={(e) =>
                        updateSlot(slot.soundbiteId, {
                          mechanismProof: e.target.value,
                        })
                      }
                      placeholder="e.g., Link to demo/diagram"
                      className="w-full px-3 py-2 bg-[#FAFAF8] border border-[#E5E6E3] rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-[#2D3538]/20"
                    />
                  </div>

                  {/* Risk Reversal */}
                  <div className="bg-white rounded-xl p-4 border border-[#E5E6E3]">
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="w-4 h-4 text-[#9D9F9F]" />
                      <span className="text-xs font-mono uppercase text-[#9D9F9F]">
                        Risk Reversal
                      </span>
                      {slot.riskReversal && (
                        <Check className="w-3 h-3 text-green-500" />
                      )}
                    </div>
                    <select
                      value={slot.riskReversal?.type || ''}
                      onChange={(e) => {
                        const type = e.target.value as RiskReversalType;
                        if (type) {
                          updateSlot(slot.soundbiteId, {
                            riskReversal: { type, details: '' },
                          });
                        } else {
                          updateSlot(slot.soundbiteId, {
                            riskReversal: undefined,
                          });
                        }
                      }}
                      className="w-full px-3 py-2 bg-[#FAFAF8] border border-[#E5E6E3] rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-[#2D3538]/20"
                    >
                      <option value="">Select...</option>
                      {RISK_REVERSAL_OPTIONS.map((opt) => (
                        <option key={opt.type} value={opt.type}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Warning if red */}
                {status === 'red' && (
                  <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-xl">
                    <AlertTriangle className="w-4 h-4 text-red-500" />
                    <span className="text-sm text-red-700">
                      This claim will sound like BS without proof
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
