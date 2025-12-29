'use client';

import React from 'react';
import {
  Move,
  GOAL_LABELS,
  CHANNEL_LABELS,
  RAGStatus,
} from '@/lib/campaigns-types';
import {
  Clock,
  ChevronRight,
  MoreHorizontal,
  AlertCircle,
  CheckCircle2,
  Circle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import styles from './Moves.module.css';

interface MoveCardEnhancedProps {
  move: Move;
  onClick: () => void;
  onLogProgress?: () => void;
  compact?: boolean;
}

/**
 * Calculate day number from startedAt
 */
function getDayNumber(move: Move): number {
  if (!move.startedAt) return 1;
  const start = new Date(move.startedAt);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - start.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return Math.min(diffDays, move.duration);
}

/**
 * Calculate progress percentage from checklist
 */
function getProgress(move: Move): {
  completed: number;
  total: number;
  percent: number;
} {
  const total = move.checklist.length;
  const completed = move.checklist.filter((i) => i.completed).length;
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
  return { completed, total, percent };
}

/**
 * Determine RAG status based on move data
 */
function calculateRAG(move: Move): { status: RAGStatus; reason: string } {
  // If RAG is explicitly set, use it
  if (move.rag && move.ragReason) {
    return { status: move.rag, reason: move.ragReason };
  }

  const dayNumber = getDayNumber(move);
  const progress = getProgress(move);
  const expectedProgress = (dayNumber / move.duration) * 100;
  const confidence = move.confidence || 5;

  // RED conditions
  if (confidence <= 3) {
    return { status: 'red', reason: `Low confidence (${confidence}/10)` };
  }
  if (progress.percent < expectedProgress - 30) {
    return {
      status: 'red',
      reason: `Behind pace — ${progress.percent}% done by day ${dayNumber}`,
    };
  }
  if (move.blockers && move.blockers.length >= 2) {
    return { status: 'red', reason: `${move.blockers.length} blockers active` };
  }

  // AMBER conditions
  if (progress.percent < expectedProgress - 15) {
    return { status: 'amber', reason: `Slightly behind pace` };
  }
  if (confidence <= 5) {
    return {
      status: 'amber',
      reason: `Moderate confidence (${confidence}/10)`,
    };
  }
  if (move.blockers && move.blockers.length === 1) {
    return { status: 'amber', reason: `1 blocker: ${move.blockers[0]}` };
  }

  // GREEN
  return { status: 'green', reason: 'On pace' };
}

/**
 * Get next uncompleted task from checklist
 */
function getNextTask(
  move: Move
): { label: string; estimatedMinutes: number } | null {
  // If nextAction is set, use it
  if (move.nextAction) {
    return {
      label: move.nextAction.label,
      estimatedMinutes: move.nextAction.estimatedMinutes,
    };
  }

  // Otherwise find first uncompleted task
  const nextTask = move.checklist.find((item) => !item.completed);
  if (nextTask) {
    return { label: nextTask.label, estimatedMinutes: move.dailyEffort };
  }
  return null;
}

/**
 * Format relative time
 */
function formatLastActivity(date?: string): string {
  if (!date) return 'No activity';
  const now = new Date();
  const then = new Date(date);
  const diffHours = Math.floor(
    (now.getTime() - then.getTime()) / (1000 * 60 * 60)
  );

  if (diffHours < 1) return 'Just now';
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays === 1) return 'Yesterday';
  return `${diffDays}d ago`;
}

