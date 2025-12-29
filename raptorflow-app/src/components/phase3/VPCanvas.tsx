'use client';

import React from 'react';
import {
  VPCData,
  VPCPain,
  VPCGain,
  VPCReliever,
  VPCCreator,
} from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import { ArrowRight, GripVertical, Link2, X, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VPCanvasProps {
  vpc: VPCData;
  onChange: (vpc: VPCData) => void;
  onContinue: () => void;
}

function PainGainCard({
  item,
  type,
  onRemove,
}: {
  item: VPCPain | VPCGain;
  type: 'pain' | 'gain';
  onRemove: () => void;
}) {
  const severity =
    'severity' in item ? item.severity : (item as VPCGain).importance;

  return (
    <div
      className={cn(
        'p-3 rounded-lg border-2 transition-all group',
        type === 'pain'
          ? 'border-red-200 bg-red-50/50 dark:border-red-900 dark:bg-red-950/20'
          : 'border-green-200 bg-green-50/50 dark:border-green-900 dark:bg-green-950/20'
      )}
    >
      <div className="flex items-start gap-2">
        <GripVertical className="h-4 w-4 text-muted-foreground/50 mt-0.5 cursor-grab" />
        <div className="flex-1 min-w-0">
          <p className="text-sm text-foreground leading-tight">{item.text}</p>
          <div className="flex gap-1 mt-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className={cn(
                  'w-2 h-2 rounded-full',
                  i < severity
                    ? type === 'pain'
                      ? 'bg-red-500'
                      : 'bg-green-500'
                    : 'bg-muted'
                )}
              />
            ))}
          </div>
        </div>
        <button
          onClick={onRemove}
          className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-all"
        >
          <X className="h-3 w-3 text-muted-foreground" />
        </button>
      </div>
    </div>
  );
}

function RelieverCreatorCard({
  item,
  type,
  linkedText,
  onRemove,
}: {
  item: VPCReliever | VPCCreator;
  type: 'reliever' | 'creator';
  linkedText?: string;
  onRemove: () => void;
}) {
  return (
    <div
      className={cn(
        'p-3 rounded-lg border-2 transition-all group',
        type === 'reliever'
          ? 'border-orange-200 bg-orange-50/50 dark:border-orange-900 dark:bg-orange-950/20'
          : 'border-teal-200 bg-teal-50/50 dark:border-teal-900 dark:bg-teal-950/20'
      )}
    >
      <div className="flex items-start gap-2">
        <div className="flex-1 min-w-0">
          <p className="text-sm text-foreground leading-tight">{item.text}</p>
          {linkedText && (
            <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
              <Link2 className="h-3 w-3" />
              <span className="truncate">{linkedText}</span>
            </div>
          )}
        </div>
        <button
          onClick={onRemove}
          className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-all"
        >
          <X className="h-3 w-3 text-muted-foreground" />
        </button>
      </div>
    </div>
  );
}

