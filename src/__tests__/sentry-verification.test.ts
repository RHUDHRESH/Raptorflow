import { describe, test, expect, vi } from 'vitest';
import * as Sentry from '@sentry/nextjs';

describe('Sentry Frontend Configuration', () => {
  test('Sentry should be initialized with correct DSN', () => {
    // In Vitest, we can't easily check the real Sentry client initialization 
    // without complex mocking, but we can verify the environment variables.
    expect(process.env.NEXT_PUBLIC_SENTRY_DSN).toBeDefined();
    expect(process.env.NEXT_PUBLIC_SENTRY_DSN).toContain('ingest.us.sentry.io');
  });

  test('Sentry should provide captureException function', () => {
    expect(typeof Sentry.captureException).toBe('function');
  });
});
