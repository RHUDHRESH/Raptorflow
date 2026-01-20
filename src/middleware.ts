import { createServerClient } from '@supabase/ssr'
import { NextResponse, NextRequest } from 'next/server'
import type { CookieOptions } from '@supabase/ssr'
import { authRateLimit, apiRateLimit, generalRateLimit } from './middleware/rate-limiter-fixed'
import { getBaseUrl } from './lib/env-utils'

// Type definitions for middleware
interface CookieToSet {
  name: string
  value: string
  options?: {
    domain?: string
    expires?: Date
    httpOnly?: boolean
    maxAge?: number
    path?: string
    sameSite?: 'lax' | 'strict' | 'none'
    secure?: boolean
  }
}

// Security configuration
const SECURITY_CONFIG = {
  // Rate limiting (requests per minute per IP)
  RATE_LIMIT: {
    anonymous: 10,
    authenticated: 100,
    admin: 1000
  },

  // Blocked user agents (bots, scrapers)
  BLOCKED_USER_AGENTS: [
    /bot/i,
    /crawler/i,
    /scraper/i,
    /spider/i,
    /headless/i,
    /phantom/i,
    /selenium/i
  ],

  // Suspicious patterns
  SUSPICIOUS_PATHS: [
    '/admin',
    '/api/admin',
    '/.env',
    '/config',
    '/wp-admin',
    '/phpmyadmin'
  ],

  // Session security
  SESSION: {
    MAX_AGE: 30 * 24 * 60 * 60 * 1000, // 30 days
    ROTATION_AGE: 7 * 24 * 60 * 60 * 1000, // 7 days
    MAX_CONCURRENT: 5 // Max sessions per user
  }
}

// Rate limiting store (in production, use Redis)
const rateLimitStore = new Map<string, { count: number; resetTime: number }>()

// Security event logging
async function logSecurityEvent(
  eventType: string,
  severity: 'low' | 'medium' | 'high' | 'critical',
  details: Record<string, any>,
  request: NextRequest
) {
  try {
    // In production, send to security monitoring service
    console.error(`SECURITY_EVENT: ${eventType}`, {
      severity,
      ip: request.ip,
      userAgent: request.headers.get('user-agent'),
      path: request.nextUrl.pathname,
      ...details
    })
  } catch (error) {
    console.error('Failed to log security event:', error)
  }
}

// Rate limiting check
function checkRateLimit(ip: string, isAuth: boolean, isAdmin: boolean = false): boolean {
  // Bypass rate limiting in development, test, or CI environments
  if (process.env.NODE_ENV === 'development' || process.env.NODE_ENV === 'test' || process.env.CI) {
    return true
  }

  const now = Date.now()
  const windowMs = 60 * 1000 // 1 minute
  const key = `rate_limit:${ip}`

  const current = rateLimitStore.get(key)

  if (!current || now > current.resetTime) {
    rateLimitStore.set(key, {
      count: 1,
      resetTime: now + windowMs
    })
    return true
  }

  const limit = isAdmin
    ? SECURITY_CONFIG.RATE_LIMIT.admin
    : isAuth
      ? SECURITY_CONFIG.RATE_LIMIT.authenticated
      : SECURITY_CONFIG.RATE_LIMIT.anonymous

  if (current.count >= limit) {
    return false
  }

  current.count++
  return true
}

// User agent validation
function validateUserAgent(userAgent: string | null): boolean {
  // Allow all user agents in development, test, or CI environments
  if (process.env.NODE_ENV === 'development' || process.env.NODE_ENV === 'test' || process.env.CI) {
    return true
  }

  if (!userAgent) return false

  return !SECURITY_CONFIG.BLOCKED_USER_AGENTS.some(pattern =>
    pattern.test(userAgent)
  )
}

// Path validation
function validatePath(path: string): boolean {
  return !SECURITY_CONFIG.SUSPICIOUS_PATHS.some(suspiciousPath =>
    path.includes(suspiciousPath)
  )
}

