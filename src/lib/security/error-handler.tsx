"use client";

// Comprehensive error handling utilities
import React, { Component } from 'react';
import { NextResponse } from 'next/server';

// Error types
export enum ErrorType {
  VALIDATION = 'VALIDATION',
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  NOT_FOUND = 'NOT_FOUND',
  RATE_LIMIT = 'RATE_LIMIT',
  DATABASE = 'DATABASE',
  EXTERNAL_SERVICE = 'EXTERNAL_SERVICE',
  INTERNAL_SERVER = 'INTERNAL_SERVER',
  NETWORK = 'NETWORK',
  TIMEOUT = 'TIMEOUT',
  UNKNOWN = 'UNKNOWN'
}

// Error severity levels
export enum ErrorSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

// Custom error class
export class AppError extends Error {
  public readonly type: ErrorType;
  public readonly severity: ErrorSeverity;
  public readonly statusCode: number;
  public readonly details?: Record<string, any>;
  public readonly timestamp: Date;
  public readonly requestId?: string;
  public readonly userId?: string;

  constructor(
    message: string,
    type: ErrorType = ErrorType.INTERNAL_SERVER,
    statusCode: number = 500,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    details?: Record<string, any>,
    requestId?: string,
    userId?: string
  ) {
    super(message);
    this.type = type;
    this.severity = severity;
    this.statusCode = statusCode;
    this.details = details;
    this.timestamp = new Date();
    this.requestId = requestId;
    this.userId = userId;
    
    // Maintain proper stack trace
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, AppError);
    }
  }

  toJSON() {
    return {
      message: this.message,
      type: this.type,
      severity: this.severity,
      statusCode: this.statusCode,
      details: this.details,
      timestamp: this.timestamp,
      requestId: this.requestId,
      userId: this.userId,
      stack: this.stack
    };
  }
}

// Specific error types
export class ValidationError extends AppError {
  constructor(message: string, details?: Record<string, any>, requestId?: string) {
    super(message, ErrorType.VALIDATION, 400, ErrorSeverity.LOW, details, requestId);
  }
}

export class AuthenticationError extends AppError {
  constructor(message: string, details?: Record<string, any>, requestId?: string) {
    super(message, ErrorType.AUTHENTICATION, 401, ErrorSeverity.MEDIUM, details, requestId);
  }
}

export class AuthorizationError extends AppError {
  constructor(message: string, details?: Record<string, any>, requestId?: string) {
    super(message, ErrorType.AUTHORIZATION, 403, ErrorSeverity.MEDIUM, details, requestId);
  }
}

export class NotFoundError extends AppError {
  constructor(message: string, details?: Record<string, any>, requestId?: string) {
    super(message, ErrorType.NOT_FOUND, 404, ErrorSeverity.LOW, details, requestId);
  }
}

export class RateLimitError extends AppError {
  constructor(message: string, details?: Record<string, any>, requestId?: string) {
    super(message, ErrorType.RATE_LIMIT, 429, ErrorSeverity.MEDIUM, details, requestId);
  }
}

export class DatabaseError extends AppError {
  constructor(message: string, details?: Record<string, any>, requestId?: string) {
    super(message, ErrorType.DATABASE, 500, ErrorSeverity.HIGH, details, requestId);
  }
}

export class ExternalServiceError extends AppError {
  constructor(message: string, details?: Record<string, any>, requestId?: string) {
    super(message, ErrorType.EXTERNAL_SERVICE, 502, ErrorSeverity.HIGH, details, requestId);
  }
}

export class NetworkError extends AppError {
  constructor(message: string, details?: Record<string, any>, requestId?: string) {
    super(message, ErrorType.NETWORK, 503, ErrorSeverity.MEDIUM, details, requestId);
  }
}

export class TimeoutError extends AppError {
  constructor(message: string, details?: Record<string, any>, requestId?: string) {
    super(message, ErrorType.TIMEOUT, 408, ErrorSeverity.MEDIUM, details, requestId);
  }
}

// Error handler utility
export class ErrorHandler {
  private static instance: ErrorHandler;
  private errorLog: AppError[] = [];
  private maxLogSize = 1000;

  private constructor() {}

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  // Log error
  logError(error: AppError): void {
    this.errorLog.push(error);
    
    // Maintain log size
    if (this.errorLog.length > this.maxLogSize) {
      this.errorLog = this.errorLog.slice(-this.maxLogSize);
    }
    
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Application Error:', error.toJSON());
    }
    
