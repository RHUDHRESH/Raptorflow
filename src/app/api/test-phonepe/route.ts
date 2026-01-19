import { NextResponse } from 'next/server'

// Test endpoint to verify PhonePe configuration
export async function GET() {
  try {
    // Check if required environment variables are set
    const requiredVars = [
      'PHONEPE_CLIENT_ID',
      'PHONEPE_CLIENT_SECRET', 
      'PHONEPE_MERCHANT_ID',
      'PHONEPE_ENV'
    ]

    const missingVars = requiredVars.filter(varName => !process.env[varName])
    
    if (missingVars.length > 0) {
      return NextResponse.json({
        status: 'error',
        message: 'Missing PhonePe configuration',
        missing: missingVars,
        setup: 'Please copy .env.example to .env and add your PhonePe credentials'
      }, { status: 400 })
    }

    // Test OAuth token generation
    const PHONEPE_BASE_URL = process.env.PHONEPE_ENV === 'PRODUCTION'
      ? 'https://api.phonepe.com/apis/pg'
      : 'https://api-preprod.phonepe.com/apis/pg-sandbox'

    const authUrl = `${PHONEPE_BASE_URL}/v1/oauth/token`
    
    const tokenResponse = await fetch(authUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: process.env.PHONEPE_CLIENT_ID!,
        client_version: process.env.PHONEPE_CLIENT_VERSION || '1',
        client_secret: process.env.PHONEPE_CLIENT_SECRET!,
      }),
    })

    if (!tokenResponse.ok) {
      const errorText = await tokenResponse.text()
      return NextResponse.json({
        status: 'error',
        message: 'PhonePe OAuth authentication failed',
        error: errorText,
        setup: 'Please verify your PhonePe credentials are correct'
      }, { status: 401 })
    }

    const tokenData = await tokenResponse.json()
    
    return NextResponse.json({
      status: 'success',
      message: 'PhonePe integration is working!',
      environment: process.env.PHONEPE_ENV,
      merchantId: process.env.PHONEPE_MERCHANT_ID,
      tokenReceived: !!tokenData.access_token,
      tokenExpiresIn: tokenData.expires_in,
      nextSteps: [
        '✅ PhonePe OAuth authentication successful',
        '🚀 Ready to test payment initiation',
        '📋 Visit /onboarding/payment to test full flow'
      ]
    })

  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'PhonePe test failed',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
