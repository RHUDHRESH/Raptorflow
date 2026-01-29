import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

// Dunning configuration
const DUNNING_RULES = [
  { days: 0, action: 'send_first_notice', template: 'payment_failed_first' },
  { days: 3, action: 'send_second_notice', template: 'payment_failed_second' },
  { days: 7, action: 'send_third_notice', template: 'payment_failed_third' },
  { days: 14, action: 'send_final_notice', template: 'payment_failed_final' },
  { days: 21, action: 'suspend_account', template: 'account_suspended' },
  { days: 30, action: 'cancel_subscription', template: 'subscription_cancelled' }
]

export async function POST(request: Request) {
  try {
    const supabase = await createServerSupabaseClient()

    // This endpoint should only be called by cron job
    if (request.headers.get('x-cron-job') !== 'process-dunning') {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get all past due subscriptions
    const { data: pastDueSubscriptions } = await supabase
      .from('subscriptions')
      .select(`
        *,
        user:users(id, email, full_name)
      `)
      .eq('status', 'past_due')
      .lt('current_period_end', new Date().toISOString())

    if (!pastDueSubscriptions || pastDueSubscriptions.length === 0) {
      return NextResponse.json({ processed: 0, message: 'No past due subscriptions found' })
    }

    let processedCount = 0

    for (const subscription of pastDueSubscriptions) {
      await processDunningForSubscription(supabase, subscription)
      processedCount++
    }

    return NextResponse.json({
      processed: processedCount,
      message: `Processed dunning for ${processedCount} subscriptions`
    })

  } catch (error) {
    console.error('Dunning process error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

async function processDunningForSubscription(supabase: any, subscription: any) {
  const daysPastDue = Math.ceil(
    (Date.now() - new Date(subscription.current_period_end).getTime()) / (1000 * 60 * 60 * 24)
  )

  // Get last dunning action for this subscription
  const { data: lastDunningAction } = await supabase
    .from('dunning_actions')
    .select('*')
    .eq('subscription_id', subscription.id)
    .order('created_at', { ascending: false })
    .limit(1)
    .single()

  // Find the next dunning rule to apply
  const nextRule = DUNNING_RULES.find(rule => {
    if (rule.action === 'cancel_subscription') {
      return daysPastDue >= rule.days
    }
    return daysPastDue >= rule.days &&
           (!lastDunningAction || lastDunningAction.action !== rule.action)
  })

  if (!nextRule) return

  // Execute the dunning action
  switch (nextRule.action) {
    case 'send_first_notice':
    case 'send_second_notice':
    case 'send_third_notice':
    case 'send_final_notice':
      await sendDunningEmail(supabase, subscription, nextRule.template)
      await logDunningAction(supabase, subscription.id, nextRule.action)
      break

    case 'suspend_account':
      await suspendUserAccount(supabase, subscription.user_id)
      await logDunningAction(supabase, subscription.id, nextRule.action)
      break

    case 'cancel_subscription':
      await cancelSubscription(supabase, subscription)
      await logDunningAction(supabase, subscription.id, nextRule.action)
      break
  }
}

async function sendDunningEmail(supabase: any, subscription: any, template: string) {
  const user = subscription.user

  // Create retry payment link
  const retryUrl = `${process.env.NEXT_PUBLIC_APP_URL}/billing/retry?subscription=${subscription.id}`

  // Send email via Resend
  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from: 'billing@raptorflow.com',
      to: [user.email],
      subject: getSubjectForTemplate(template),
      html: getEmailBodyForTemplate(template, user.full_name, retryUrl)
    })
  })

  // Log email
  await supabase
    .from('email_logs')
    .insert({
      user_id: subscription.user_id,
      template_name: template,
      to_email: user.email,
      subject: getSubjectForTemplate(template),
      status: response.ok ? 'sent' : 'failed',
      sent_at: response.ok ? new Date().toISOString() : null
    })
}

function getSubjectForTemplate(template: string): string {
  switch (template) {
    case 'payment_failed_first':
      return 'Payment Failed - Action Required'
    case 'payment_failed_second':
      return 'Second Notice: Payment Still Required'
    case 'payment_failed_third':
      return 'Final Notice: Account Will Be Suspended'
    case 'payment_failed_final':
      return 'URGENT: Account Suspension Imminent'
    case 'account_suspended':
      return 'Your Account Has Been Suspended'
    case 'subscription_cancelled':
      return 'Your Subscription Has Been Cancelled'
    default:
      return 'Payment Notification'
  }
}

