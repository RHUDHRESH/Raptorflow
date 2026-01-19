import { createClient } from '@supabase/supabase-js'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const { newPlanId, billingCycle } = await request.json()
    
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    )
    
    // Get current user
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    
    // Get user
    const { data: user } = await supabase
      .from('users')
      .select('id, onboarding_status')
      .eq('auth_user_id', session.user.id)
      .single()
    
    if (!user || user.onboarding_status !== 'active') {
      return NextResponse.json(
        { error: 'Invalid user status' },
        { status: 400 }
      )
    }
    
    // Get current subscription
    const { data: currentSubscription } = await supabase
      .from('subscriptions')
      .select('*')
      .eq('user_id', user.id)
      .eq('status', 'active')
      .single()
    
    if (!currentSubscription) {
      return NextResponse.json(
        { error: 'No active subscription found' },
        { status: 404 }
      )
    }
    
    // Get new plan
    const { data: newPlan } = await supabase
      .from('plans')
      .select('*')
      .eq('id', newPlanId)
      .single()
    
    if (!newPlan) {
      return NextResponse.json({ error: 'Plan not found' }, { status: 404 })
    }
    
    // Check if this is an upgrade or downgrade
    const currentPrice = billingCycle === 'yearly' 
      ? currentSubscription.price_yearly_paise 
      : currentSubscription.price_monthly_paise
    const newPrice = billingCycle === 'yearly'
      ? newPlan.price_yearly_paise
      : newPlan.price_monthly_paise
    
    const isUpgrade = newPrice > currentPrice
    const isDowngrade = newPrice < currentPrice
    
    // Handle different scenarios
    if (isUpgrade) {
      // For upgrades, create prorated charge immediately
      const { error: upgradeError } = await handleUpgrade(
        supabase,
        currentSubscription,
        newPlan,
        billingCycle,
        user.id
      )
      
      if (upgradeError) throw upgradeError
      
    } else if (isDowngrade) {
      // For downgrades, schedule for end of current period
      const { error: downgradeError } = await handleDowngrade(
        supabase,
        currentSubscription,
        newPlan,
        billingCycle,
        user.id
      )
      
      if (downgradeError) throw downgradeError
      
    } else {
      // Same price, just update the plan
      const { error: updateError } = await supabase
        .from('subscriptions')
        .update({
          plan_id: newPlan.id,
          plan_name: newPlan.name,
          billing_cycle: billingCycle
        })
        .eq('id', currentSubscription.id)
      
      if (updateError) throw updateError
    }
    
    // Log the action
    await supabase
      .from('audit_logs')
      .insert({
        actor_id: user.id,
        action: 'subscription_changed',
        action_category: 'subscription',
        description: `Changed from ${currentSubscription.plan_name} to ${newPlan.name}`,
        ip_address: request.headers.get('x-forwarded-for') || 'unknown',
        user_agent: request.headers.get('user-agent') || 'unknown'
      })
    
    return NextResponse.json({
      success: true,
      isUpgrade,
      isDowngrade,
      effectiveDate: isDowngrade ? currentSubscription.current_period_end : 'immediately'
    })
    
  } catch (error) {
    console.error('Change plan error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

async function handleUpgrade(
  supabase: any,
  currentSubscription: any,
  newPlan: any,
  billingCycle: string,
  userId: string
) {
  // Calculate prorated amount
  const daysRemaining = Math.ceil(
    (new Date(currentSubscription.current_period_end).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  )
  
  const newPrice = billingCycle === 'yearly'
    ? newPlan.price_yearly_paise
    : newPlan.price_monthly_paise
  
  const currentPrice = billingCycle === 'yearly'
    ? currentSubscription.price_yearly_paise
    : currentSubscription.price_monthly_paise
  
  const priceDifference = newPrice - currentPrice
  const proratedAmount = Math.ceil((priceDifference * daysRemaining) / 30)
  
  // Create prorated charge
  const { error: transactionError } = await supabase
    .from('payment_transactions')
    .insert({
      user_id: userId,
      amount_paise: proratedAmount,
      status: 'pending',
      plan_id: newPlan.id,
      billing_cycle: billingCycle,
      description: `Prorated upgrade to ${newPlan.name}`
    })
  
  if (transactionError) throw transactionError
  
  // Update subscription
  const { error: updateError } = await supabase
    .from('subscriptions')
    .update({
      plan_id: newPlan.id,
      plan_name: newPlan.name,
      price_monthly_paise: newPlan.price_monthly_paise,
      price_yearly_paise: newPlan.price_yearly_paise,
      billing_cycle: billingCycle
    })
    .eq('id', currentSubscription.id)
  
  if (updateError) throw updateError
  
  return { error: null }
}

async function handleDowngrade(
  supabase: any,
  currentSubscription: any,
  newPlan: any,
  billingCycle: string,
  userId: string
) {
  // Schedule downgrade for end of period
  const { error: scheduledChangeError } = await supabase
    .from('scheduled_subscription_changes')
    .insert({
      subscription_id: currentSubscription.id,
      user_id: userId,
      new_plan_id: newPlan.id,
      new_plan_name: newPlan.name,
      new_billing_cycle: billingCycle,
      effective_date: currentSubscription.current_period_end,
      change_type: 'downgrade'
    })
  
  if (scheduledChangeError) throw scheduledChangeError
  
  return { error: null }
}

// Function to process scheduled changes (run daily)
export async function PATCH(request: Request) {
  if (request.headers.get('x-cron-job') !== 'process-scheduled-changes') {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    )
  
  try {
    // Get all scheduled changes due today
    const { data: scheduledChanges } = await supabase
      .from('scheduled_subscription_changes')
      .select('*')
      .lte('effective_date', new Date().toISOString())
      .eq('processed', false)
    
    if (!scheduledChanges || scheduledChanges.length === 0) {
      return NextResponse.json({ processed: 0 })
    }
    
    let processedCount = 0
    
    for (const change of scheduledChanges) {
      // Update subscription
      const { error: updateError } = await supabase
        .from('subscriptions')
        .update({
          plan_id: change.new_plan_id,
          plan_name: change.new_plan_name,
          billing_cycle: change.new_billing_cycle
        })
        .eq('id', change.subscription_id)
      
      if (!updateError) {
        // Mark as processed
        await supabase
          .from('scheduled_subscription_changes')
          .update({ processed: true, processed_at: new Date().toISOString() })
          .eq('id', change.id)
        
        // Send notification email
        await sendDowngradeNotification(supabase, change.user_id, change.new_plan_name)
        
        processedCount++
      }
    }
    
    return NextResponse.json({ processed: processedCount })
    
  } catch (error) {
    console.error('Process scheduled changes error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

async function sendDowngradeNotification(supabase: any, userId: string, newPlanName: string) {
  const { data: user } = await supabase
    .from('users')
    .select('email')
    .eq('id', userId)
    .single()
  
  if (!user) return
  
  // Send email notification
  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from: 'noreply@raptorflow.com',
      to: [user.email],
      subject: 'Your Subscription Plan Has Changed',
      html: `
        <h1>Subscription Plan Updated</h1>
        <p>Your subscription has been downgraded to ${newPlanName} as requested.</p>
        <p>The change is effective immediately. Your next billing date remains the same.</p>
        <p>If you have any questions, please contact our support team.</p>
      `
    })
  })
}
