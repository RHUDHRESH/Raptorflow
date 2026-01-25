/**
 * Environment Variable Validation
 * Validates required environment variables at startup
 */

import { getBaseUrl } from './env-utils'

interface ValidationResult {
  isValid: boolean
  missing: string[]
  invalid: string[]
}

/**
 * Validate required Supabase environment variables
 */
export function validateSupabaseConfig(): ValidationResult {
  const required = [
    'NEXT_PUBLIC_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY'
  ]
  
  const missing: string[] = []
  const invalid: string[] = []
  
  for (const envVar of required) {
    const value = process.env[envVar]
    if (!value) {
      missing.push(envVar)
    } else if (envVar.includes('URL') && !isValidUrl(value)) {
      invalid.push(`${envVar} (invalid URL)`)
    }
  }
  
  return {
    isValid: missing.length === 0 && invalid.length === 0,
    missing,
    invalid
  }
}

/**
 * Validate OAuth provider environment variables
 */
export function validateOAuthConfig(): ValidationResult {
  const providers = ['google', 'github', 'microsoft', 'apple']
  const missing: string[] = []
  const invalid: string[] = []
  
  for (const provider of providers) {
    const clientId = process.env[`${provider.toUpperCase()}_CLIENT_ID`]
    const clientSecret = process.env[`${provider.toUpperCase()}_CLIENT_SECRET`]
    
    if (clientId && !clientSecret) {
      missing.push(`${provider.toUpperCase()}_CLIENT_SECRET`)
    } else if (!clientId && clientSecret) {
      missing.push(`${provider.toUpperCase()}_CLIENT_ID`)
    }
  }
  
  return {
    isValid: missing.length === 0 && invalid.length === 0,
    missing,
    invalid
  }
}

/**
 * Validate all external services environment variables
 */
export function validateServicesConfig(): ValidationResult {
  const missing: string[] = []
  
  // Sentry
  if (!process.env.SENTRY_DSN && !process.env.NEXT_PUBLIC_SENTRY_DSN) {
    missing.push('SENTRY_DSN')
  }
  
  // Resend
  if (!process.env.RESEND_API_KEY) {
    missing.push('RESEND_API_KEY')
  }
  
  // Upstash Redis
  if (!process.env.UPSTASH_REDIS_URL && !process.env.NEXT_PUBLIC_UPSTASH_REDIS_URL) {
    missing.push('UPSTASH_REDIS_URL')
  }
  if (!process.env.UPSTASH_REDIS_TOKEN && !process.env.NEXT_PUBLIC_UPSTASH_REDIS_TOKEN) {
    missing.push('UPSTASH_REDIS_TOKEN')
  }
  
  return {
    isValid: missing.length === 0,
    missing,
    invalid: []
  }
}

/**
 * Validate all auth-related environment variables
 */
export function validateAuthConfig(): ValidationResult {
  const supabase = validateSupabaseConfig()
  const oauth = validateOAuthConfig()
  const services = validateServicesConfig()
  
  const allMissing = [...supabase.missing, ...oauth.missing, ...services.missing]
  const allInvalid = [...supabase.invalid, ...oauth.invalid, ...services.invalid]
  
  return {
    isValid: supabase.isValid && oauth.isValid && services.isValid,
    missing: allMissing,
    invalid: allInvalid
  }
}

/**
 * Validate environment and log warnings/errors
 */
export function validateEnvironment(): void {
  const validation = validateAuthConfig()
  
  if (!validation.isValid) {
    console.error('❌ Environment validation failed:')
    
    if (validation.missing.length > 0) {
      console.error('Missing variables:', validation.missing.join(', '))
    }
    
    if (validation.invalid.length > 0) {
      console.error('Invalid variables:', validation.invalid.join(', '))
    }
    
    if (process.env.NODE_ENV === 'production') {
      throw new Error('Production environment validation failed')
    }
  } else {
    console.log('✅ Environment validation passed')
  }
}

/**
 * Check if string is a valid URL
 */
function isValidUrl(string: string): boolean {
  try {
    new URL(string)
    return true
  } catch {
    return false
  }
}

/**
 * Get environment summary for debugging
 */
export function getEnvironmentSummary(): Record<string, string> {
  return {
    environment: process.env.NODE_ENV || 'unknown',
    appEnv: process.env.NEXT_PUBLIC_APP_ENV || 'not set',
    baseUrl: getBaseUrl(),
    vercelUrl: process.env.VERCEL_URL || 'not set',
    vercelEnv: process.env.VERCEL_ENV || 'not set',
    hasSupabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ? 'yes' : 'no',
    hasSupabaseKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? 'yes' : 'no',
    hasGoogleOAuth: process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET ? 'yes' : 'no',
    hasSentry: process.env.SENTRY_DSN || process.env.NEXT_PUBLIC_SENTRY_DSN ? 'yes' : 'no',
    hasResend: process.env.RESEND_API_KEY ? 'yes' : 'no',
    hasRedis: process.env.UPSTASH_REDIS_URL || process.env.NEXT_PUBLIC_UPSTASH_REDIS_URL ? 'yes' : 'no',
    isVercelPreview: process.env.VERCEL_ENV === 'preview' ? 'yes' : 'no',
    isDevelopment: process.env.NODE_ENV === 'development' ? 'yes' : 'no',
    isProduction: process.env.NODE_ENV === 'production' ? 'yes' : 'no'
  }
}
