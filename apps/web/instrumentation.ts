import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  // Set tracesSampleRate to 1.0 to capture all
  tracesSampleRate: 1.0,
  // Set profileSessionSampleRate to 1.0 to profile all sessions
  profileSessionSampleRate: 1.0,
  // Enable debug logging in development
  debug: process.env.NODE_ENV === "development",
});