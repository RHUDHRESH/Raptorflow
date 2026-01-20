/**
 * @vitest-environment jsdom
 */
import { describe, test, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useApi } from '../lib/api/useApi';

describe('useApi Hook', () => {
  test('should handle success response', async () => {
    const mockCall = vi.fn().mockResolvedValue({
      success: true,
      data: { id: 1 },
      error: null,
      meta: { timestamp: '' }
    });

    const { result } = renderHook(() => useApi(mockCall));

    expect(result.current.loading).toBe(true);

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.data).toEqual({ id: 1 });
    expect(result.current.error).toBeNull();
  });

  test('should handle error response', async () => {
    const mockCall = vi.fn().mockResolvedValue({
      success: false,
      data: null,
      error: { code: 'TEST_ERROR', message: 'Failed' },
      meta: { timestamp: '' }
    });

    const { result } = renderHook(() => useApi(mockCall));

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.data).toBeNull();
    expect(result.current.error).toEqual({ code: 'TEST_ERROR', message: 'Failed' });
  });
});
