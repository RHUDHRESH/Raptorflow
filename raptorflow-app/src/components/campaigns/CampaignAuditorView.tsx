'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { ShieldCheck, AlertTriangle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AlignmentResult {
  uvp_title: string;
  is_aligned: boolean;
  score: number;
  feedback: string;
}

interface CampaignAuditorViewProps {
  alignments: AlignmentResult[];
  overallScore?: number;
}

/**
 * SOTA Campaign Auditor Feedback Component
 * Visualizes the agentic critique of the campaign strategy.
 */
export function CampaignAuditorView({
  alignments,
  overallScore,
}: CampaignAuditorViewProps) {
  if (!alignments || alignments.length === 0) {
    return (
      <div className="flex items-center gap-3 p-4 rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800 text-zinc-400 italic text-sm">
        <Info className="w-4 h-4" />
        No audit data available for this campaign yet.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between px-1">
        <h3 className="text-xs font-bold uppercase tracking-widest text-zinc-400">
          Strategic Alignment Audit
        </h3>
        {overallScore !== undefined && (
          <span
            className={cn(
              'text-[10px] font-bold px-2 py-0.5 rounded-full border',
              overallScore > 0.8
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-amber-50 text-amber-700 border-amber-200'
            )}
          >
            {Math.round(overallScore * 100)}% Match
          </span>
        )}
      </div>

      <div className="grid gap-3">
        {alignments.map((item, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl border border-zinc-100 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 flex gap-4"
          >
            <div
              className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center shrink-0',
                item.is_aligned
                  ? 'bg-emerald-50 text-emerald-600'
                  : 'bg-amber-50 text-amber-600'
              )}
            >
              {item.is_aligned ? (
                <ShieldCheck className="w-4 h-4" />
              ) : (
                <AlertTriangle className="w-4 h-4" />
              )}
            </div>
            <div className="space-y-1">
              <div className="text-sm font-semibold flex items-center gap-2">
                {item.uvp_title}
                <span className="text-[10px] text-zinc-400 font-normal tabular-nums">
                  Score: {item.score}
                </span>
              </div>
              <p className="text-xs text-zinc-500 leading-relaxed">
                {item.feedback}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
