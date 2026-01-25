/**
 * Centralized Error Handler
 * Provides consistent error handling across the application
 */

export enum ErrorType {
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  VALIDATION = 'VALIDATION',
  NETWORK = 'NETWORK',
  SERVER = 'SERVER',
  CLIENT = 'CLIENT',
  UNKNOWN = 'UNKNOWN'
}

export enum ErrorSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export interface AppError {
  type: ErrorType;
  severity: ErrorSeverity;
  message: string;
  code?: string;
  details?: Record<string, any>;
  requestId?: string;
  timestamp: string;
  stack?: string;
}

export class AuthenticationError extends Error {
  public readonly type = ErrorType.AUTHENTICATION;
  public readonly severity = ErrorSeverity.HIGH;
  public readonly code?: string;
  public readonly details?: Record<string, any>;
  public readonly requestId?: string;
  public readonly timestamp: string;

  constructor(
    message: string,
    details?: Record<string, any>,
    requestId?: string,
    code?: string
  ) {
    super(message);
    this.name = 'AuthenticationError';
    this.details = details;
    this.requestId = requestId;
    this.code = code;
    this.timestamp = new Date().toISOString();
  }
}

export class AuthorizationError extends Error {
  public readonly type = ErrorType.AUTHORIZATION;
  public readonly severity = ErrorSeverity.HIGH;
  public readonly code?: string;
  public readonly details?: Record<string, any>;
  public readonly requestId?: string;
  public readonly timestamp: string;

  constructor(
    message: string,
    details?: Record<string, any>,
    requestId?: string,
    code?: string
  ) {
    super(message);
    this.name = 'AuthorizationError';
    this.details = details;
    this.requestId = requestId;
    this.code = code;
    this.timestamp = new Date().toISOString();
  }
}

export class ValidationError extends Error {
  public readonly type = ErrorType.VALIDATION;
  public readonly severity = ErrorSeverity.MEDIUM;
  public readonly code?: string;
  public readonly details?: Record<string, any>;
  public readonly requestId?: string;
  public readonly timestamp: string;

  constructor(
    message: string,
    details?: Record<string, any>,
    requestId?: string,
    code?: string
  ) {
    super(message);
    this.name = 'ValidationError';
    this.details = details;
    this.requestId = requestId;
    this.code = code;
    this.timestamp = new Date().toISOString();
  }
}

export class NetworkError extends Error {
  public readonly type = ErrorType.NETWORK;
  public readonly severity = ErrorSeverity.MEDIUM;
  public readonly code?: string;
  public readonly details?: Record<string, any>;
  public readonly requestId?: string;
  public readonly timestamp: string;

  constructor(
    message: string,
    details?: Record<string, any>,
    requestId?: string,
    code?: string
  ) {
    super(message);
    this.name = 'NetworkError';
    this.details = details;
    this.requestId = requestId;
    this.code = code;
    this.timestamp = new Date().toISOString();
  }
}

export class ServerError extends Error {
  public readonly type = ErrorType.SERVER;
  public readonly severity = ErrorSeverity.HIGH;
  public readonly code?: string;
  public readonly details?: Record<string, any>;
  public readonly requestId?: string;
  public readonly timestamp: string;

  constructor(
    message: string,
    details?: Record<string, any>,
    requestId?: string,
    code?: string
  ) {
    super(message);
    this.name = 'ServerError';
    this.details = details;
    this.requestId = requestId;
    this.code = code;
    this.timestamp = new Date().toISOString();
  }
}

/**
 * Error Handler Class
 */
export class ErrorHandler {
  private static instance: ErrorHandler;

  private constructor() {}

  public static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  /**
   * Handle HTTP response errors
   */
  public handleHttpError(error: any, requestId?: string): AppError {
    if (error instanceof AuthenticationError ||
        error instanceof AuthorizationError ||
        error instanceof ValidationError ||
        error instanceof NetworkError ||
        error instanceof ServerError) {
      return error;
    }

    // Handle fetch errors
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return new NetworkError(
        'Network request failed',
        { originalError: error.message },
        requestId,
        'NETWORK_ERROR'
      );
    }

