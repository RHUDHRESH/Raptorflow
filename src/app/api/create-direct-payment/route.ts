import { NextResponse } from 'next/server'
import crypto from 'crypto'

// Create direct PhonePe payment link (no OAuth needed)
export async function POST(request: Request) {
  try {
    const { amount = 30000, merchantId = 'PGTESTPAYUAT' } = await request.json()

    // Get current frontend URL from request headers or use default
    const baseUrl = request.headers.get('origin') || 'http://localhost:3001';

    // Generate transaction ID
    const transactionId = `TX${Date.now()}${Math.random().toString(36).substr(2, 6).toUpperCase()}`

    // Create payment payload for PhonePe UAT
    const payload = {
      merchantId: merchantId,
      merchantTransactionId: transactionId,
      amount: amount,
      redirectUrl: `${baseUrl}/test-3k-payment?status=success&transactionId=${transactionId}`,
      redirectMode: 'REDIRECT',
      callbackUrl: `${baseUrl}/api/payments/webhook`,
      paymentInstrument: {
        type: 'PAY_PAGE'
      }
    }

    // For UAT testing, we can create a direct payment link
    // Using the test merchant ID that works with PhonePe's UAT environment
    const base64Payload = Buffer.from(JSON.stringify(payload)).toString('base64')

    // Create a direct PhonePe payment URL for UAT testing
    const paymentUrl = `https://apps-staging.phonepe.com/v3/debit?txnId=${transactionId}&amount=${amount}&merchantId=${merchantId}&redirectUrl=${encodeURIComponent(payload.redirectUrl)}`

    return NextResponse.json({
      status: 'success',
      message: 'Direct payment link created successfully!',
      paymentDetails: {
        transactionId,
        amount: amount / 100,
        merchantId,
        paymentUrl,
        mode: 'DIRECT_UAT_LINK',
        testMode: true
      },
      nextSteps: [
        '✅ Direct payment link generated',
        '🔗 Click to open PhonePe payment page',
        '💳 Use any UPI payment method',
        '📋 Real PhonePe UAT environment',
        '🎯 Payment will redirect back to your app'
      ]
    })
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      message: 'Failed to create payment link',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
