import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const supabase = createServerSupabaseClient()

    // Get current user session
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // First get the user ID from public.users
    const { data: user } = await supabase
      .from('users')
      .select('id')
      .eq('auth_user_id', session.user.id)
      .single()

    if (!user) {
      return NextResponse.json({ selectedPlan: null })
    }

    // Get user's pending subscription with plan details
    const { data: subscription } = await supabase
      .from('subscriptions')
      .select(`
        id,
        plan_id,
        plan_name,
        billing_cycle,
        price_monthly_paise,
        status
      `)
      .eq('user_id', user.id)
      .eq('status', 'pending')
      .single()

    if (!subscription) {
      return NextResponse.json({ selectedPlan: null })
    }

    // Get the full plan details
    const { data: plan } = await supabase
      .from('plans')
      .select('*')
      .eq('id', subscription.plan_id)
      .single()

    // Enforce latest 2026 industrial pricing on the response
    const planData = plan || {
      id: subscription.plan_id,
      name: subscription.plan_name,
      price_monthly_paise: subscription.price_monthly_paise,
      price_yearly_paise: subscription.price_monthly_paise * 10
    };

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
