'use client';

import React, { useState } from 'react';
import { Alert } from '../types';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, ExternalLink, ArrowRight } from 'lucide-react';

interface AlertCardProps {
  alert: Alert;
  onDismiss?: (id: string) => void;
  onCreateMove?: (alert: Alert) => void;
}

function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return 'Just now';
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function AlertCard({ alert, onDismiss, onCreateMove }: AlertCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <article
      className={cn(
        'bg-white border border-[#E5E6E3] rounded-2xl transition-all duration-300',
        'hover:shadow-[0_8px_24px_rgba(0,0,0,0.04)]',
        isExpanded && 'shadow-[0_12px_32px_rgba(0,0,0,0.06)]'
      )}
    >
      {/* Main Content */}
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-6 mb-4">
          <div className="flex-1 min-w-0">
            <h3 className="font-serif text-xl text-[#2D3538] leading-tight mb-2">
              {alert.title}
            </h3>
            <div className="flex items-center gap-3 text-[12px] text-[#5B5F61]">
              <span className="font-medium text-[#2D3538]">
                {alert.competitorName}
              </span>
              <span className="opacity-40">•</span>
              <span>{alert.watchlistName}</span>
              <span className="opacity-40">•</span>
              <span>{formatTimeAgo(alert.createdAt)}</span>
            </div>
          </div>

          {/* Impact Indicator — Monochrome */}
          <div className="shrink-0 text-right">
            <span className="text-[10px] font-semibold uppercase tracking-[0.1em] text-[#9D9F9F]">
              {alert.impact}
            </span>
          </div>
        </div>

        {/* Summary */}
        <p className="text-[15px] text-[#5B5F61] leading-relaxed">
          {alert.summary}
        </p>

        {/* Expandable Details */}
        {isExpanded && (
          <div className="mt-6 pt-6 border-t border-[#E5E6E3] animate-in slide-in-from-top-2 duration-200">
            {/* Details List */}
            {alert.details && alert.details.length > 0 && (
              <ul className="space-y-3 mb-6">
                {alert.details.map((detail, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-3 text-[14px] text-[#2D3538]"
                  >
                    <span className="text-[#9D9F9F] mt-1">•</span>
                    {detail}
                  </li>
                ))}
              </ul>
            )}

            {/* Evidence */}
            {alert.evidence.length > 0 && (
              <div className="mb-6">
                <span className="text-[10px] font-semibold uppercase tracking-[0.15em] text-[#9D9F9F] block mb-3">
                  Evidence
                </span>
                <div className="flex flex-wrap gap-2">
                  {alert.evidence.map((ev) => (
                    <a
                      key={ev.id}
                      href={ev.value}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-3 py-2 bg-[#F8F9F7] hover:bg-[#E5E6E3] rounded-lg text-[13px] font-medium text-[#2D3538] transition-colors"
                    >
                      {ev.name}
                      <ExternalLink className="w-3 h-3 opacity-40" />
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => onCreateMove?.(alert)}
                className="inline-flex items-center gap-3 h-12 px-6 bg-[#1A1D1E] text-white rounded-xl font-medium text-[14px] transition-all hover:bg-black hover:shadow-[0_8px_20px_rgba(0,0,0,0.2)]"
              >
                Create Move
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => onDismiss?.(alert.id)}
                className="text-[13px] font-medium text-[#9D9F9F] hover:text-[#2D3538] transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {/* Expand/Collapse */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-5 flex items-center gap-2 text-[12px] font-medium text-[#9D9F9F] hover:text-[#2D3538] transition-colors"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="w-4 h-4" />
              Show less
            </>
          ) : (
            <>
              <ChevronDown className="w-4 h-4" />
              View details
            </>
          )}
        </button>
      </div>
    </article>
  );
}