// IP-based security checks
function validateIP(ip: string | null): boolean {
  // In development/test/CI, allow all IPs (even null/undefined)
  if (process.env.NODE_ENV === 'development' || process.env.NODE_ENV === 'test' || process.env.CI) {
    return true
  }

  if (!ip) return false

  // Block private IPs in production (adjust as needed)
  const privateIPRanges = [
    /^10\./,
    /^172\.(1[6-9]|2[0-9]|3[0-1])\./,
    /^192\.168\./,
    /^127\./,
    /^localhost$/i
  ]

  // In development, allow private IPs
  if (process.env.NODE_ENV === 'development') {
    return true
  }

  // Check for common proxy headers
  if (ip.startsWith('192.168.') || ip.startsWith('10.') || ip.startsWith('172.')) {
    return false
  }

  return true
}

// Session validation and rotation
async function validateSession(
  supabase: any,
  request: NextRequest
): Promise<{ valid: boolean; user?: any; needsRotation?: boolean }> {
  try {
    const { data: { session }, error } = await supabase.auth.getSession()

    if (error || !session) {
      return { valid: false }
    }

    // Check session age
    const sessionAge = Date.now() - new Date(session.expires_at!).getTime()
    const needsRotation = sessionAge > SECURITY_CONFIG.SESSION.ROTATION_AGE

    // For now, we trust the Supabase session without requiring a database lookup.
    // This allows new users who haven't been inserted into public.users yet to proceed.
    // The application layer should handle profile creation if needed.
    const user = {
      id: session.user.id,
      email: session.user.email,
      role: session.user.user_metadata?.role || 'user',
      is_active: true,
      is_banned: false,
      workspace_id: session.user.user_metadata?.workspace_id
    }

    return {
      valid: true,
      user: { ...session.user, ...user },
      needsRotation
    }
  } catch (error) {
    console.error('Session validation error:', error)
    return { valid: false }
  }
}

