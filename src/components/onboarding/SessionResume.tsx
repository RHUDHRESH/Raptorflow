'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';

interface SessionData {
  sessionId: string;
  userId: string;
  currentStep: number;
  completedSteps: number[];
  formData: Record<string, any>;
  lastActivity: string;
  status: 'active' | 'abandoned' | 'completed';
}

interface SessionResumeProps {
  onSessionResume?: (sessionData: SessionData) => void;
  onSessionStart?: () => void;
  onSessionDismiss?: () => void;
  className?: string;
}

export function SessionResume({
  onSessionResume,
  onSessionStart,
  onSessionDismiss,
  className
}: SessionResumeProps) {
  const router = useRouter();
  const [availableSessions, setAvailableSessions] = useState<SessionData[]>([]);
  const [selectedSession, setSelectedSession] = useState<SessionData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showResumeDialog, setShowResumeDialog] = useState(false);

  // Load available sessions from localStorage and API
  useEffect(() => {
    const loadSessions = async () => {
      try {
        setIsLoading(true);

        // Get sessions from localStorage
        const localSessions = localStorage.getItem('onboarding_sessions');
        const sessions: SessionData[] = localSessions ? JSON.parse(localSessions) : [];

        // Filter for active or abandoned sessions
        const activeSessions = sessions.filter(
          session => session.status === 'active' || session.status === 'abandoned'
        );

        // Sort by last activity (most recent first)
        activeSessions.sort((a, b) =>
          new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime()
        );

        setAvailableSessions(activeSessions);

        // Show resume dialog if there are sessions
        if (activeSessions.length > 0) {
          setShowResumeDialog(true);
        }
      } catch (error) {
        console.error('Failed to load sessions:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadSessions();
  }, []);

  // Resume session
  const handleResumeSession = async (session: SessionData) => {
    try {
      // Update session status to active
      const updatedSession = { ...session, status: 'active' as const };

      // Save to localStorage
      const localSessions = localStorage.getItem('onboarding_sessions');
      const sessions: SessionData[] = localSessions ? JSON.parse(localSessions) : [];
      const sessionIndex = sessions.findIndex(s => s.sessionId === session.sessionId);

      if (sessionIndex >= 0) {
        sessions[sessionIndex] = updatedSession;
        localStorage.setItem('onboarding_sessions', JSON.stringify(sessions));
      }

      // Call callback
      if (onSessionResume) {
        onSessionResume(updatedSession);
      }

      // Navigate to the current step
      router.push(`/onboarding/session/step/${session.currentStep}`);

      setShowResumeDialog(false);
    } catch (error) {
      console.error('Failed to resume session:', error);
    }
  };

  // Start new session
  const handleStartNew = () => {
    if (onSessionStart) {
      onSessionStart();
    }

    // Clear existing sessions
    localStorage.removeItem('onboarding_sessions');

    // Navigate to first step
    router.push('/onboarding/session/step/1');

    setShowResumeDialog(false);
  };

  // Dismiss dialog
  const handleDismiss = () => {
    setShowResumeDialog(false);
    if (onSessionDismiss) {
      onSessionDismiss();
    }
  };

  // Delete session
  const handleDeleteSession = (sessionId: string) => {
    const localSessions = localStorage.getItem('onboarding_sessions');
    const sessions: SessionData[] = localSessions ? JSON.parse(localSessions) : [];

    const filteredSessions = sessions.filter(s => s.sessionId !== sessionId);
    localStorage.setItem('onboarding_sessions', JSON.stringify(filteredSessions));

    setAvailableSessions(prev => prev.filter(s => s.sessionId !== sessionId));

    if (selectedSession?.sessionId === sessionId) {
      setSelectedSession(null);
    }
  };

  // Format last activity time
  const formatLastActivity = (lastActivity: string) => {
    const date = new Date(lastActivity);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else {
      return 'Less than an hour ago';
    }
  };

  // Get step progress percentage
  const getProgressPercentage = (completedSteps: number[], totalSteps = 23) => {
    return Math.round((completedSteps.length / totalSteps) * 100);
  };

  if (isLoading) {
    return (
      <div className={cn("flex items-center justify-center p-8", className)}>
        <div className="text-center space-y-4">
          <div className="w-8 h-8 border-2 border-[var(--blueprint)] border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-[var(--muted)] font-technical">Loading sessions...</p>
        </div>
      </div>
    );
  }

  if (!showResumeDialog || availableSessions.length === 0) {
    return null;
  }

  return (
    <div className={cn("fixed inset-0 z-50 flex items-center justify-center p-4", className)}>
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={handleDismiss}
      />

      {/* Dialog */}
      <div className="relative bg-[var(--paper)] border border-[var(--border)] rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
        {/* Blueprint corner marks */}
        <div className="absolute -top-px -left-px w-4 h-4 border-t-2 border-l-2 border-[var(--blueprint)]" />
        <div className="absolute -top-px -right-px w-4 h-4 border-t-2 border-r-2 border-[var(--blueprint)]" />
        <div className="absolute -bottom-px -left-px w-4 h-4 border-b-2 border-l-2 border-[var(--blueprint)]" />
        <div className="absolute -bottom-px -right-px w-4 h-4 border-b-2 border-r-2 border-[var(--blueprint)]" />

        {/* Header */}
        <div className="p-6 border-b border-[var(--border)]">
          <h2 className="text-xl font-serif text-[var(--ink)]">Resume Onboarding</h2>
          <p className="text-sm text-[var(--muted)] mt-1">
            We found {availableSessions.length} incomplete session{availableSessions.length > 1 ? 's' : ''}
          </p>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
          {availableSessions.map((session) => {
            const progress = getProgressPercentage(session.completedSteps);
            const isSelected = selectedSession?.sessionId === session.sessionId;

            return (
              <div
                key={session.sessionId}
                className={cn(
                  "p-4 border rounded-lg cursor-pointer transition-all duration-200",
                  isSelected
                    ? "border-[var(--blueprint)] bg-blue-50"
                    : "border-[var(--border)] hover:border-[var(--blueprint)] hover:bg-[var(--paper)]"
                )}
                onClick={() => setSelectedSession(session)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-medium text-[var(--ink)]">
                        Session {session.sessionId.slice(-8)}
                      </h3>
                      <span className={cn(
                        "px-2 py-1 text-xs font-technical rounded",
                        session.status === 'active'
                          ? "bg-green-100 text-green-700"
                          : "bg-orange-100 text-orange-700"
                      )}>
                        {session.status === 'active' ? 'Active' : 'Abandoned'}
                      </span>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-[var(--muted)] font-technical">
                          Step {session.currentStep} of 23
                        </span>
                        <span className="text-[var(--muted)] font-technical">
                          {progress}% Complete
                        </span>
                      </div>

                      {/* Progress bar */}
                      <div className="w-full h-2 bg-[var(--border)] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-[var(--blueprint)] transition-all duration-300"
                          style={{ width: `${progress}%` }}
                        />
                      </div>

                      <div className="flex items-center justify-between text-xs text-[var(--muted)]">
                        <span className="font-technical">
                          Last activity: {formatLastActivity(session.lastActivity)}
                        </span>
                        <span className="font-technical">
                          {session.completedSteps.length} steps completed
                        </span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteSession(session.sessionId);
                    }}
                    className="ml-4 p-2 text-[var(--muted)] hover:text-red-500 transition-colors"
                  >
                    ✕
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Actions */}
        <div className="p-6 border-t border-[var(--border)] space-y-3">
          <div className="flex gap-3">
            <button
              onClick={() => selectedSession && handleResumeSession(selectedSession)}
              disabled={!selectedSession}
              className={cn(
                "flex-1 px-4 py-2 rounded font-technical transition-colors",
                selectedSession
                  ? "bg-[var(--blueprint)] text-white hover:bg-blue-600"
                  : "bg-[var(--paper)] text-[var(--muted)] border border-[var(--border)] cursor-not-allowed"
              )}
            >
              Resume Selected
            </button>

            <button
              onClick={handleStartNew}
              className="flex-1 px-4 py-2 rounded font-technical bg-[var(--paper)] text-[var(--ink)] border border-[var(--border)] hover:bg-gray-50 transition-colors"
            >
              Start New Session
            </button>
          </div>

          <button
            onClick={handleDismiss}
            className="w-full px-4 py-2 text-sm text-[var(--muted)] hover:text-[var(--ink)] font-technical transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

// Hook for session management
export function useOnboardingSession() {
  const [currentSession, setCurrentSession] = useState<SessionData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Create new session
  const createSession = (userId: string) => {
    const newSession: SessionData = {
      sessionId: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      userId,
      currentStep: 1,
      completedSteps: [],
      formData: {},
      lastActivity: new Date().toISOString(),
      status: 'active'
    };

    // Save to localStorage
    const localSessions = localStorage.getItem('onboarding_sessions');
    const sessions: SessionData[] = localSessions ? JSON.parse(localSessions) : [];
    sessions.push(newSession);
    localStorage.setItem('onboarding_sessions', JSON.stringify(sessions));

    setCurrentSession(newSession);
    return newSession;
  };

  // Update session progress
  const updateSession = (updates: Partial<SessionData>) => {
    if (!currentSession) return;

    const updatedSession = {
      ...currentSession,
      ...updates,
      lastActivity: new Date().toISOString()
    };

    // Update localStorage
    const localSessions = localStorage.getItem('onboarding_sessions');
    const sessions: SessionData[] = localSessions ? JSON.parse(localSessions) : [];
    const sessionIndex = sessions.findIndex(s => s.sessionId === currentSession.sessionId);

    if (sessionIndex >= 0) {
      sessions[sessionIndex] = updatedSession;
      localStorage.setItem('onboarding_sessions', JSON.stringify(sessions));
    }

    setCurrentSession(updatedSession);
  };

  // Complete session
  const completeSession = () => {
    if (!currentSession) return;

    updateSession({
      status: 'completed',
      currentStep: 23,
      completedSteps: Array.from({ length: 23 }, (_, i) => i + 1)
    });
  };

  return {
    currentSession,
    isLoading,
    createSession,
    updateSession,
    completeSession
  };
}