    // Handle 401 errors
    if (error.status === 401) {
      return new AuthenticationError(
        'Authentication required',
        { originalError: error.message },
        requestId,
        'AUTH_REQUIRED'
      );
    }

    // Handle 403 errors
    if (error.status === 403) {
      return new AuthorizationError(
        'Access denied',
        { originalError: error.message },
        requestId,
        'ACCESS_DENIED'
      );
    }

    // Handle 404 errors
    if (error.status === 404) {
      return new ValidationError(
        'Resource not found',
        { originalError: error.message },
        requestId,
        'NOT_FOUND'
      );
    }

    // Handle 500 errors
    if (error.status === 500) {
      return new ServerError(
        'Internal server error',
        { originalError: error.message },
        requestId,
        'SERVER_ERROR'
      );
    }

    // Default error handling
    return new Error(error.message || 'Unknown error') as AppError;
  }

  /**
   * Log error for debugging
   */
  public logError(error: AppError, context?: string): void {
    const logLevel = this.getLogLevel(error.severity);
    const logMessage = this.formatLogMessage(error, context);

    switch (logLevel) {
      case 'CRITICAL':
        console.error(`🚨 CRITICAL: ${logMessage}`);
        break;
      case 'HIGH':
        console.error(`🔴 HIGH: ${logMessage}`);
        break;
      case 'MEDIUM':
        console.warn(`🟡 MEDIUM: ${logMessage}`);
        break;
      case 'LOW':
        console.log(`🟢 LOW: ${logMessage}`);
        break;
      default:
        console.log(`ℹ️ INFO: ${logMessage}`);
    }
  }

  /**
   * Get appropriate log level for error severity
   */
  private getLogLevel(severity: ErrorSeverity): string {
    switch (severity) {
      case ErrorSeverity.CRITICAL:
        return 'CRITICAL';
      case ErrorSeverity.HIGH:
        return 'HIGH';
      case ErrorSeverity.MEDIUM:
        return 'MEDIUM';
      case ErrorSeverity.LOW:
        return 'LOW';
      default:
        return 'INFO';
    }
  }

  /**
   * Format error message for logging
   */
  private formatLogMessage(error: AppError, context?: string): string {
    const parts = [
      `[${error.type}]`,
      error.message,
      error.code ? `(${error.code})` : '',
      error.requestId ? `[${error.requestId}]` : '',
      context ? `Context: ${context}` : '',
      error.timestamp ? `Time: ${error.timestamp}` : ''
    ].filter(Boolean).join(' ');

    return parts;
  }

  /**
   * Create user-friendly error message
   */
  public getUserMessage(error: AppError): string {
    switch (error.type) {
      case ErrorType.AUTHENTICATION:
        return 'Please log in to continue';
      case ErrorType.AUTHORIZATION:
        return 'You don\'t have permission to do that';
      case ErrorType.VALIDATION:
        return 'Please check your input and try again';
      case ErrorType.NETWORK:
        return 'Connection problem. Please check your internet and try again';
      case ErrorType.SERVER:
        return 'Server problem. Please try again later';
      default:
        return 'Something went wrong. Please try again';
    }
  }

  /**
   * Determine if error should trigger a redirect
   */
  public shouldRedirect(error: AppError): boolean {
    return error.type === ErrorType.AUTHENTICATION ||
           error.type === ErrorType.AUTHORIZATION;
  }

  /**
   * Get redirect URL for error type
   */
  public getRedirectUrl(error: AppError): string {
    switch (error.type) {
      case ErrorType.AUTHENTICATION:
        return '/login';
      case ErrorType.AUTHORIZATION:
        return '/unauthorized';
      default:
        return '/error';
    }
  }
}

// Export singleton instance
export const errorHandler = ErrorHandler.getInstance();
