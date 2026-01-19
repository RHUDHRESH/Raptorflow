import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'
import crypto from 'crypto'

// PhonePe 2026 Webhook Configuration
const PHONEPE_WEBHOOK_USERNAME = process.env.PHONEPE_WEBHOOK_USERNAME
const PHONEPE_WEBHOOK_PASSWORD = process.env.PHONEPE_WEBHOOK_PASSWORD

export async function POST(request: Request) {
  try {
    const body = await request.text()
    const signature = request.headers.get('x-verify')
    const authHeader = request.headers.get('authorization')

    // Basic webhook validation for 2026 API
    if (!authHeader || !signature) {
      console.error('Missing webhook headers')
      return NextResponse.json(
        { error: 'Missing required headers' },
        { status: 401 }
      )
    }

    // Parse webhook data
    let webhookData
    try {
      webhookData = JSON.parse(body)
    } catch (err) {
      console.error('Invalid webhook JSON:', err)
      return NextResponse.json(
        { error: 'Invalid webhook payload' },
        { status: 400 }
      )
    }

    // Log webhook for debugging
    console.log('PhonePe webhook received:', {
      type: webhookData.type,
      code: webhookData.code,
      transactionId: webhookData.data?.transactionId,
      state: webhookData.data?.state,
    })

    const supabase = createServerSupabaseClient()

    // Handle different webhook types
    const webhookType = webhookData.type

    if (webhookType === 'PAYMENT_SUCCESS') {
      await handlePaymentSuccess(webhookData, supabase)
    } else if (webhookType === 'PAYMENT_FAILED') {
      await handlePaymentFailure(webhookData, supabase)
    } else if (webhookType === 'REFUND_SUCCESS') {
      await handleRefundSuccess(webhookData, supabase)
    } else {
      console.log('Unknown webhook type:', webhookType)
    }

    return NextResponse.json({ status: 'success' })

  } catch (err) {
    console.error('Webhook processing error:', err)
    return NextResponse.json(
      { error: 'Webhook processing failed' },
      { status: 500 }
    )
  }
}

async function handlePaymentSuccess(webhookData: any, supabase: any) {
  const data = webhookData.data
  const transactionId = data.transactionId
  const merchantTransactionId = data.merchantTransactionId
  const amount = data.amount
  const paymentInstrument = data.paymentInstrument

  console.log(`Payment successful: ${transactionId}`)

  try {
    // Update payment transaction
    await supabase
      .from('payment_transactions')
      .update({
        status: 'completed',
        phonepe_transaction_id: transactionId,
        payment_method: paymentInstrument?.type || 'UNKNOWN',
        payment_instrument: paymentInstrument,
        completed_at: new Date().toISOString(),
      })
      .eq('transaction_id', merchantTransactionId)

    // Get transaction details to activate subscription
    const { data: transaction } = await supabase
      .from('payment_transactions')
      .select('user_id, plan_id, billing_cycle')
      .eq('transaction_id', merchantTransactionId)
      .single()

    if (transaction) {
      // Activate subscription
      await supabase
        .from('subscriptions')
        .upsert({
          user_id: transaction.user_id,
          plan_id: transaction.plan_id,
          billing_cycle: transaction.billing_cycle,
          status: 'active',
          current_period_start: new Date().toISOString(),
          current_period_end: getPeriodEnd(transaction.billing_cycle),
          updated_at: new Date().toISOString(),
        }, {
          onConflict: 'user_id'
        })

      // Update user onboarding status
      await supabase
        .from('users')
        .update({
          onboarding_status: 'completed',
          subscription_tier: transaction.plan_id,
          updated_at: new Date().toISOString(),
        })
        .eq('id', transaction.user_id)

      console.log(`Subscription activated for user: ${transaction.user_id}`)
    }

  } catch (error) {
    console.error('Error handling payment success:', error)
  }
}

async function handlePaymentFailure(webhookData: any, supabase: any) {
  const data = webhookData.data
  const merchantTransactionId = data.merchantTransactionId
  const responseCode = data.responseCode

  console.log(`Payment failed: ${merchantTransactionId} - ${responseCode}`)

  try {
    // Update payment transaction
    await supabase
      .from('payment_transactions')
      .update({
        status: 'failed',
        error_code: responseCode,
        error_message: data.responseMessage,
        updated_at: new Date().toISOString(),
      })
      .eq('transaction_id', merchantTransactionId)

  } catch (error) {
    console.error('Error handling payment failure:', error)
  }
}

async function handleRefundSuccess(webhookData: any, supabase: any) {
  const data = webhookData.data
  const refundTransactionId = data.refundTransactionId
  const originalTransactionId = data.originalTransactionId

  console.log(`Refund successful: ${refundTransactionId}`)

  try {
    // Log refund event
    await supabase
      .from('refund_events')
      .insert({
        refund_transaction_id: refundTransactionId,
        original_transaction_id: originalTransactionId,
        status: 'completed',
        webhook_data: webhookData,
        created_at: new Date().toISOString(),
      })

  } catch (error) {
    console.error('Error handling refund success:', error)
  }
}

function getPeriodEnd(billingCycle: string): string {
  const now = new Date()
  if (billingCycle === 'monthly') {
    const endDate = new Date(now)
    endDate.setMonth(endDate.getMonth() + 1)
    return endDate.toISOString()
  } else {
    const endDate = new Date(now)
    endDate.setFullYear(endDate.getFullYear() + 1)
    return endDate.toISOString()
  }
}
