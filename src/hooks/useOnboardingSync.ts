/**
 * Onboarding Sync Hook - Frontend synchronization with backend
 * Provides real-time state management and WebSocket connection.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import { useAuth } from '@/components/auth/AuthProvider';

export interface OnboardingStep {
  id: string;
  name: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'failed' | 'skipped';
  started_at?: number;
  completed_at?: number;
  error_message?: string;
  retry_count?: number;
  result_data?: any;
}

export interface OnboardingState {
  workspace_id: string;
  total_steps: number;
  completed_steps: number;
  failed_steps: number;
  in_progress_steps: number;
  progress_percentage: number;
  current_step?: string;
  next_step?: string;
  steps: Record<string, OnboardingStep>;
  is_locked: boolean;
}

export interface StepExecutionResult {
  success: boolean;
  step_id: string;
  result?: any;
  next_step?: string;
  progress?: OnboardingState;
  error?: string;
  validation_errors?: string[];
}

export class OnboardingSyncError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'OnboardingSyncError';
  }
}

export const useOnboardingSync = () => {
  const { workspace } = useWorkspace();
  const { user } = useAuth();

  const [state, setState] = useState<OnboardingState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const websocketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (!workspace?.id || !user) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/api/v1/onboarding/ws/${workspace.id}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Onboarding WebSocket connected');
      setIsConnected(true);
      setError(null);

      // Start heartbeat
      heartbeatIntervalRef.current = setInterval(() => {
        ws.send(JSON.stringify({ type: 'ping' }));
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);

        switch (message.type) {
          case 'step_completed':
            console.log('Step completed:', message.step_id);
            // Refresh state
            fetchState();
            break;

          case 'step_reset':
            console.log('Step reset:', message.step_id);
            fetchState();
            break;

          case 'status_update':
            setState(message.data);
            break;

          case 'pong':
            // Heartbeat response
            break;

          default:
            console.log('Unknown WebSocket message:', message);
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    ws.onclose = (event) => {
      console.log('Onboarding WebSocket disconnected:', event.code, event.reason);
      setIsConnected(false);

      // Clear heartbeat
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }

      // Reconnect after delay
      if (event.code !== 1000) { // Not a normal closure
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 5000);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('WebSocket connection error');
    };

    websocketRef.current = ws;
  }, [workspace?.id, user]);

  // Fetch current state
  const fetchState = useCallback(async () => {
    if (!workspace?.id) return;

    try {
      setLoading(true);
      const response = await fetch(`/api/v1/onboarding/status?workspace_id=${workspace.id}`, {
        headers: {
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setState(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching onboarding state:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch state');
    } finally {
      setLoading(false);
    }
  }, [workspace?.id, user]);

  // Execute step
  const executeStep = useCallback(async (stepId: string, data: any): Promise<StepExecutionResult> => {
    if (!workspace?.id) {
      throw new OnboardingSyncError('No workspace selected', 'NO_WORKSPACE');
    }

    try {
      const response = await fetch('/api/v1/onboarding/step', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
        body: JSON.stringify({
          step_id: stepId,
          data,
          workspace_id: workspace.id,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new OnboardingSyncError(
          errorData.detail || `HTTP ${response.status}`,
          errorData.code || 'HTTP_ERROR',
          errorData
        );
      }

      const result = await response.json();

      // Update local state
      if (result.progress) {
        setState(result.progress);
      }

      return result;
    } catch (err) {
      if (err instanceof OnboardingSyncError) {
        throw err;
      }
      throw new OnboardingSyncError(
        err instanceof Error ? err.message : 'Failed to execute step',
        'EXECUTION_ERROR'
      );
    }
  }, [workspace?.id, user]);

  // Resume onboarding
  const resumeOnboarding = useCallback(async () => {
    if (!workspace?.id) {
      throw new OnboardingSyncError('No workspace selected', 'NO_WORKSPACE');
    }

    try {
      const response = await fetch('/api/v1/onboarding/resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
        body: JSON.stringify({
          workspace_id: workspace.id,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new OnboardingSyncError(
          errorData.detail || `HTTP ${response.status}`,
          errorData.code || 'HTTP_ERROR'
        );
      }

      const result = await response.json();

      // Update local state
      if (result.progress) {
        setState(result.progress);
      }

      return result;
    } catch (err) {
      if (err instanceof OnboardingSyncError) {
        throw err;
      }
      throw new OnboardingSyncError(
        err instanceof Error ? err.message : 'Failed to resume onboarding',
        'RESUME_ERROR'
      );
    }
  }, [workspace?.id, user]);

  // Get next step
  const getNextStep = useCallback(async () => {
    if (!workspace?.id) {
      throw new OnboardingSyncError('No workspace selected', 'NO_WORKSPACE');
    }

    try {
      const response = await fetch(`/api/v1/onboarding/next-step?workspace_id=${workspace.id}`, {
        headers: {
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      throw new OnboardingSyncError(
        err instanceof Error ? err.message : 'Failed to get next step',
        'NEXT_STEP_ERROR'
      );
    }
  }, [workspace?.id, user]);

  // Get step data
  const getStepData = useCallback(async (stepId: string) => {
    if (!workspace?.id) {
      throw new OnboardingSyncError('No workspace selected', 'NO_WORKSPACE');
    }

    try {
      const response = await fetch(`/api/v1/onboarding/step-data/${stepId}?workspace_id=${workspace.id}`, {
        headers: {
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      throw new OnboardingSyncError(
        err instanceof Error ? err.message : 'Failed to get step data',
        'STEP_DATA_ERROR'
      );
    }
  }, [workspace?.id, user]);

  // Reset step (for debugging)
  const resetStep = useCallback(async (stepId: string) => {
    if (!workspace?.id) {
      throw new OnboardingSyncError('No workspace selected', 'NO_WORKSPACE');
    }

    try {
      const response = await fetch('/api/v1/onboarding/reset-step', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
        body: JSON.stringify({
          step_id: stepId,
          workspace_id: workspace.id,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // Refresh state
      await fetchState();

      return await response.json();
    } catch (err) {
      throw new OnboardingSyncError(
        err instanceof Error ? err.message : 'Failed to reset step',
        'RESET_ERROR'
      );
    }
  }, [workspace?.id, user, fetchState]);

  // Check sync status
  const checkSync = useCallback(async () => {
    if (!workspace?.id) {
      throw new OnboardingSyncError('No workspace selected', 'NO_WORKSPACE');
    }

    try {
      const response = await fetch(`/api/v1/onboarding/sync-check?workspace_id=${workspace.id}`, {
        headers: {
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      throw new OnboardingSyncError(
        err instanceof Error ? err.message : 'Failed to check sync',
        'SYNC_CHECK_ERROR'
      );
    }
  }, [workspace?.id, user]);

  // Initialize connection and fetch state
  useEffect(() => {
    if (workspace?.id && user) {
      fetchState();
      connectWebSocket();
    }

    return () => {
      // Cleanup
      if (websocketRef.current) {
        websocketRef.current.close(1000, 'Component unmounted');
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
    };
  }, [workspace?.id, user, fetchState, connectWebSocket]);

  return {
    // State
    state,
    loading,
    error,
    isConnected,

    // Actions
    executeStep,
    resumeOnboarding,
    getNextStep,
    getStepData,
    resetStep,
    checkSync,
    fetchState,

    // Utilities
    clearError: () => setError(null),
    reconnect: () => connectWebSocket(),
  };
};
