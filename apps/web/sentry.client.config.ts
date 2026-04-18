import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  // Enable debug logging in development
  debug: process.env.NODE_ENV === "development",
  // Set environment
  environment: process.env.NODE_ENV,
});