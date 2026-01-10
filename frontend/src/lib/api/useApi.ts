/**
 * React hooks for API integration
 * Provides easy-to-use hooks for common API operations
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient, ApiResponse, Agent, Skill, Tool, Workflow } from './client';

// Generic hook for API requests
export function useApi<T>(
  apiCall: () => Promise<ApiResponse<T>>
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiCall();
      if (response.status === 'success' || response.status === 'active') {
        setData(response.data as T);
      } else {
        setError(response.message || 'API request failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

// Specific hooks for different endpoints
export function useAgents() {
  return useApi<Agent[]>(() => apiClient.getAgents());
}

export function useSkills() {
  return useApi<Skill[]>(() => apiClient.getSkills());
}

export function useTools() {
  return useApi<Tool[]>(() => apiClient.getTools());
}

export function useWorkflows() {
  return useApi<Workflow[]>(() => apiClient.getWorkflows());
}

export function useSystemHealth() {
  return useApi(() => apiClient.getHealth());
}

export function useSystemInfo() {
  return useApi(() => apiClient.getSystemInfo());
}

// Hook for real-time data updates
export function useRealTimeData<T>(
  apiCall: () => Promise<ApiResponse<T>>,
  intervalMs: number = 30000
) {
  const { data, loading, error, refetch } = useApi(apiCall);

  useEffect(() => {
    const interval = setInterval(refetch, intervalMs);
    return () => clearInterval(interval);
  }, [refetch, intervalMs]);

  return { data, loading, error, refetch };
}

// Hook for mutations (POST, PUT, DELETE)
export function useApiMutation<T, P = unknown>(
  apiCall: (params: P) => Promise<ApiResponse<T>>
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<T | null>(null);

  const mutate = useCallback(async (params: P) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiCall(params);
      if (response.status === 'success') {
        setData(response.data as T);
        return response;
      } else {
        setError(response.message || 'Mutation failed');
        throw new Error(response.message || 'Mutation failed');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  return { mutate, loading, error, data, reset: () => setData(null) };
}
