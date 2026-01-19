import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const { planId, billingCycle } = await request.json()

    const supabase = createServerSupabaseClient()

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

    // Allow plan selection from both states (user might navigate back)
    const validStates = ['pending_plan_selection', 'pending_payment']
    if (!user || !validStates.includes(user.onboarding_status)) {
      return NextResponse.json(
        { error: 'Invalid onboarding state' },
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

    // Create or update subscription
    const { error: subError } = await supabase
      .from('subscriptions')
      .upsert({
        user_id: user.id,
        plan_id: plan.id,
        plan_name: plan.name,
        price_monthly_paise: plan.price_monthly_paise,
        billing_cycle: billingCycle || 'monthly',
        status: 'pending'
      }, {
        onConflict: 'user_id'
      })

    if (subError) {
      console.error('Subscription error:', subError)
      return NextResponse.json(
        { error: 'Failed to select plan' },
        { status: 500 }
      )
    }

    // Update user onboarding status
    await supabase
      .from('users')
      .update({ onboarding_status: 'pending_payment' })
      .eq('id', user.id)

    // Log the action
    await supabase.from('audit_logs').insert({
      actor_id: user.id,
      action: 'plan_selected',
      action_category: 'onboarding',
      description: `Selected plan: ${plan.name} (${billingCycle})`,
      ip_address: request.headers.get('x-forwarded-for') || 'unknown',
      user_agent: request.headers.get('user-agent') || 'unknown',
    })

    return NextResponse.json({ success: true })

  } catch (err) {
    console.error('Select plan error:', err)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
