/**
 * Unified Auth Configuration
 * Centralized configuration for all authentication-related settings
 */

import { getBaseUrl, getAuthCallbackUrl, isDevelopment, isProduction, isVercelPreview } from './env-utils'
import { validateAuthConfig, getEnvironmentSummary } from './env-validation'

// =============================================================================
// AUTH CONFIGURATION EXPORTS
// =============================================================================

/**
 * Get complete auth configuration
 */
export function getAuthConfig() {
  return {
    // URLs
    baseUrl: getBaseUrl(),
    authCallbackUrl: getAuthCallbackUrl(),
    
    // Environment
    isDevelopment,
    isProduction,
    isVercelPreview,
    
    // OAuth providers
    oauth: {
      google: {
        enabled: !!(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET),
        clientId: process.env.GOOGLE_CLIENT_ID,
        redirectUrl: getAuthCallbackUrl()
      },
      github: {
        enabled: !!(process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET),
        clientId: process.env.GITHUB_CLIENT_ID,
        redirectUrl: getAuthCallbackUrl()
      },
      microsoft: {
        enabled: !!(process.env.MICROSOFT_CLIENT_ID && process.env.MICROSOFT_CLIENT_SECRET),
        clientId: process.env.MICROSOFT_CLIENT_ID,
        redirectUrl: getAuthCallbackUrl()
      },
      apple: {
        enabled: !!(process.env.APPLE_CLIENT_ID && process.env.APPLE_CLIENT_SECRET),
        clientId: process.env.APPLE_CLIENT_ID,
        redirectUrl: getAuthCallbackUrl()
      }
    },
    
    // Supabase
    supabase: {
      url: process.env.NEXT_PUBLIC_SUPABASE_URL,
      hasAnonKey: !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
    }
  }
}

/**
 * Get redirect URLs for Supabase configuration
 */
export function getSupabaseRedirectUrls(): string[] {
  const baseUrl = getBaseUrl()
  const urls = [
    `${baseUrl}/auth/callback`,
    `${baseUrl}/auth/reset-password`
  ]
  
  // Add localhost for development
  if (isDevelopment()) {
    urls.push('http://localhost:3000/auth/callback')
    urls.push('http://localhost:3000/auth/reset-password')
  }
  
  return Array.from(new Set(urls)) // Remove duplicates
}

/**
 * Validate and log auth configuration
 */
export function validateAndLogAuthConfig(): boolean {
  const validation = validateAuthConfig()
  const config = getAuthConfig()
  const envSummary = getEnvironmentSummary()
  
  console.log('🔐 Auth Configuration Summary:')
  console.log('Environment:', envSummary.environment)
  console.log('Base URL:', config.baseUrl)
  console.log('Auth Callback:', config.authCallbackUrl)
  console.log('Enabled OAuth Providers:', Object.entries(config.oauth)
    .filter(([_, provider]) => provider.enabled)
    .map(([name]) => name)
    .join(', ') || 'None')
  
  if (!validation.isValid) {
    console.error('❌ Auth configuration validation failed:')
    if (validation.missing.length > 0) {
      console.error('Missing:', validation.missing.join(', '))
    }
    if (validation.invalid.length > 0) {
      console.error('Invalid:', validation.invalid.join(', '))
    }
    return false
  }
  
  console.log('✅ Auth configuration is valid')
  return true
}

/**
 * Get OAuth configuration for specific provider
 */
export function getOAuthProviderConfig(provider: 'google' | 'github' | 'microsoft' | 'apple') {
  const config = getAuthConfig()
  return config.oauth[provider]
}

/**
 * Check if any OAuth provider is configured
 */
export function hasOAuthProviders(): boolean {
  const config = getAuthConfig()
  return Object.values(config.oauth).some(provider => provider.enabled)
}

/**
 * Get default OAuth provider (first enabled)
 */
export function getDefaultOAuthProvider(): 'google' | 'github' | 'microsoft' | 'apple' | null {
  const config = getAuthConfig()
  const providers: Array<'google' | 'github' | 'microsoft' | 'apple'> = ['google', 'github', 'microsoft', 'apple']
  
  for (const provider of providers) {
    if (config.oauth[provider].enabled) {
      return provider
    }
  }
  
  return null
}

/**
 * Environment-specific auth settings
 */
export const authSettings = {
  // Session settings
  sessionTimeout: 30 * 24 * 60 * 60 * 1000, // 30 days
  sessionRotationAge: 7 * 24 * 60 * 60 * 1000, // 7 days
  maxConcurrentSessions: 5,
  
  // Rate limiting
  rateLimit: {
    anonymous: 10, // requests per minute
    authenticated: 100,
    admin: 1000
  },
  
  // Security
  security: {
    maxLoginAttempts: 5,
    lockoutDuration: 15 * 60 * 1000, // 15 minutes
    passwordMinLength: 8,
    requireEmailVerification: isProduction()
  }
}