    // In production, you would log to external service
    this.sendToExternalService(error);
  }

  // Handle error and return appropriate response
  handleError(error: unknown, requestId?: string, userId?: string): NextResponse {
    let appError: AppError;

    if (error instanceof AppError) {
      appError = error;
    } else if (error instanceof Error) {
      appError = new AppError(
        error.message,
        ErrorType.INTERNAL_SERVER,
        500,
        ErrorSeverity.MEDIUM,
        { originalError: error.name, stack: error.stack },
        requestId,
        userId
      );
    } else {
      appError = new AppError(
        'Unknown error occurred',
        ErrorType.UNKNOWN,
        500,
        ErrorSeverity.MEDIUM,
        { originalError: String(error) },
        requestId,
        userId
      );
    }

    // Log the error
    this.logError(appError);

    // Return appropriate response
    return this.createErrorResponse(appError);
  }

  // Create error response
  private createErrorResponse(error: AppError): NextResponse {
    const response = {
      error: {
        type: error.type,
        message: error.message,
        timestamp: error.timestamp,
        requestId: error.requestId
      }
    };

    // Include details in development
    if (process.env.NODE_ENV === 'development') {
      (response.error as any).details = error.details;
      (response.error as any).stack = error.stack;
    }

    return NextResponse.json(response, { status: error.statusCode });
  }

  // Send to external logging service
  private async sendToExternalService(error: AppError): Promise<void> {
    // In production, you would send to services like:
    // - Sentry
    // - Datadog
    // - Loggly
    // - Custom logging endpoint
    
    if (process.env.NODE_ENV === 'production' && error.severity === ErrorSeverity.CRITICAL) {
      try {
        // Example: Send to external service
        await fetch(process.env.ERROR_LOGGING_ENDPOINT || '', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${process.env.ERROR_LOGGING_TOKEN || ''}`
          },
          body: JSON.stringify(error.toJSON())
        });
      } catch (logError) {
        console.error('Failed to log error to external service:', logError);
      }
    }
  }

  // Get error statistics
  getErrorStats(): {
    total: number;
    byType: Record<ErrorType, number>;
    bySeverity: Record<ErrorSeverity, number>;
    recent: AppError[];
  } {
    const stats = {
      total: this.errorLog.length,
      byType: {} as Record<ErrorType, number>,
      bySeverity: {} as Record<ErrorSeverity, number>,
      recent: this.errorLog.slice(-10)
    };

    // Count by type
    Object.values(ErrorType).forEach(type => {
      stats.byType[type] = this.errorLog.filter(e => e.type === type).length;
    });

    // Count by severity
    Object.values(ErrorSeverity).forEach(severity => {
      stats.bySeverity[severity] = this.errorLog.filter(e => e.severity === severity).length;
    });

    return stats;
  }

  // Get errors by time range
  getErrorsByTimeRange(startTime: Date, endTime: Date): AppError[] {
    return this.errorLog.filter(error => 
      error.timestamp >= startTime && error.timestamp <= endTime
    );
  }

  // Clear error log
  clearLog(): void {
    this.errorLog = [];
  }
}

// Error handling middleware helper
export function withErrorHandling(
  handler: (req: Request, context?: any) => Promise<Response>
) {
  return async (req: Request, context?: any): Promise<Response> => {
    try {
      return await handler(req, context);
    } catch (error) {
      const requestId = req.headers.get('x-request-id') || undefined;
      const userId = req.headers.get('x-user-id') || undefined;
      
      const errorHandler = ErrorHandler.getInstance();
      const errorResponse = errorHandler.handleError(error, requestId, userId);
      
      return errorResponse;
    }
  };
}

// Async error wrapper
export function asyncErrorWrapper<T extends any[], R>(
  fn: (...args: T) => Promise<R>
) {
  return (...args: T): Promise<R> => {
    return fn(...args).catch((error) => {
      const errorHandler = ErrorHandler.getInstance();
      throw errorHandler.handleError(error);
    });
  };
}

// Error boundary for React components
export interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: any;
}

export class ErrorBoundary extends Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: any): void {
    this.setState({ error, errorInfo });
    
    const errorHandler = ErrorHandler.getInstance();
    errorHandler.logError(new AppError(
      error.message,
      ErrorType.INTERNAL_SERVER,
      500,
      ErrorSeverity.HIGH,
      { errorInfo }
    ));
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', border: '1px solid #ff0000', borderRadius: '8px' }}>
          <h2>Something went wrong</h2>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo.componentStack}
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

// Validation error helper
export function createValidationError(
  field: string,
  message: string,
  value?: any
): ValidationError {
  return new ValidationError(
    `Validation failed for ${field}: ${message}`,
    { field, value }
  );
}

// Database error helper
export function createDatabaseError(
  operation: string,
  originalError: any,
  requestId?: string
): DatabaseError {
  return new DatabaseError(
    `Database operation failed: ${operation}`,
    { operation, originalError: originalError.message || String(originalError) },
    requestId
  );
}

// External service error helper
export function createExternalServiceError(
  service: string,
  operation: string,
  originalError: any,
  requestId?: string
): ExternalServiceError {
  return new ExternalServiceError(
    `External service error: ${service} - ${operation}`,
    { service, operation, originalError: originalError.message || String(originalError) },
    requestId
  );
}

// Timeout error helper
export function createTimeoutError(
  operation: string,
  timeout: number,
  requestId?: string
): TimeoutError {
  return new TimeoutError(
    `Operation timed out: ${operation} after ${timeout}ms`,
    { operation, timeout },
    requestId
  );
}

// Rate limit error helper
export function createRateLimitError(
  limit: number,
  windowMs: number,
  requestId?: string
): RateLimitError {
  return new RateLimitError(
    `Rate limit exceeded: ${limit} requests per ${windowMs}ms`,
    { limit, windowMs },
    requestId
  );
}

// Export singleton instance
export const errorHandler = ErrorHandler.getInstance();

export default errorHandler;
