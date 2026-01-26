import { createClient } from '@supabase/supabase-js'
import { NextRequest } from 'next/server'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

interface RateLimitConfig {
  windowMs: number // Window in milliseconds
  maxRequests: number // Max requests per window
  skipSuccessfulRequests?: boolean
  skipFailedRequests?: boolean
}

const defaultLimits: Record<string, RateLimitConfig> = {
  // Authentication endpoints
  '/api/auth/callback': { windowMs: 60 * 1000, maxRequests: 10 },
  '/api/login': { windowMs: 15 * 60 * 1000, maxRequests: 5 },

  // Payment endpoints
  '/api/payments/initiate': { windowMs: 60 * 1000, maxRequests: 3 },
  '/api/payments/verify': { windowMs: 60 * 1000, maxRequests: 10 },

  // Admin endpoints
  '/api/admin': { windowMs: 60 * 1000, maxRequests: 100 },

  // General API limits
  '/api/': { windowMs: 60 * 1000, maxRequests: 60 },

  // Data export
  '/api/gdpr/data-export': { windowMs: 60 * 60 * 1000, maxRequests: 1 },

  // Email sending
  '/api/send-email': { windowMs: 60 * 1000, maxRequests: 10 }
}

export async function rateLimit(
  request: NextRequest,
  identifier: string,
  endpoint: string
): Promise<{ success: boolean; limit: number; remaining: number; resetTime: number }> {
  // Find matching limit config
  const config = Object.entries(defaultLimits).find(([path]) =>
    endpoint.startsWith(path)
  )?.[1] || defaultLimits['/api/']

  const now = new Date()
  const windowStart = new Date(now.getTime() - config.windowMs)
  const windowEnd = now

  try {
    // Clean up old entries
    await supabase
      .from('api_rate_limits')
      .delete()
      .lt('window_end', windowStart.toISOString())

    // Get current count
    const { data: existing } = await supabase
      .from('api_rate_limits')
      .select('request_count, window_start, window_end')
      .eq('identifier', identifier)
      .eq('endpoint', endpoint)
      .gte('window_start', windowStart.toISOString())
      .lte('window_end', windowEnd.toISOString())
      .single()

    let currentCount = 0
    const resetTime = windowEnd.getTime()

    if (existing) {
      currentCount = existing.request_count

      // Update existing record
      await supabase
        .from('api_rate_limits')
        .update({
          request_count: currentCount + 1,
          window_end: windowEnd.toISOString()
        })
        .eq('identifier', identifier)
        .eq('endpoint', endpoint)
        .eq('window_start', existing.window_start)
    } else {
      // Create new record
      await supabase
        .from('api_rate_limits')
        .insert({
          identifier,
          endpoint,
          request_count: 1,
          window_start: windowStart.toISOString(),
          window_end: windowEnd.toISOString()
        })

      currentCount = 1
    }

    const remaining = Math.max(0, config.maxRequests - currentCount)
    const success = currentCount <= config.maxRequests

    // Log rate limit violations
    if (!success) {
      await supabase
        .from('security_events')
        .insert({
          user_id: null, // We don't always have user context
          event_type: 'suspicious_activity',
          details: {
            type: 'rate_limit_exceeded',
            identifier,
            endpoint,
            requestCount: currentCount,
            limit: config.maxRequests
          },
          risk_score: 50
        })
    }

    return {
      success,
      limit: config.maxRequests,
      remaining,
      resetTime
    }

  } catch (error) {
    console.error('Rate limiting error:', error)
    // Fail open - allow request if rate limiting fails
    return {
      success: true,
      limit: config.maxRequests,
      remaining: config.maxRequests - 1,
      resetTime: Date.now() + config.windowMs
    }
  }
}

