'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import {
  Move,
  GOAL_LABELS,
  CHANNEL_LABELS,
  RAGStatus,
} from '@/lib/campaigns-types';
import { MoreHorizontal, Clock, BrainCircuit } from 'lucide-react';

interface MoveCardProps {
  move: Move;
  onClick: () => void;
  onLogProgress?: () => void;
  onViewRationale?: () => void;
  className?: string; // Allow optional className
}

// Calculate RAG status deterministically
function calculateRAG(move: Move): { status: RAGStatus; reason: string } {
  // If already set, use it
  if (move.rag && move.ragReason) {
    return { status: move.rag, reason: move.ragReason };
  }

  const now = new Date();
  const startedAt = move.startedAt ? new Date(move.startedAt) : null;

  if (!startedAt || move.status !== 'active') {
    return { status: 'green', reason: 'Ready to start' };
  }

  // Calculate days elapsed
  const daysElapsed =
    Math.floor((now.getTime() - startedAt.getTime()) / (1000 * 60 * 60 * 24)) +
    1;
  const dayNumber = Math.min(daysElapsed, move.duration);

  // Calculate completion rate
  const totalTasks = move.checklist?.length || 0;
  const completedTasks = move.checklist?.filter((t) => t.completed).length || 0;
  const expectedProgress = (dayNumber / move.duration) * totalTasks;
  const actualProgress = completedTasks;

  // Check confidence trend (if available)
  const confidence = move.confidence || 7;

  // RAG logic
  if (confidence <= 4) {
    return { status: 'red', reason: `Low confidence (${confidence}/10)` };
  }

  if (actualProgress < expectedProgress * 0.5) {
    return { status: 'red', reason: 'Behind pace by 50%+' };
  }

  if (actualProgress < expectedProgress * 0.7) {
    return { status: 'amber', reason: 'Behind expected pace' };
  }

  if (confidence <= 6) {
    return {
      status: 'amber',
      reason: `Confidence dropping (${confidence}/10)`,
    };
  }

  return { status: 'green', reason: 'On pace' };
}

// Calculate day number
function getDayNumber(move: Move): number {
  if (!move.startedAt) return 0;
  const now = new Date();
  const startedAt = new Date(move.startedAt);
  const daysElapsed =
    Math.floor((now.getTime() - startedAt.getTime()) / (1000 * 60 * 60 * 24)) +
    1;
  return Math.min(daysElapsed, move.duration);
}

// Get progress percentage
function getProgress(move: Move): number {
  const total = move.checklist?.length || 0;
  const completed = move.checklist?.filter((t) => t.completed).length || 0;
  return total > 0 ? Math.round((completed / total) * 100) : 0;
}

// Get last activity
function getLastActivity(move: Move): string {
  // Check daily metrics for most recent
  if (move.dailyMetrics && move.dailyMetrics.length > 0) {
    const last = move.dailyMetrics[move.dailyMetrics.length - 1];
    if (last.submittedAt) {
      const date = new Date(last.submittedAt);
      const now = new Date();
      const diffDays = Math.floor(
        (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)
      );
      if (diffDays === 0) return 'today';
      if (diffDays === 1) return 'yesterday';
      return `${diffDays}d ago`;
    }
  }
  return 'never';
}

