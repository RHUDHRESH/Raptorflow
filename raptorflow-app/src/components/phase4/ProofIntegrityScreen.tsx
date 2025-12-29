'use client';

import React, { useState } from 'react';
import {
  ChevronRight,
  Check,
  AlertCircle,
  Upload,
  FileText,
  RefreshCw,
  Download,
  Lock,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Phase4Data, ProofIntegrityItem, ProofTier } from '@/lib/foundation';
import { v4 as uuidv4 } from 'uuid';

interface ProofIntegrityScreenProps {
  phase4: Phase4Data;
  onUpdate: (updates: Partial<Phase4Data>) => void;
  onContinue: () => void;
  onBack: () => void;
}

const TIER_INFO: Record<
  ProofTier,
  { label: string; color: string; description: string }
> = {
  1: {
    label: 'Tier 1',
    color: 'bg-green-100 text-green-700 border-green-200',
    description: 'Quantified case study',
  },
  2: {
    label: 'Tier 2',
    color: 'bg-blue-100 text-blue-700 border-blue-200',
    description: 'Benchmark/third-party',
  },
  3: {
    label: 'Tier 3',
    color: 'bg-amber-100 text-amber-700 border-amber-200',
    description: 'Testimonial',
  },
  4: {
    label: 'Tier 4',
    color: 'bg-red-100 text-red-700 border-red-200',
    description: 'Internal assertion',
  },
};

