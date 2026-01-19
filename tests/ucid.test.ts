import { test, expect } from '@playwright/test';
import { generateUCID } from '../src/lib/utils';

test.describe('UCID Utility', () => {
  test('generates correct format for sequence number', () => {
    const currentYear = new Date().getFullYear();
    const ucid = generateUCID(1);
    expect(ucid).toBe(`RF-${currentYear}-0001`);
  });

  test('pads sequence numbers with leading zeros', () => {
    const currentYear = new Date().getFullYear();
    const ucid = generateUCID(123);
    expect(ucid).toBe(`RF-${currentYear}-0123`);
  });

  test('handles large sequence numbers', () => {
    const currentYear = new Date().getFullYear();
    const ucid = generateUCID(9999);
    expect(ucid).toBe(`RF-${currentYear}-9999`);
  });
});
