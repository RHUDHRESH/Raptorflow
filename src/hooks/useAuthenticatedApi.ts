"use client";

import { useAuth } from '@/components/auth/AuthProvider';
import { useRouter } from 'next/navigation';
import { errorHandler, AppError, AuthenticationError, AuthorizationError, ValidationError, NetworkError, ServerError } from '@/lib/errorHandler';

/**
 * Hook for making authenticated API calls
 * Ensures user is authenticated before making requests
 * Handles 401 responses by redirecting to login
 */
export function useAuthenticatedApi() {
  const { user, isAuthenticated } = useAuth();
  const router = useRouter();

  const authenticatedFetch = async (url: string, options?: RequestInit) => {
    // Check authentication before making request
    if (!isAuthenticated || !user) {
      router.push('/login');
      throw new Error('User not authenticated');
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      // Handle 401 responses
      if (response.status === 401) {
        router.push('/login');
        throw new Error('Session expired');
      }

      // Handle 403 responses
      if (response.status === 403) {
        router.push('/unauthorized');
        throw new Error('Access denied');
      }

      // Handle other HTTP errors
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error = errorHandler.handleHttpError({
          status: response.status,
          message: errorData.error || `HTTP ${response.status}`,
          ...errorData
        });

        // Log error for debugging
        errorHandler.logError(error, `API call to ${url}`);

        // Redirect if needed
        if (errorHandler.shouldRedirect(error)) {
          router.push(errorHandler.getRedirectUrl(error));
        }

        throw error;
      }

      return response;
    } catch (error) {
      // If it's already an AppError, re-throw
      if (error instanceof Error &&
          (error instanceof AuthenticationError ||
           error instanceof AuthorizationError ||
           error instanceof ValidationError ||
           error instanceof NetworkError ||
           error instanceof ServerError)) {
        throw error;
      }

      // Handle network errors
      if (error instanceof Error && error.message.includes('fetch')) {
        const networkError = errorHandler.handleHttpError(error);
        errorHandler.logError(networkError, `API call to ${url}`);
        throw networkError;
      }

      // For other errors, ensure they're thrown properly
      throw error;
    }
  };

  return { authenticatedFetch, user, isAuthenticated };
}
