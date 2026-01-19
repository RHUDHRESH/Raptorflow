import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

// PhonePe 2026 API Configuration
const PHONEPE_BASE_URL = process.env.PHONEPE_ENV === 'PRODUCTION'
  ? 'https://api.phonepe.com/apis/pg'
  : 'https://api-preprod.phonepe.com/apis/pg-sandbox'

const PHONEPE_MERCHANT_ID = process.env.PHONEPE_MERCHANT_ID!
const PHONEPE_CLIENT_ID = process.env.PHONEPE_CLIENT_ID!
const PHONEPE_CLIENT_SECRET = process.env.PHONEPE_CLIENT_SECRET!
const PHONEPE_CLIENT_VERSION = process.env.PHONEPE_CLIENT_VERSION || '1'

export async function GET(
  request: Request,
  { params }: { params: { transactionId: string } }
) {
  try {
    const { transactionId } = params

    if (!transactionId) {
      return NextResponse.json(
        { error: 'Transaction ID is required' },
        { status: 400 }
      )
    }

    // Get OAuth token for 2026 API
    const tokenResponse = await fetch(`${PHONEPE_BASE_URL}/v1/oauth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: PHONEPE_CLIENT_ID,
        client_version: PHONEPE_CLIENT_VERSION,
        client_secret: PHONEPE_CLIENT_SECRET,
      }),
    })

    if (!tokenResponse.ok) {
      console.error('Failed to get PhonePe OAuth token:', await tokenResponse.text())
      return NextResponse.json(
        { error: 'Payment service authentication failed' },
        { status: 500 }
      )
    }

    const tokenData = await tokenResponse.json()
    const accessToken = tokenData.access_token

    // Check payment status using 2026 API
    const response = await fetch(
      `${PHONEPE_BASE_URL}/pg/v1/status/${PHONEPE_MERCHANT_ID}/${transactionId}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'X-MERCHANT-ID': PHONEPE_MERCHANT_ID,
        },
      }
    )

    if (!response.ok) {
      console.error('PhonePe status check failed:', await response.text())
      return NextResponse.json(
        { error: 'Failed to check payment status' },
        { status: 500 }
      )
    }

    const data = await response.json()

    if (data.success) {
      const paymentData = data.data
      return NextResponse.json({
        success: true,
        status: paymentData.state, // COMPLETED, PENDING, FAILED
        transactionId: paymentData.transactionId,
        amount: paymentData.amount,
        paymentInstrument: paymentData.paymentInstrument,
        responseCode: paymentData.responseCode,
        responseMessage: paymentData.responseMessage,
      })
    } else {
      return NextResponse.json(
        { error: data.message || 'Payment status check failed' },
        { status: 400 }
      )
    }

  } catch (err) {
    console.error('Payment status check error:', err)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
