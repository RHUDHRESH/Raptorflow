"use client";

import { useState, useEffect } from 'react';
import {
  Play as PlayIcon,
  Pause,
  Square,
  RotateCcw,
  GitBranch,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap,
  Settings,
  Eye,
  MoreVertical,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Filter,
  Activity,
  Target,
  BarChart3,
  Trash2,
  Edit,
  Copy
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { Play, PlayStatus, PlayExecutionStatus } from '@/types/campaign';
import { cn } from '@/lib/utils';
import { format, formatDistanceToNow } from 'date-fns';

interface PlayExecutionUIProps {
  campaignId?: string;
}

interface PlayStepExecution {
  stepId: string;
  stepName: string;
  status: PlayExecutionStatus;
  moves: {
    moveId: string;
    moveName: string;
    status: PlayExecutionStatus;
    progress: number;
    startedAt?: Date;
    completedAt?: Date;
  }[];
  conditions?: {
    type: string;
    value: any;
    met: boolean;
  }[];
  startedAt?: Date;
  completedAt?: Date;
  parallel?: boolean;
}

interface PlayExecution {
  playId: string;
  playName: string;
  status: PlayExecutionStatus;
  currentStep: number;
  totalSteps: number;
  steps: PlayStepExecution[];
  startedAt?: Date;
  completedAt?: Date;
  metrics?: {
    totalMoves: number;
    completedMoves: number;
    failedMoves: number;
    duration: number;
  };
}

export function PlayExecutionUI({ campaignId }: PlayExecutionUIProps) {
  const campaigns = useEnhancedCampaignStore(state => state.campaigns);
  const plays = useEnhancedCampaignStore(state => state.plays);
  const movesStore = useEnhancedCampaignStore(state => state.moves);
  const updatePlay = useEnhancedCampaignStore(state => state.updatePlay);
  const executePlay = useEnhancedCampaignStore(state => state.executePlay);
  const pausePlay = useEnhancedCampaignStore(state => state.pausePlay);
  const resumePlay = useEnhancedCampaignStore(state => state.resumePlay);

  const [selectedPlay, setSelectedPlay] = useState<string | null>(null);
  const [expandedPlays, setExpandedPlays] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState<'all' | 'running' | 'completed' | 'failed' | 'scheduled'>('all');
  const [executions, setExecutions] = useState<Record<string, PlayExecution>>({});
  const [isLoading, setIsLoading] = useState(false);

  // Mock execution data
  useEffect(() => {
    const mockExecutions: Record<string, PlayExecution> = {};

    Object.values(plays).forEach(play => {
      mockExecutions[play.id] = {
        playId: play.id,
        playName: play.name,
        status: play.isActive ? PlayExecutionStatus.RUNNING : PlayExecutionStatus.PENDING,
        currentStep: play.isActive ? Math.floor(Math.random() * play.moves.length) : 0,
        totalSteps: play.moves.length,
        steps: play.moves.map((moveId, index) => {
          const move = movesStore[moveId];
          return {
            stepId: moveId,
            stepName: move?.name || `Step ${index + 1}`,
            status: play.isActive && index < 2 ? PlayExecutionStatus.COMPLETED :
              play.isActive && index === 2 ? PlayExecutionStatus.RUNNING :
                play.isActive && index === 3 ? PlayExecutionStatus.PENDING : PlayExecutionStatus.SKIPPED,
            moves: [{
              moveId,
              moveName: move?.name || `Move ${moveId}`,
              status: play.isActive && index < 2 ? PlayExecutionStatus.COMPLETED :
                play.isActive && index === 2 ? PlayExecutionStatus.RUNNING : PlayExecutionStatus.PENDING,
              progress: play.isActive && index < 2 ? 100 :
                play.isActive && index === 2 ? 45 : 0,
              startedAt: play.isActive && index <= 2 ? new Date(Date.now() - 3600000) : undefined,
              completedAt: play.isActive && index < 2 ? new Date(Date.now() - 1800000) : undefined
            }],
            conditions: [], // No conditions in flat move list for now
            startedAt: play.isActive && index <= 2 ? new Date(Date.now() - 3600000) : undefined,
            completedAt: play.isActive && index < 2 ? new Date(Date.now() - 1800000) : undefined
          };
        }),
        startedAt: play.isActive ? new Date(Date.now() - 3600000) : undefined,
        metrics: play.isActive ? {
          totalMoves: play.moves.length,
          completedMoves: Math.floor(Math.random() * 10),
          failedMoves: Math.floor(Math.random() * 3),
          duration: 3600
        } : undefined
      };
    });

    setExecutions(mockExecutions);
  }, [plays, movesStore]);

  // Get filtered plays
  const allPlays = Object.values(plays);
  const filteredPlays = allPlays.filter(play => {
    const execution = executions[play.id];
    if (!execution) return filter === 'all' || filter === 'scheduled';

    switch (filter) {
      case 'running':
        return execution.status === PlayExecutionStatus.RUNNING;
      case 'completed':
        return execution.status === PlayExecutionStatus.COMPLETED;
      case 'failed':
        return execution.status === PlayExecutionStatus.FAILED;
      case 'scheduled':
        return execution.status === PlayExecutionStatus.SCHEDULED;
      default:
        return true;
    }
  });

  // Toggle play expansion
  const togglePlayExpansion = (playId: string) => {
    setExpandedPlays(prev => {
      const newSet = new Set(prev);
      if (newSet.has(playId)) {
        newSet.delete(playId);
      } else {
        newSet.add(playId);
      }
      return newSet;
    });
  };

  // Execute play
  const handleExecutePlay = async (playId: string) => {
    setIsLoading(true);
    try {
      await executePlay(playId);
      // Update execution state
      const execution = executions[playId];
      if (execution) {
        setExecutions(prev => ({
          ...prev,
          [playId]: {
            ...execution,
            status: PlayExecutionStatus.RUNNING,
            startedAt: new Date()
          }
        }));
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Pause play
  const handlePausePlay = async (playId: string) => {
    await pausePlay(playId);
    const execution = executions[playId];
    if (execution) {
      setExecutions(prev => ({
        ...prev,
        [playId]: {
          ...execution,
          status: PlayExecutionStatus.SKIPPED // Using SKIPPED for paused as PAUSED not in ExecutionStatus or add PAUSED
        }
      }));
    }
  };

  // Resume play
  const handleResumePlay = async (playId: string) => {
    await resumePlay(playId);
    const execution = executions[playId];
    if (execution) {
      setExecutions(prev => ({
        ...prev,
        [playId]: {
          ...execution,
          status: PlayExecutionStatus.RUNNING
        }
      }));
    }
  };

  // Stop play
  const handleStopPlay = async (playId: string) => {
    await updatePlay(playId, { isActive: false });
    const execution = executions[playId];
    if (execution) {
      setExecutions(prev => ({
        ...prev,
        [playId]: {
          ...execution,
          status: PlayExecutionStatus.COMPLETED,
          completedAt: new Date()
        }
      }));
    }
  };

  // Get status color
  const getStatusColor = (status: PlayExecutionStatus) => {
    switch (status) {
      case PlayExecutionStatus.RUNNING:
        return 'text-[var(--warning)] bg-[var(--warning-light)]/10';
      case PlayExecutionStatus.COMPLETED:
        return 'text-[var(--success)] bg-[var(--success-light)]/10';
      case PlayExecutionStatus.FAILED:
        return 'text-[var(--destructive)] bg-[var(--destructive-light)]/10';
      case PlayExecutionStatus.SKIPPED:
        return 'text-[var(--ink-muted)] bg-[var(--surface)]';
      case PlayExecutionStatus.SCHEDULED:
        return 'text-[var(--blueprint)] bg-[var(--blueprint-light)]/10';
      default:
        return 'text-[var(--ink-muted)] bg-[var(--surface)]';
    }
  };

  // Get status icon
  const getStatusIcon = (status: PlayExecutionStatus) => {
    switch (status) {
      case PlayExecutionStatus.RUNNING:
        return PlayIcon;
      case PlayExecutionStatus.COMPLETED:
        return CheckCircle;
      case PlayExecutionStatus.FAILED:
        return AlertCircle;
      case PlayExecutionStatus.SKIPPED:
        return Pause;
      case PlayExecutionStatus.SCHEDULED:
        return Clock;
      default:
        return Clock;
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">Play Execution</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">
            Monitor and control automated play executions
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
        </div>
      </div>

      {/* Summary Stats */}
      <div className="p-6 border-b border-[var(--structure-subtle)]">
        <div className="grid grid-cols-4 gap-4">
          <BlueprintCard className="p-4 text-center">
            <div className="text-2xl font-bold text-[var(--ink)]">
              {allPlays.filter(p => executions[p.id]?.status === PlayExecutionStatus.RUNNING).length}
            </div>
            <div className="text-xs text-[var(--ink-muted)]">Running</div>
          </BlueprintCard>

          <BlueprintCard className="p-4 text-center">
            <div className="text-2xl font-bold text-[var(--success)]">
              {allPlays.filter(p => executions[p.id]?.status === PlayExecutionStatus.COMPLETED).length}
            </div>
            <div className="text-xs text-[var(--ink-muted)]">Completed</div>
          </BlueprintCard>

          <BlueprintCard className="p-4 text-center">
            <div className="text-2xl font-bold text-[var(--destructive)]">
              {allPlays.filter(p => executions[p.id]?.status === PlayExecutionStatus.FAILED).length}
            </div>
            <div className="text-xs text-[var(--ink-muted)]">Failed</div>
          </BlueprintCard>

          <BlueprintCard className="p-4 text-center">
            <div className="text-2xl font-bold text-[var(--blueprint)]">
              {allPlays.filter(p => executions[p.id]?.status === PlayExecutionStatus.SCHEDULED).length}
            </div>
            <div className="text-xs text-[var(--ink-muted)]">Scheduled</div>
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
              <option value="all">All Plays</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="scheduled">Scheduled</option>
            </select>
          </div>

          <div className="flex items-center gap-2 text-sm text-[var(--ink-muted)]">
            <Activity size={16} />
            {allPlays.filter(p => executions[p.id]?.status === PlayExecutionStatus.RUNNING).length} plays running
          </div>
        </div>
      </div>

      {/* Plays List */}
      <div className="flex-1 overflow-y-auto p-6">
        {filteredPlays.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <GitBranch size={48} className="text-[var(--ink-ghost)] mb-4" />
            <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">No plays found</h3>
            <p className="text-sm text-[var(--ink-muted)]">
              {filter === 'all' ? 'Create plays to see them here' : `No ${filter} plays`}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredPlays.map((play) => {
              const isExpanded = expandedPlays.has(play.id);
              const execution = executions[play.id];
              const StatusIcon = getStatusIcon(execution?.status || PlayExecutionStatus.PENDING);

              return (
                <BlueprintCard key={play.id} className="overflow-hidden">
                  <div className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={cn(
                          "w-10 h-10 rounded-lg flex items-center justify-center",
                          getStatusColor(execution?.status || PlayExecutionStatus.PENDING)
                        )}>
                          <StatusIcon size={20} />
                        </div>

                        <div className="flex-1">
                          <h3 className="text-sm font-semibold text-[var(--ink)]">{play.name}</h3>
                          <div className="flex items-center gap-3 mt-1">
                            <BlueprintBadge variant="blueprint" size="sm">
                              {play.category}
                            </BlueprintBadge>
                            <span className="text-xs text-[var(--ink-muted)]">
                              {play.moves.length} steps
                            </span>
                            {execution?.startedAt && (
                              <span className="text-xs text-[var(--ink-muted)]">
                                Started {formatDistanceToNow(execution.startedAt, { addSuffix: true })}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {execution?.status === PlayExecutionStatus.RUNNING && (
                          <BlueprintBadge variant="default" size="sm" className="animate-pulse">
                            Step {execution.currentStep + 1}/{execution.totalSteps}
                          </BlueprintBadge>
                        )}

                        {execution?.metrics && (
                          <BlueprintBadge variant="default" size="sm">
                            {execution.metrics.completedMoves}/{execution.metrics.totalMoves} moves
                          </BlueprintBadge>
                        )}

                        <button
                          onClick={() => togglePlayExpansion(play.id)}
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
                                Edit Play
                              </button>
                              <button className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2">
                                <Copy size={12} />
                                Duplicate
                              </button>
                              <hr className="my-1 border-[var(--structure-subtle)]" />

                              {!execution || execution.status === PlayExecutionStatus.PENDING ? (
                                <button
                                  onClick={() => handleExecutePlay(play.id)}
                                  className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                                  disabled={isLoading}
                                >
                                  <PlayIcon size={12} />
                                  Execute
                                </button>
                              ) : execution.status === PlayExecutionStatus.RUNNING ? (
                                <button
                                  onClick={() => handlePausePlay(play.id)}
                                  className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                                >
                                  <Pause size={12} />
                                  Pause
                                </button>
                              ) : execution.status === PlayExecutionStatus.SKIPPED ? (
                                <button
                                  onClick={() => handleResumePlay(play.id)}
                                  className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2"
                                >
                                  <PlayIcon size={12} />
                                  Resume
                                </button>
                              ) : null}

                              {execution?.status === PlayExecutionStatus.RUNNING && (
                                <button
                                  onClick={() => handleStopPlay(play.id)}
                                  className="w-full px-3 py-2 text-xs text-left text-[var(--destructive)] hover:bg-[var(--destructive-light)]/10 flex items-center gap-2"
                                >
                                  <Square size={12} />
                                  Stop
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    {isExpanded && execution && (
                      <div className="mt-4 pt-4 border-t border-[var(--structure-subtle)]">
                        {/* Progress Bar */}
                        <div className="mb-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-[var(--ink)]">Progress</span>
                            <span className="text-xs text-[var(--ink-muted)]">
                              {execution.currentStep + 1} of {execution.totalSteps} steps
                            </span>
                          </div>
                          <div className="w-full bg-[var(--surface)] rounded-full h-2">
                            <div
                              className="bg-[var(--success)] h-2 rounded-full transition-all"
                              style={{ width: `${((execution.currentStep + 1) / execution.totalSteps) * 100}%` }}
                            />
                          </div>
                        </div>

                        {/* Steps Flow */}
                        <div className="space-y-2">
                          <h4 className="text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide">
                            Step Execution Flow
                          </h4>
                          {execution.steps.map((step, index) => (
                            <div key={step.stepId} className="flex items-center gap-3 p-3 bg-[var(--surface)] rounded-lg">
                              <div className="flex-shrink-0">
                                <div className={cn(
                                  "w-6 h-6 rounded-full flex items-center justify-center text-xs",
                                  step.status === PlayExecutionStatus.COMPLETED ? "bg-[var(--success)] text-white" :
                                    step.status === PlayExecutionStatus.RUNNING ? "bg-[var(--warning)] text-white" :
                                      step.status === PlayExecutionStatus.FAILED ? "bg-[var(--destructive)] text-white" :
                                        step.status === PlayExecutionStatus.PENDING ? "bg-[var(--blueprint)] text-white" :
                                          "bg-[var(--ink-ghost)] text-[var(--ink)]"
                                )}>
                                  {step.status === PlayExecutionStatus.COMPLETED ? '✓' :
                                    step.status === PlayExecutionStatus.RUNNING ? '▶' :
                                      step.status === PlayExecutionStatus.FAILED ? '✕' :
                                        step.status === PlayExecutionStatus.PENDING ? '⏸' :
                                          '○'}
                                </div>
                              </div>

                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <p className="text-sm font-medium text-[var(--ink)] truncate">
                                    {step.stepName}
                                  </p>
                                  {step.parallel && (
                                    <BlueprintBadge variant="blueprint" size="xs">Parallel</BlueprintBadge>
                                  )}
                                </div>

                                <div className="flex items-center gap-4 mt-1">
                                  <span className="text-xs text-[var(--ink-muted)]">
                                    {step.moves.length} moves
                                  </span>
                                  {step.startedAt && (
                                    <span className="text-xs text-[var(--ink-muted)]">
                                      {formatDistanceToNow(step.startedAt, { addSuffix: true })}
                                    </span>
                                  )}
                                </div>

                                {/* Move Progress */}
                                {step.moves.length > 0 && (
                                  <div className="mt-2">
                                    <div className="flex items-center gap-2">
                                      {step.moves.slice(0, 3).map((move, idx) => (
                                        <div key={idx} className="flex-1">
                                          <div className="flex items-center justify-between mb-1">
                                            <span className="text-xs text-[var(--ink-ghost)] truncate">
                                              {move.moveName}
                                            </span>
                                            <span className="text-xs text-[var(--ink-ghost)]">
                                              {move.progress}%
                                            </span>
                                          </div>
                                          <div className="w-full bg-[var(--structure-subtle)] rounded-full h-1">
                                            <div
                                              className={cn(
                                                "h-1 rounded-full",
                                                move.status === PlayExecutionStatus.COMPLETED ? "bg-[var(--success)]" :
                                                  move.status === PlayExecutionStatus.RUNNING ? "bg-[var(--warning)]" :
                                                    move.status === PlayExecutionStatus.FAILED ? "bg-[var(--destructive)]" :
                                                      "bg-[var(--ink-ghost)]"
                                              )}
                                              style={{ width: `${move.progress}%` }}
                                            />
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {/* Conditions */}
                                {step.conditions && step.conditions.length > 0 && (
                                  <div className="mt-2 flex items-center gap-2">
                                    <Target size={12} className="text-[var(--ink-ghost)]" />
                                    {step.conditions.map((cond, idx) => (
                                      <BlueprintBadge
                                        key={idx}
                                        variant={cond.met ? "success" : "default"}
                                        size="xs"
                                        className={cond.met ? "bg-[var(--success)]" : ""}
                                      >
                                        {cond.type}: {cond.value}
                                      </BlueprintBadge>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Performance Metrics */}
                        {execution.metrics && (
                          <div className="mt-4 pt-4 border-t border-[var(--structure-subtle)]">
                            <h4 className="text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide mb-2">
                              Performance Metrics
                            </h4>
                            <div className="grid grid-cols-4 gap-4">
                              <div className="text-center">
                                <p className="text-lg font-semibold text-[var(--ink)]">
                                  {execution.metrics.totalMoves}
                                </p>
                                <p className="text-xs text-[var(--ink-muted)]">Total Moves</p>
                              </div>
                              <div className="text-center">
                                <p className="text-lg font-semibold text-[var(--success)]">
                                  {execution.metrics.completedMoves}
                                </p>
                                <p className="text-xs text-[var(--ink-muted)]">Completed</p>
                              </div>
                              <div className="text-center">
                                <p className="text-lg font-semibold text-[var(--destructive)]">
                                  {execution.metrics.failedMoves}
                                </p>
                                <p className="text-xs text-[var(--ink-muted)]">Failed</p>
                              </div>
                              <div className="text-center">
                                <p className="text-lg font-semibold text-[var(--ink)]">
                                  {Math.floor(execution.metrics.duration / 60)}m
                                </p>
                                <p className="text-xs text-[var(--ink-muted)]">Duration</p>
                              </div>
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
