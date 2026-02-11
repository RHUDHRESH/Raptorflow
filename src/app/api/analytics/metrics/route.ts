/**
 * Custom metrics analytics endpoint
 * Receives and logs custom performance metrics
 */

import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const metric = await request.json()
    
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log('Custom Metric:', metric)
    }
    
    // In production, send to analytics service
    if (process.env.NODE_ENV === 'production') {
      // Example: Send to monitoring service
    }
    
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Failed to log custom metric:', error)
    return NextResponse.json({ success: false }, { status: 500 })
  }
}
