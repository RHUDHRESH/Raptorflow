'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Target,
  TrendingUp,
  Users,
  AlertTriangle,
  Check,
  ChevronDown,
  ChevronUp,
  Edit3,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { CandidateSegment, ICPFitScore } from '@/lib/foundation';

interface ICPCandidateGeneratorProps {
  candidates: CandidateSegment[];
  onSelectPrimary: (id: string) => void;
  onSelectSecondary: (id: string) => void;
  onUpdateCandidate: (id: string, updates: Partial<CandidateSegment>) => void;
  primaryId?: string;
  secondaryIds: string[];
}

function FitScoreBar({ score, label }: { score: number; label: string }) {
  const percentage = (score / 5) * 100;
  return (
    <div className="flex items-center gap-2">
      <span className="text-[10px] font-mono uppercase text-[#9D9F9F] w-20 flex-shrink-0">
        {label}
      </span>
      <div className="flex-1 h-1.5 bg-[#F3F4EE] rounded-full overflow-hidden">
        <div
          className="h-full bg-[#2D3538] rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-[10px] font-mono text-[#9D9F9F] w-4">{score}</span>
    </div>
  );
}

function CandidateCard({
  candidate,
  index,
  isPrimary,
  isSecondary,
  onSelectPrimary,
  onSelectSecondary,
  expanded,
  onToggleExpand,
}: {
  candidate: CandidateSegment;
  index: number;
  isPrimary: boolean;
  isSecondary: boolean;
  onSelectPrimary: () => void;
  onSelectSecondary: () => void;
  expanded: boolean;
  onToggleExpand: () => void;
}) {
  const fitScore = candidate.fitScore;
  const scoreColor =
    fitScore.total >= 80
      ? 'text-green-600'
      : fitScore.total >= 60
        ? 'text-yellow-600'
        : 'text-red-600';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`bg-white border-2 rounded-2xl overflow-hidden transition-all ${
        isPrimary
          ? 'border-[#2D3538] shadow-lg'
          : isSecondary
            ? 'border-[#9D9F9F]'
            : 'border-[#E5E6E3]'
      }`}
    >
      {/* Header */}
      <div className="p-6 border-b border-[#E5E6E3]">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                isPrimary ? 'bg-[#2D3538]' : 'bg-[#F3F4EE]'
              }`}
            >
              <Users
                className={`w-5 h-5 ${isPrimary ? 'text-white' : 'text-[#2D3538]'}`}
              />
            </div>
            <div>
              <span className="text-[9px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                Candidate {String.fromCharCode(65 + index)}
              </span>
              {isPrimary && (
                <span className="ml-2 text-[9px] font-mono uppercase bg-[#2D3538] text-white px-2 py-0.5 rounded">
                  Primary
                </span>
              )}
              {isSecondary && (
                <span className="ml-2 text-[9px] font-mono uppercase bg-[#9D9F9F] text-white px-2 py-0.5 rounded">
                  Secondary
                </span>
              )}
            </div>
          </div>
          <div className="text-right">
            <span className={`font-mono text-2xl font-bold ${scoreColor}`}>
              {fitScore.total}
            </span>
            <span className="text-[10px] font-mono text-[#9D9F9F] block">
              Fit Score
            </span>
          </div>
        </div>

        <h3 className="font-serif text-xl text-[#2D3538] mb-2">
          {candidate.label}
        </h3>
        <p className="text-sm text-[#5B5F61]">
          Displacing:{' '}
          <span className="font-medium text-[#2D3538]">
            {candidate.displacedAlternative}
          </span>
        </p>
      </div>

      {/* Content */}
      <div className="p-6 space-y-4">
        {/* Dominant Value */}
        <div>
          <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-2 block">
            Dominant Value
          </span>
          <p className="text-sm text-[#2D3538] bg-[#F3F4EE] rounded-xl px-4 py-3">
            {candidate.dominantValue || 'Not defined'}
          </p>
        </div>

        {/* Score Breakdown */}
        <div className="space-y-2">
          <FitScoreBar score={fitScore.valueFit} label="Value Fit" />
          <FitScoreBar score={fitScore.switchability} label="Switch" />
          <FitScoreBar score={fitScore.reachability} label="Reach" />
          <FitScoreBar score={fitScore.dealSize} label="Deal Size" />
          <FitScoreBar score={fitScore.confidence} label="Confidence" />
        </div>

        {/* Expanded Details */}
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="pt-4 border-t border-[#E5E6E3] space-y-4"
          >
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
                  Why This Segment
                </span>
                <p className="text-sm text-[#5B5F61]">
                  {candidate.reason ||
                    'Auto-matched based on pain/trigger alignment'}
                </p>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
                  Status
                </span>
                <div className="flex items-center gap-2">
                  {candidate.kept ? (
                    <div className="flex items-center gap-1 text-green-600">
                      <Check className="w-4 h-4" />
                      <span className="text-sm">Kept</span>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1 text-[#9D9F9F]">
                      <AlertTriangle className="w-4 h-4" />
                      <span className="text-sm">Not selected</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Actions */}
      <div className="px-6 py-4 bg-[#FAFAF8] border-t border-[#E5E6E3] flex items-center justify-between">
        <button
          onClick={onToggleExpand}
          className="flex items-center gap-2 text-sm text-[#5B5F61] hover:text-[#2D3538] transition-colors"
        >
          {expanded ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
          {expanded ? 'Less' : 'More'}
        </button>

        <div className="flex gap-2">
          {!isPrimary && (
            <Button
              onClick={onSelectPrimary}
              variant={isPrimary ? 'default' : 'outline'}
              size="sm"
              className="rounded-xl"
            >
              Set Primary
            </Button>
          )}
          {!isPrimary && !isSecondary && (
            <Button
              onClick={onSelectSecondary}
              variant="outline"
              size="sm"
              className="rounded-xl"
            >
              Add Secondary
            </Button>
          )}
          {isSecondary && (
            <Button
              onClick={onSelectSecondary}
              variant="outline"
              size="sm"
              className="rounded-xl text-red-600 border-red-200 hover:bg-red-50"
            >
              Remove
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export function ICPCandidateGenerator({
  candidates,
  onSelectPrimary,
  onSelectSecondary,
  onUpdateCandidate,
  primaryId,
  secondaryIds,
}: ICPCandidateGeneratorProps) {
  const [expandedCards, setExpandedCards] = useState<Set<string>>(new Set());

  const toggleExpand = (id: string) => {
    setExpandedCards((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // Sort candidates by fit score, show top 3
  const sortedCandidates = [...candidates]
    .sort((a, b) => b.fitScore.total - a.fitScore.total)
    .slice(0, 3);

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="flex items-center gap-3 p-4 bg-[#F3F4EE] rounded-xl">
        <Sparkles className="w-5 h-5 text-[#2D3538]" />
        <p className="text-sm text-[#5B5F61]">
          <span className="font-medium text-[#2D3538]">
            {candidates.length} candidate segments
          </span>{' '}
          generated. Select a Primary ICP and optionally add Secondary ICPs.
        </p>
      </div>

      {/* Candidate Cards */}
      <div className="grid gap-6">
        {sortedCandidates.map((candidate, index) => (
          <CandidateCard
            key={candidate.id}
            candidate={candidate}
            index={index}
            isPrimary={primaryId === candidate.id}
            isSecondary={secondaryIds.includes(candidate.id)}
            onSelectPrimary={() => onSelectPrimary(candidate.id)}
            onSelectSecondary={() => onSelectSecondary(candidate.id)}
            expanded={expandedCards.has(candidate.id)}
            onToggleExpand={() => toggleExpand(candidate.id)}
          />
        ))}
      </div>

      {/* Selection Summary */}
      {(primaryId || secondaryIds.length > 0) && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-[#2D3538] rounded-2xl p-6 text-white"
        >
          <h4 className="text-[10px] font-mono uppercase tracking-[0.15em] text-white/60 mb-3">
            Your Selection
          </h4>
          <div className="flex flex-wrap gap-3">
            {primaryId && (
              <div className="bg-white/10 rounded-xl px-4 py-2 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-white" />
                <span className="text-sm">
                  Primary:{' '}
                  {
                    candidates
                      .find((c) => c.id === primaryId)
                      ?.label.split(' (')[0]
                  }
                </span>
              </div>
            )}
            {secondaryIds.map((id) => (
              <div
                key={id}
                className="bg-white/5 rounded-xl px-4 py-2 flex items-center gap-2"
              >
                <div className="w-2 h-2 rounded-full bg-white/60" />
                <span className="text-sm text-white/80">
                  Secondary:{' '}
                  {candidates.find((c) => c.id === id)?.label.split(' (')[0]}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