// Main middleware function
export async function middleware(request: NextRequest) {
  const response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  try {
    // Extract client information
    const ip = request.ip ||
      request.headers.get('x-forwarded-for')?.split(',')[0] ||
      request.headers.get('x-real-ip')

    const userAgent = request.headers.get('user-agent')
    const path = request.nextUrl.pathname

    // Security validations
    if (!validateIP(ip)) {
      await logSecurityEvent('INVALID_IP', 'medium', { ip }, request)
      return new NextResponse('Forbidden', { status: 403 })
    }

    if (!validateUserAgent(userAgent)) {
      await logSecurityEvent('BLOCKED_USER_AGENT', 'medium', { userAgent }, request)
      return new NextResponse('Forbidden', { status: 403 })
    }

    if (!validatePath(path)) {
      await logSecurityEvent('SUSPICIOUS_PATH_ACCESS', 'high', { path }, request)
      return new NextResponse('Forbidden', { status: 403 })
    }

    // Create Supabase client
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return request.cookies.getAll()
          },
          setAll(cookiesToSet: CookieToSet[]) {
            cookiesToSet.forEach(({ name, value, options }: CookieToSet) => {
              request.cookies.set(name, value)
              response.cookies.set(name, value, options)
            })
          },
        },
      }
    )

    // Validate session
    const sessionValidation = await validateSession(supabase, request)
    const isAuth = sessionValidation.valid
    const user = sessionValidation.user

    // Rate limiting
    if (!checkRateLimit(ip!, isAuth, user?.role === 'admin')) {
      await logSecurityEvent('RATE_LIMIT_EXCEEDED', 'medium', {
        ip,
        isAuth,
        path
      }, request)
      return new NextResponse('Too Many Requests', { status: 429 })
    }

    // Security headers
    response.headers.set('X-Content-Type-Options', 'nosniff')
    response.headers.set('X-Frame-Options', 'DENY')
    response.headers.set('X-XSS-Protection', '1; mode=block')
    response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')

    // Content Security Policy
    response.headers.set(
      'Content-Security-Policy',
      [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https: blob:",
        "font-src 'self' data:",
        "connect-src 'self' https://api.supabase.io https://*.supabase.co http://127.0.0.1:54321 ws://127.0.0.1:54321 http://localhost:54321 ws://localhost:54321 http://localhost:8000 http://localhost:3000",
        "frame-ancestors 'none'"
      ].join('; ')
    )

    // Route protection
    const protectedRoutes = ['/dashboard', '/onboarding', '/admin', '/api/protected']
    const authRoutes = ['/login', '/signup', '/auth']
    const adminRoutes = ['/admin', '/api/admin']

    // Redirect unauthenticated users from protected routes
    if (protectedRoutes.some(route => path.startsWith(route)) && !isAuth) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', path)
      return NextResponse.redirect(loginUrl)
    }

    // Redirect authenticated users from auth routes
    if (authRoutes.some(route => path.startsWith(route)) && isAuth) {
      // If user has a workspace or completed onboarding, go to dashboard
      // Otherwise, go to onboarding. 
      // Note: we check workspace_id from metadata which was populated in validateSession
      if (user?.workspace_id || user?.user_metadata?.onboarding_status === 'active') {
        return NextResponse.redirect(new URL('/dashboard', request.url))
      }
      return NextResponse.redirect(new URL('/onboarding', request.url))
    }

    // New: If authenticated but on dashboard/other routes and has no workspace, redirect to onboarding
    if (path.startsWith('/dashboard') && isAuth && !user?.workspace_id) {
       return NextResponse.redirect(new URL('/onboarding', request.url))
    }

    // Admin route protection
    if (adminRoutes.some(route => path.startsWith(route)) && isAuth) {
      if (!['admin', 'super_admin'].includes(user.role)) {
        await logSecurityEvent('UNAUTHORIZED_ADMIN_ACCESS', 'high', {
          userId: user.id,
          userRole: user.role,
          path
        }, request)
        return new NextResponse('Forbidden', { status: 403 })
      }
    }

    // Session rotation
    if (isAuth && sessionValidation.needsRotation) {
      const { data: { session: newSession }, error: rotationError } =
        await supabase.auth.refreshSession()

      if (!rotationError && newSession) {
        response.cookies.set('access_token', newSession.access_token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          maxAge: SECURITY_CONFIG.SESSION.MAX_AGE / 1000
        })

        await logSecurityEvent('SESSION_ROTATED', 'low', {
          userId: user.id
        }, request)
      }
    }

    // Add user context to headers for downstream use
    if (isAuth && user) {
      response.headers.set('x-user-id', user.id)
      response.headers.set('x-user-role', user.role)
      response.headers.set('x-workspace-id', user.workspace_id || '')
    }

    // Check for domain mismatch and handle gracefully
    const requestOrigin = request.headers.get('origin')
    const expectedBaseUrl = getBaseUrl()
    if (requestOrigin && requestOrigin !== expectedBaseUrl) {
      console.log('Domain mismatch detected:', { requestOrigin, expectedBaseUrl })
      // In development, allow mismatch; in production, this might indicate a misconfiguration
      if (process.env.NODE_ENV === 'production') {
        await logSecurityEvent('DOMAIN_MISMATCH', 'medium', {
          requestOrigin,
          expectedBaseUrl,
          userId: user?.id
        }, request)
      }
    }

    return response

  } catch (error) {
    console.error('Middleware error:', error)
    await logSecurityEvent('MIDDLEWARE_ERROR', 'critical', {
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined
    }, request)

    // Fail securely - deny access on middleware errors
    return new NextResponse('Internal Server Error', { status: 500 })
  }
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.jpg$|.*\\.svg$).*)',
  ],
}
