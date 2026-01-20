import { describe, test, expect } from 'vitest';
import { BrandKitDomain } from '../domain/BrandKitDomain';

describe('BrandKit Domain', () => {
  test('should generate a valid analysis prompt', () => {
    const samples = ['Hello world', 'RaptorFlow is great'];
    const prompt = BrandKitDomain.generateAnalysisPrompt(samples);

    expect(prompt).toContain('Analyze the following content samples');
    expect(prompt).toContain('Hello world');
    expect(prompt).toContain('RaptorFlow is great');
    expect(prompt).toContain('OUTPUT JSON format:');
  });

  test('should generate a valid apply prompt', () => {
    const content = 'Test content';
    const profile = {
      name: 'Professional',
      tone: 'Serious',
      style_rules: ['Be concise'],
      vocabulary: ['Optimal'],
      prohibited_patterns: ['Slang'],
    };
    const prompt = BrandKitDomain.generateApplyPrompt(content, profile);

    expect(prompt).toContain('Rewrite the following content');
    expect(prompt).toContain('Test content');
    expect(prompt).toContain('Professional');
    expect(prompt).toContain('Serious');
  });
});