export function VPCanvas({ vpc, onChange, onContinue }: VPCanvasProps) {
  const removePain = (id: string) => {
    onChange({
      ...vpc,
      customerProfile: {
        ...vpc.customerProfile,
        pains: vpc.customerProfile.pains.filter((p) => p.id !== id),
      },
      valueMap: {
        ...vpc.valueMap,
        painRelievers: vpc.valueMap.painRelievers.filter(
          (r) => r.painId !== id
        ),
      },
    });
  };

  const removeGain = (id: string) => {
    onChange({
      ...vpc,
      customerProfile: {
        ...vpc.customerProfile,
        gains: vpc.customerProfile.gains.filter((g) => g.id !== id),
      },
      valueMap: {
        ...vpc.valueMap,
        gainCreators: vpc.valueMap.gainCreators.filter((c) => c.gainId !== id),
      },
    });
  };

  const removeReliever = (id: string) => {
    onChange({
      ...vpc,
      valueMap: {
        ...vpc.valueMap,
        painRelievers: vpc.valueMap.painRelievers.filter((r) => r.id !== id),
      },
    });
  };

  const removeCreator = (id: string) => {
    onChange({
      ...vpc,
      valueMap: {
        ...vpc.valueMap,
        gainCreators: vpc.valueMap.gainCreators.filter((c) => c.id !== id),
      },
    });
  };

  const getPainText = (painId: string) => {
    return vpc.customerProfile.pains.find((p) => p.id === painId)?.text;
  };

  const getGainText = (gainId: string) => {
    return vpc.customerProfile.gains.find((g) => g.id === gainId)?.text;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-serif font-bold text-foreground">
          Value Proposition Canvas
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          The left side is your customer. The right side is your solution. Lines
          show the fit.
        </p>
      </div>

      {/* Fit Coverage Bar */}
      <div className="max-w-2xl mx-auto bg-card border rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Fit Coverage</span>
          <span
            className={cn(
              'text-sm font-bold',
              vpc.fitCoverage.score >= 70
                ? 'text-green-600'
                : vpc.fitCoverage.score >= 40
                  ? 'text-amber-600'
                  : 'text-red-600'
            )}
          >
            {vpc.fitCoverage.score}%
          </span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full rounded-full transition-all',
              vpc.fitCoverage.score >= 70
                ? 'bg-green-500'
                : vpc.fitCoverage.score >= 40
                  ? 'bg-amber-500'
                  : 'bg-red-500'
            )}
            style={{ width: `${vpc.fitCoverage.score}%` }}
          />
        </div>
        {vpc.fitCoverage.gaps.length > 0 && (
          <p className="text-xs text-muted-foreground mt-2">
            Gaps: {vpc.fitCoverage.gaps.slice(0, 2).join(', ')}
          </p>
        )}
      </div>

      {/* Canvas Grid */}
      <div className="grid grid-cols-2 gap-6 max-w-4xl mx-auto">
        {/* Customer Profile */}
        <div className="space-y-6">
          <h2 className="text-center font-semibold text-muted-foreground uppercase tracking-wider text-xs">
            Customer Profile
          </h2>

          {/* Pains */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-red-600 dark:text-red-400">
              Pains
            </h3>
            {vpc.customerProfile.pains.map((pain) => (
              <PainGainCard
                key={pain.id}
                item={pain}
                type="pain"
                onRemove={() => removePain(pain.id)}
              />
            ))}
          </div>

          {/* Gains */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-green-600 dark:text-green-400">
              Gains
            </h3>
            {vpc.customerProfile.gains.map((gain) => (
              <PainGainCard
                key={gain.id}
                item={gain}
                type="gain"
                onRemove={() => removeGain(gain.id)}
              />
            ))}
          </div>
        </div>

        {/* Value Map */}
        <div className="space-y-6">
          <h2 className="text-center font-semibold text-muted-foreground uppercase tracking-wider text-xs">
            Value Map
          </h2>

          {/* Pain Relievers */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-orange-600 dark:text-orange-400">
              Pain Relievers
            </h3>
            {vpc.valueMap.painRelievers.map((reliever) => (
              <RelieverCreatorCard
                key={reliever.id}
                item={reliever}
                type="reliever"
                linkedText={getPainText(reliever.painId)}
                onRemove={() => removeReliever(reliever.id)}
              />
            ))}
          </div>

          {/* Gain Creators */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-teal-600 dark:text-teal-400">
              Gain Creators
            </h3>
            {vpc.valueMap.gainCreators.map((creator) => (
              <RelieverCreatorCard
                key={creator.id}
                item={creator}
                type="creator"
                linkedText={getGainText(creator.gainId)}
                onRemove={() => removeCreator(creator.id)}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          size="lg"
          onClick={onContinue}
          className="px-8 py-6 text-lg rounded-xl"
        >
          Continue <ArrowRight className="h-5 w-5 ml-2" />
        </Button>
      </div>
    </div>
  );
}