export function MoveCard({ move, onClick, onLogProgress, onViewRationale, className }: MoveCardProps) {
  const rag = calculateRAG(move);
  const dayNumber = getDayNumber(move);
  const progress = getProgress(move);
  const lastActivity = getLastActivity(move);
  const totalTasks = move.checklist?.length || 0;
  const completedTasks = move.checklist?.filter((t) => t.completed).length || 0;

  // Get next action
  const nextAction =
    move.nextAction ||
    (() => {
      const nextTask = move.checklist?.find((t) => !t.completed);
      if (nextTask) {
        return {
          label: nextTask.label,
          dueDate: 'today',
          estimatedMinutes: 20,
        };
      }
      return null;
    })();

  // Micro metrics (default or from dailyMetrics)
  const latestMetrics = move.dailyMetrics?.[move.dailyMetrics.length - 1];
  const leads = latestMetrics?.leads || 0;
  const replies = latestMetrics?.replies || 0;
  const calls = latestMetrics?.calls || 0;
  const confidence = move.confidence || 7;

  // RAG colors
  const ragColors = {
    green: { bg: 'bg-[#F0FDF4]', dot: 'bg-[#22C55E]', text: 'text-[#16A34A]' },
    amber: { bg: 'bg-[#FFFBEB]', dot: 'bg-[#F59E0B]', text: 'text-[#D97706]' },
    red: { bg: 'bg-[#FEF2F2]', dot: 'bg-[#EF4444]', text: 'text-[#DC2626]' },
  };

  return (
    <motion.div
      layoutId={`move-${move.id}`}
      className={cn(
        "group relative bg-canvas-card border rounded-xl overflow-hidden transition-all duration-200 hover:shadow-md cursor-pointer",
        // Status styling
        move.status === 'completed' && "opacity-75 bg-canvas-muted/50",
        className // Merge passed className
      )}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-[16px] font-semibold text-[#2D3538] mb-1.5">
            {move.name}
          </h3>
          <div className="flex items-center gap-1.5">
            <span className="h-[22px] px-2 bg-[#F8F9F7] rounded-md text-[10px] font-semibold uppercase tracking-[0.05em] text-[#5B5F61] flex items-center">
              {GOAL_LABELS[move.goal]?.label || move.goal}
            </span>
            <span className="h-[22px] px-2 bg-[#F8F9F7] rounded-md text-[10px] font-semibold uppercase tracking-[0.05em] text-[#5B5F61] flex items-center">
              {CHANNEL_LABELS[move.channel]}
            </span>
            <span className="h-[22px] px-2 bg-[#F8F9F7] rounded-md text-[10px] font-semibold uppercase tracking-[0.05em] text-[#5B5F61] flex items-center">
              {move.duration}D
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onViewRationale?.();
            }}
            title="View Council Rationale"
            className="h-8 w-8 bg-[#F8F9F7] border border-[#E5E6E3] rounded-lg flex items-center justify-center text-[#5B5F61] hover:bg-accent/10 hover:border-accent/30 hover:text-accent transition-colors"
          >
            <BrainCircuit className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onLogProgress?.();
            }}
            className="h-8 px-3.5 bg-[#F8F9F7] border border-[#E5E6E3] rounded-lg text-[12px] font-medium text-[#2D3538] hover:bg-[#1A1D1E] hover:border-[#1A1D1E] hover:text-white transition-colors"
          >
            Log progress
          </button>
        </div>
      </div>

      {/* Outcome */}
      {move.outcomeTarget && (
        <p className="text-[14px] text-[#5B5F61] mb-4 leading-relaxed">
          <strong className="text-[#2D3538]">Outcome:</strong>{' '}
          {move.outcomeTarget}
        </p>
      )}

      {/* Progress Row */}
      <div className="flex items-center gap-4 mb-3">
        <span className="text-[12px] font-mono font-medium text-[#2D3538]">
          Day {dayNumber}/{move.duration}
        </span>
        <div className="flex-1 h-1 bg-[#E5E6E3] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#2D3538] rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="text-[11px] font-mono text-[#9D9F9F]">
          Tasks {completedTasks}/{totalTasks}
        </span>
        <span className="text-[11px] text-[#C0C1BE]">Last: {lastActivity}</span>
      </div>

      {/* RAG Status */}
      <div
        className={`flex items-center gap-2 mb-3 px-3 py-2 rounded-lg ${ragColors[rag.status].bg}`}
      >
        <div className={`w-2 h-2 rounded-full ${ragColors[rag.status].dot}`} />
        <span
          className={`text-[11px] font-semibold uppercase tracking-[0.05em] ${ragColors[rag.status].text}`}
        >
          {rag.status.toUpperCase()}
        </span>
        <span className="text-[12px] text-[#5B5F61]">— {rag.reason}</span>
      </div>

      {/* Next Action */}
      {nextAction && (
        <div className="flex items-center gap-2 px-4 py-3 bg-[#1A1D1E] rounded-xl mb-4">
          <span className="text-[11px] font-semibold uppercase tracking-[0.1em] text-white/50">
            Next:
          </span>
          <span className="flex-1 text-[14px] font-medium text-white">
            {nextAction.label}
          </span>
          <span className="text-[11px] font-mono text-white/50">
            Due {nextAction.dueDate}
          </span>
        </div>
      )}

      {/* Micro Metrics */}
      <div className="flex items-center gap-4 pt-3 border-t border-[#E5E6E3]">
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] text-[#9D9F9F]">Leads</span>
          <span className="text-[13px] font-mono font-medium text-[#2D3538]">
            {leads}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] text-[#9D9F9F]">Replies</span>
          <span className="text-[13px] font-mono font-medium text-[#2D3538]">
            {replies}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] text-[#9D9F9F]">Calls</span>
          <span className="text-[13px] font-mono font-medium text-[#2D3538]">
            {calls}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] text-[#9D9F9F]">Conf</span>
          <span className="text-[13px] font-mono font-medium text-[#2D3538]">
            {confidence}/10
          </span>
        </div>
      </div>
    </motion.div>
  );
}
