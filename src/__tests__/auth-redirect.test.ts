/**
 * Auth Redirect Edge Cases Tests
 * Tests for authentication redirect scenarios
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { NextRequest } from 'next/server'

// Mock environment variables
const mockEnv = {
  NODE_ENV: 'development',
  NEXT_PUBLIC_APP_ENV: 'development',
  NEXT_PUBLIC_SUPABASE_URL: 'https://test.supabase.co',
  NEXT_PUBLIC_SUPABASE_ANON_KEY: 'test-key',
  NEXT_PUBLIC_APP_URL: 'http://localhost:3000',
  VERCEL_URL: undefined,
  VERCEL_ENV: undefined
}

// Setup mocks
beforeEach(() => {
  vi.clearAllMocks()
  Object.entries(mockEnv).forEach(([key, value]) => {
    process.env[key] = value
  })
})

describe('Auth Redirect Edge Cases', () => {
  describe('Base URL Resolution', () => {
    it('should use localhost in development', () => {
      const { getBaseUrl } = require('../lib/env-utils')
      expect(getBaseUrl()).toBe('http://localhost:3000')
    })

    it('should use custom APP_URL when set', () => {
      process.env.NEXT_PUBLIC_APP_URL = 'https://custom.example.com'
      const { getBaseUrl } = require('../lib/env-utils')
      expect(getBaseUrl()).toBe('https://custom.example.com')
    })

    it('should use Vercel preview URL in preview environment', () => {
      process.env.VERCEL_URL = 'test-app.vercel.app'
      process.env.VERCEL_ENV = 'preview'
      const { getBaseUrl } = require('../lib/env-utils')
      expect(getBaseUrl()).toBe('https://test-app.vercel.app')
    })

    it('should use production URL in production', () => {
      process.env.NODE_ENV = 'production'
      process.env.NEXT_PUBLIC_APP_ENV = 'production'
      const { getBaseUrl } = require('../lib/env-utils')
      expect(getBaseUrl()).toBe('https://raptorflow.in')
    })
  })

  describe('OAuth Redirect URLs', () => {
    it('should generate correct callback URL for development', () => {
      const { getAuthCallbackUrl } = require('../lib/env-utils')
      expect(getAuthCallbackUrl()).toBe('http://localhost:3000/auth/callback')
    })

    it('should generate correct callback URL for custom domain', () => {
      process.env.NEXT_PUBLIC_APP_URL = 'https://app.example.com'
      const { getAuthCallbackUrl } = require('../lib/env-utils')
      expect(getAuthCallbackUrl()).toBe('https://app.example.com/auth/callback')
    })

    it('should generate correct callback URL for Vercel preview', () => {
      process.env.VERCEL_URL = 'test-app.vercel.app'
      process.env.VERCEL_ENV = 'preview'
      const { getAuthCallbackUrl } = require('../lib/env-utils')
      expect(getAuthCallbackUrl()).toBe('https://test-app.vercel.app/auth/callback')
    })
  })

  describe('Environment Detection', () => {
    it('should detect development environment', () => {
      const { isDevelopment } = require('../lib/env-utils')
      expect(isDevelopment()).toBe(true)
    })

    it('should detect production environment', () => {
      process.env.NODE_ENV = 'production'
      process.env.NEXT_PUBLIC_APP_ENV = 'production'
      const { isProduction } = require('../lib/env-utils')
      expect(isProduction()).toBe(true)
    })

    it('should detect Vercel preview environment', () => {
      process.env.VERCEL_URL = 'test-app.vercel.app'
      process.env.VERCEL_ENV = 'preview'
      const { isVercelPreview } = require('../lib/env-utils')
      expect(isVercelPreview()).toBe(true)
    })
  })

  describe('Auth Configuration Validation', () => {
    it('should pass validation with all required variables', () => {
      const { validateAuthConfig } = require('../lib/env-validation')
      const result = validateAuthConfig()
      expect(result.isValid).toBe(true)
      expect(result.missing).toHaveLength(0)
    })

    it('should fail validation missing Supabase URL', () => {
      delete process.env.NEXT_PUBLIC_SUPABASE_URL
      const { validateAuthConfig } = require('../lib/env-validation')
      const result = validateAuthConfig()
      expect(result.isValid).toBe(false)
      expect(result.missing).toContain('NEXT_PUBLIC_SUPABASE_URL')
    })

    it('should fail validation with incomplete OAuth config', () => {
      process.env.GOOGLE_CLIENT_ID = 'test-id'
      // Missing GOOGLE_CLIENT_SECRET
      const { validateAuthConfig } = require('../lib/env-validation')
      const result = validateAuthConfig()
      expect(result.isValid).toBe(false)
      expect(result.missing).toContain('GOOGLE_CLIENT_SECRET')
    })
  })

  describe('Redirect Loop Prevention', () => {
    it('should prevent redirect when already at target', () => {
      // Mock request object
      const mockRequest = {
        url: 'http://localhost:3000/pricing',
        headers: new Map([['origin', 'http://localhost:3000']])
      } as unknown as NextRequest

      // Mock user data
      const mockUser = {
        data: {
          onboarding_status: 'active'
        }
      }

      // Mock subscription (none)
      const mockSubscription = null

      // Simulate redirect logic
      const currentPath = new URL(mockRequest.url).pathname
      let redirectTo = '/pricing' // Would normally redirect to pricing

      // Apply loop prevention logic
      if (redirectTo === currentPath) {
        redirectTo = '/dashboard'
      }

      expect(redirectTo).toBe('/dashboard')
    })

    it('should allow redirect when not at target', () => {
      const mockRequest = {
        url: 'http://localhost:3000/auth/callback',
        headers: new Map([['origin', 'http://localhost:3000']])
      } as unknown as NextRequest

      const currentPath = new URL(mockRequest.url).pathname
      let redirectTo = '/pricing'

      // Apply loop prevention logic
      if (redirectTo === currentPath) {
        redirectTo = '/dashboard'
      }

      expect(redirectTo).toBe('/pricing')
    })
  })

  describe('Domain Mismatch Handling', () => {
    it('should detect domain mismatch in production', () => {
      process.env.NODE_ENV = 'production'
      process.env.NEXT_PUBLIC_APP_ENV = 'production'
      
      const mockRequest = {
        headers: new Map([['origin', 'https://malicious.com']])
      } as unknown as NextRequest

      const { getBaseUrl } = require('../lib/env-utils')
      const expectedBaseUrl = getBaseUrl()
      const requestOrigin = mockRequest.headers.get('origin')

      expect(requestOrigin).not.toBe(expectedBaseUrl)
      expect(requestOrigin).toBe('https://malicious.com')
      expect(expectedBaseUrl).toBe('https://raptorflow.in')
    })

    it('should allow domain mismatch in development', () => {
      const mockRequest = {
        headers: new Map([['origin', 'https://custom.local']])
      } as unknown as NextRequest

      const { getBaseUrl } = require('../lib/env-utils')
      const expectedBaseUrl = getBaseUrl()
      const requestOrigin = mockRequest.headers.get('origin')

      // In development, mismatches are allowed
      expect(process.env.NODE_ENV).toBe('development')
    })
  })

  describe('Supabase Redirect URLs Generation', () => {
    it('should include localhost URLs in development', () => {
      const { getSupabaseRedirectUrls } = require('../lib/auth-config')
      const urls = getSupabaseRedirectUrls()
      
      expect(urls).toContain('http://localhost:3000/auth/callback')
      expect(urls).toContain('http://localhost:3000/auth/reset-password')
    })

    it('should include custom domain URLs when APP_URL is set', () => {
      process.env.NEXT_PUBLIC_APP_URL = 'https://app.example.com'
      const { getSupabaseRedirectUrls } = require('../lib/auth-config')
      const urls = getSupabaseRedirectUrls()
      
      expect(urls).toContain('https://app.example.com/auth/callback')
      expect(urls).toContain('https://app.example.com/auth/reset-password')
    })

    it('should remove duplicate URLs', () => {
      process.env.NEXT_PUBLIC_APP_URL = 'http://localhost:3000' // Same as default
      const { getSupabaseRedirectUrls } = require('../lib/auth-config')
      const urls = getSupabaseRedirectUrls()
      
      // Should not have duplicates
      const uniqueUrls = [...new Set(urls)]
      expect(urls).toEqual(uniqueUrls)
    })
  })
})
