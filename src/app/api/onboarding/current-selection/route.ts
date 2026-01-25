import { createServerSupabaseClient, createServiceSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'
export const revalidate = 0

export async function GET() {
  try {
    // Prefer service client to bypass RLS issues during onboarding, fallback to server client
    let supabase
    try {
      supabase = await createServiceSupabaseClient()
    } catch {
      supabase = await createServerSupabaseClient()
    }

    // Get current user session
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // First get the user ID; try public.users then profiles as fallback
    const { data: user } = await supabase
      .from('users')
      .select('id')
      .eq('auth_user_id', session.user.id)
      .single()

    const userId = user?.id || (await supabase
      .from('profiles')
      .select('id')
      .eq('auth_user_id', session.user.id)
      .single()
    ).data?.id

    if (!userId) {
      return NextResponse.json({ selectedPlan: null })
    }

    console.log('🔍 current-selection: userId', userId)

    // Get user's most recent subscription with plan details from user_subscriptions (any status)
    let { data: subscription } = await supabase
      .from('user_subscriptions')
      .select(`
        id,
        plan_id,
        billing_cycle,
        amount_paid,
        status,
        subscription_plans ( slug, name, price_monthly, price_annual, features )
      `)
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(1)
      .single()

    // Fallback: if nothing found, fetch latest non-cancelled subscription
    if (!subscription) {
      console.log('ℹ️ current-selection: no subscription found, checking latest non-cancelled')
      const { data: latest } = await supabase
        .from('user_subscriptions')
        .select(`
          id,
          plan_id,
          billing_cycle,
          amount_paid,
          status,
          subscription_plans ( slug, name, price_monthly, price_annual, features )
        `)
        .eq('user_id', userId)
        .not('status', 'in', '({"cancelled","refunded"})')
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      subscription = latest || null
    }

    // Legacy fallback: check subscriptions table if user_subscriptions empty
    if (!subscription) {
      console.log('ℹ️ current-selection: checking legacy subscriptions table')
      const { data: legacy } = await supabase
        .from('subscriptions')
        .select(`
          id,
          plan_id,
          plan_name,
          billing_cycle,
          price_monthly_paise,
          status
        `)
        .eq('user_id', userId)
        .in('status', ['pending', 'pending_payment', 'active'])
        .order('created_at', { ascending: false })
        .limit(1)
        .single()

      if (legacy) {
        subscription = {
          ...legacy,
          amount_paid: legacy.price_monthly_paise,
          subscription_plans: null
        } as any
      }
    }

    if (!subscription) {
      console.log('⚠️ current-selection: no subscription found')
      return NextResponse.json({ selectedPlan: null })
    }

    console.log('✅ current-selection: subscription found', {
      id: subscription.id,
      status: subscription.status,
      plan_id: subscription.plan_id,
      billing_cycle: subscription.billing_cycle,
    })

    const planRelation = subscription.subscription_plans
    const plan = Array.isArray(planRelation) ? planRelation[0] : planRelation

    // Build plan data even if join is missing
    const planId = plan?.slug || subscription.plan_id || 'ascent'
    const planName = plan?.name || subscription.plan_id || 'Ascent'
    const planData = {
      id: planId,
      name: planName,
      price_monthly_paise: plan?.price_monthly ?? subscription.amount_paid ?? 0,
      price_yearly_paise: plan?.price_annual ?? ((subscription.amount_paid ?? 0) * 10)
    }

    // Enforce latest 2026 industrial pricing on known slugs
    if (planData.id === 'ascent') {
      planData.price_monthly_paise = 500000;
      planData.price_yearly_paise = 5000000;
    } else if (planData.id === 'glide') {
      planData.price_monthly_paise = 700000;
      planData.price_yearly_paise = 7000000;
    } else if (planData.id === 'soar') {
      planData.price_monthly_paise = 1000000;
      planData.price_yearly_paise = 10000000;
    }

    return NextResponse.json({
      selectedPlan: {
        plan: planData,
        billingCycle: subscription.billing_cycle || 'monthly'
      }
    })

  } catch (err) {
    console.error('Current selection error:', err)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
