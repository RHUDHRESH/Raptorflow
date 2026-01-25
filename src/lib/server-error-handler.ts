// Simple server-side error handling for API routes

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class DatabaseError extends Error {
  public cause?: any;

  constructor(message: string, originalError?: any) {
    super(message);
    this.name = 'DatabaseError';
    this.cause = originalError;
  }
}

export function createDatabaseError(operation: string, originalError: any): DatabaseError {
  return new DatabaseError(`Database operation failed: ${operation}`, originalError);
}

export function sanitizeInput(input: string): string {
  if (typeof input !== 'string') {
    throw new ValidationError('Input must be a string');
  }

  // Basic sanitization
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .substring(0, 1000); // Limit length
}

export function validateUuid(uuid: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}
