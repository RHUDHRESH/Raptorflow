import * as Sentry from '@sentry/nextjs'

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN || process.env.SENTRY_DSN
const SENTRY_ENVIRONMENT = process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || 'development'

Sentry.init({
  dsn: SENTRY_DSN,
  environment: SENTRY_ENVIRONMENT,
  tracesSampleRate: SENTRY_ENVIRONMENT === 'production' ? 0.1 : 1.0,
  debug: false,
  replaysOnErrorSampleRate: 1.0,
  replaysSessionSampleRate: 1.0,
  integrations: [],
  beforeSend(event: any) {
    // Recursive scrubber for PII
    const PII_PATTERNS = ['api_key', 'email', 'password', 'token', 'secret', 'auth', 'key'];
    const scrub = (obj: any) => {
      if (!obj || typeof obj !== 'object') return obj;
      Object.keys(obj).forEach(key => {
        if (PII_PATTERNS.some(p => key.toLowerCase().includes(p))) {
          obj[key] = '[FILTERED]';
        } else if (typeof obj[key] === 'object') {
          scrub(obj[key]);
        }
      });
      return obj;
    };

    // Scrub context and extra data
    if (event.contexts) scrub(event.contexts);
    if (event.extra) scrub(event.extra);
    if (event.request && event.request.data) scrub(event.request.data);

    // Filter out certain errors
    if (event.exception) {
      const error = event.exception.values?.[0]

      // Ignore network errors in development
      if (SENTRY_ENVIRONMENT === 'development' && error?.value?.includes('NetworkError')) {
        return null
      }

      // Ignore Chrome extension errors
      if (error?.value?.includes('Non-Error promise rejection captured')) {
        return null
      }
    }

    // Add custom context
    event.tags = {
      ...event.tags,
      component: 'frontend',
      framework: 'nextjs'
    }

    return event
  },
  ignoreErrors: [
    // Random plugins/extensions
    'top.GLOBALS',
    // Facebook borked
    'fb_xd_fragment',
    // Network errors
    'NetworkError',
    'Failed to fetch',
    // Chrome extensions
    /^chrome:\/\//i,
    /^chrome-extension:\/\//i,
  ],
  denyUrls: [
    // Chrome extensions
    /extensions\//i,
    /^chrome:\/\//i,
    /^chrome-extension:\/\//i,
    // Firefox extensions
    /^resource:\/\//i,
    /^moz-extension:\/\//i,
    // Third-party scripts
    /graph\.facebook\.com/i,
    /connect\.facebook\.net/i,
  ],
  enabled: SENTRY_ENVIRONMENT !== 'test',
})

export { Sentry }
export const onRouterTransitionStart = Sentry.captureRouterTransitionStart
