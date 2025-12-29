'use client';

import React from 'react';
import { Phase3Data } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import {
  Lock,
  Download,
  Check,
  ArrowRight,
  Star,
  Layers,
  Target,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Phase3SummaryProps {
  data: Phase3Data;
  onLock: () => void;
  onDownload?: () => void;
}

function SummaryCard({
  icon: Icon,
  title,
  children,
  color,
}: {
  icon: React.ElementType;
  title: string;
  children: React.ReactNode;
  color: string;
}) {
  return (
    <div className="bg-card border rounded-xl p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className={cn('p-2 rounded-lg', color)}>
          <Icon className="h-4 w-4" />
        </div>
        <h3 className="font-semibold">{title}</h3>
      </div>
      {children}
    </div>
  );
}

export function Phase3Summary({
  data,
  onLock,
  onDownload,
}: Phase3SummaryProps) {
  const primaryClaim = data.claims.find((c) => c.id === data.primaryClaimId);
  const provenDiffs = data.differentiators.filter(
    (d) => d.status === 'proven'
  ).length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-serif font-bold text-foreground">
          Differentiation Blueprint
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Your value thesis is complete. Lock it to proceed to positioning.
        </p>
      </div>

      {/* Value Thesis */}
      <div className="max-w-2xl mx-auto bg-gradient-to-br from-primary/5 to-primary/10 border-2 border-primary/20 rounded-2xl p-6">
        <div className="text-center space-y-4">
          <div className="text-sm text-muted-foreground uppercase tracking-wider">
            Your Value Thesis
          </div>
          <p className="text-xl font-serif font-semibold text-foreground">
            We help{' '}
            <span className="text-primary">{data.primaryContext.to}</span> to{' '}
            <span className="text-primary">
              {data.primaryContext.soTheyCan}
            </span>{' '}
            by delivering{' '}
            <span className="text-primary">{data.primaryContext.youSell}</span>.
          </p>
        </div>
      </div>

      {/* Summary Grid */}
      <div className="grid md:grid-cols-2 gap-4 max-w-3xl mx-auto">
        {/* Primary UVP */}
        <SummaryCard
          icon={Star}
          title="Primary UVP"
          color="bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
        >
          {primaryClaim ? (
            <div className="space-y-2">
              <p className="text-sm font-medium">{primaryClaim.promise}</p>
              <p className="text-xs text-muted-foreground">
                For: {primaryClaim.audience}
              </p>
              <div className="flex gap-2 mt-2">
                {primaryClaim.isSpecific && (
                  <Check className="h-3 w-3 text-green-500" />
                )}
                {primaryClaim.isUnique && (
                  <Check className="h-3 w-3 text-green-500" />
                )}
                {primaryClaim.movesBuyers && (
                  <Check className="h-3 w-3 text-green-500" />
                )}
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No primary claim selected
            </p>
          )}
        </SummaryCard>

        {/* JTBD Core */}
        <SummaryCard
          icon={Target}
          title="Core Job"
          color="bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
        >
          <div className="space-y-2">
            {data.jtbd.jobs
              .filter((j) => j.isPrimary)
              .map((job) => (
                <p key={job.id} className="text-sm">
                  {job.statement}
                </p>
              ))}
            <div className="flex flex-wrap gap-2 mt-2">
              <span className="text-xs bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 px-2 py-0.5 rounded">
                Push: {data.jtbd.forces.push.length}
              </span>
              <span className="text-xs bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 px-2 py-0.5 rounded">
                Pull: {data.jtbd.forces.pull.length}
              </span>
            </div>
          </div>
        </SummaryCard>

        {/* VPC Fit */}
        <SummaryCard
          icon={Layers}
          title="Value Fit"
          color="bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400"
        >
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm">Coverage</span>
              <span
                className={cn(
                  'text-sm font-bold',
                  data.vpc.fitCoverage.score >= 70
                    ? 'text-green-600'
                    : 'text-amber-600'
                )}
              >
                {data.vpc.fitCoverage.score}%
              </span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-500 rounded-full"
                style={{ width: `${data.vpc.fitCoverage.score}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              {data.vpc.customerProfile.pains.length} pains,{' '}
              {data.vpc.valueMap.painRelievers.length} relievers
            </p>
          </div>
        </SummaryCard>

        {/* ERRC Summary */}
        <SummaryCard
          icon={Zap}
          title="ERRC Trade-offs"
          color="bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400"
        >
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-red-50 dark:bg-red-950/30 p-2 rounded">
              <span className="font-medium text-red-700 dark:text-red-400">
                Eliminate:
              </span>{' '}
              {data.errc.eliminate.length}
            </div>
            <div className="bg-amber-50 dark:bg-amber-950/30 p-2 rounded">
              <span className="font-medium text-amber-700 dark:text-amber-400">
                Reduce:
              </span>{' '}
              {data.errc.reduce.length}
            </div>
            <div className="bg-blue-50 dark:bg-blue-950/30 p-2 rounded">
              <span className="font-medium text-blue-700 dark:text-blue-400">
                Raise:
              </span>{' '}
              {data.errc.raise.length}
            </div>
            <div className="bg-green-50 dark:bg-green-950/30 p-2 rounded">
              <span className="font-medium text-green-700 dark:text-green-400">
                Create:
              </span>{' '}
              {data.errc.create.length}
            </div>
          </div>
        </SummaryCard>
      </div>

      {/* Proof Status */}
      <div className="max-w-md mx-auto text-center">
        <p className="text-sm text-muted-foreground">
          {provenDiffs} of {data.differentiators.length} differentiators have
          proof attached
        </p>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
        {onDownload && (
          <Button
            variant="outline"
            size="lg"
            onClick={onDownload}
            className="px-6"
          >
            <Download className="h-4 w-4 mr-2" /> Download PDF
          </Button>
        )}
        <Button
          size="lg"
          onClick={onLock}
          className="px-8 py-6 text-lg rounded-xl"
        >
          <Lock className="h-5 w-5 mr-2" /> Lock Phase 3 & Continue
        </Button>
      </div>
    </div>
  );
}
