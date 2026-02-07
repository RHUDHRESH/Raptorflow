import { NextResponse, NextRequest } from 'next/server'
import { createServerAuth } from './lib/auth-server'
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

const INTERNAL_API_TOKEN = process.env.INTERNAL_API_TOKEN

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
    const ip = request.headers.get('x-forwarded-for')?.split(',')[0] ||
      request.headers.get('x-real-ip') ||
      '127.0.0.1'

    console.error(`SECURITY_EVENT: ${eventType}`, {
      severity,
      ip,
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

  // Allow localhost and private IPs for development and behind proxies
  const allowedIPRanges = [
    /^10\./,           // Private network
    /^172\.(1[6-9]|2[0-9]|3[0-1])\./, // Private network
    /^192\.168\./,    // Private network
    /^127\./,         // Localhost (127.x.x.x)
    /^localhost$/i,   // Localhost
    /^::1$/,          // IPv6 localhost
    /^fc00:/,         // IPv6 private
    /^fe80:/,         // IPv6 link-local
    /^169\.254\./,    // Link-local (Windows DHCP)
    /^0\./,           // Reserved for localhost
    /^::ffff:127\./,  // IPv4-mapped IPv6 localhost
    /^::ffff:10\./,   // IPv4-mapped private network
    /^::ffff:172\.(1[6-9]|2[0-9]|3[0-1])\./, // IPv4-mapped private network
    /^::ffff:192\.168\./ // IPv4-mapped private network
  ]

  // Check if IP is in allowed ranges
  for (const range of allowedIPRanges) {
    if (range.test(ip)) {
      return true
    }
  }

  // For production, you might want to be more restrictive
  // For now, allow all IPs but log suspicious ones
  console.log('IP validation:', { ip, userAgent: 'logged for security monitoring' })

  return true
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
    const ip = request.headers.get('x-forwarded-for')?.split(',')[0] ||
      request.headers.get('x-real-ip') ||
      '127.0.0.1'

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

    // Create auth service instance
    const serverAuth = createServerAuth(request, response)

    // Validate session
    const sessionValidation = await serverAuth.validateSession()
    const isAuth = sessionValidation.valid
    const user = sessionValidation.user

    // Rate limiting with bypass for health checks
    if (!checkRateLimit(ip!, isAuth, user?.role === 'admin')) {
      // Bypass rate limiting for health checks and monitoring
      if (path.startsWith('/api/health')) {
        // Allow health checks to pass through
      } else {
        await logSecurityEvent('RATE_LIMIT_EXCEEDED', 'medium', {
          ip,
          isAuth,
          path
        }, request)
        return new NextResponse('Too Many Requests', { status: 429 })
      }
    }

    // Security headers
    response.headers.set('X-Content-Type-Options', 'nosniff')
    response.headers.set('X-Frame-Options', 'DENY')
    response.headers.set('X-XSS-Protection', '1; mode=block')
    response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')

    // Content Security Policy - Updated to include localhost ports 3001-3005
    response.headers.set(
      'Content-Security-Policy',
      [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https: blob:",
        "font-src 'self' data:",
        "connect-src 'self' https://api.supabase.io https://*.supabase.co http://127.0.0.1:54321 ws://127.0.0.1:54321 http://localhost:54321 ws://localhost:54321 http://localhost:8000 http://localhost:3000 http://localhost:3001 http://localhost:3002 http://localhost:3003 http://localhost:3004 http://localhost:3005 ws://localhost:3001 ws://localhost:3002 ws://localhost:3003 ws://localhost:3004 ws://localhost:3005",
        "frame-ancestors 'none'"
      ].join('; ')
    )

    // Route protection
    const protectedRoutes = ['/dashboard', '/onboarding', '/admin', '/api/protected']
    const authRoutes = ['/signin', '/signup', '/auth/reset-password']
    // Explicitly exclude callback route from all redirect logic - it must process OAuth codes
    const callbackRoute = '/auth/callback'
    const adminRoutes = ['/admin', '/api/admin']
    const requiresProfile = protectedRoutes.some(route => path.startsWith(route))

    // Profile/payment readiness check (skip for auth routes and public assets)
    let profileStatus: {
      profile_exists: boolean
      workspace_exists: boolean
      needs_payment: boolean
      workspace_id?: string
    } | null = null

    const isPublicPath = (path: string) => {
      if (path === '/' || path === '') return true
      const publicPrefixes = ['/signin', '/signup', '/auth/callback', '/auth/reset-password', '/test-auth.html']
      return publicPrefixes.some((prefix) => path === prefix || path.startsWith(`${prefix}/`))
    }

    if (isAuth && !isPublicPath(path)) {
      try {
        // Use environment-specific backend URL for reliability
        const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const profileUrl = `${backendUrl}/api/v1/auth/verify-profile`

        console.log('Middleware profile verification:', {
          userId: user?.id,
          path,
          profileUrl,
          backendUrl: process.env.BACKEND_URL,
          apiUrl: process.env.NEXT_PUBLIC_API_URL
        })

        const verifyHeaders: Record<string, string> = {
          'Content-Type': 'application/json',
          'Cookie': request.headers.get('cookie') || '',
          'Authorization': request.headers.get('authorization') || '',
          'X-Forwarded-For': ip,
          'X-User-Agent': userAgent || '',
        }

        if (user?.id) {
          verifyHeaders['X-User-Id'] = user.id
        }
        if (user?.workspace_id) {
          verifyHeaders['X-Workspace-Id'] = user.workspace_id
        }
        if (user?.email) {
          verifyHeaders['X-User-Email'] = user.email
        }
        if (INTERNAL_API_TOKEN) {
          verifyHeaders['X-Internal-Token'] = INTERNAL_API_TOKEN
        }

        const verifyResponse = await fetch(profileUrl, {
          method: 'GET',
          headers: verifyHeaders,
          cache: 'no-store',
          signal: AbortSignal.timeout(5000), // 5 second timeout
        })

        if (verifyResponse.ok) {
          profileStatus = await verifyResponse.json()
          console.log('Profile verification successful:', {
            userId: user?.id,
            profileExists: profileStatus?.profile_exists,
            workspaceExists: profileStatus?.workspace_exists,
            needsPayment: profileStatus?.needs_payment
          })
        } else {
          const errorText = await verifyResponse.text()
          console.error('Profile verification failed:', {
            status: verifyResponse.status,
            statusText: verifyResponse.statusText,
            errorText,
            userId: user?.id,
            path
          })

          // Log security event for failed verification
          await logSecurityEvent('PROFILE_VERIFICATION_FAILED', 'medium', {
            status: verifyResponse.status,
            errorText: errorText.substring(0, 200), // Truncate for logging
            userId: user?.id,
            path
          }, request)
        }
      } catch (error) {
        console.error('Middleware profile verification error:', {
          error: error instanceof Error ? error.message : 'Unknown error',
          userId: user?.id,
          path,
          stack: error instanceof Error ? error.stack : undefined
        })

        // Log security event for verification errors
        await logSecurityEvent('PROFILE_VERIFICATION_ERROR', 'medium', {
          error: error instanceof Error ? error.message : 'Unknown error',
          userId: user?.id,
          path
        }, request)

        // Fail closed - block access if we can't verify profile
        if (requiresProfile) {
          console.log('Failing closed due to profile verification error')
          return new NextResponse('Profile verification failed', {
            status: 503,
            headers: {
              'Retry-After': '30',
              'Content-Type': 'text/plain'
            }
          })
        }
      }
    }

    // Skip all auth route logic for callback route - it must process OAuth codes
    if (path.startsWith(callbackRoute)) {
      return response
    }

    // Redirect unauthenticated users from protected routes
    if (requiresProfile && !isAuth) {
      const signinUrl = new URL('/signin', request.url)
      signinUrl.searchParams.set('redirect', path)
      return NextResponse.redirect(signinUrl)
    }

    if (isAuth && profileStatus && requiresProfile) {
      const hasActiveSubscription = user?.subscription_status === 'active'

      if (!profileStatus.profile_exists || !profileStatus.workspace_exists) {
        return NextResponse.redirect(
          new URL(hasActiveSubscription ? '/onboarding/start' : '/onboarding/plans', request.url)
        )
      }

      if (profileStatus.needs_payment || !hasActiveSubscription) {
        return NextResponse.redirect(new URL('/onboarding/plans', request.url))
      }
    }

    // Redirect authenticated users from auth routes (but not /auth/callback which needs to process OAuth)
    if (authRoutes.some(route => path === route || path.startsWith(route + '/')) && isAuth) {
      // If user has active subscription and completed onboarding, go to dashboard
      if (user?.subscription_status === 'active' && user?.onboarding_status === 'active') {
        return NextResponse.redirect(new URL('/dashboard', request.url))
      }
      // If user has active subscription but not completed onboarding, go to step 1
      if (user?.subscription_status === 'active' && user?.onboarding_status !== 'active') {
        return NextResponse.redirect(new URL('/onboarding/session/step/1', request.url))
      }
      // For users without active subscription, redirect to plans (PhonePe payment required)
      return NextResponse.redirect(new URL('/onboarding/plans', request.url))
    }

    // If on dashboard without active subscription, redirect to plans (payment required)
    if (path.startsWith('/dashboard') && isAuth && user?.subscription_status !== 'active') {
      return NextResponse.redirect(new URL('/onboarding/plans', request.url))
    }

    // If on dashboard with subscription but onboarding not done, redirect to onboarding step 1
    if (path.startsWith('/dashboard') && isAuth && user?.subscription_status === 'active' && user?.onboarding_status !== 'active') {
      return NextResponse.redirect(new URL('/onboarding/session/step/1', request.url))
    }

    // Block access to onboarding steps if no active subscription (payment required first)
    if (path.startsWith('/onboarding/session') && isAuth && user?.subscription_status !== 'active') {
      return NextResponse.redirect(new URL('/onboarding/plans', request.url))
    }

    // Admin route protection
    if (adminRoutes.some(route => path.startsWith(route)) && isAuth) {
      if (!user || !['admin', 'super_admin'].includes(user.role)) {
        await logSecurityEvent('UNAUTHORIZED_ADMIN_ACCESS', 'high', {
          userId: user?.id,
          userRole: user?.role,
          path
        }, request)
        return new NextResponse('Forbidden', { status: 403 })
      }
    }

    // Session rotation
    if (isAuth && sessionValidation.needsRotation) {
      const rotationResult = await serverAuth.rotateSession()

      if (rotationResult.success && rotationResult.session) {
        response.cookies.set('access_token', rotationResult.session.access_token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: 'lax',
          maxAge: SECURITY_CONFIG.SESSION.MAX_AGE / 1000
        })

        await logSecurityEvent('SESSION_ROTATED', 'low', {
          userId: user?.id
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
