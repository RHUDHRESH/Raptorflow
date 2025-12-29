'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import {
  TrendingUp,
  Eye,
  MousePointer,
  AlertTriangle,
  CheckCircle,
  Sparkles,
} from 'lucide-react';

interface PredictionData {
  openRate: number;
  clickRate: number;
  engagementScore: number;
  confidence: number;
  suggestions: string[];
}

interface PredictionPanelProps {
  content: string;
  assetType?: string;
  className?: string;
}

// Mock prediction - would call AI in production
function generatePredictions(content: string): PredictionData {
  if (!content || content.length < 20) {
    return {
      openRate: 0,
      clickRate: 0,
      engagementScore: 0,
      confidence: 0,
      suggestions: ['Add more content to get predictions'],
    };
  }

  const hasQuestion = content.includes('?');
  const hasNumber = /\d/.test(content);
  const wordCount = content.split(/\s+/).length;
  const hasCTA =
    /\b(click|sign up|learn more|get started|try|discover|join)\b/i.test(
      content
    );

  let openRate = 20 + Math.random() * 30;
  let clickRate = 2 + Math.random() * 5;
  let engagementScore = 50 + Math.random() * 30;

  if (hasQuestion) {
    openRate += 8;
    engagementScore += 5;
  }
  if (hasNumber) {
    openRate += 5;
    clickRate += 1;
  }
  if (hasCTA) {
    clickRate += 3;
    engagementScore += 10;
  }
  if (wordCount > 100 && wordCount < 300) {
    engagementScore += 5;
  }

  const suggestions: string[] = [];
  if (!hasQuestion)
    suggestions.push('Try adding a question to increase open rates');
  if (!hasCTA) suggestions.push('Add a clear call-to-action');
  if (wordCount < 50) suggestions.push('Consider adding more detail');
  if (wordCount > 500)
    suggestions.push('Content may be too long - consider shortening');

  return {
    openRate: Math.min(Math.round(openRate), 65),
    clickRate: Math.min(Math.round(clickRate * 10) / 10, 12),
    engagementScore: Math.min(Math.round(engagementScore), 95),
    confidence: 65 + Math.random() * 25,
    suggestions: suggestions.slice(0, 3),
  };
}

function getScoreColor(score: number, max: number) {
  const ratio = score / max;
  if (ratio >= 0.7) return 'text-green-500';
  if (ratio >= 0.4) return 'text-amber-500';
  return 'text-red-500';
}

export function PredictionPanel({
  content,
  assetType = 'email',
  className,
}: PredictionPanelProps) {
  const predictions = generatePredictions(content);

  if (predictions.confidence === 0) {
    return (
      <div
        className={cn(
          'p-4 rounded-xl border border-border/60 bg-card',
          className
        )}
      >
        <div className="flex items-center gap-3 text-muted-foreground">
          <Sparkles className="h-5 w-5" />
          <p className="text-sm">
            Add more content to see performance predictions
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium">Performance Predictions</span>
        </div>
        <span className="text-xs text-muted-foreground">
          {Math.round(predictions.confidence)}% confidence
        </span>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-3 gap-3">
        {/* Open Rate */}
        <div className="p-3 rounded-lg bg-muted/30 text-center">
          <Eye className="h-4 w-4 mx-auto text-muted-foreground mb-1" />
          <p
            className={cn(
              'text-xl font-bold',
              getScoreColor(predictions.openRate, 50)
            )}
          >
            {predictions.openRate}%
          </p>
          <p className="text-xs text-muted-foreground">Open Rate</p>
        </div>

        {/* Click Rate */}
        <div className="p-3 rounded-lg bg-muted/30 text-center">
          <MousePointer className="h-4 w-4 mx-auto text-muted-foreground mb-1" />
          <p
            className={cn(
              'text-xl font-bold',
              getScoreColor(predictions.clickRate, 8)
            )}
          >
            {predictions.clickRate}%
          </p>
          <p className="text-xs text-muted-foreground">Click Rate</p>
        </div>

        {/* Engagement */}
        <div className="p-3 rounded-lg bg-muted/30 text-center">
          <TrendingUp className="h-4 w-4 mx-auto text-muted-foreground mb-1" />
          <p
            className={cn(
              'text-xl font-bold',
              getScoreColor(predictions.engagementScore, 80)
            )}
          >
            {predictions.engagementScore}
          </p>
          <p className="text-xs text-muted-foreground">Engagement</p>
        </div>
      </div>

      {/* Overall assessment */}
      <div
        className={cn(
          'flex items-center gap-3 p-3 rounded-lg',
          predictions.engagementScore >= 70
            ? 'bg-green-500/10 text-green-600'
            : predictions.engagementScore >= 50
              ? 'bg-amber-500/10 text-amber-600'
              : 'bg-red-500/10 text-red-600'
        )}
      >
        {predictions.engagementScore >= 70 ? (
          <CheckCircle className="h-5 w-5 shrink-0" />
        ) : (
          <AlertTriangle className="h-5 w-5 shrink-0" />
        )}
        <p className="text-sm">
          {predictions.engagementScore >= 70
            ? 'This content should perform well'
            : predictions.engagementScore >= 50
              ? 'Decent performance expected, room for improvement'
              : 'Consider revising to improve performance'}
        </p>
      </div>

      {/* Suggestions */}
      {predictions.suggestions.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Suggestions
          </p>
          <ul className="space-y-1.5">
            {predictions.suggestions.map((suggestion, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <Sparkles className="h-3.5 w-3.5 text-muted-foreground shrink-0 mt-0.5" />
                <span className="text-muted-foreground">{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-[10px] text-muted-foreground/60 text-center">
        Predictions are estimates based on content analysis. Actual results may
        vary.
      </p>
    </div>
  );
}

// Compact inline version
export function PredictionBadge({
  content,
  className,
}: {
  content: string;
  className?: string;
}) {
  const predictions = generatePredictions(content);

  if (predictions.confidence === 0) return null;

  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 px-2.5 py-1.5 rounded-lg',
        'border border-border/60 bg-card text-xs',
        className
      )}
    >
      <TrendingUp className="h-3 w-3 text-muted-foreground" />
      <span>{predictions.engagementScore}</span>
      <span className="text-muted-foreground">/100</span>
    </div>
  );
}
