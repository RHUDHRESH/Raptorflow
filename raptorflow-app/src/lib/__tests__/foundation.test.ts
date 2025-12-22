import { describe, it, expect, beforeEach, vi } from 'vitest';
import { brandKitSchema, saveBrandKit, getBrandKit } from '../foundation';

describe('Brand Kit Validation', () => {
  // ... existing tests ...
  it('should validate a correct brand kit', () => {
    const validData = {
      brandVoice: 'Professional and Strategic',
      positioning: 'RaptorFlow is the OS for founder marketing.',
      messagingPillars: ['Clarity', 'Control', 'Speed'],
    };
    const result = brandKitSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('should fail if brandVoice is missing', () => {
    const invalidData = {
      positioning: 'Value proposition here.',
      messagingPillars: ['Pillar 1'],
    };
    const result = brandKitSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });

  it('should fail if messagingPillars has more than 5 items', () => {
    const invalidData = {
      brandVoice: 'Voice',
      positioning: 'Positioning',
      messagingPillars: ['P1', 'P2', 'P3', 'P4', 'P5', 'P6'],
    };
    const result = brandKitSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });

  it('should fail if messagingPillars is empty', () => {
     const invalidData = {
      brandVoice: 'Voice',
      positioning: 'Positioning',
      messagingPillars: [],
    };
    const result = brandKitSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });
});

describe('Brand Kit Persistence', () => {
  beforeEach(() => {
    vi.stubGlobal('localStorage', {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    });
  });

  it('should save brand kit to localStorage', () => {
    const kit = {
      brandVoice: 'Bold',
      positioning: 'Leading OS',
      messagingPillars: ['Innovation'],
    };
    saveBrandKit(kit);
    expect(localStorage.setItem).toHaveBeenCalledWith('rf_brand_kit', JSON.stringify(kit));
  });

  it('should retrieve brand kit from localStorage', () => {
    const kit = {
      brandVoice: 'Bold',
      positioning: 'Leading OS',
      messagingPillars: ['Innovation'],
    };
    vi.mocked(localStorage.getItem).mockReturnValue(JSON.stringify(kit));
    const result = getBrandKit();
    expect(result).toEqual(kit);
  });

  it('should return null if no brand kit is found', () => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);
    const result = getBrandKit();
    expect(result).toBeNull();
  });
});