export function ProofIntegrityScreen({
  phase4,
  onUpdate,
  onContinue,
  onBack,
}: ProofIntegrityScreenProps) {
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null);

  // Build proof integrity items from claims
  const buildProofItems = (): ProofIntegrityItem[] => {
    if (phase4.proofIntegrity?.length) return phase4.proofIntegrity;

    const items: ProofIntegrityItem[] = [];

    // From value claims
    phase4.valueClaims?.forEach((claim) => {
      items.push({
        id: claim.id,
        claimId: claim.id,
        claim: claim.claim,
        claimText: claim.claimText,
        evidenceAttached: claim.evidence.length > 0,
        tier: claim.evidence.length > 0 ? 2 : 4,
        tierLabel: claim.evidence.length > 0 ? 'Has proof' : 'Needs proof',
        needsFix: claim.evidence.length === 0 && (claim.isSelected ?? false),
        isHypothesis: claim.evidence.length === 0,
      });
    });

    // From positioning statement components
    if (phase4.positioningStatement) {
      items.push({
        id: uuidv4(),
        claimId: 'positioning-statement',
        claim: phase4.positioningStatement,
        claimText: phase4.positioningStatement,
        evidenceAttached: (phase4.proofStack?.length || 0) > 0,
        tier: 2,
        tierLabel: 'Positioning Statement',
        needsFix: (phase4.proofStack?.length || 0) === 0,
        isHypothesis: false,
      });
    }

    return items.length > 0
      ? items
      : [
          {
            id: uuidv4(),
            claim: 'Save 10+ hours per week on marketing operations',
            claimText: 'Save 10+ hours per week on marketing operations',
            evidenceAttached: true,
            tier: 1 as ProofTier,
            tierLabel: 'Case study available',
            needsFix: false,
            isHypothesis: false,
          },
          {
            id: uuidv4(),
            claim: 'Unified positioning for all marketing activities',
            claimText: 'Unified positioning for all marketing activities',
            evidenceAttached: false,
            tier: 4 as ProofTier,
            tierLabel: 'No proof yet',
            needsFix: true,
            isHypothesis: true,
          },
          {
            id: uuidv4(),
            claim: 'AI-powered insights that competitors lack',
            claimText: 'AI-powered insights that competitors lack',
            evidenceAttached: false,
            tier: 4 as ProofTier,
            tierLabel: 'No proof yet',
            needsFix: true,
            isHypothesis: true,
          },
        ];
  };

  const proofItems = buildProofItems();
  const needsFixItems = proofItems.filter((p) => p.needsFix);
  const verifiedItems = proofItems.filter(
    (p) => !p.needsFix && !p.isHypothesis
  );

  const handleTierChange = (itemId: string, tier: ProofTier) => {
    const updated = proofItems.map((p) =>
      p.id === itemId
        ? {
            ...p,
            tier,
            tierLabel: TIER_INFO[tier].description,
            needsFix: tier === 4,
            isHypothesis: tier === 4,
          }
        : p
    );
    onUpdate({ proofIntegrity: updated });
  };

  const handleMarkHypothesis = (itemId: string) => {
    const updated = proofItems.map((p) =>
      p.id === itemId
        ? {
            ...p,
            isHypothesis: true,
            needsFix: false,
            tierLabel: 'Marked as hypothesis',
          }
        : p
    );
    onUpdate({ proofIntegrity: updated });
  };

  const integrityScore =
    proofItems.length > 0
      ? Math.round((verifiedItems.length / proofItems.length) * 100)
      : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-[#F3F4EE] rounded-2xl p-5 border border-[#E5E6E3]">
        <p className="text-sm text-[#5B5F61]">
          <strong>Anti-BS Firewall:</strong> Every claim must attach proof or be
          marked as hypothesis. This is where you stop sounding like every other
          SaaS. No claim without evidence.
        </p>
      </div>

      {/* Integrity Score */}
      <div className="bg-white border border-[#E5E6E3] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-serif text-xl text-[#2D3538]">
              Claim Integrity Score
            </h3>
            <p className="text-sm text-[#5B5F61] mt-1">
              {verifiedItems.length} verified • {needsFixItems.length} need
              attention
            </p>
          </div>
          <div
            className={`text-4xl font-serif ${
              integrityScore > 70
                ? 'text-green-600'
                : integrityScore > 40
                  ? 'text-amber-600'
                  : 'text-red-600'
            }`}
          >
            {integrityScore}%
          </div>
        </div>
        <div className="h-2 bg-[#E5E6E3] rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              integrityScore > 70
                ? 'bg-green-500'
                : integrityScore > 40
                  ? 'bg-amber-500'
                  : 'bg-red-500'
            }`}
            style={{ width: `${integrityScore}%` }}
          />
        </div>
      </div>

      {/* Fix What's Weak Section */}
      {needsFixItems.length > 0 && (
        <div>
          <h3 className="font-serif text-lg text-[#2D3538] mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-amber-500" />
            Fix Weak Claims ({needsFixItems.length})
          </h3>

          <div className="space-y-3">
            {needsFixItems.map((item) => (
              <div
                key={item.id}
                className="bg-amber-50 border border-amber-200 rounded-xl p-5"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <p className="text-sm text-[#2D3538] font-medium mb-2">
                      "{item.claimText}"
                    </p>
                    <span
                      className={`text-[10px] font-mono uppercase px-2 py-1 rounded border ${TIER_INFO[item.tier].color}`}
                    >
                      {TIER_INFO[item.tier].description}
                    </span>
                  </div>
                  <div className="flex flex-col gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-amber-400 text-amber-700 hover:bg-amber-100"
                    >
                      <Upload className="w-3 h-3 mr-1" /> Upload Proof
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => item.id && handleMarkHypothesis(item.id)}
                      className="text-[#5B5F61]"
                    >
                      Mark as Hypothesis
                    </Button>
                  </div>
                </div>

                {/* Tier Selector */}
                <div className="mt-4 pt-4 border-t border-amber-200">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-amber-600 block mb-2">
                    Proof strength
                  </span>
                  <div className="flex gap-2">
                    {([1, 2, 3, 4] as ProofTier[]).map((tier) => (
                      <button
                        key={tier}
                        onClick={() => item.id && handleTierChange(item.id, tier)}
                        className={`px-3 py-1.5 rounded-lg text-[10px] font-mono transition-colors ${
                          item.tier === tier
                            ? TIER_INFO[tier].color + ' border'
                            : 'bg-white text-[#5B5F61] hover:bg-[#F3F4EE]'
                        }`}
                      >
                        {TIER_INFO[tier].label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Verified Claims */}
      {verifiedItems.length > 0 && (
        <div>
          <h3 className="font-serif text-lg text-[#2D3538] mb-4 flex items-center gap-2">
            <Check className="w-5 h-5 text-green-500" />
            Verified Claims ({verifiedItems.length})
          </h3>

          <div className="space-y-2">
            {verifiedItems.map((item) => (
              <div
                key={item.id}
                className="bg-white border border-[#E5E6E3] rounded-xl p-4 flex items-center gap-4"
              >
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Check className="w-3.5 h-3.5 text-green-600" />
                </div>
                <p className="text-sm text-[#2D3538] flex-1">
                  {item.claimText}
                </p>
                <span
                  className={`text-[10px] font-mono uppercase px-2 py-1 rounded border ${TIER_INFO[item.tier].color}`}
                >
                  {TIER_INFO[item.tier].label}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hypothesis Claims */}
      {proofItems.filter((p) => p.isHypothesis && !p.needsFix).length > 0 && (
        <div>
          <h3 className="font-serif text-lg text-[#2D3538] mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-[#5B5F61]" />
            Hypotheses (to validate later)
          </h3>

          <div className="space-y-2">
            {proofItems
              .filter((p) => p.isHypothesis && !p.needsFix)
              .map((item) => (
                <div
                  key={item.id}
                  className="bg-[#F3F4EE] border border-dashed border-[#C0C1BE] rounded-xl p-4 flex items-center gap-4"
                >
                  <p className="text-sm text-[#5B5F61] flex-1 italic">
                    {item.claimText}
                  </p>
                  <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                    Hypothesis
                  </span>
                </div>
              ))}
          </div>
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
