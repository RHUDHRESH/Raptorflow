import * as Sentry from "@sentry/nextjs";
import {
  sentryEnvironment,
  sentryPublicDsn,
  sentryRelease,
} from "./src/lib/sentry";

Sentry.init({
  dsn: sentryPublicDsn,
  environment: sentryEnvironment,
  release: sentryRelease,
  integrations: [Sentry.browserTracingIntegration()],
  tracesSampleRate: 1.0,
  profileSessionSampleRate: 1.0,
  sendDefaultPii: false,
  debug: process.env.NODE_ENV === "development",
});

export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
