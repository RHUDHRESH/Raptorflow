"use client";

import React, { useEffect, useState } from "react";
import { Loader2, CheckCircle2, Circle, AlertCircle, Clock, ChevronRight, ChevronLeft, Zap, Target, TrendingUp } from "lucide-react";
import { useOnboardingStore } from "@/stores/onboardingStore";
import { ONBOARDING_PHASES, ONBOARDING_STEPS, type StepStatus } from "@/lib/onboarding-tokens";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton } from "@/components/ui/BlueprintButton";

interface OnboardingProgressEnhancedProps {
  className?: string;
  showDetails?: boolean;
  compact?: boolean;
  interactive?: boolean;
  onStepClick?: (stepId: number) => void;
  onPhaseClick?: (phaseId: number) => void;
}

interface SessionProgress {
  sessionId: string;
  workspaceId: string;
  completionPercentage: number;
  completedSteps: number;
  totalSteps: number;
  lastActivity: string;
  estimatedTimeRemaining?: number;
  currentPhase: number;
  bcmGenerated?: boolean;
  finalizedAt?: string;
}

export function OnboardingProgressEnhanced({
  className = "",
  showDetails = true,
  compact = false,
  interactive = true,
  onStepClick,
  onPhaseClick,
}: OnboardingProgressEnhancedProps) {
  const {
    currentStep,
    steps,
    getProgress,
    canProceedToStep,
    session,
    saveStatus,
    lastSyncedAt
  } = useOnboardingStore();

  const [sessionProgress, setSessionProgress] = useState<SessionProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedPhase, setExpandedPhase] = useState<number | null>(null);

  // Fetch session progress from backend
  useEffect(() => {
    const fetchSessionProgress = async () => {
      if (!session?.sessionId) {
        setLoading(false);
        return;
      }

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/onboarding/${session.sessionId}/progress`);

        if (response.ok) {
          const data = await response.json();
          setSessionProgress({
            sessionId: data.session_id,
            workspaceId: data.workspace_id,
            completionPercentage: data.progress.percentage,
            completedSteps: data.progress.completed,
            totalSteps: data.progress.total,
            lastActivity: data.last_activity,
            estimatedTimeRemaining: data.estimated_time_remaining,
            currentPhase: data.current_phase,
            bcmGenerated: data.bcm_generated,
            finalizedAt: data.finalized_at,
          });
        }
      } catch (error) {
        console.error("Failed to fetch session progress:", error);
        // Fallback to local progress
        const localProgress = getProgress();
        setSessionProgress({
          sessionId: session.sessionId,
          workspaceId: "",
          completionPercentage: localProgress.percentage,
          completedSteps: localProgress.completed,
          totalSteps: localProgress.total,
          lastActivity: new Date().toISOString(),
          currentPhase: getCurrentPhase(currentStep),
        });
      } finally {
        setLoading(false);
      }
    };

    fetchSessionProgress();
  }, [session?.sessionId, currentStep, getProgress]);

  const getCurrentPhase = (stepId: number): number => {
    const step = ONBOARDING_STEPS.find(s => s.id === stepId);
    return step?.phase || 1;
  };

  const getStepIcon = (status: StepStatus) => {
    switch (status) {
      case "complete":
        return <CheckCircle2 size={16} className="text-[var(--success)]" />;
      case "in-progress":
        return <Loader2 size={16} className="text-[var(--accent)] animate-spin" />;
      case "blocked":
        return <AlertCircle size={16} className="text-[var(--error)]" />;
      case "error":
        return <AlertCircle size={16} className="text-[var(--error)]" />;
      default:
        return <Circle size={16} className="text-[var(--muted)]" />;
    }
  };

  const getPhaseProgress = (phaseId: number) => {
    const phase = ONBOARDING_PHASES.find(p => p.id === phaseId);
    if (!phase) return { completed: 0, total: 0, percentage: 0 };

    const phaseSteps = steps.filter(s => phase.steps.includes(s.id));
    const completed = phaseSteps.filter(s => s.status === "complete").length;
    const total = phaseSteps.length;

    return { completed, total, percentage: total > 0 ? Math.round((completed / total) * 100) : 0 };
  };

  const handleStepClick = (stepId: number) => {
    if (interactive && canProceedToStep(stepId)) {
      onStepClick?.(stepId);
    }
  };

  const handlePhaseClick = (phaseId: number) => {
    if (interactive) {
      setExpandedPhase(expandedPhase === phaseId ? null : phaseId);
      onPhaseClick?.(phaseId);
    }
  };

  if (loading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <Loader2 size={24} className="text-[var(--muted)] animate-spin" />
      </div>
    );
  }

  const progress = sessionProgress || getProgress();

  // Helper function to safely get progress values
  const getProgressValue = (key: 'percentage' | 'completed' | 'total'): number => {
    // If we have session progress with the required property, use it
    if (sessionProgress && typeof sessionProgress === 'object' && key in sessionProgress) {
      return (sessionProgress as any)[key];
    }
    // Otherwise fall back to local progress
    return progress[key as keyof typeof progress];
  };

  if (compact) {
    return (
      <div className={`flex items-center gap-4 ${className}`}>
        <div className="flex items-center gap-2">
          <div className="text-sm text-[var(--muted)]">Progress</div>
          <div className="text-lg font-semibold text-[var(--ink)]">
            {getProgressValue('percentage')}%
          </div>
        </div>
        <div className="flex-1 bg-[var(--border-subtle)] rounded-full h-2">
          <div
            className="bg-[var(--accent)] h-2 rounded-full transition-all duration-300"
            style={{ width: `${getProgressValue('percentage')}%` }}
          />
        </div>
        <div className="text-sm text-[var(--muted)]">
          {getProgressValue('completed')} of {getProgressValue('total')} steps
        </div>
      </div>
    );
  }

  return (
    <BlueprintCard className={`p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[var(--blueprint)] rounded-[var(--radius-md)] flex items-center justify-center">
            <Target size={20} className="text-[var(--paper)]" />
          </div>
          <div>
            <h3 className="font-semibold text-[var(--ink)]">Onboarding Progress</h3>
            <p className="text-sm text-[var(--muted)]">
              Session {sessionProgress?.sessionId?.slice(-8) || 'Local'}
            </p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-2xl font-bold text-[var(--ink)]">
            {getProgressValue('percentage')}%
          </div>
          <div className="text-sm text-[var(--muted)]">
            {getProgressValue('completed')} of {getProgressValue('total')} steps
          </div>
        </div>
      </div>

      {/* Overall Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-sm text-[var(--muted)] mb-2">
          <span>Overall Progress</span>
          <span>{getProgressValue('percentage')}% Complete</span>
        </div>
        <div className="bg-[var(--border-subtle)] rounded-full h-3">
          <div
            className="bg-gradient-to-r from-[var(--accent)] to-[var(--accent-hover)] h-3 rounded-full transition-all duration-500"
            style={{ width: `${getProgressValue('percentage')}%` }}
          />
        </div>
      </div>

      {/* Phases */}
      <div className="space-y-4">
        {ONBOARDING_PHASES.map((phase) => {
          const phaseProgress = getPhaseProgress(phase.id);
          const isCurrentPhase = getCurrentPhase(currentStep) === phase.id;
          const isExpanded = expandedPhase === phase.id;

          return (
            <div key={phase.id} className="border border-[var(--border-subtle)] rounded-[var(--radius-lg)] overflow-hidden">
              {/* Phase Header */}
              <div
                className={`p-4 cursor-pointer transition-colors ${
                  isCurrentPhase ? 'bg-[var(--accent-light)]' : 'hover:bg-[var(--canvas-elevated)]'
                }`}
                onClick={() => handlePhaseClick(phase.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      isCurrentPhase ? 'bg-[var(--accent)]' : 'bg-[var(--surface)]'
                    }`}>
                      {phaseProgress.completed === phaseProgress.total ? (
                        <CheckCircle2 size={16} className="text-white" />
                      ) : (
                        <span className="text-sm font-semibold">{phase.id}</span>
                      )}
                    </div>
                    <div>
                      <h4 className="font-medium text-[var(--ink)]">{phase.name}</h4>
                      <p className="text-sm text-[var(--muted)]">
                        {phaseProgress.completed}/{phaseProgress.total} steps
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-sm font-medium text-[var(--ink)]">
                        {phaseProgress.percentage}%
                      </div>
                      <div className="text-xs text-[var(--muted)]">
                        {phaseProgress.completed === phaseProgress.total ? 'Complete' : 'In Progress'}
                      </div>
                    </div>
                    {isExpanded ? (
                      <ChevronLeft size={16} className="text-[var(--muted)]" />
                    ) : (
                      <ChevronRight size={16} className="text-[var(--muted)]" />
                    )}
                  </div>
                </div>

                {/* Phase Progress Bar */}
                <div className="mt-3">
                  <div className="bg-[var(--border-subtle)] rounded-full h-2">
                    <div
                      className="bg-[var(--accent)] h-2 rounded-full transition-all duration-300"
                      style={{ width: `${phaseProgress.percentage}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Expanded Steps */}
              {isExpanded && (
                <div className="border-t border-[var(--border-subtle)] p-4 space-y-2">
                  {phase.steps.map((stepId) => {
                    const step = steps.find(s => s.id === stepId);
                    const stepConfig = ONBOARDING_STEPS.find(s => s.id === stepId);
                    const isCurrentStep = currentStep === stepId;
                    const canProceed = canProceedToStep(stepId);

                    return (
                      <div
                        key={stepId}
                        className={`flex items-center justify-between p-3 rounded-[var(--radius-md)] cursor-pointer transition-colors ${
                          isCurrentStep
                            ? 'bg-[var(--accent-light)] border border-[var(--accent)]'
                            : canProceed
                              ? 'hover:bg-[var(--canvas-elevated)]'
                              : 'opacity-50 cursor-not-allowed'
                        }`}
                        onClick={() => handleStepClick(stepId)}
                      >
                        <div className="flex items-center gap-3">
                          {getStepIcon(step?.status || 'pending')}
                          <div>
                            <div className="font-medium text-[var(--ink)]">
                              {stepConfig?.name || `Step ${stepId}`}
                            </div>
                            <div className="text-xs text-[var(--muted)]">
                              {step?.status === 'complete' && 'Completed'}
                              {step?.status === 'in-progress' && 'In Progress'}
                              {step?.status === 'pending' && 'Not Started'}
                              {step?.status === 'blocked' && 'Blocked'}
                              {step?.status === 'error' && 'Error'}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          {stepConfig?.required && (
                            <span className="px-2 py-1 bg-[var(--error-light)] text-[var(--error)] text-xs rounded-[var(--radius-sm)]">
                              Required
                            </span>
                          )}
                          {isCurrentStep && (
                            <span className="px-2 py-1 bg-[var(--accent)] text-white text-xs rounded-[var(--radius-sm)]">
                              Current
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Status and Actions */}
      {showDetails && (
        <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Clock size={16} className="text-[var(--muted)]" />
              <span className="text-sm text-[var(--muted)]">
                Last activity: {sessionProgress?.lastActivity ? new Date(sessionProgress.lastActivity).toLocaleDateString() : 'Unknown'}
              </span>
            </div>

            {saveStatus && (
              <div className="flex items-center gap-2">
                {saveStatus === 'saved' && lastSyncedAt && (
                  <span className="text-sm text-[var(--success)]">
                    Synced {new Date(lastSyncedAt).toLocaleTimeString()}
                  </span>
                )}
                {saveStatus === 'saving' && (
                  <div className="flex items-center gap-2 text-[var(--muted)]">
                    <Loader2 size={14} className="animate-spin" />
                    <span className="text-sm">Saving...</span>
                  </div>
                )}
                {saveStatus === 'error' && (
                  <span className="text-sm text-[var(--error)]">Sync failed</span>
                )}
              </div>
            )}
          </div>

          {/* BCM Status */}
          {sessionProgress?.bcmGenerated && (
            <div className="flex items-center gap-2 p-3 bg-[var(--success-light)] rounded-[var(--radius-md)]">
              <CheckCircle2 size={16} className="text-[var(--success)]" />
              <span className="text-sm text-[var(--success)]">
                Business Context Generated
              </span>
            </div>
          )}

          {/* Finalization Status */}
          {sessionProgress?.finalizedAt && (
            <div className="flex items-center gap-2 p-3 bg-[var(--accent-light)] rounded-[var(--radius-md)]">
              <Zap size={16} className="text-[var(--accent)]" />
              <span className="text-sm text-[var(--accent)]">
                Finalized {new Date(sessionProgress.finalizedAt).toLocaleDateString()}
              </span>
            </div>
          )}

          {/* Action Buttons */}
          {interactive && (
            <div className="flex gap-3 mt-4">
              <BlueprintButton
                variant="outline"
                size="sm"
                onClick={() => onStepClick?.(currentStep)}
                disabled={!canProceedToStep(currentStep)}
              >
                Continue Current Step
              </BlueprintButton>

              {getProgressValue('percentage') >= 50 && (
                <BlueprintButton
                  variant="blueprint"
                  size="sm"
                  onClick={() => {
                    // Trigger finalization
                    window.location.href = `/onboarding/session/${session?.sessionId}/finalize`;
                  }}
                >
                  <TrendingUp size={16} className="mr-2" />
                  Finalize
                </BlueprintButton>
              )}
            </div>
          )}
        </div>
      )}
    </BlueprintCard>
  );
}
