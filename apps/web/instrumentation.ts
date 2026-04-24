import * as Sentry from "@sentry/nextjs";
import { sentryEnvironment, sentryRelease, sentryServerDsn } from "./src/lib/sentry";

Sentry.init({
  dsn: sentryServerDsn,
  environment: sentryEnvironment,
  release: sentryRelease,
  tracesSampleRate: 1.0,
  profileSessionSampleRate: 1.0,
  debug: process.env.NODE_ENV === "development",
});

export const onRequestError = Sentry.captureRequestError;
