/**
 * React hooks for API integration
 * Provides easy-to-use hooks for common API operations
 * Aligned with the RaptorFlow Bespoke API Standard.
 */

import { useState, useEffect, useCallback } from 'react';
import { RaptorResponse } from '../../modules/infrastructure/types/api';

// Generic hook for API requests
export function useApi<T>(
  apiCall: () => Promise<RaptorResponse<T>>
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ code: string; message: string } | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiCall();
      if (response.success) {
        setData(response.data);
      } else {
        setError(response.error);
      }
    } catch (err) {
      setError({ 
        code: 'NETWORK_ERROR', 
        message: err instanceof Error ? err.message : 'An error occurred' 
      });
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

// Hook for mutations (POST, PUT, DELETE)
export function useApiMutation<T, P = unknown>(
  apiCall: (params: P) => Promise<RaptorResponse<T>>
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ code: string; message: string } | null>(null);
  const [data, setData] = useState<T | null>(null);

  const mutate = useCallback(async (params: P) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiCall(params);
      if (response.success) {
        setData(response.data);
        return response;
      } else {
        const err = response.error || { code: 'UNKNOWN_ERROR', message: 'Mutation failed' };
        setError(err);
        throw err;
      }
    } catch (err) {
      const apiError = (err as any).code 
        ? err as { code: string; message: string }
        : { code: 'NETWORK_ERROR', message: err instanceof Error ? err.message : 'Unknown error' };
      
      setError(apiError);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  return { mutate, loading, error, data, reset: () => setData(null) };
}