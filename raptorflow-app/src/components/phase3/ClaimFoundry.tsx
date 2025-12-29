'use client';

import React from 'react';
import { Claim } from '@/lib/foundation';
import { Button } from '@/components/ui/button';
import {
  ArrowRight,
  Check,
  X,
  AlertTriangle,
  Shield,
  Star,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ClaimFoundryProps {
  claims: Claim[];
  primaryClaimId: string;
  onChange: (claims: Claim[], primaryId: string) => void;
  onContinue: () => void;
}

function USPGate({ label, passed }: { label: string; passed: boolean }) {
  return (
    <div
      className={cn(
        'flex items-center gap-2 text-xs',
        passed ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'
      )}
    >
      {passed ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
      <span>{label}</span>
    </div>
  );
}

function ClaimCard({
  claim,
  isPrimary,
  onSetPrimary,
  onToggleGate,
  onMarkBlocked,
}: {
  claim: Claim;
  isPrimary: boolean;
  onSetPrimary: () => void;
  onToggleGate: (gate: 'isSpecific' | 'isUnique' | 'movesBuyers') => void;
  onMarkBlocked: () => void;
}) {
  const proofStrengthColors: Record<string, string> = {
    A: 'bg-green-500',
    B: 'bg-blue-500',
    C: 'bg-amber-500',
    D: 'bg-red-500',
  };

  const allGatesPassed =
    claim.isSpecific && claim.isUnique && claim.movesBuyers;
  const isBlocked = claim.riskFlags.includes('blocked');

  return (
    <div
      className={cn(
        'relative p-5 rounded-xl border-2 transition-all',
        isPrimary ? 'border-primary bg-primary/5' : 'border-border bg-card',
        isBlocked && 'opacity-50'
      )}
    >
      {/* Primary Badge */}
      {isPrimary && (
        <div className="absolute -top-2 -right-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full flex items-center gap-1">
          <Star className="h-3 w-3 fill-current" /> Primary
        </div>
      )}

      {/* Claim Structure */}
      <div className="space-y-3">
        <div className="text-sm">
          <span className="text-muted-foreground">For </span>
          <span className="font-medium">{claim.audience}</span>
        </div>
        <div className="text-lg font-semibold text-foreground">
          {claim.promise}
        </div>
        <div className="text-sm text-muted-foreground">
          <span className="text-muted-foreground">By </span>
          {claim.mechanism}
        </div>
        {claim.uniqueness && (
          <div className="text-xs text-muted-foreground italic">
            Unique: {claim.uniqueness}
          </div>
        )}

        {/* Proof Strength Meter */}
        <div className="flex items-center gap-2 mt-4">
          <span className="text-xs text-muted-foreground">Proof:</span>
          <div className="flex gap-1">
            {['A', 'B', 'C', 'D'].map((grade) => (
              <div
                key={grade}
                className={cn(
                  'w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center',
                  claim.proofStrength === grade
                    ? `${proofStrengthColors[grade]} text-white`
                    : 'bg-muted text-muted-foreground'
                )}
              >
                {grade}
              </div>
            ))}
          </div>
          {claim.proof.length === 0 && (
            <span className="text-xs text-amber-600 flex items-center gap-1">
              <AlertTriangle className="h-3 w-3" /> Needs proof
            </span>
          )}
        </div>

        {/* USP Gates (Reeves) */}
        <div className="flex flex-wrap gap-4 pt-3 border-t">
          <button onClick={() => onToggleGate('isSpecific')}>
            <USPGate label="Specific benefit" passed={claim.isSpecific} />
          </button>
          <button onClick={() => onToggleGate('isUnique')}>
            <USPGate label="Uniquely defensible" passed={claim.isUnique} />
          </button>
          <button onClick={() => onToggleGate('movesBuyers')}>
            <USPGate label="Moves buyers" passed={claim.movesBuyers} />
          </button>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 pt-3">
          {!isPrimary && !isBlocked && (
            <Button
              size="sm"
              variant="outline"
              onClick={onSetPrimary}
              disabled={!allGatesPassed}
            >
              <Star className="h-3 w-3 mr-1" /> Set as Primary
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={onMarkBlocked}
            className="text-muted-foreground"
          >
            <Shield className="h-3 w-3 mr-1" /> Can't say legally
          </Button>
        </div>
      </div>
    </div>
  );
}

export function ClaimFoundry({
  claims,
  primaryClaimId,
  onChange,
  onContinue,
}: ClaimFoundryProps) {
  const handleSetPrimary = (claimId: string) => {
    onChange(claims, claimId);
  };

  const handleToggleGate = (
    claimId: string,
    gate: 'isSpecific' | 'isUnique' | 'movesBuyers'
  ) => {
    onChange(
      claims.map((c) => (c.id === claimId ? { ...c, [gate]: !c[gate] } : c)),
      primaryClaimId
    );
  };

  const handleMarkBlocked = (claimId: string) => {
    onChange(
      claims.map((c) =>
        c.id === claimId
          ? {
              ...c,
              riskFlags: c.riskFlags.includes('blocked')
                ? c.riskFlags.filter((f) => f !== 'blocked')
                : [...c.riskFlags, 'blocked'],
            }
          : c
      ),
      primaryClaimId === claimId ? '' : primaryClaimId
    );
  };

  const hasPrimary = claims.some(
    (c) => c.id === primaryClaimId && !c.riskFlags.includes('blocked')
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-serif font-bold text-foreground">
          Claim Foundry
        </h1>
        <p className="text-muted-foreground max-w-lg mx-auto">
          Choose your primary UVP. Every claim must pass the Reeves USP gates:
          specific, unique, moves buyers.
        </p>
      </div>

      {/* Claims Grid */}
      <div className="grid gap-6 max-w-3xl mx-auto">
        {claims.map((claim) => (
          <ClaimCard
            key={claim.id}
            claim={claim}
            isPrimary={claim.id === primaryClaimId}
            onSetPrimary={() => handleSetPrimary(claim.id)}
            onToggleGate={(gate) => handleToggleGate(claim.id, gate)}
            onMarkBlocked={() => handleMarkBlocked(claim.id)}
          />
        ))}
      </div>

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          size="lg"
          onClick={onContinue}
          disabled={!hasPrimary}
          className="px-8 py-6 text-lg rounded-xl"
        >
          {hasPrimary ? 'Continue' : 'Select a Primary Claim'}{' '}
          <ArrowRight className="h-5 w-5 ml-2" />
        </Button>
      </div>
    </div>
  );
}
