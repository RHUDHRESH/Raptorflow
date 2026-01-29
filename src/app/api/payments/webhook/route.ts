import { createServerSupabaseClient, getProfileByAnyId, updateProfileRecord } from '@/lib/auth-server'
import { NextResponse } from 'next/server'
import { sendWelcomeEmail, sendPaymentConfirmationEmail } from '@/lib/email'

// PhonePe 2026 Webhook Configuration
const PHONEPE_WEBHOOK_USERNAME = process.env.PHONEPE_WEBHOOK_USERNAME
const PHONEPE_WEBHOOK_PASSWORD = process.env.PHONEPE_WEBHOOK_PASSWORD

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
        completed_at: new Date().toISOString(),
      })
      .eq('transaction_id', merchantTransactionId)

    // Get transaction details to activate subscription
    const { data: transaction } = await supabaseClient
      .from('payment_transactions')
      .select('user_id, plan_id, billing_cycle, amount')
      .eq('transaction_id', merchantTransactionId)
      .single()

    if (transaction) {
      const nowIso = new Date().toISOString()
      const periodEnd = getPeriodEnd(transaction.billing_cycle)
      const { planRecord, entitlements } = await resolvePlanEntitlements(
        supabaseClient,
        transaction.plan_id,
        transaction.billing_cycle
      )
      const planName = PLAN_NAMES[transaction.plan_id] || planRecord?.name || transaction.plan_id

      // Activate subscription in subscriptions table
      const { error: subscriptionError } = await supabaseClient
        .from('subscriptions')
        .upsert({
          user_id: transaction.user_id,
          plan_id: transaction.plan_id,
          plan_name: planName,
          billing_cycle: transaction.billing_cycle,
          status: 'active',
          current_period_start: nowIso,
          current_period_end: periodEnd,
          updated_at: nowIso,
        }, {
          onConflict: 'user_id'
        })

      if (subscriptionError) {
        console.error('Subscription activation failed:', subscriptionError)
      }

      // Keep unified subscriptions table in sync when available
      const { error: unifiedSubError } = await supabaseClient
        .from('user_subscriptions')
        .upsert({
          user_id: transaction.user_id,
          plan_id: planRecord?.id || transaction.plan_id,
          billing_cycle: transaction.billing_cycle,
          amount_paid: transaction.amount,
          status: 'active',
          current_period_start: nowIso,
          current_period_end: periodEnd,
          phonepe_order_id: merchantTransactionId,
          updated_at: nowIso,
        }, {
          onConflict: 'user_id'
        })

      if (unifiedSubError) {
        console.error('Unified subscription activation failed:', unifiedSubError)
      }

      const subscriptionActive = !subscriptionError

      if (subscriptionActive) {
        // Update profile with subscription status (PRIMARY source for routing)
        await updateProfileRecord(
          supabaseClient,
          { profileId: transaction.user_id },
          {
            subscription_plan: transaction.plan_id,
            subscription_status: 'active',
            onboarding_status: 'active',
            updated_at: nowIso,
          }
        )

        await upsertEntitlements(
          supabaseClient,
          transaction.user_id,
          {
            ...entitlements,
            onboarding_unlocked: true,
            activated_at: nowIso,
          },
          nowIso
        )

        await logSubscriptionActivation(
          supabaseClient,
          transaction.user_id,
          transaction.plan_id,
          merchantTransactionId,
          entitlements
        )
      }

      console.log(`Subscription activated for user: ${transaction.user_id}`)

      // Get user profile for email
      const { profile } = await getProfileByAnyId(supabaseClient, transaction.user_id)

      if (profile) {
        const userEmail = profile.email || ''
        const userName = profile.full_name || userEmail.split('@')[0] || 'User'
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
        updated_at: new Date().toISOString(),
      })
      .eq('transaction_id', merchantTransactionId)

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

async function resolvePlanEntitlements(
  supabaseClient: any,
  planId: string | null,
  billingCycle: string | null
) {
  let planRecord = null

  if (planId) {
    const { data: planBySlug } = await supabaseClient
      .from('subscription_plans')
      .select('id, slug, name, features, limits')
      .eq('slug', planId)
      .maybeSingle()

    planRecord = planBySlug

    if (!planRecord && isUuid(planId)) {
      const { data: planById } = await supabaseClient
        .from('subscription_plans')
        .select('id, slug, name, features, limits')
        .eq('id', planId)
        .maybeSingle()
      planRecord = planById
    }
  }

  return {
    planRecord,
    entitlements: {
      plan_id: planRecord?.slug || planId,
      plan_name: planRecord?.name || planId,
      billing_cycle: billingCycle,
      features: planRecord?.features || {},
      limits: planRecord?.limits || {},
    }
  }
}

async function upsertEntitlements(
  supabaseClient: any,
  userId: string,
  entitlements: Record<string, any>,
  nowIso: string
) {
  try {
    const { data: profileRecord, error: profileError } = await supabaseClient
      .from('profiles')
      .select('workspace_preferences')
      .eq('id', userId)
      .maybeSingle()

    if (profileError) {
      console.warn('Unable to load workspace preferences:', profileError)
      return
    }

    const workspacePreferences = profileRecord?.workspace_preferences || {}
    const mergedPreferences = {
      ...workspacePreferences,
      entitlements
    }

    const { error: updateError } = await supabaseClient
      .from('profiles')
      .update({
        workspace_preferences: mergedPreferences,
        updated_at: nowIso
      })
      .eq('id', userId)

    if (updateError) {
      console.warn('Unable to persist entitlement flags:', updateError)
    }

    const { error: userProfilesError } = await supabaseClient
      .from('user_profiles')
      .update({
        plan_features: entitlements,
        updated_at: nowIso
      })
      .eq('id', userId)

    if (userProfilesError) {
      console.warn('Unable to persist entitlement flags in user_profiles:', userProfilesError)
    }
  } catch (error) {
    console.warn('Failed to update entitlement flags:', error)
  }
}

async function logSubscriptionActivation(
  supabaseClient: any,
  userId: string,
  planId: string,
  transactionId: string,
  entitlements: Record<string, any>
) {
  try {
    const { error } = await supabaseClient
      .from('audit_logs')
      .insert({
        actor_id: userId,
        action: 'subscription_activated',
        action_category: 'subscription',
        description: `Subscription activated for plan ${planId}`,
        target_type: 'subscription',
        target_id: transactionId,
        changes: {
          plan_id: planId,
          entitlements
        },
        status: 'success'
      })

    if (error) {
      console.warn('Failed to log subscription activation:', error)
    }
  } catch (error) {
    console.warn('Failed to log subscription activation:', error)
  }
}

function isUuid(value: string) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value)
}
