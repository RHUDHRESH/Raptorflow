import { createServerSupabaseClient, getProfileByAuthUserId } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

// PhonePe 2026 API Configuration
const PHONEPE_BASE_URL = process.env.PHONEPE_ENV === 'PRODUCTION'
  ? 'https://api.phonepe.com/apis/pg'
  : 'https://api-preprod.phonepe.com/apis/pg-sandbox'

const PHONEPE_MERCHANT_ID = process.env.PHONEPE_MERCHANT_ID!
const PHONEPE_CLIENT_ID = process.env.PHONEPE_CLIENT_ID!
const PHONEPE_CLIENT_SECRET = process.env.PHONEPE_CLIENT_SECRET!
const PHONEPE_CLIENT_VERSION = process.env.PHONEPE_CLIENT_VERSION || '1'

export async function POST(request: Request) {
  try {
    const { planId, billingCycle } = await request.json()

    const supabase = await createServerSupabaseClient()

    // Get current user
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { profile } = await getProfileByAuthUserId(supabase, session.user.id)
    const onboardingStatus = profile?.onboarding_status

    if (!profile || (onboardingStatus && onboardingStatus !== 'pending_payment')) {
      return NextResponse.json(
        { error: 'Invalid state for payment. Please select a plan first.' },
        { status: 400 }
      )
    }


    // Get plan
    const { data: plan } = await supabase
      .from('plans')
      .select('*')
      .eq('id', planId)
      .single()

    if (!plan) {
      return NextResponse.json({ error: 'Plan not found' }, { status: 404 })
    }

    // Calculate amount
    const amount = billingCycle === 'monthly'
      ? plan.price_monthly_paise
      : plan.price_yearly_paise

    // Generate unique transaction ID
    const transactionId = `TXN_${profile.id.slice(0, 8)}_${Date.now()}`

    // Store pending subscription
    await supabase
      .from('subscriptions')
      .upsert({
        user_id: profile.id,
        plan_id: plan.id,
        plan_name: plan.name,
        price_monthly_paise: plan.price_monthly_paise,
        billing_cycle: billingCycle,
        status: 'pending'
      }, {
        onConflict: 'user_id'
      })

    // Store transaction reference
    await supabase
      .from('payment_transactions')
      .insert({
        user_id: profile.id,
        transaction_id: transactionId,
        amount_paise: amount,
        status: 'initiated',
        plan_id: planId,
        billing_cycle: billingCycle
      })

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

    // Prepare PhonePe 2026 payload
    const payload = {
      merchantId: PHONEPE_MERCHANT_ID,
      merchantTransactionId: transactionId,
      merchantUserId: profile.id,
      amount: amount, // In paise
      redirectUrl: `${process.env.NEXT_PUBLIC_APP_URL}/onboarding/payment?status=pending&transactionId=${transactionId}`,
      redirectMode: 'REDIRECT',
      callbackUrl: `${process.env.NEXT_PUBLIC_API_URL}/api/payments/webhook`,
      paymentInstrument: {
        type: 'PAY_PAGE'
      }
    }

    // Call PhonePe 2026 API with OAuth token
    const response = await fetch(`${PHONEPE_BASE_URL}/pg/v1/pay`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'X-MERCHANT-ID': PHONEPE_MERCHANT_ID,
      },
      body: JSON.stringify({ request: Buffer.from(JSON.stringify(payload)).toString('base64') }),
    })

    const data = await response.json()

    if (data.success && data.data?.instrumentResponse?.redirectInfo?.url) {
      return NextResponse.json({
        redirectUrl: data.data.instrumentResponse.redirectInfo.url,
        transactionId,
      })
    }

    console.error('PhonePe error:', data)
    return NextResponse.json(
      { error: 'Failed to initiate payment' },
      { status: 500 }
    )

  } catch (err) {
    console.error('Payment initiation error:', err)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
