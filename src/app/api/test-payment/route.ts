import { NextResponse } from 'next/server'
import { createServerSupabaseClient } from '@/lib/auth-server'

// Test payment initiation flow
export async function POST(request: Request) {
  try {
    const { amount = 100, planId = 'starter' } = await request.json()

    // Test payment initiation
    const PHONEPE_BASE_URL = process.env.PHONEPE_ENV === 'PRODUCTION'
      ? 'https://api.phonepe.com/apis/pg'
      : 'https://api-preprod.phonepe.com/apis/pg-sandbox'

    // Get OAuth token
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

    if (!tokenResponse.ok) {
      throw new Error('OAuth token generation failed')
    }

    const tokenData = await tokenResponse.json()
    const accessToken = tokenData.access_token

    // Create test transaction
    const transactionId = `TEST_${Date.now()}`
    const payload = {
      merchantId: process.env.PHONEPE_MERCHANT_ID!,
      merchantTransactionId: transactionId,
      amount: amount, // Amount in paise
      redirectUrl: `${process.env.NEXT_PUBLIC_APP_URL}/api/test-payment/callback`,
      redirectMode: 'REDIRECT',
      callbackUrl: `${process.env.NEXT_PUBLIC_API_URL}/api/payments/webhook`,
      paymentInstrument: {
        type: 'PAY_PAGE'
      }
    }

    // Initiate payment
    const paymentResponse = await fetch(`${PHONEPE_BASE_URL}/pg/v1/pay`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'X-MERCHANT-ID': process.env.PHONEPE_MERCHANT_ID!,
      },
      body: JSON.stringify({ 
        request: Buffer.from(JSON.stringify(payload)).toString('base64') 
      }),
    })

    const paymentData = await paymentResponse.json()

    if (paymentData.success && paymentData.data?.instrumentResponse?.redirectInfo?.url) {
      return NextResponse.json({
        status: 'success',
        message: 'Payment initiation test successful!',
        testResults: {
          transactionId,
          amount: amount / 100, // Convert to rupees for display
          phonePeTransactionId: paymentData.data.transactionId,
          paymentUrl: paymentData.data.instrumentResponse.redirectInfo.url,
          redirectMethod: paymentData.data.instrumentResponse.redirectInfo.method,
        },
        nextSteps: [
          '✅ Payment initiation successful',
          '🔗 Payment URL generated',
          '💳 Ready to redirect to PhonePe',
          '📋 Test with: ' + paymentData.data.instrumentResponse.redirectInfo.url
        ]
      })
    } else {
      return NextResponse.json({
        status: 'error',
        message: 'Payment initiation failed',
        error: paymentData,
        troubleshooting: [
          '❌ Check PhonePe credentials',
          '❌ Verify merchant ID is correct',
          '❌ Ensure UAT environment is accessible',
          '❌ Check network connectivity'
        ]
      }, { status: 400 })
    }

  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Payment test failed',
      error: error instanceof Error ? error.message : 'Unknown error',
      troubleshooting: [
        '🔧 Check environment variables',
        '🔧 Verify PhonePe credentials',
        '🔧 Check network connectivity',
        '🔧 Review error logs'
      ]
    }, { status: 500 })
  }
}
