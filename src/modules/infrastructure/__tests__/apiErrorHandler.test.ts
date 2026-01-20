import { describe, test, expect, vi } from 'vitest';
import { handleError, RaptorError } from '../services/apiErrorHandler';
import { RaptorErrorCodes } from '../services/apiResponse';

describe('API Error Handler', () => {
  // Mock Global Response since we are in Vitest/Node
  if (typeof Response === 'undefined') {
    (global as any).Response = {
      json: vi.fn((data, init) => ({
        json: async () => data,
        status: init.status,
      })),
    };
  } else {
    vi.spyOn(Response, 'json');
  }

  test('should handle RaptorError', async () => {
    const error = RaptorError.notFound('Custom Not Found');
    const response: any = handleError(error);

    expect(response.status).toBe(444);
    const body = await response.json();
    expect(body.success).toBe(false);
    expect(body.error.code).toBe(RaptorErrorCodes.NOT_FOUND);
    expect(body.error.message).toBe('Custom Not Found');
  });

  test('should handle generic Error', async () => {
    const error = new Error('Generic error');
    const response: any = handleError(error);

    expect(response.status).toBe(500);
    const body = await response.json();
    expect(body.success).toBe(false);
    expect(body.error.code).toBe(RaptorErrorCodes.INTERNAL_SERVER_ERROR);
  });
});
