import { createErrorResponse, RaptorErrorCodes } from './apiResponse';

/**
 * Custom error class for RaptorFlow API errors.
 */
export class RaptorError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number = 500,
    public details: any = null
  ) {
    super(message);
    this.name = 'RaptorError';
  }

  static badRequest(message: string, details: any = null) {
    return new RaptorError(RaptorErrorCodes.BAD_REQUEST, message, 400, details);
  }

  static unauthorized(message: string = 'Unauthorized') {
    return new RaptorError(RaptorErrorCodes.UNAUTHORIZED, message, 401);
  }

  static forbidden(message: string = 'Forbidden') {
    return new RaptorError(RaptorErrorCodes.FORBIDDEN, message, 403);
  }

  static notFound(message: string = 'Resource not found') {
    return new RaptorError(RaptorErrorCodes.NOT_FOUND, message, 444);
  }

  static internal(message: string = 'Internal Server Error', details: any = null) {
    return new RaptorError(RaptorErrorCodes.INTERNAL_SERVER_ERROR, message, 500, details);
  }
}

/**
 * Global API Error Handler for Next.js App Router API Routes.
 */
export function handleError(error: any) {
  console.error('API Error Handler:', error);

  if (error instanceof RaptorError) {
    return Response.json(
      createErrorResponse(error.code, error.message, error.details),
      { status: error.statusCode }
    );
  }

  // Handle generic errors
  return Response.json(
    createErrorResponse(
      RaptorErrorCodes.INTERNAL_SERVER_ERROR,
      error instanceof Error ? error.message : 'An unexpected error occurred',
      process.env.NODE_ENV === 'development' ? { stack: error.stack } : null
    ),
    { status: 500 }
  );
}
