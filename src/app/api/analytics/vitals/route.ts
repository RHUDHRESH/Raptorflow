/**
 * Web Vitals analytics endpoint
 * Receives and logs Web Vitals metrics
 */

import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const metric = await request.json()
    
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log('Web Vital:', metric)
    }
    
    // In production, send to analytics service (Sentry, Vercel Analytics, etc.)
    if (process.env.NODE_ENV === 'production') {
      // Example: Send to Sentry
      // Sentry.captureMessage('Web Vital', {
      //   level: 'info',
      //   extra: metric,
      // })
    }
    
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Failed to log Web Vital:', error)
    return NextResponse.json({ success: false }, { status: 500 })
  }
}
