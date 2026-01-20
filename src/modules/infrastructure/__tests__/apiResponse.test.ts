import { describe, test, expect } from 'vitest';
import { createSuccessResponse, createErrorResponse, RaptorErrorCodes } from '../services/apiResponse';

describe('API Response Utility', () => {
  test('should create a success response', () => {
    const data = { id: 1, name: 'Test' };
    const response = createSuccessResponse(data);

    expect(response.success).toBe(true);
    expect(response.data).toEqual(data);
    expect(response.error).toBeNull();
    expect(response.meta.timestamp).toBeDefined();
  });

  test('should create an error response', () => {
    const message = 'Something went wrong';
    const code = RaptorErrorCodes.INTERNAL_SERVER_ERROR;
    const details = { stack: '...' };
    const response = createErrorResponse(code, message, details);

    expect(response.success).toBe(false);
    expect(response.data).toBeNull();
    expect(response.error).toEqual({
      code,
      message,
      details,
    });
    expect(response.meta.timestamp).toBeDefined();
  });

  test('should include custom meta in success response', () => {
    const data = 'ok';
    const meta = { requestId: '123' };
    const response = createSuccessResponse(data, meta);

    expect(response.meta.requestId).toBe('123');
  });
});
