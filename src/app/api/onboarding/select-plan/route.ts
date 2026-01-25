import { createServerSupabaseClient, createServiceSupabaseClient, getProfileByAuthUserId, upsertProfileForAuthUser, updateProfileRecord } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const { planId, billingCycle } = await request.json()

    const supabase = await createServerSupabaseClient()
    
    // Use getUser() for secure authentication (not getSession which can be spoofed)
    const { data: { user: authUser }, error: authError } = await supabase.auth.getUser()

    if (authError || !authUser) {
      console.error('❌ Auth error in select-plan:', authError?.message)
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Use service client for profile operations to bypass RLS issues during onboarding
    const serviceClient = await createServiceSupabaseClient()
    const { profile: initialProfile } = await getProfileByAuthUserId(serviceClient, authUser.id)
    let user = initialProfile

    console.log('📊 User profile lookup:', { user, userId: authUser.id })

    // Allow plan selection from multiple states (new users, navigating back, etc.)
    // 'pending' = new user from OAuth
    // 'pending_plan_selection' = user in plan selection flow  
    // 'pending_payment' = user navigating back from payment
    // 'none' = fallback for edge cases
    const validStates = ['pending', 'pending_plan_selection', 'pending_payment', 'none', null, undefined]
    if (!user) {
      console.warn('⚠️ Profile missing, attempting to create profile')
      const created = await upsertProfileForAuthUser(serviceClient, authUser)

      if (!created.profile) {
        console.error('❌ Failed to create profile for user:', authUser.id)
        return NextResponse.json(
          { error: 'User profile not found. Please try logging in again.' },
          { status: 404 }
        )
      }

      user = created.profile
      console.log('✅ Profile created successfully:', user.id)
    }

    if (!validStates.includes(user.onboarding_status)) {
      console.error('❌ Invalid onboarding status:', user.onboarding_status)
      return NextResponse.json(
        { error: `Invalid onboarding state: ${user.onboarding_status}` },
        { status: 400 }
      )
    }

    // Get plan (use service client to avoid RLS issues)
    // Try subscription_plans first, then fallback to plans table
    let plan = null;
    let planError = null;

    // Try subscription_plans table
    const { data: planData, error: subPlanError } = await serviceClient
      .from('subscription_plans')
      .select('*')
      .eq('slug', planId)
      .single();

    if (!subPlanError && planData) {
      plan = planData;
    } else {
      // Fallback to plans table
      const { data: fallbackPlan, error: fallbackError } = await serviceClient
        .from('plans')
        .select('*')
        .eq('slug', planId)
        .single();
      
      plan = fallbackPlan;
      planError = fallbackError;
    }

    if (planError) {
      console.error('❌ Plan fetch error:', planError.message)
    }

    if (!plan) {
      return NextResponse.json({ error: 'Plan not found' }, { status: 404 })
    }

    // Create subscription using the new unified schema function
    const { data: subscription, error: subError } = await serviceClient
      .rpc('create_user_subscription', {
        p_user_id: user.id,
        p_plan_slug: planId,
        p_billing_cycle: billingCycle || 'monthly',
        p_phonepe_order_id: null, // Will be set after payment
        p_amount_paid: billingCycle === 'annual' ? plan.price_annual : plan.price_monthly
      });

    if (subError) {
      console.error('❌ Subscription error:', {
        message: subError.message,
        code: subError.code,
        details: subError.details,
        hint: subError.hint,
        userId: user.id,
        planId: plan.id
      })
      return NextResponse.json(
        { error: `Failed to select plan: ${subError.message}` },
        { status: 500 }
      )
    }

    console.log('✅ Subscription created/updated for user:', user.id)

    // Update user onboarding status in profiles table
    const updateResult = await updateProfileRecord(
      serviceClient,
      { authUserId: authUser.id, profileId: user.id },
      { onboarding_status: 'pending_payment', updated_at: new Date().toISOString() }
    )

    if (!updateResult.success) {
      console.error('Profile update error')
    }

    // Log the action (use service client)
    await serviceClient.from('audit_logs').insert({
      actor_id: user.id,
      action: 'plan_selected',
      action_category: 'onboarding',
      description: `Selected plan: ${plan.name} (${billingCycle})`,
      ip_address: request.headers.get('x-forwarded-for') || 'unknown',
      user_agent: request.headers.get('user-agent') || 'unknown',
    }).then(({ error }: any) => {
      if (error) console.warn('Audit log error:', error)
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
