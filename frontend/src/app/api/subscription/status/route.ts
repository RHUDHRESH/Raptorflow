/**
 * 📊 SUBSCRIPTION STATUS API
 * Returns user's current subscription, workspace, and onboarding status
 */

import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase client
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export async function GET(request: NextRequest) {
  try {
    // Get user from authentication
    const authResponse = await fetch(`${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/api/auth/me`, {
      headers: request.headers,
    });

    if (!authResponse.ok) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const authData = await authResponse.json();
    const user = authData.user;

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    const userId = user.userId;

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
      .eq('owner_id', userId)
      .single();

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
      onboardingCompleted: workspaceData.onboarding_completed || false,
      onboardingStep: workspaceData.onboarding_step || 1,
      businessContextUrl: workspaceData.business_context_url || null,
    } : {
      hasWorkspace: false,
      workspaceId: null,
      workspaceName: null,
      onboardingCompleted: false,
      onboardingStep: 0,
      businessContextUrl: null,
    };

    return NextResponse.json({
      success: true,
      user: {
        id: userId,
        email: user.email,
      },
      subscription,
      workspace,
      canAccessApp: subscription.hasSubscription && workspace.hasWorkspace,
    });

  } catch (error) {
    console.error('Subscription status error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

