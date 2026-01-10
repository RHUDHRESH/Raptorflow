"use client";

import { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  Square,
  RotateCcw,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap,
  Settings,
  Eye,
  MoreVertical,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Filter,
  Calendar,
  BarChart3,
  Trash2,
  Edit,
  Copy
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore, Move, MoveStatus } from '@/stores/enhancedCampaignStore';
import { useExecutionEngine } from '@/stores/executionEngine';
import { cn } from '@/lib/utils';
import { format, formatDistanceToNow } from 'date-fns';

interface MoveExecutionUIProps {
  campaignId?: string;
}

interface ExecutionLog {
  id: string;
  timestamp: Date;
  level: 'info' | 'warn' | 'error';
  message: string;
  details?: any;
}

export function MoveExecutionUI({ campaignId }: MoveExecutionUIProps) {
  const campaigns = useEnhancedCampaignStore(state => state.campaigns);
  const moves = useEnhancedCampaignStore(state => state.moves);
  const updateMove = useEnhancedCampaignStore(state => state.updateMove);
  const executeMove = useEnhancedCampaignStore(state => state.executeMove);
  const pauseMove = useEnhancedCampaignStore(state => state.pauseMove);
  const resumeMove = useEnhancedCampaignStore(state => state.resumeMove);

  const {
    queue,
    processing,
    currentExecution,
    logs,
    history,
    processQueue,
    pauseQueue,
    resumeQueue,
    getQueueStatus,
    getMoveLogs,
    getMoveHistory
  } = useExecutionEngine();

  const [selectedMove, setSelectedMove] = useState<string | null>(null);
  const [expandedMoves, setExpandedMoves] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState<'all' | 'running' | 'completed' | 'failed' | 'queued'>('all');
  const [selectedCampaign, setSelectedCampaign] = useState<string>(campaignId || 'all');

  // Get filtered moves
  const allMoves = Object.values(moves).filter(move => {
    if (selectedCampaign === 'all') return true;
    return Object.values(campaigns).some(campaign =>
      campaign.id === selectedCampaign && campaign.moves.includes(move.id)
    );
  });

  const filteredMoves = allMoves.filter(move => {
    switch (filter) {
      case 'running':
        return move.status === MoveStatus.RUNNING;
      case 'completed':
        return move.status === MoveStatus.COMPLETED;
      case 'failed':
        return move.status === MoveStatus.FAILED;
      case 'queued':
        return queue.some(item => item.moveId === move.id);
      default:
        return true;
    }
  });

  const queueStatus = getQueueStatus();

  // Toggle move expansion
  const toggleMoveExpansion = (moveId: string) => {
    setExpandedMoves(prev => {
      const newSet = new Set(prev);
      if (newSet.has(moveId)) {
        newSet.delete(moveId);
      } else {
        newSet.add(moveId);
      }
      return newSet;
    });
  };

  // Execute move
  const handleExecuteMove = async (moveId: string) => {
    const move = moves[moveId];
    if (move) {
      await executeMove(moveId);
    }
  };

  // Pause move
  const handlePauseMove = async (moveId: string) => {
    await pauseMove(moveId);
  };

  // Resume move
  const handleResumeMove = async (moveId: string) => {
    await resumeMove(moveId);
  };

  // Retry move
  const handleRetryMove = async (moveId: string) => {
    const move = moves[moveId];
    if (move) {
      await updateMove(moveId, { status: MoveStatus.DRAFT });
      await executeMove(moveId);
    }
  };

  // Get status color
  const getStatusColor = (status: MoveStatus) => {
    switch (status) {
      case MoveStatus.RUNNING:
        return 'text-[var(--warning)] bg-[var(--warning-light)]/10';
      case MoveStatus.COMPLETED:
        return 'text-[var(--success)] bg-[var(--success-light)]/10';
      case MoveStatus.FAILED:
        return 'text-[var(--destructive)] bg-[var(--destructive-light)]/10';
      case MoveStatus.SCHEDULED:
        return 'text-[var(--blueprint)] bg-[var(--blueprint-light)]/10';
      default:
        return 'text-[var(--ink-muted)] bg-[var(--surface)]';
    }
  };

  // Get status icon
  const getStatusIcon = (status: MoveStatus) => {
    switch (status) {
      case MoveStatus.RUNNING:
        return Play;
      case MoveStatus.COMPLETED:
        return CheckCircle;
      case MoveStatus.FAILED:
        return AlertCircle;
      case MoveStatus.SCHEDULED:
        return Clock;
      case MoveStatus.CANCELLED:
        return Square;
      default:
        return Clock;
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Move Execution</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Monitor and control move execution in real-time
          </p>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={() => window.location.reload()}
            className="flex items-center gap-2"
          >
            <RefreshCw size={16} />
            Refresh
          </BlueprintButton>

          {processing ? (
            <BlueprintButton
              variant="secondary"
              size="sm"
              onClick={pauseQueue}
              className="flex items-center gap-2"
            >
              <Pause size={16} />
              Pause Queue
            </BlueprintButton>
          ) : (
            <BlueprintButton
              size="sm"
              onClick={resumeQueue}
              className="flex items-center gap-2"
              disabled={queue.length === 0}
            >
              <Play size={16} />
              Resume Queue
            </BlueprintButton>
          )}
        </div>
      </div>

      {/* Queue Status */}
      <div className="p-6 border-b border-[var(--structure-subtle)]">
        <div className="grid grid-cols-5 gap-4">
          <BlueprintCard className="p-4 text-center">
            <div className="text-2xl font-bold text-[var(--ink)]">{queueStatus.pending}</div>
            <div className="text-xs text-[var(--ink-muted)]">Pending</div>
          </BlueprintCard>

          <BlueprintCard className="p-4 text-center">
            <div className="text-2xl font-bold text-[var(--warning)]">{queueStatus.processing}</div>
            <div className="text-xs text-[var(--ink-muted)]">Processing</div>
          </BlueprintCard>

          <BlueprintCard className="p-4 text-center">
            <div className="text-2xl font-bold text-[var(--success)]">{queueStatus.completed}</div>
            <div className="text-xs text-[var(--ink-muted)]">Completed</div>
          </BlueprintCard>

          <BlueprintCard className="p-4 text-center">
            <div className="text-2xl font-bold text-[var(--destructive)]">{queueStatus.failed}</div>
            <div className="text-xs text-[var(--ink-muted)]">Failed</div>
          </BlueprintCard>

          <BlueprintCard className="p-4 text-center">
            <div className="text-2xl font-bold text-[var(--ink)]">
              {currentExecution ? '1' : '0'}
            </div>
            <div className="text-xs text-[var(--ink-muted)]">Current</div>
          </BlueprintCard>
        </div>
      </div>

      {/* Filters */}
      <div className="px-6 py-4 border-b border-[var(--structure-subtle)]">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-[var(--ink-ghost)]" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as any)}
              className="px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
            >
              <option value="all">All Moves</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="queued">Queued</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <Calendar size={16} className="text-[var(--ink-ghost)]" />
            <select
              value={selectedCampaign}
              onChange={(e) => setSelectedCampaign(e.target.value)}
              className="px-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)]"
            >
              <option value="all">All Campaigns</option>
              {Object.values(campaigns).map(campaign => (
                <option key={campaign.id} value={campaign.id}>
                  {campaign.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2 text-sm text-[var(--ink-muted)]">
            {processing && (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-[var(--warning)] rounded-full animate-pulse" />
                Processing queue...
              </div>
            )}
            {currentExecution && (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-[var(--success)] rounded-full animate-pulse" />
                Executing: {moves[currentExecution]?.name || 'Unknown'}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Moves List */}
      <div className="flex-1 overflow-y-auto p-6">
        {filteredMoves.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <Zap size={48} className="text-[var(--ink-ghost)] mb-4" />
            <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">No moves found</h3>
            <p className="text-sm text-[var(--ink-muted)]">
              {filter === 'all' ? 'Create moves to see them here' : `No ${filter} moves`}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredMoves.map((move) => {
              const isExpanded = expandedMoves.has(move.id);
              const StatusIcon = getStatusIcon(move.status);
              const moveHistory = getMoveHistory(move.id);
              const moveLogs = getMoveLogs(move.id);
              const isInQueue = queue.some(item => item.moveId === move.id);
              const isCurrentlyExecuting = currentExecution === move.id;

              return (
                <BlueprintCard key={move.id} className="overflow-hidden">
                  <div className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          "w-10 h-10 rounded-lg flex items-center justify-center",
                          getStatusColor(move.status)
                        )}>
                          <StatusIcon size={20} />
                        </div>

                        <div className="flex-1">
                          <h3 className="text-sm font-semibold text-[var(--ink)]">{move.name}</h3>
                          <div className="flex items-center gap-3 mt-1">
                            <BlueprintBadge variant="outline" size="sm">
                              {move.type}
                            </BlueprintBadge>
                            <span className="text-xs text-[var(--ink-muted)]">
                              {move.execution.attempts} attempts
                            </span>
                            {move.execution.startedAt && (
                              <span className="text-xs text-[var(--ink-muted)]">
                                Started {formatDistanceToNow(move.execution.startedAt, { addSuffix: true })}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {isCurrentlyExecuting && (
                          <BlueprintBadge variant="default" size="sm" className="animate-pulse">
                            Executing
                          </BlueprintBadge>
                        )}

                        {isInQueue && (
                          <BlueprintBadge variant="outline" size="sm">
                            Queued
                          </BlueprintBadge>
                        )}

                        <button
                          onClick={() => toggleMoveExpansion(move.id)}
                          className="p-1 text-[var(--ink-muted)] hover:text-[var(--ink)]"
                        >
                          {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                        </button>

                        <div className="relative group">
                          <button className="p-1 text-[var(--ink-muted)] hover:text-[var(--ink)]">
                            <MoreVertical size={16} />
                          </button>

                          {/* Dropdown */}
                          <div className="absolute right-0 top-full mt-1 w-48 bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                            <div className="py-1">
                              <button className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2">
                                <Eye size={12} />
                                View Details
                              </button>
                              <button className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2">
                                <Edit size={12} />
                                Edit Move
                              </button>
                              <button className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2">
                                <Copy size={12} />
                                Duplicate
                              </button>
                              <hr className="my-1 border-[var(--structure-subtle)]" />

                              {move.status === MoveStatus.DRAFT || move.status === MoveStatus.SCHEDULED ? (
                                <button
                                  onClick={() => handleExecuteMove(move.id)}
                                  className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                                >
                                  <Play size={12} />
                                  Execute
                                </button>
                              ) : move.status === MoveStatus.RUNNING ? (
                                <button
                                  onClick={() => handlePauseMove(move.id)}
                                  className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                                >
                                  <Pause size={12} />
                                  Pause
                                </button>
                              ) : move.status === MoveStatus.CANCELLED ? (
                                <button
                                  onClick={() => handleResumeMove(move.id)}
                                  className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                                >
                                  <Play size={12} />
                                  Resume
                                </button>
                              ) : null}

                              {move.status === MoveStatus.FAILED && (
                                <button
                                  onClick={() => handleRetryMove(move.id)}
                                  className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                                >
                                  <RotateCcw size={12} />
                                  Retry
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {isExpanded && (
                      <div className="mt-4 pt-4 border-t border-[var(--structure-subtle)]">
                        <div className="grid grid-cols-2 gap-4">
                          {/* Execution Details */}
                          <div>
                            <h4 className="text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide mb-2">
                              Execution Details
                            </h4>
                            <div className="space-y-1 text-xs">
                              <div className="flex justify-between">
                                <span className="text-[var(--ink-muted)]">Status:</span>
                                <span className="text-[var(--ink)] capitalize">{move.status}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-[var(--ink-muted)]">Attempts:</span>
                                <span className="text-[var(--ink)]">{move.execution.attempts}</span>
                              </div>
                              {move.execution.startedAt && (
                                <div className="flex justify-between">
                                  <span className="text-[var(--ink-muted)]">Started:</span>
                                  <span className="text-[var(--ink)]">
                                    {format(move.execution.startedAt, 'MMM d, h:mm a')}
                                  </span>
                                </div>
                              )}
                              {move.execution.completedAt && (
                                <div className="flex justify-between">
                                  <span className="text-[var(--ink-muted)]">Completed:</span>
                                  <span className="text-[var(--ink)]">
                                    {format(move.execution.completedAt, 'MMM d, h:mm a')}
                                  </span>
                                </div>
                              )}
                              {move.execution.lastError && (
                                <div className="flex justify-between">
                                  <span className="text-[var(--ink-muted)]">Error:</span>
                                  <span className="text-[var(--destructive)]">
                                    {move.execution.lastError}
                                  </span>
                                </div>
                              )}
                            </div>
                          </div>

                          {/* Performance Metrics */}
                          <div>
                            <h4 className="text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide mb-2">
                              Performance Metrics
                            </h4>
                            {moveHistory?.metrics ? (
                              <div className="space-y-1 text-xs">
                                {Object.entries(moveHistory.metrics).map(([key, value]) => (
                                  <div key={key} className="flex justify-between">
                                    <span className="text-[var(--ink-muted)] capitalize">
                                      {key.replace(/_/g, ' ')}:
                                    </span>
                                    <span className="text-[var(--ink)]">
                                      {typeof value === 'number' ? value.toLocaleString() : value}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <p className="text-xs text-[var(--ink-muted)]">No metrics available</p>
                            )}
                          </div>
                        </div>

                        {/* Execution Logs */}
                        {moveLogs.length > 0 && (
                          <div className="mt-4">
                            <h4 className="text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide mb-2">
                              Recent Logs
                            </h4>
                            <div className="space-y-1 max-h-32 overflow-y-auto">
                              {moveLogs.slice(-5).map((log) => (
                                <div
                                  key={log.id}
                                  className={cn(
                                    "text-xs p-2 rounded font-mono",
                                    log.level === 'error' ? "bg-[var(--destructive-light)]/10 text-[var(--destructive)]" :
                                    log.level === 'warn' ? "bg-[var(--warning-light)]/10 text-[var(--warning)]" :
                                    "bg-[var(--surface)] text-[var(--ink-muted)]"
                                  )}
                                >
                                  [{format(log.timestamp, 'HH:mm:ss')}] {log.message}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </BlueprintCard>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
