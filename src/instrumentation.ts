export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('../sentry.server.config')
    
    // Validate environment variables on server startup
    const { validateEnvironment } = await import('./lib/env-validation')
    try {
      validateEnvironment()
    } catch (error) {
      console.error('Environment validation failed during instrumentation:', error)
    }
  }

  if (process.env.NEXT_RUNTIME === 'edge') {
    await import('../sentry.edge.config')
  }
}