export function MoveCardEnhanced({
  move,
  onClick,
  onLogProgress,
  compact = false,
}: MoveCardEnhancedProps) {
  const dayNumber = getDayNumber(move);
  const progress = getProgress(move);
  const rag = calculateRAG(move);
  const nextTask = getNextTask(move);
  const isActive = move.status === 'active';
  const isDone = move.status === 'completed' || move.status === 'abandoned';

  // Get metrics
  const latestMetrics = move.dailyMetrics?.[move.dailyMetrics.length - 1];
  const leads = latestMetrics?.leads ?? 0;
  const replies = latestMetrics?.replies ?? 0;
  const calls = latestMetrics?.calls ?? 0;
  const confidence = move.confidence ?? 5;

  return (
    <div className={styles.moveCard} onClick={onClick}>
      {/* Header Row */}
      <div className={styles.moveCardHeader}>
        <div>
          <h3 className={styles.moveTitle}>{move.name}</h3>
          <div className={styles.moveChips}>
            <span className={cn(styles.chip, styles.objective)}>
              {GOAL_LABELS[move.goal]?.label || move.goal}
            </span>
            <span className={cn(styles.chip, styles.channel)}>
              {CHANNEL_LABELS[move.channel]}
            </span>
            <span className={cn(styles.chip, styles.duration)}>
              {move.duration}D
            </span>
            {move.campaignName && (
              <span
                className={cn(styles.chip, styles.objective)}
                style={{ opacity: 0.6 }}
              >
                {move.campaignName}
              </span>
            )}
          </div>
        </div>
        <button
          className={styles.actionButton + ' ' + styles.secondary}
          style={{ padding: '8px', width: '36px', height: '36px' }}
          onClick={(e) => {
            e.stopPropagation();
          }}
        >
          <MoreHorizontal className="w-4 h-4" />
        </button>
      </div>

      {/* Outcome Line */}
      {move.outcomeTarget && (
        <p className={styles.moveOutcome}>
          <strong>Outcome:</strong> {move.outcomeTarget}
        </p>
      )}

      {/* Progress Row */}
      {isActive && (
        <div className={styles.progressRow}>
          <span className={styles.dayCounter}>
            Day {dayNumber}/{move.duration}
          </span>
          <div className={styles.progressBar}>
            <div
              className={styles.progressFill}
              style={{ width: `${progress.percent}%` }}
            />
          </div>
          <span className={styles.taskCount}>
            {progress.completed}/{progress.total} tasks
          </span>
          <span className={styles.lastActivity}>
            {formatLastActivity(move.startedAt)}
          </span>
        </div>
      )}

      {/* RAG Status */}
      {isActive && (
        <div className={cn(styles.ragRow, styles[rag.status])}>
          <div className={cn(styles.ragDot, styles[rag.status])} />
          <span className={cn(styles.ragLabel, styles[rag.status])}>
            {rag.status.toUpperCase()}
          </span>
          <span className={styles.ragReason}>— {rag.reason}</span>
        </div>
      )}

      {/* Next Action */}
      {nextTask && isActive && (
        <div className={styles.nextAction}>
          <span className={styles.nextActionLabel}>Next:</span>
          <span className={styles.nextActionText}>{nextTask.label}</span>
          <span className={styles.nextActionDue}>
            ~{nextTask.estimatedMinutes}m
          </span>
        </div>
      )}

      {/* Metrics Row */}
      {isActive && !compact && (
        <div className={styles.metricsRow}>
          <div className={styles.metric}>
            <span className={styles.metricLabel}>Leads</span>
            <span className={styles.metricValue}>{leads}</span>
          </div>
          <div className={styles.metric}>
            <span className={styles.metricLabel}>Replies</span>
            <span className={styles.metricValue}>{replies}</span>
          </div>
          <div className={styles.metric}>
            <span className={styles.metricLabel}>Calls</span>
            <span className={styles.metricValue}>{calls}</span>
          </div>
          <div className={styles.metric}>
            <span className={styles.metricLabel}>Confidence</span>
            <span className={styles.metricValue}>{confidence}/10</span>
          </div>
        </div>
      )}

      {/* Card Actions */}
      <div className={styles.cardActions}>
        {isActive && onLogProgress && (
          <button
            className={cn(styles.actionButton, styles.primary)}
            onClick={(e) => {
              e.stopPropagation();
              onLogProgress();
            }}
          >
            Log Progress
          </button>
        )}
        <button
          className={cn(styles.actionButton, styles.secondary)}
          onClick={(e) => {
            e.stopPropagation();
            onClick();
          }}
        >
          Open
          <ChevronRight className="w-4 h-4 ml-1" />
        </button>
      </div>
    </div>
  );
}
