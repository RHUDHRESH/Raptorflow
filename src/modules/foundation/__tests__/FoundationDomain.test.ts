import { describe, test, expect } from 'vitest';
import { FoundationDomain } from '../domain/FoundationDomain';

describe('Foundation Domain', () => {
  test('should validate correct foundation data', () => {
    const validData = {
      company_name: 'RaptorFlow',
      values: ['Innovation', 'Excellence'],
    };
    expect(FoundationDomain.validate(validData)).toBe(true);
  });

  test('should throw error if company_name is missing', () => {
    const invalidData = {
      mission: 'To rule the world',
    };
    expect(() => FoundationDomain.validate(invalidData)).toThrow('Required field missing: company_name');
  });

  test('should throw error if company_name is too long', () => {
    const invalidData = {
      company_name: 'A'.repeat(101),
    };
    expect(() => FoundationDomain.validate(invalidData)).toThrow('Company name too long (max 100 characters)');
  });

  test('should throw error if values is not an array', () => {
    const invalidData = {
      company_name: 'RaptorFlow',
      values: 'Innovation' as any,
    };
    expect(() => FoundationDomain.validate(invalidData)).toThrow('values must be a list');
  });
});
