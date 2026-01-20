/**
 * 📊 SUBSCRIPTION STATUS API
 * Returns user's current subscription, workspace, and onboarding status
 */

import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/auth-helpers-nextjs';

type CookieOptions = Parameters<ReturnType<typeof NextResponse.json>['cookies']['set']>[2];
type PendingCookie = { name: string; value: string; options?: CookieOptions };

export async function GET() {
  try {
    const cookieStore = await cookies();
    const pendingCookies: PendingCookie[] = [];
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll: () => cookieStore.getAll(),
          setAll: (cookiesToSet) => {
            pendingCookies.push(...cookiesToSet);
          }
        }
      }
    );
    const { data: { user }, error } = await supabase.auth.getUser();

    if (error || !user) {
      const response = NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      pendingCookies.forEach(({ name, value, options }) => {
        response.cookies.set(name, value, options);
      });
      return response;
    }

    const userId = user.id;

    // Get subscription data directly from table
    const { data: subscriptionData, error: subError } = await supabase
      .from('subscriptions')
      .select('*')
      .eq('user_id', userId)
      .eq('status', 'active')
      .single();

    // Get workspace data
    const { data: workspaceData, error: wsError } = await supabase
      .from('workspaces')
      .select('*')
      .eq('user_id', userId)
      .single();

    const { data: onboardingSession } = workspaceData
      ? await supabase
          .from('onboarding_sessions')
          .select('status, current_step')
          .eq('workspace_id', workspaceData.id)
          .maybeSingle()
      : { data: null };

    // Build response
    const subscription = subscriptionData ? {
      hasSubscription: true,
      planId: subscriptionData.plan_id,
      planName: subscriptionData.plan_name,
      planSlug: subscriptionData.plan_slug,
      status: subscriptionData.status,
      expiresAt: subscriptionData.expires_at,
      createdAt: subscriptionData.created_at,
    } : {
      hasSubscription: false,
      planId: null,
      planName: null,
      planSlug: null,
      status: null,
      expiresAt: null,
      createdAt: null,
    };

    const workspace = workspaceData ? {
      hasWorkspace: true,
      workspaceId: workspaceData.id,
      workspaceName: workspaceData.name,
      onboardingCompleted: onboardingSession?.status === 'completed',
      onboardingStep: onboardingSession?.current_step ?? 1,
      businessContextUrl: null,
    } : {
      hasWorkspace: false,
      workspaceId: null,
      workspaceName: null,
      onboardingCompleted: false,
      onboardingStep: 0,
      businessContextUrl: null,
    };

    const response = NextResponse.json({
      success: true,
      user: {
        id: userId,
        email: user.email,
      },
      subscription,
      workspace,
      canAccessApp: subscription.hasSubscription && workspace.hasWorkspace,
    });
    pendingCookies.forEach(({ name, value, options }) => {
      response.cookies.set(name, value, options);
    });
    return response;

  } catch (error) {
    console.error('Subscription status error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

