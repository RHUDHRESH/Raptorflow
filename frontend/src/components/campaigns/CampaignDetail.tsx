"use client";

import { useState, useEffect } from 'react';
import {
  Calendar,
  Play,
  Pause,
  Settings,
  Edit,
  Trash2,
  Plus,
  ChevronDown,
  ChevronUp,
  Clock,
  Users,
  DollarSign,
  BarChart3,
  TrendingUp,
  Eye,
  Copy,
  MoreVertical,
  Zap,
  Target,
  AlertCircle
} from 'lucide-react';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { useEnhancedCampaignStore } from '@/stores/enhancedCampaignStore';
import { useCampaignMoves } from '@/stores/enhancedCampaignStore';
import { Campaign, CampaignStatus, MoveStatus } from '@/types/campaign';
import { MoveComposer } from './MoveComposer';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';
import { formatDistanceToNow } from 'date-fns/formatDistanceToNow';

interface CampaignDetailProps {
  campaignId: string;
  onClose?: () => void;
  onEdit?: () => void;
}

interface MoveExecutionStatus {
  moveId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  lastRun?: Date;
  nextRun?: Date;
  metrics?: Record<string, number>;
}

export function CampaignDetail({ campaignId, onClose, onEdit }: CampaignDetailProps) {
  const campaign = useEnhancedCampaignStore(state => state.campaigns[campaignId]);
  const moves = useCampaignMoves(campaignId);
  const updateCampaign = useEnhancedCampaignStore(state => state.updateCampaign);
  const deleteCampaign = useEnhancedCampaignStore(state => state.deleteCampaign);
  const duplicateCampaign = useEnhancedCampaignStore(state => state.duplicateCampaign);
  const executeMove = useEnhancedCampaignStore(state => state.executeMove);
  const pauseMove = useEnhancedCampaignStore(state => state.pauseMove);
  const resumeMove = useEnhancedCampaignStore(state => state.resumeMove);

  const [activeTab, setActiveTab] = useState<'overview' | 'moves' | 'analytics' | 'settings'>('overview');
  const [showMoveComposer, setShowMoveComposer] = useState(false);
  const [expandedMoves, setExpandedMoves] = useState<Set<string>>(new Set());
  const [moveStatuses, setMoveStatuses] = useState<Record<string, MoveExecutionStatus>>({});
  const [isExecuting, setIsExecuting] = useState(false);

  if (!campaign) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <AlertCircle size={48} className="text-[var(--ink-ghost)] mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">Campaign Not Found</h3>
          <p className="text-sm text-[var(--ink-muted)]">The campaign you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  // Calculate metrics
  const totalBudget = campaign.budget.total;
  const spentBudget = campaign.budget.spent;
  const remainingBudget = campaign.budget.remaining;
  const budgetProgress = totalBudget > 0 ? (spentBudget / totalBudget) * 100 : 0;

  const totalMoves = moves.length;
  const completedMoves = moves.filter(m => m.status === MoveStatus.COMPLETED).length;
  const runningMoves = moves.filter(m => m.status === MoveStatus.RUNNING).length;
  const moveProgress = totalMoves > 0 ? (completedMoves / totalMoves) * 100 : 0;

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

  // Execute all moves
  const executeAllMoves = async () => {
    setIsExecuting(true);
    try {
      for (const move of moves) {
        if (move.status === MoveStatus.DRAFT || move.status === MoveStatus.SCHEDULED) {
          await executeMove(move.id);
        }
      }
    } finally {
      setIsExecuting(false);
    }
  };

  // Pause all moves
  const pauseAllMoves = async () => {
    for (const move of moves) {
      if (move.status === MoveStatus.RUNNING) {
        await pauseMove(move.id);
      }
    }
  };

  // Render overview tab
  const renderOverview = () => (
    <div className="space-y-6">
      {/* Campaign Stats */}
      <div className="grid grid-cols-4 gap-4">
        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Status</span>
            <div className={cn(
              "w-2 h-2 rounded-full",
              campaign.status === CampaignStatus.ACTIVE ? "bg-[var(--success)]" :
                campaign.status === CampaignStatus.PAUSED ? "bg-[var(--warning)]" :
                  campaign.status === CampaignStatus.COMPLETED ? "bg-[var(--blueprint)]" :
                    "bg-[var(--ink-ghost)]"
            )} />
          </div>
          <p className="text-lg font-semibold text-[var(--ink)] capitalize">
            {campaign.status}
          </p>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Budget</span>
            <DollarSign size={16} className="text-[var(--ink-ghost)]" />
          </div>
          <p className="text-lg font-semibold text-[var(--ink)]">
            ${spentBudget.toLocaleString()}
          </p>
          <p className="text-xs text-[var(--ink-muted)]">
            of ${totalBudget.toLocaleString()}
          </p>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Moves</span>
            <Zap size={16} className="text-[var(--ink-ghost)]" />
          </div>
          <p className="text-lg font-semibold text-[var(--ink)]">
            {completedMoves}/{totalMoves}
          </p>
          <p className="text-xs text-[var(--ink-muted)]">
            {runningMoves} running
          </p>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">ROI</span>
            <TrendingUp size={16} className="text-[var(--ink-ghost)]" />
          </div>
          <p className="text-lg font-semibold text-[var(--ink)]">
            {campaign.analytics.overview.roi}%
          </p>
          <p className="text-xs text-[var(--success)]">
            +12% vs target
          </p>
        </BlueprintCard>
      </div>

      {/* Progress Bars */}
      <div className="grid grid-cols-2 gap-6">
        <BlueprintCard className="p-4">
          <h3 className="text-sm font-semibold text-[var(--ink)] mb-3">Budget Usage</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-[var(--ink-muted)]">Spent</span>
              <span className="text-[var(--ink)]">${spentBudget.toLocaleString()}</span>
            </div>
            <div className="w-full bg-[var(--surface)] rounded-full h-2">
              <div
                className="bg-[var(--warning)] h-2 rounded-full transition-all"
                style={{ width: `${Math.min(budgetProgress, 100)}%` }}
              />
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-[var(--ink-muted)]">Remaining</span>
              <span className="text-[var(--ink)]">${remainingBudget.toLocaleString()}</span>
            </div>
          </div>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <h3 className="text-sm font-semibold text-[var(--ink)] mb-3">Move Progress</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-[var(--ink-muted)]">Completed</span>
              <span className="text-[var(--ink)]">{completedMoves} moves</span>
            </div>
            <div className="w-full bg-[var(--surface)] rounded-full h-2">
              <div
                className="bg-[var(--success)] h-2 rounded-full transition-all"
                style={{ width: `${moveProgress}%` }}
              />
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-[var(--ink-muted)]">In Progress</span>
              <span className="text-[var(--ink)]">{runningMoves} moves</span>
            </div>
          </div>
        </BlueprintCard>
      </div>

      {/* Recent Activity */}
      <BlueprintCard className="p-4">
        <h3 className="text-sm font-semibold text-[var(--ink)] mb-3">Recent Activity</h3>
        <div className="space-y-3">
          {moves.slice(0, 5).map(move => (
            <div key={move.id} className="flex items-center justify-between py-2 border-b border-[var(--structure-subtle)] last:border-0">
              <div className="flex items-center gap-3">
                <div className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center",
                  move.status === MoveStatus.COMPLETED ? "bg-[var(--success-light)]/10" :
                    move.status === MoveStatus.RUNNING ? "bg-[var(--warning-light)]/10" :
                      "bg-[var(--surface)]"
                )}>
                  <Zap size={16} className={
                    move.status === MoveStatus.COMPLETED ? "text-[var(--success)]" :
                      move.status === MoveStatus.RUNNING ? "text-[var(--warning)]" :
                        "text-[var(--ink-ghost)]"
                  } />
                </div>
                <div>
                  <p className="text-sm font-medium text-[var(--ink)]">{move.name}</p>
                  <p className="text-xs text-[var(--ink-muted)]">
                    {move.execution.completedAt
                      ? `Completed ${formatDistanceToNow(move.execution.completedAt, { addSuffix: true })}`
                      : move.status === MoveStatus.RUNNING
                        ? 'Running now'
                        : 'Not started'
                    }
                  </p>
                </div>
              </div>
              <BlueprintBadge
                variant="default"
                size="sm"
                className={cn(
                  move.status === MoveStatus.COMPLETED ? "border-[var(--success)] text-[var(--success)]" :
                    move.status === MoveStatus.RUNNING ? "border-[var(--warning)] text-[var(--warning)]" :
                      "border-[var(--ink-ghost)] text-[var(--ink-ghost)]"
                )}
              >
                {move.status}
              </BlueprintBadge>
            </div>
          ))}
        </div>
      </BlueprintCard>
    </div>
  );

  // Render moves tab
  const renderMoves = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[var(--ink)]">Campaign Moves</h3>
        <div className="flex items-center gap-2">
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={pauseAllMoves}
            disabled={runningMoves === 0}
          >
            <Pause size={16} />
            Pause All
          </BlueprintButton>
          <BlueprintButton
            size="sm"
            onClick={executeAllMoves}
            disabled={isExecuting || completedMoves === totalMoves}
          >
            <Play size={16} />
            {isExecuting ? 'Executing...' : 'Execute All'}
          </BlueprintButton>
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={() => setShowMoveComposer(true)}
          >
            <Plus size={16} />
            Add Move
          </BlueprintButton>
        </div>
      </div>

      {moves.length === 0 ? (
        <BlueprintCard className="p-8 text-center">
          <Zap size={48} className="text-[var(--ink-ghost)] mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">No moves yet</h3>
          <p className="text-sm text-[var(--ink-muted)] mb-4">
            Add moves to start executing your campaign
          </p>
          <BlueprintButton onClick={() => setShowMoveComposer(true)}>
            Add Your First Move
          </BlueprintButton>
        </BlueprintCard>
      ) : (
        <div className="space-y-3">
          {moves.map((move, index) => {
            const isExpanded = expandedMoves.has(move.id);
            const status = moveStatuses[move.id];

            return (
              <BlueprintCard key={move.id} className="overflow-hidden">
                <div className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="text-sm font-medium text-[var(--ink-muted)] w-8">
                        #{index + 1}
                      </div>
                      <div className={cn(
                        "w-10 h-10 rounded-lg flex items-center justify-center",
                        move.status === MoveStatus.COMPLETED ? "bg-[var(--success-light)]/10" :
                          move.status === MoveStatus.RUNNING ? "bg-[var(--warning-light)]/10" :
                            move.status === MoveStatus.FAILED ? "bg-[var(--destructive-light)]/10" :
                              "bg-[var(--surface)]"
                      )}>
                        <Target size={20} className={
                          move.status === MoveStatus.COMPLETED ? "text-[var(--success)]" :
                            move.status === MoveStatus.RUNNING ? "text-[var(--warning)]" :
                              move.status === MoveStatus.FAILED ? "text-[var(--destructive)]" :
                                "text-[var(--ink-ghost)]"
                        } />
                      </div>
                      <div className="flex-1">
                        <h4 className="text-sm font-semibold text-[var(--ink)]">{move.name}</h4>
                        <p className="text-xs text-[var(--ink-muted)] mt-1">
                          {move.type} ΓÇó {move.status}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {move.status === MoveStatus.RUNNING && (
                        <BlueprintBadge variant="default" size="sm" className="animate-pulse">
                          Running
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
                              Edit
                            </button>
                            <button className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2">
                              <Copy size={12} />
                              Duplicate
                            </button>
                            <hr className="my-1 border-[var(--structure-subtle)]" />
                            {move.status === MoveStatus.RUNNING ? (
                              <button className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2">
                                <Pause size={12} />
                                Pause
                              </button>
                            ) : (
                              <button className="w-full px-3 py-2 text-xs text-left text-[var(--ink)] hover:bg-[var(--surface)] flex items-center gap-2">
                                <Play size={12} />
                                Execute
                              </button>
                            )}
                            <button className="w-full px-3 py-2 text-xs text-left text-[var(--destructive)] hover:bg-[var(--destructive-light)]/10 flex items-center gap-2">
                              <Trash2 size={12} />
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-[var(--structure-subtle)]">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <h5 className="text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide mb-2">
                            Configuration
                          </h5>
                          <div className="space-y-1">
                            <p className="text-xs text-[var(--ink)]">
                              Type: <span className="text-[var(--ink-muted)]">{move.type}</span>
                            </p>

                            {move.config.delay && (
                              <p className="text-xs text-[var(--ink)]">
                                Delay: <span className="text-[var(--ink-muted)]">{move.config.delay} hours</span>
                              </p>
                            )}
                          </div>
                        </div>

                        <div>
                          <h5 className="text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide mb-2">
                            Execution
                          </h5>
                          <div className="space-y-1">
                            <p className="text-xs text-[var(--ink)]">
                              Attempts: <span className="text-[var(--ink-muted)]">{move.execution.attempts}</span>
                            </p>
                            {move.execution.startedAt && (
                              <p className="text-xs text-[var(--ink)]">
                                Started: <span className="text-[var(--ink-muted)]">
                                  {format(move.execution.startedAt, 'MMM d, h:mm a')}
                                </span>
                              </p>
                            )}
                            {move.execution.completedAt && (
                              <p className="text-xs text-[var(--ink)]">
                                Completed: <span className="text-[var(--ink-muted)]">
                                  {format(move.execution.completedAt, 'MMM d, h:mm a')}
                                </span>
                              </p>
                            )}
                          </div>
                        </div>
                      </div>

                      {move.execution.logs && move.execution.logs.length > 0 && (
                        <div className="mt-4">
                          <h5 className="text-xs font-medium text-[var(--ink-muted)] uppercase tracking-wide mb-2">
                            Recent Logs
                          </h5>
                          <div className="space-y-1 max-h-32 overflow-y-auto">
                            {move.execution.logs.slice(-3).map((log, idx) => (
                              <div key={idx} className="text-xs text-[var(--ink-muted)] p-2 bg-[var(--surface)] rounded">
                                {log.message}
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
  );

  // Render analytics tab
  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Reach</span>
            <Users size={16} className="text-[var(--ink-ghost)]" />
          </div>
          <p className="text-lg font-semibold text-[var(--ink)]">
            {campaign.analytics.overview.totalReach.toLocaleString()}
          </p>
          <p className="text-xs text-[var(--success)]">+15% vs last week</p>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Engagement</span>
            <BarChart3 size={16} className="text-[var(--ink-ghost)]" />
          </div>
          <p className="text-lg font-semibold text-[var(--ink)]">
            {campaign.analytics.overview.totalEngagement.toLocaleString()}
          </p>
          <p className="text-xs text-[var(--success)]">+8% vs last week</p>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Conversions</span>
            <Target size={16} className="text-[var(--ink-ghost)]" />
          </div>
          <p className="text-lg font-semibold text-[var(--ink)]">
            {campaign.analytics.overview.totalConversions.toLocaleString()}
          </p>
          <p className="text-xs text-[var(--success)]">+12% vs last week</p>
        </BlueprintCard>

        <BlueprintCard className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-[var(--ink-muted)] uppercase tracking-wide">Revenue</span>
            <DollarSign size={16} className="text-[var(--ink-ghost)]" />
          </div>
          <p className="text-lg font-semibold text-[var(--ink)]">
            ${campaign.analytics.overview.totalRevenue.toLocaleString()}
          </p>
          <p className="text-xs text-[var(--success)]">+20% vs last week</p>
        </BlueprintCard>
      </div>

      {/* Performance Chart */}
      <BlueprintCard className="p-4">
        <h3 className="text-sm font-semibold text-[var(--ink)] mb-3">Performance Trend</h3>
        <div className="h-64 bg-[var(--surface)] rounded-[var(--radius)] flex items-center justify-center">
          <p className="text-sm text-[var(--ink-muted)]">Chart visualization would go here</p>
        </div>
      </BlueprintCard>
    </div>
  );

  // Render settings tab
  const renderSettings = () => (
    <div className="space-y-6">
      <BlueprintCard className="p-4">
        <h3 className="text-sm font-semibold text-[var(--ink)] mb-3">Campaign Settings</h3>
        <div className="space-y-4">
          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={campaign.settings.autoOptimization}
                onChange={(e) => updateCampaign({
                  id: campaign.id,
                  settings: {
                    ...campaign.settings,
                    autoOptimization: e.target.checked
                  }
                })}
                className="rounded border-[var(--structure-subtle)] text-[var(--blueprint)]"
              />
              <span className="text-sm text-[var(--ink)]">Auto-optimization</span>
            </label>
            <p className="text-xs text-[var(--ink-muted)] mt-1 ml-6">
              Automatically optimize moves based on performance
            </p>
          </div>

          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={campaign.settings.abTesting}
                onChange={(e) => updateCampaign({
                  id: campaign.id,
                  settings: {
                    ...campaign.settings,
                    abTesting: e.target.checked
                  }
                })}
                className="rounded border-[var(--structure-subtle)] text-[var(--blueprint)]"
              />
              <span className="text-sm text-[var(--ink)]">A/B Testing</span>
            </label>
            <p className="text-xs text-[var(--ink-muted)] mt-1 ml-6">
              Test different variations of moves
            </p>
          </div>
        </div>
      </BlueprintCard>

      <BlueprintCard className="p-4">
        <h3 className="text-sm font-semibold text-[var(--ink)] mb-3">Notifications</h3>
        <div className="space-y-4">
          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={campaign.settings.notifications.email}
                onChange={(e) => updateCampaign({
                  id: campaign.id,
                  settings: {
                    ...campaign.settings,
                    notifications: {
                      ...campaign.settings.notifications,
                      email: e.target.checked
                    }
                  }
                })}
                className="rounded border-[var(--structure-subtle)] text-[var(--blueprint)]"
              />
              <span className="text-sm text-[var(--ink)]">Email Notifications</span>
            </label>
          </div>

          <div>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={campaign.settings.notifications.push}
                onChange={(e) => updateCampaign({
                  id: campaign.id,
                  settings: {
                    ...campaign.settings,
                    notifications: {
                      ...campaign.settings.notifications,
                      push: e.target.checked
                    }
                  }
                })}
                className="rounded border-[var(--structure-subtle)] text-[var(--blueprint)]"
              />
              <span className="text-sm text-[var(--ink)]">Push Notifications</span>
            </label>
          </div>
        </div>
      </BlueprintCard>

      <BlueprintCard className="p-4">
        <h3 className="text-sm font-semibold text-[var(--ink)] mb-3 text-[var(--destructive)]">Danger Zone</h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-[var(--ink)]">Delete Campaign</p>
            <p className="text-xs text-[var(--ink-muted)]">This action cannot be undone</p>
          </div>
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={() => {
              if (confirm('Are you sure you want to delete this campaign?')) {
                deleteCampaign(campaign.id);
                onClose?.();
              }
            }}
            className="text-[var(--destructive)] hover:bg-[var(--destructive-light)]/10"
          >
            Delete Campaign
          </BlueprintButton>
        </div>
      </BlueprintCard>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-[var(--structure-subtle)]">
        <div>
          <h1 className="text-2xl font-bold text-[var(--ink)]">{campaign.name}</h1>
          <p className="text-sm text-[var(--ink-muted)] mt-1">{campaign.description}</p>
        </div>

        <div className="flex items-center gap-2">
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={() => duplicateCampaign(campaign.id)}
          >
            <Copy size={16} />
            Duplicate
          </BlueprintButton>
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={onEdit}
          >
            <Edit size={16} />
            Edit
          </BlueprintButton>
          <BlueprintButton
            variant="secondary"
            size="sm"
            onClick={onClose}
          >
            Back to Dashboard
          </BlueprintButton>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-6 px-6 border-b border-[var(--structure-subtle)]">
        {[
          { id: 'overview', label: 'Overview' },
          { id: 'moves', label: 'Moves', count: moves.length },
          { id: 'analytics', label: 'Analytics' },
          { id: 'settings', label: 'Settings' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={cn(
              "py-3 px-1 text-sm font-medium border-b-2 transition-colors",
              activeTab === tab.id
                ? "text-[var(--ink)] border-[var(--ink)]"
                : "text-[var(--ink-muted)] border-transparent hover:text-[var(--ink)]"
            )}
          >
            {tab.label}
            {tab.count !== undefined && (
              <span className="ml-2 text-xs text-[var(--ink-ghost)]">({tab.count})</span>
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'moves' && renderMoves()}
        {activeTab === 'analytics' && renderAnalytics()}
        {activeTab === 'settings' && renderSettings()}
      </div>

      {/* Move Composer Modal */}
      {showMoveComposer && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="w-full h-full max-w-6xl max-h-[90vh] bg-[var(--paper)] rounded-[var(--radius)] overflow-hidden">
            <MoveComposer
              onSave={() => setShowMoveComposer(false)}
              initialMoves={moves.map(m => m.config)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
