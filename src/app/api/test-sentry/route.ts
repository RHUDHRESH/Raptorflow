import { NextRequest, NextResponse } from 'next/server';
import * as Sentry from '@sentry/nextjs';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const shouldError = searchParams.get('error') === 'true';

    if (shouldError) {
      // Simulate an error with sensitive data
      const error = new Error('Sentry Test Error: PII Scrubbing Verification');
      Sentry.setContext('sensitive_data', {
        api_key: 'sk-test-1234567890abcdef',
        email: 'test-user@example.com',
        password: 'super-secret-password'
      });
      throw error;
    }

    return NextResponse.json({
      message: 'Sentry test route is active. Use ?error=true to trigger an error.',
      env: process.env.NODE_ENV,
      dsn_configured: !!process.env.NEXT_PUBLIC_SENTRY_DSN
    });
  } catch (error) {
    Sentry.captureException(error);
    return NextResponse.json(
      { error: 'Internal Server Error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
