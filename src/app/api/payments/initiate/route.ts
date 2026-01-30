import { createServerSupabaseClient, createServiceSupabaseClient, getProfileByAuthUserId } from '@/lib/auth-server'
import { NextResponse } from 'next/server'
import crypto from 'crypto'

// PhonePe 2026 API Configuration
const PHONEPE_BASE_URL = process.env.PHONEPE_ENV === 'PRODUCTION'
  ? 'https://api.phonepe.com/apis/pg'
  : 'https://api-preprod.phonepe.com/apis/pg-sandbox'

const PHONEPE_MERCHANT_ID = process.env.PHONEPE_MERCHANT_ID!
const PHONEPE_CLIENT_ID = process.env.PHONEPE_CLIENT_ID!
const PHONEPE_CLIENT_SECRET = process.env.PHONEPE_CLIENT_SECRET!
const PHONEPE_CLIENT_VERSION = process.env.PHONEPE_CLIENT_VERSION || '1'
const PHONEPE_SALT_KEY = process.env.PHONEPE_SALT_KEY
const PHONEPE_SALT_INDEX = process.env.PHONEPE_SALT_INDEX || '1'

// Hardcoded plan pricing for reliability
const PLAN_PRICING: Record<string, { monthly: number; yearly: number; name: string }> = {
  'ascent': { monthly: 500000, yearly: 5000000, name: 'Ascent' },
  'glide': { monthly: 700000, yearly: 7000000, name: 'Glide' },
  'soar': { monthly: 1000000, yearly: 10000000, name: 'Soar' }
}

function buildPhonePePayload(params: {
  merchantId: string
  transactionId: string
  userId: string
  amount: number
  redirectUrl: string
  callbackUrl: string
}) {
  return {
    merchantId: params.merchantId,
    merchantTransactionId: params.transactionId,
    merchantUserId: params.userId,
    amount: params.amount,
    redirectUrl: params.redirectUrl,
    redirectMode: 'REDIRECT',
    callbackUrl: params.callbackUrl,
    paymentInstrument: {
      type: 'PAY_PAGE'
    }
  }
}

function buildPhonePeRequestBody(payload: Record<string, unknown>) {
  const encodedPayload = Buffer.from(JSON.stringify(payload)).toString('base64')
  return { encodedPayload, requestBody: { request: encodedPayload } }
}

function buildPhonePeSignature(encodedPayload: string) {
  if (!PHONEPE_SALT_KEY) {
    return null
  }
  const signature = crypto
    .createHash('sha256')
    .update(`${encodedPayload}/pg/v1/pay${PHONEPE_SALT_KEY}`)
    .digest('hex')
  return `${signature}###${PHONEPE_SALT_INDEX}`
}

export async function POST(request: Request) {
  try {
    const { planId, billingCycle } = await request.json()

    const supabase = await createServerSupabaseClient()

    // Get current user
    const { data: { user: authUser }, error: authError } = await supabase.auth.getUser()

    if (authError || !authUser) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Use service client for profile operations to bypass RLS
    let serviceClient;
    try {
      serviceClient = await createServiceSupabaseClient()
    } catch {
      serviceClient = supabase
    }

    const { profile } = await getProfileByAuthUserId(serviceClient, authUser.id)

    if (!profile) {
      return NextResponse.json(
        { error: 'User profile not found. Please try logging in again.' },
        { status: 404 }
      )
    }

    const onboardingStatus = profile.onboarding_status

    // Allow payment from pending_payment status or when navigating back
    const validStates = ['pending_payment', 'pending_plan_selection', 'pending', null, undefined]
    if (onboardingStatus && !validStates.includes(onboardingStatus)) {
      return NextResponse.json(
        { error: `Invalid state for payment: ${onboardingStatus}. Please select a plan first.` },
        { status: 400 }
      )
    }

    // Get plan pricing - try hardcoded first, then DB
    let planPricing = PLAN_PRICING[planId]
    let planName = planPricing?.name || planId

    if (!planPricing) {
      // Try to get from subscription_plans table
      const { data: dbPlan } = await serviceClient
        .from('subscription_plans')
        .select('name, price_monthly, price_annual')
        .eq('slug', planId)
        .single()

      if (dbPlan) {
        planPricing = {
          monthly: dbPlan.price_monthly,
          yearly: dbPlan.price_annual,
          name: dbPlan.name
        }
        planName = dbPlan.name
      } else {
        return NextResponse.json({ error: 'Plan not found' }, { status: 404 })
      }
    }

    // Calculate amount
    const amount = billingCycle === 'yearly'
      ? planPricing.yearly
      : planPricing.monthly

    // Generate unique transaction ID
    const transactionId = `TXN_${profile.id.slice(0, 8)}_${Date.now()}`

    // Store pending subscription in user_subscriptions table
    const { error: subError } = await serviceClient
      .from('user_subscriptions')
      .upsert({
        user_id: profile.id,
        plan_id: planId,
        billing_cycle: billingCycle,
        amount_paid: amount,
        status: 'pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }, {
        onConflict: 'user_id'
      })

    if (subError) {
      console.error('Subscription upsert error:', subError)
      // Continue anyway - payment is more important
    }

    // Store payment in payments table for status transitions
    const { error: paymentInsertError } = await serviceClient
      .from('payments')
      .insert({
        user_id: profile.id,
        transaction_id: transactionId,
        plan_id: planId,
        amount: amount,
        currency: 'INR',
        status: 'initiated',
        payment_method: 'phonepe',
        created_at: new Date().toISOString()
      })

    if (paymentInsertError) {
      console.error('Payments insert error:', paymentInsertError)
    }

    // Store transaction reference
    const { error: txnError } = await serviceClient
      .from('payment_transactions')
      .insert({
        user_id: profile.id,
        transaction_id: transactionId,
        amount_paise: amount,
        status: 'initiated',
        plan_id: planId,
        billing_cycle: billingCycle
      })

    if (txnError) {
      console.error('Transaction insert error:', txnError)
      // Continue anyway
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

    const payload = buildPhonePePayload({
      merchantId: PHONEPE_MERCHANT_ID,
      transactionId,
      userId: profile.id,
      amount,
      redirectUrl: `${process.env.NEXT_PUBLIC_APP_URL}/onboarding/payment/status?transactionId=${transactionId}`,
      callbackUrl: `${process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_APP_URL}/api/payments/webhook`
    })
    const { encodedPayload, requestBody } = buildPhonePeRequestBody(payload)
    const xVerify = buildPhonePeSignature(encodedPayload)

    // Call PhonePe 2026 API with OAuth token
    const response = await fetch(`${PHONEPE_BASE_URL}/pg/v1/pay`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
        'X-MERCHANT-ID': PHONEPE_MERCHANT_ID,
        ...(xVerify ? { 'X-VERIFY': xVerify } : {}),
      },
      body: JSON.stringify(requestBody),
    })

    const data = await response.json()

    if (data.success && data.data?.instrumentResponse?.redirectInfo?.url) {
      await serviceClient
        .from('payments')
        .update({
          status: 'pending',
          phonepe_transaction_id: data.data.merchantTransactionId || null,
          verified_at: new Date().toISOString()
        })
        .eq('transaction_id', transactionId)

      return NextResponse.json({
        redirectUrl: data.data.instrumentResponse.redirectInfo.url,
        transactionId,
      })
    }

    console.error('PhonePe error:', data)
    await serviceClient
      .from('payments')
      .update({
        status: 'failed',
        verified_at: new Date().toISOString()
      })
      .eq('transaction_id', transactionId)

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
