import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useOnboarding } from './useOnboarding';
import * as foundation from '@/lib/foundation';

// Mock foundation library
vi.mock('@/lib/foundation', () => ({
  emptyFoundation: {
    currentStep: 0,
    business: {},
    phase3: {},
    phase6: {},
  },
  saveFoundation: vi.fn(),
  loadFoundationDB: vi.fn().mockResolvedValue({
    currentStep: 0,
    business: { name: 'Test Corp' },
  }),
}));

describe('useOnboarding hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads data on mount', async () => {
    const { result } = renderHook(() => useOnboarding());

    // Initially loading
    expect(result.current.isLoading).toBe(true);

    // Wait for useEffect
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data.business.name).toBe('Test Corp');
  });

  it('updates data locally', async () => {
    const { result } = renderHook(() => useOnboarding());

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    act(() => {
      result.current.updateData((prev) => ({
        ...prev,
        business: { ...prev.business, name: 'New Name' },
      }));
    });

    expect(result.current.data.business.name).toBe('New Name');
  });

  it('saves progress to DB', async () => {
    const { result } = renderHook(() => useOnboarding());

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    await act(async () => {
      await result.current.saveProgress();
    });

    expect(foundation.saveFoundation).toHaveBeenCalled();
  });
});
