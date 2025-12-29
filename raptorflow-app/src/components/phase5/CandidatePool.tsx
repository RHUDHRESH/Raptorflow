'use client';

import React from 'react';
import { CandidateSegment, ICPFitScore } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { ArrowRight, Check, X, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CandidatePoolProps {
  candidates: CandidateSegment[];
  onChange: (candidates: CandidateSegment[]) => void;
  onContinue: () => void;
}

function FitScoreBreakdown({ score }: { score: ICPFitScore }) {
  const bars = [
    { label: 'Value Fit', value: score.valueFit, color: 'bg-blue-500' },
    {
      label: 'Switchability',
      value: score.switchability,
      color: 'bg-green-500',
    },
    {
      label: 'Reachability',
      value: score.reachability,
      color: 'bg-purple-500',
    },
    { label: 'Deal Size', value: score.dealSize, color: 'bg-amber-500' },
    { label: 'Confidence', value: score.confidence, color: 'bg-teal-500' },
  ];

  return (
    <div className="space-y-2">
      {bars.map(({ label, value, color }) => (
        <div key={label} className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground w-20">{label}</span>
          <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
            <div
              className={cn('h-full rounded-full', color)}
              style={{ width: `${(value / 5) * 100}%` }}
            />
          </div>
          <span className="text-xs font-medium w-4">{value}</span>
        </div>
      ))}
    </div>
  );
}

function CandidateCard({
  candidate,
  onToggle,
}: {
  candidate: CandidateSegment;
  onToggle: () => void;
}) {
  const [expanded, setExpanded] = React.useState(false);

  return (
    <div
      className={cn(
        'p-5 rounded-xl border-2 transition-all',
        candidate.kept
          ? 'border-green-500 bg-green-50/30 dark:bg-green-950/20'
          : 'border-border bg-card opacity-60'
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-semibold">{candidate.label.split(' (')[0]}</h3>
            <span
              className={cn(
                'text-lg font-bold',
                candidate.fitScore.total >= 80
                  ? 'text-green-600'
                  : candidate.fitScore.total >= 60
                    ? 'text-amber-600'
                    : 'text-red-600'
              )}
            >
              {candidate.fitScore.total}%
            </span>
          </div>
          <p className="text-sm text-muted-foreground mb-2">
            Displacing:{' '}
            <span className="font-medium">
              {candidate.displacedAlternative}
            </span>
          </p>
          <p className="text-sm text-muted-foreground">
            Value hook:{' '}
            <span className="font-medium">{candidate.dominantValue}</span>
          </p>
        </div>

        <div className="flex flex-col gap-2">
          <Button
            size="sm"
            variant={candidate.kept ? 'default' : 'outline'}
            onClick={onToggle}
          >
            {candidate.kept ? (
              <Check className="h-4 w-4 mr-1" />
            ) : (
              <X className="h-4 w-4 mr-1" />
            )}
            {candidate.kept ? 'Keep' : 'Discard'}
          </Button>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-muted-foreground flex items-center gap-1"
          >
            {expanded ? (
              <ChevronUp className="h-3 w-3" />
            ) : (
              <ChevronDown className="h-3 w-3" />
            )}
            Details
          </button>
        </div>
      </div>

      {expanded && (
        <div className="mt-4 pt-4 border-t">
          <FitScoreBreakdown score={candidate.fitScore} />
        </div>
      )}
    </div>
  );
}

export function CandidatePool({
  candidates,
  onChange,
  onContinue,
}: CandidatePoolProps) {
  const keptCount = candidates.filter((c) => c.kept).length;

  const handleToggle = (candidateId: string) => {
    onChange(
      candidates.map((c) =>
        c.id === candidateId ? { ...c, kept: !c.kept } : c
      )
    );
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-serif font-bold text-foreground">
          Candidate ICP Pool
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Review the generated segment candidates. Keep 3-5 to become your ICPs.
        </p>
      </div>

      {/* Stats */}
      <div className="flex justify-center gap-8 text-center">
        <div>
          <div className="text-3xl font-bold text-primary">{keptCount}</div>
          <div className="text-xs text-muted-foreground">Kept</div>
        </div>
        <div>
          <div className="text-3xl font-bold text-muted-foreground">
            {candidates.length - keptCount}
          </div>
          <div className="text-xs text-muted-foreground">Discarded</div>
        </div>
      </div>

      {/* Candidates */}
      <div className="grid gap-4 max-w-3xl mx-auto">
        {candidates.map((candidate) => (
          <CandidateCard
            key={candidate.id}
            candidate={candidate}
            onToggle={() => handleToggle(candidate.id)}
          />
        ))}
      </div>

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          size="lg"
          onClick={onContinue}
          disabled={keptCount < 1 || keptCount > 5}
          className="px-8 py-6 text-lg rounded-xl"
        >
          {keptCount < 1
            ? 'Keep at least 1 ICP'
            : keptCount > 5
              ? 'Max 5 ICPs'
              : `Continue with ${keptCount} ICP${keptCount > 1 ? 's' : ''}`}
          <ArrowRight className="h-5 w-5 ml-2" />
        </Button>
      </div>
    </div>
  );
}
