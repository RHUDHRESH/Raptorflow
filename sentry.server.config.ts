import * as Sentry from '@sentry/nextjs'
import { ProfilingIntegration } from '@sentry/profiling-node'

const SENTRY_DSN = process.env.SENTRY_DSN
const SENTRY_ENVIRONMENT = process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || 'development'

Sentry.init({
  dsn: SENTRY_DSN,
  environment: SENTRY_ENVIRONMENT,
  tracesSampleRate: SENTRY_ENVIRONMENT === 'production' ? 0.1 : 1.0,
  profilesSampleRate: SENTRY_ENVIRONMENT === 'production' ? 0.1 : 1.0,
  debug: false,
  integrations: [
    new ProfilingIntegration(),
    new Sentry.Integrations.Http({ tracing: true }),
  ],
  beforeSend(event, hint) {
    // Add request context
    if (event.request) {
      event.request.headers = {
        ...event.request.headers,
        // Remove sensitive headers
        authorization: undefined,
        cookie: undefined,
        'x-api-key': undefined,
      }
    }
    
    // Filter out certain errors
    if (event.exception) {
      const error = event.exception.values?.[0]
      
      // Ignore 404 errors
      if (error?.value?.includes('404')) {
        return null
      }
      
      // Ignore health check errors
      if (event.request?.url?.includes('/health') || event.request?.url?.includes('/api/health')) {
        return null
      }
    }
    
    // Add custom context
    event.tags = {
      ...event.tags,
      component: 'backend',
      runtime: 'nodejs',
    }
    
    // Add user context if available
    if (hint?.originalError instanceof Error && 'userId' in hint.originalError) {
      event.user = {
        id: (hint.originalError as any).userId,
      }
    }
    
    return event
  },
  ignoreErrors: [
    // Network errors
    'ECONNRESET',
    'ETIMEDOUT',
    'ENOTFOUND',
    // Database connection errors
    'database connection',
    'connection timeout',
    // Health check errors
    'health check failed',
  ],
  beforeSendTransaction(event) {
    // Filter out health check transactions
    if (event.transaction?.includes('/health') || event.transaction?.includes('/api/health')) {
      return null
    }
    
    // Filter out static assets
    if (event.transaction?.includes('/_next/static/')) {
      return null
    }
    
    return event
  },
  enabled: SENTRY_ENVIRONMENT !== 'test',
})

export { Sentry }
