import { RaptorResponse } from '../types/api';

/**
 * RaptorFlow Bespoke API Standard
 * Utility for standardized success and error responses.
 */

/**
 * Creates a standardized success response.
 */
export function createSuccessResponse<T>(data: T, meta: Record<string, any> = {}): RaptorResponse<T> {
  return {
    success: true,
    data,
    error: null,
    meta: {
      timestamp: new Date().toISOString(),
      ...meta,
    },
  };
}

/**
 * Creates a standardized error response.
 */
export function createErrorResponse(
  code: string,
  message: string,
  details: any = null,
  meta: Record<string, any> = {}
): RaptorResponse<null> {
  return {
    success: false,
    data: null,
    error: {
      code,
      message,
      details,
    },
    meta: {
      timestamp: new Date().toISOString(),
      ...meta,
    },
  };
}

/**
 * Common Error Codes
 */
export const RaptorErrorCodes = {
  BAD_REQUEST: 'BAD_REQUEST',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  INTERNAL_SERVER_ERROR: 'INTERNAL_SERVER_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  UNPROCESSABLE_ENTITY: 'UNPROCESSABLE_ENTITY',
  AI_ENGINE_ERROR: 'AI_ENGINE_ERROR',
  RATE_LIMITED: 'RATE_LIMITED',
  NETWORK_ERROR: 'NETWORK_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
};

export const RaptorErrorMessages: Record<string, string> = {
  [RaptorErrorCodes.BAD_REQUEST]: 'The request could not be processed.',
  [RaptorErrorCodes.UNAUTHORIZED]:
    'Your session has expired or you do not have permission. Please log in again.',
  [RaptorErrorCodes.FORBIDDEN]: 'You do not have access to this resource.',
  [RaptorErrorCodes.NOT_FOUND]: 'The requested item was not found.',
  [RaptorErrorCodes.INTERNAL_SERVER_ERROR]: 'A system error occurred. We are working on a fix.',
  [RaptorErrorCodes.VALIDATION_ERROR]: 'Please check your input and try again.',
  [RaptorErrorCodes.UNPROCESSABLE_ENTITY]: 'The request could not be completed as provided.',
  [RaptorErrorCodes.AI_ENGINE_ERROR]:
    'The Intelligence Engine encountered an issue. Our team has been notified.',
  [RaptorErrorCodes.RATE_LIMITED]: 'Too many requests. Please try again shortly.',
  [RaptorErrorCodes.NETWORK_ERROR]:
    'Unable to connect to the server. Please check your internet connection.',
  [RaptorErrorCodes.UNKNOWN_ERROR]: 'An unexpected error occurred.',
};
