'use client';

import React, { useMemo } from 'react';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus, Lightbulb } from 'lucide-react';

interface HookScoreProps {
  text: string;
  className?: string;
}

// Mock scoring algorithm - in production this would call AI
function calculateHookScore(text: string): {
  score: number;
  tips: string[];
  strengths: string[];
} {
  if (!text || text.trim().length === 0) {
    return { score: 0, tips: ['Start typing to get a score'], strengths: [] };
  }

  let score = 50; // Base score
  const tips: string[] = [];
  const strengths: string[] = [];

  const words = text.split(/\s+/).filter((w) => w.length > 0);
  const hasQuestion = text.includes('?');
  const hasNumber = /\d/.test(text);
  const hasPowerWord =
    /\b(free|new|proven|secret|instant|exclusive|limited|guaranteed|discover|unlock|transform|master)\b/i.test(
      text
    );
  const startsWithYou = /^you\b/i.test(text.trim());
  const isShort = words.length <= 10;
  const isVeryLong = words.length > 20;

  // Positive signals
  if (hasQuestion) {
    score += 12;
    strengths.push('Questions drive curiosity');
  }
  if (hasNumber) {
    score += 10;
    strengths.push('Numbers add specificity');
  }
  if (hasPowerWord) {
    score += 15;
    strengths.push('Power words increase urgency');
  }
  if (startsWithYou) {
    score += 8;
    strengths.push('Reader-focused opening');
  }
  if (isShort) {
    score += 5;
    strengths.push('Concise and scannable');
  }

  // Negative signals
  if (isVeryLong) {
    score -= 15;
    tips.push('Too long — try to cut words');
  }
  if (!hasQuestion && !hasPowerWord) {
    tips.push('Try adding a question or power word');
  }
  if (!startsWithYou && words.length > 3) {
    tips.push('Try starting with "You" to be reader-focused');
  }

  // Clamp score
  score = Math.max(0, Math.min(100, score));

  return { score, tips, strengths };
}

function getScoreColor(score: number) {
  if (score >= 70) return 'text-green-500';
  if (score >= 40) return 'text-amber-500';
  return 'text-red-500';
}

function getScoreRing(score: number) {
  if (score >= 70) return 'stroke-green-500';
  if (score >= 40) return 'stroke-amber-500';
  return 'stroke-red-500';
}

function getScoreLabel(score: number) {
  if (score >= 80) return 'Excellent';
  if (score >= 70) return 'Strong';
  if (score >= 50) return 'Good';
  if (score >= 40) return 'Fair';
  if (score >= 20) return 'Weak';
  return 'Needs work';
}

export function HookScore({ text, className }: HookScoreProps) {
  const { score, tips, strengths } = useMemo(
    () => calculateHookScore(text),
    [text]
  );

  const circumference = 2 * Math.PI * 40; // radius = 40
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={cn('space-y-4', className)}>
      {/* Score circle */}
      <div className="flex items-center gap-4">
        <div className="relative w-24 h-24">
          <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              className="text-muted/30"
            />
            {/* Score arc */}
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              strokeWidth="8"
              strokeLinecap="round"
              className={cn('transition-all duration-500', getScoreRing(score))}
              style={{
                strokeDasharray: circumference,
                strokeDashoffset: strokeDashoffset,
              }}
            />
          </svg>
          {/* Score number */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={cn('text-2xl font-bold', getScoreColor(score))}>
              {score}
            </span>
            <span className="text-[10px] text-muted-foreground uppercase tracking-wide">
              /100
            </span>
          </div>
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            {score >= 50 ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : score >= 30 ? (
              <Minus className="h-4 w-4 text-amber-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
            <span className="font-medium">{getScoreLabel(score)}</span>
          </div>
          <p className="text-xs text-muted-foreground">
            {score >= 70
              ? 'This hook should grab attention'
              : score >= 40
                ? 'Some room for improvement'
                : 'Consider strengthening this hook'}
          </p>
        </div>
      </div>

      {/* Strengths */}
      {strengths.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Strengths
          </p>
          <ul className="space-y-1">
            {strengths.map((strength, i) => (
              <li
                key={i}
                className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400"
              >
                <span className="w-1 h-1 rounded-full bg-green-500" />
                {strength}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tips */}
      {tips.length > 0 && (
        <div className="space-y-1">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Tips to improve
          </p>
          <ul className="space-y-1">
            {tips.map((tip, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <Lightbulb className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// Compact inline badge version
export function HookScoreBadge({ text, className }: HookScoreProps) {
  const { score } = useMemo(() => calculateHookScore(text), [text]);

  if (score === 0) return null;

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-1 rounded-full',
        'border text-xs font-medium',
        score >= 70 &&
          'border-green-500/30 bg-green-500/10 text-green-600 dark:text-green-400',
        score >= 40 &&
          score < 70 &&
          'border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400',
        score < 40 &&
          'border-red-500/30 bg-red-500/10 text-red-600 dark:text-red-400',
        className
      )}
    >
      <span className="font-bold">{score}</span>
      <span className="opacity-60">/100</span>
    </div>
  );
}