export function getIdentifier(request: NextRequest): string {
  // Try to get user ID from auth header
  const authHeader = request.headers.get('authorization')
  if (authHeader?.startsWith('Bearer ')) {
    // In a real implementation, you'd decode the JWT to get user ID
    // For now, use the token as identifier
    return `user:${authHeader.slice(7)}`
  }

  // Fall back to IP address
  const forwarded = request.headers.get('x-forwarded-for')
  const ip = forwarded ? forwarded.split(',')[0] : request.ip || 'unknown'

  return `ip:${ip}`
}

// Enhanced rate limiting for DDoS protection
export async function ddosProtection(request: NextRequest): Promise<{
  blocked: boolean
  reason?: string
  score: number
}> {
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0] || request.ip || 'unknown'

  try {
    // Get recent requests from this IP
    const { data: recentRequests } = await supabase
      .from('api_rate_limits')
      .select('request_count, endpoint')
      .eq('identifier', `ip:${ip}`)
      .gte('window_start', new Date(Date.now() - 60 * 1000).toISOString())

    let riskScore = 0
    let blocked = false
    let reason: string | undefined

    if (recentRequests) {
      const totalRequests = recentRequests.reduce((sum: number, r: any) => sum + r.request_count, 0)

      // Calculate risk score
      if (totalRequests > 1000) {
        riskScore += 80
        reason = 'Excessive request rate'
      } else if (totalRequests > 500) {
        riskScore += 50
      } else if (totalRequests > 200) {
        riskScore += 20
      }

      // Check for suspicious patterns
      const uniqueEndpoints = new Set(recentRequests.map((r: any) => r.endpoint)).size
      if (uniqueEndpoints === 1 && totalRequests > 100) {
        riskScore += 40
        reason = 'Single endpoint abuse'
      }

      // Check for authentication attempts
      const authAttempts = recentRequests
        .filter((r: any) => r.endpoint.includes('/api/auth') || r.endpoint.includes('/api/login'))
        .reduce((sum: number, r: any) => sum + r.request_count, 0)

      if (authAttempts > 20) {
        riskScore += 60
        reason = 'Excessive authentication attempts'
      }
    }

    // Block if risk score is too high
    if (riskScore >= 80) {
      blocked = true

      // Log DDoS attempt
      await supabase
        .from('security_events')
        .insert({
          user_id: null,
          event_type: 'suspicious_activity',
          details: {
            type: 'ddos_attempt',
            ip,
            riskScore,
            reason
          },
          risk_score: riskScore
        })
    }

    return { blocked, reason, score: riskScore }

  } catch (error) {
    console.error('DDoS protection error:', error)
    return { blocked: false, score: 0 }
  }
}

// Middleware function
export async function applyRateLimit(request: NextRequest, endpoint: string) {
  // First check DDoS protection
  const ddosResult = await ddosProtection(request)

  if (ddosResult.blocked) {
    return {
      allowed: false,
      error: 'Too many requests',
      statusCode: 429,
      headers: {
        'Retry-After': '60',
        'X-RateLimit-Limit': '0',
        'X-RateLimit-Remaining': '0',
        'X-RateLimit-Reset': Math.ceil(Date.now() / 1000 + 60).toString()
      }
    }
  }

  // Apply normal rate limiting
  const identifier = getIdentifier(request)
  const rateLimitResult = await rateLimit(request, identifier, endpoint)

  if (!rateLimitResult.success) {
    return {
      allowed: false,
      error: 'Rate limit exceeded',
      statusCode: 429,
      headers: {
        'Retry-After': Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000).toString(),
        'X-RateLimit-Limit': rateLimitResult.limit.toString(),
        'X-RateLimit-Remaining': rateLimitResult.remaining.toString(),
        'X-RateLimit-Reset': Math.ceil(rateLimitResult.resetTime / 1000).toString()
      }
    }
  }

  return {
    allowed: true,
    headers: {
      'X-RateLimit-Limit': rateLimitResult.limit.toString(),
      'X-RateLimit-Remaining': rateLimitResult.remaining.toString(),
      'X-RateLimit-Reset': Math.ceil(rateLimitResult.resetTime / 1000).toString()
    }
  }
}