function getEmailBodyForTemplate(template: string, userName: string | null, retryUrl: string): string {
  const name = userName || 'Customer'

  switch (template) {
    case 'payment_failed_first':
      return `
        <h1>Payment Failed</h1>
        <p>Hi ${name},</p>
        <p>We were unable to process your recent payment. This could be due to insufficient funds, an expired card, or other banking issues.</p>
        <p><a href="${retryUrl}" style="background: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Update Payment Method</a></p>
        <p>Please update your payment method within 3 days to avoid service interruption.</p>
      `

    case 'payment_failed_second':
      return `
        <h1>Second Notice: Payment Required</h1>
        <p>Hi ${name},</p>
        <p>Your payment is still overdue. We've sent you a reminder 3 days ago but haven't received a response.</p>
        <p><a href="${retryUrl}" style="background: #EF4444; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Pay Now to Avoid Suspension</a></p>
        <p>Your account will be suspended in 4 days if payment is not received.</p>
      `

    case 'payment_failed_third':
      return `
        <h1>Final Notice Before Suspension</h1>
        <p>Hi ${name},</p>
        <p>This is your final notice. Your account will be suspended in 7 days due to non-payment.</p>
        <p><a href="${retryUrl}" style="background: #DC2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Immediate Payment Required</a></p>
        <p>After suspension, you'll lose access to all features and data.</p>
      `

    case 'payment_failed_final':
      return `
        <h1>URGENT: Suspension Tomorrow</h1>
        <p>Hi ${name},</p>
        <p>Your account will be suspended tomorrow if payment is not made immediately.</p>
        <p><a href="${retryUrl}" style="background: #991B1B; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Pay Now to Save Your Account</a></p>
        <p>This is your last chance to avoid suspension.</p>
      `

    default:
      return `<p>Please update your payment method.</p>`
  }
}

async function suspendUserAccount(supabase: any, userId: string) {
  // Update user status
  await supabase
    .from('users')
    .update({ onboarding_status: 'suspended' })
    .eq('id', userId)

  // Revoke all active sessions
  await supabase
    .from('user_sessions')
    .update({ is_active: false })
    .eq('user_id', userId)

  // Log security event
  await supabase
    .from('security_events')
    .insert({
      user_id: userId,
      event_type: 'account_suspended',
      details: { reason: 'non_payment' }
    })
}

async function cancelSubscription(supabase: any, subscription: any) {
  // Update subscription status
  await supabase
    .from('subscriptions')
    .update({ status: 'canceled' })
    .eq('id', subscription.id)

  // Update user status
  await supabase
    .from('users')
    .update({ onboarding_status: 'cancelled' })
    .eq('id', subscription.user_id)

  // Log the cancellation
  await supabase
    .from('audit_logs')
    .insert({
      actor_id: subscription.user_id,
      action: 'subscription_cancelled_dunning',
      action_category: 'billing',
      description: 'Subscription cancelled due to non-payment'
    })
}

async function logDunningAction(supabase: any, subscriptionId: string, action: string) {
  await supabase
    .from('dunning_actions')
    .insert({
      subscription_id: subscriptionId,
      action,
      created_at: new Date().toISOString()
    })
}

// Manual retry endpoint for users
export async function PATCH(request: Request) {
  try {
    const { subscriptionId } = await request.json()

    const supabase = createRouteHandlerClient({ cookies })

    // Get current user
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get subscription
    const { data: subscription } = await supabase
      .from('subscriptions')
      .select('*')
      .eq('id', subscriptionId)
      .eq('user_id', (
        supabase.from('users').select('id').eq('auth_user_id', session.user.id).single()
      ))
      .single()

    if (!subscription) {
      return NextResponse.json({ error: 'Subscription not found' }, { status: 404 })
    }

    // Check if subscription is past due
    if (subscription.status !== 'past_due') {
      return NextResponse.json({ error: 'Subscription is not past due' }, { status: 400 })
    }

    // Create new payment attempt
    const { data: paymentIntent } = await supabase.functions.invoke('create-payment-intent', {
      body: {
        subscriptionId,
        amount: subscription.billing_cycle === 'yearly'
          ? subscription.price_yearly_paise
          : subscription.price_monthly_paise,
        currency: 'inr'
      }
    })

    if (!paymentIntent.clientSecret) {
      return NextResponse.json({ error: 'Failed to create payment intent' }, { status: 500 })
    }

    // Clear previous dunning actions
    await supabase
      .from('dunning_actions')
      .delete()
      .eq('subscription_id', subscriptionId)

    return NextResponse.json({
      clientSecret: paymentIntent.clientSecret,
      message: 'Payment intent created successfully'
    })

  } catch (error) {
    console.error('Retry payment error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
