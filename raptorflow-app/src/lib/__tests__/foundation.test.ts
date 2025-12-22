import { describe, it, expect } from 'vitest';
import { brandKitSchema } from '../foundation';

describe('Brand Kit Validation', () => {
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
