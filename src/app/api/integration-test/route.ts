import { NextResponse } from 'next/server'

// Simple payment test without complex dependencies
export async function GET() {
  try {
    // Test 1: Environment variables
    const envCheck = {
      clientId: !!process.env.PHONEPE_CLIENT_ID,
      clientSecret: !!process.env.PHONEPE_CLIENT_SECRET,
      merchantId: !!process.env.PHONEPE_MERCHANT_ID,
      environment: process.env.PHONEPE_ENV,
    }

    // Test 2: OAuth token generation
    const PHONEPE_BASE_URL = process.env.PHONEPE_ENV === 'PRODUCTION'
      ? 'https://api.phonepe.com/apis/pg'
      : 'https://api-preprod.phonepe.com/apis/pg-sandbox'

    const tokenResponse = await fetch(`${PHONEPE_BASE_URL}/v1/oauth/token`, {
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

    const tokenData = await tokenResponse.json()
    const tokenSuccess = tokenResponse.ok && !!tokenData.access_token

    // Test 3: Payment payload creation
    const transactionId = `TEST_${Date.now()}`
    const payload = {
      merchantId: process.env.PHONEPE_MERCHANT_ID!,
      merchantTransactionId: transactionId,
      amount: 100, // ₹1.00 in paise
      redirectUrl: `${process.env.NEXT_PUBLIC_APP_URL}/test/callback`,
      redirectMode: 'REDIRECT',
      callbackUrl: `${process.env.NEXT_PUBLIC_API_URL}/api/payments/webhook`,
      paymentInstrument: {
        type: 'PAY_PAGE'
      }
    }

    const payloadValid = !!payload.merchantId && !!payload.merchantTransactionId && payload.amount > 0

    return NextResponse.json({
      status: 'success',
      message: 'PhonePe integration test results',
      tests: {
        environment: {
          status: Object.values(envCheck).every(Boolean) ? 'PASS' : 'FAIL',
          details: envCheck
        },
        oauth: {
          status: tokenSuccess ? 'PASS' : 'FAIL',
          details: {
            tokenReceived: !!tokenData.access_token,
            expiresIn: tokenData.expires_in,
            error: !tokenResponse.ok ? tokenData : null
          }
        },
        payload: {
          status: payloadValid ? 'PASS' : 'FAIL',
          details: {
            valid: payloadValid,
            transactionId,
            amount: payload.amount
          }
        }
      },
      overall: {
        status: Object.values(envCheck).every(Boolean) && tokenSuccess && payloadValid ? 'READY' : 'NEEDS_ATTENTION',
        message: Object.values(envCheck).every(Boolean) && tokenSuccess && payloadValid 
          ? '✅ PhonePe integration is ready for payment testing!' 
          : '⚠️ Some components need attention before testing payments'
      },
      nextSteps: [
        '🧪 Test payment initiation with: POST /api/test-payment',
        '📊 Monitor payment status with: GET /api/payments/status/{transactionId}',
        '🔔 Test webhook handling with PhonePe simulator'
      ]
    })

  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Integration test failed',
      error: error instanceof Error ? error.message : 'Unknown error',
      troubleshooting: [
        '🔧 Check PhonePe credentials in .env file',
        '🔧 Verify network connectivity to PhonePe servers',
        '🔧 Review error logs for detailed information'
      ]
    }, { status: 500 })
  }
}
