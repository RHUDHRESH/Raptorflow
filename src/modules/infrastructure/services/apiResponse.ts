/**
 * RaptorFlow Bespoke API Standard
 * Utility for standardized success and error responses.
 */

export interface RaptorResponse<T = any> {
  success: boolean;
  data: T | null;
  error: {
    code: string;
    message: string;
    details?: any;
  } | null;
  meta: {
    timestamp: string;
    requestId?: string;
    [key: string]: any;
  };
}

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
};
