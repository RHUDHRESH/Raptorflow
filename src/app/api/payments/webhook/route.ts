import { createServerSupabaseClient, getProfileByAnyId, updateProfileRecord } from '@/lib/auth-server'
import { NextResponse } from 'next/server'
import crypto from 'crypto'
import { sendWelcomeEmail, sendPaymentConfirmationEmail } from '@/lib/email'

// PhonePe 2026 Webhook Configuration
const PHONEPE_SALT_KEY = process.env.PHONEPE_SALT_KEY
const PHONEPE_SALT_INDEX = process.env.PHONEPE_SALT_INDEX || '1'

// Plan name mapping
const PLAN_NAMES: Record<string, string> = {
  'ascent': 'Ascent',
  'glide': 'Glide',
  'soar': 'Soar'
}

export async function POST(request: Request) {
  try {
    const body = await request.text()
    const signature = request.headers.get('x-verify')

    // Basic webhook validation for 2026 API
    if (!signature) {
      console.error('Missing webhook signature header')
      return NextResponse.json(
        { error: 'Missing required headers' },
        { status: 401 }
      )
    }

    if (!PHONEPE_SALT_KEY) {
      console.error('Missing PhonePe salt key')
      return NextResponse.json(
        { error: 'Webhook verification not configured' },
        { status: 500 }
      )
    }

    const expectedSignature = crypto
      .createHash('sha256')
      .update(body + PHONEPE_SALT_KEY)
      .digest('hex')
    const normalizedSignature = signature.replace(/^sha256:/, '')
    const expectedWithIndex = `${expectedSignature}###${PHONEPE_SALT_INDEX}`

    if (normalizedSignature !== expectedWithIndex) {
      console.error('Webhook signature mismatch')
      return NextResponse.json(
        { error: 'Invalid webhook signature' },
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

    const supabase = await createServerSupabaseClient()

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

async function handlePaymentSuccess(webhookData: any, supabaseClient: any) {
  const data = webhookData.data
  const transactionId = data.transactionId
  const merchantTransactionId = data.merchantTransactionId
  const amount = data.amount
  const paymentInstrument = data.paymentInstrument

  console.log(`Payment successful: ${transactionId}`)

  try {
    // Check if we've already processed this transaction (idempotency)
    const { data: existingPayment } = await supabaseClient
      .from('payments')
      .select('id, welcome_email_sent_at, invoice_email_sent_at')
      .eq('transaction_id', merchantTransactionId)
      .single()

    // Update payment transaction
    await supabaseClient
      .from('payment_transactions')
      .update({
        status: 'completed',
        phonepe_transaction_id: transactionId,
        payment_method: paymentInstrument?.type || 'UNKNOWN',
        payment_instrument: paymentInstrument,
        phonepe_response: webhookData,
        completed_at: new Date().toISOString(),
      })
      .eq('transaction_id', merchantTransactionId)

    await supabaseClient
      .from('payments')
      .update({
        status: 'completed',
        phonepe_transaction_id: transactionId,
        verified_at: new Date().toISOString(),
      })
      .eq('transaction_id', merchantTransactionId)

    // Get transaction details to activate subscription
    const { data: transaction } = await supabaseClient
      .from('payment_transactions')
      .select('user_id, plan_id, billing_cycle, amount')
      .eq('transaction_id', merchantTransactionId)
      .single()

    if (transaction) {
      // Activate subscription in subscriptions table
      await supabaseClient
        .from('subscriptions')
        .upsert({
          user_id: transaction.user_id,
          plan_id: transaction.plan_id,
          billing_cycle: transaction.billing_cycle,
          status: 'active',
          current_period_start: new Date().toISOString(),
          current_period_end: getPeriodEnd(transaction.billing_cycle),
          phonepe_transaction_id: transactionId,
          updated_at: new Date().toISOString(),
        }, {
          onConflict: 'user_id'
        })

      // Update profile with subscription status (PRIMARY source for routing)
      await updateProfileRecord(
        supabaseClient,
        { profileId: transaction.user_id },
        {
          subscription_plan: transaction.plan_id,
          subscription_status: 'active',
          onboarding_status: 'pending',
          updated_at: new Date().toISOString(),
        }
      )

      console.log(`Subscription activated for user: ${transaction.user_id}`)

      // Get user profile for email
      const { profile } = await getProfileByAnyId(supabaseClient, transaction.user_id)

      if (profile) {
        const userEmail = profile.email || ''
        const userName = profile.full_name || userEmail.split('@')[0] || 'User'
        const planName = PLAN_NAMES[transaction.plan_id] || transaction.plan_id
        const amountInRupees = `₹${((transaction.amount || amount) / 100).toLocaleString('en-IN')}`
        const date = new Date().toLocaleDateString('en-IN', {
          day: 'numeric',
          month: 'long',
          year: 'numeric'
        })

        // Send welcome email (idempotent)
        if (!existingPayment?.welcome_email_sent_at) {
          console.log(`Sending welcome email to: ${userEmail}`)
          const welcomeResult = await sendWelcomeEmail(userEmail, userName)

          if (welcomeResult.success) {
            await supabaseClient
              .from('payments')
              .update({ welcome_email_sent_at: new Date().toISOString() })
              .eq('transaction_id', merchantTransactionId)
            console.log('Welcome email sent successfully')
          } else {
            console.error('Failed to send welcome email:', welcomeResult.error)
          }
        }

        // Send payment confirmation email (idempotent)
        if (!existingPayment?.invoice_email_sent_at) {
          console.log(`Sending payment confirmation email to: ${userEmail}`)
          const invoiceResult = await sendPaymentConfirmationEmail({
            email: userEmail,
            name: userName,
            planName: planName,
            amount: amountInRupees,
            transactionId: merchantTransactionId,
            date: date
          })

          if (invoiceResult.success) {
            await supabaseClient
              .from('payments')
              .update({ invoice_email_sent_at: new Date().toISOString() })
              .eq('transaction_id', merchantTransactionId)
            console.log('Payment confirmation email sent successfully')
          } else {
            console.error('Failed to send payment confirmation email:', invoiceResult.error)
          }
        }
      }
    }

  } catch (error) {
    console.error('Error handling payment success:', error)
  }
}

async function handlePaymentFailure(webhookData: any, supabaseClient: any) {
  const data = webhookData.data
  const merchantTransactionId = data.merchantTransactionId
  const responseCode = data.responseCode

  console.log(`Payment failed: ${merchantTransactionId} - ${responseCode}`)

  try {
    // Update payment transaction
    await supabaseClient
      .from('payment_transactions')
      .update({
        status: 'failed',
        error_code: responseCode,
        error_message: data.responseMessage,
        phonepe_response: webhookData,
        updated_at: new Date().toISOString(),
      })
      .eq('transaction_id', merchantTransactionId)

    await supabaseClient
      .from('payments')
      .update({
        status: 'failed',
        verified_at: new Date().toISOString(),
      })
      .eq('transaction_id', merchantTransactionId)

    const { data: transaction } = await supabaseClient
      .from('payment_transactions')
      .select('user_id')
      .eq('transaction_id', merchantTransactionId)
      .single()

    if (transaction?.user_id) {
      await supabaseClient
        .from('subscriptions')
        .update({
          status: 'past_due',
          updated_at: new Date().toISOString(),
        })
        .eq('user_id', transaction.user_id)
    }

  } catch (error) {
    console.error('Error handling payment failure:', error)
  }
}

async function handleRefundSuccess(webhookData: any, supabaseClient: any) {
  const data = webhookData.data
  const refundTransactionId = data.refundTransactionId
  const originalTransactionId = data.originalTransactionId

  console.log(`Refund successful: ${refundTransactionId}`)

  try {
    // Log refund event
    await supabaseClient
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
