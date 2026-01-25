import { createServerClient } from '@supabase/ssr';
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { getProfileByAuthUserId, upsertProfileForAuthUser } from '@/lib/auth-server';

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');

  console.log('🔍 Auth callback started', {
    code: !!code,
    url: request.url,
    supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL ? 'SET' : 'NOT_SET',
    anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? 'SET' : 'NOT_SET',
    anonKeyLength: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.length || 0,
    anonKeyPreview: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.substring(0, 20) + '...',
    serviceKey: process.env.SUPABASE_SERVICE_ROLE_KEY ? 'SET' : 'NOT_SET'
  });

  if (code) {
    try {
      const cookieStore = await cookies();

      // Create Supabase client with proper cookie handling
      // For code exchange, use anon key (service role key may not work for OAuth)
      const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
          cookies: {
            get(name: string) {
              return cookieStore.get(name)?.value
            },
            set(name: string, value: string, options: any) {
              try {
                cookieStore.set({ name, value, ...options })
              } catch {
                // Ignore cookie setting errors in callback
              }
            },
            remove(name: string, options: any) {
              try {
                cookieStore.set({ name, value: '', ...options })
              } catch {
                // Ignore cookie deletion errors in callback
              }
            },
          },
        }
      );

      console.log('🔐 Exchanging code for session...');
      const { data: { session }, error } = await supabase.auth.exchangeCodeForSession(code);

      if (error) {
        console.error('❌ Auth callback error:', {
          message: error.message,
          status: error.status,
          code: error.code,
          details: error
        });
        return NextResponse.redirect(`${requestUrl.origin}/login?error=auth_failed&reason=${encodeURIComponent(error.message)}`);
      }

      if (session?.user) {
        console.log('✅ Auth successful for user:', session.user.email);

        // Wait for database trigger to create profile with polling instead of blocking setTimeout
        let attempts = 0;
        const maxAttempts = 15; // 15 attempts with 200ms delay = 3 seconds max
        let profile = null;
        let profileSource = null;

        while (attempts < maxAttempts) {
          const result = await getProfileByAuthUserId(supabase, session.user.id)
          profile = result.profile
          profileSource = result.source

          if (profile) {
            break
          }

          // Wait before next attempt
          await new Promise(resolve => setTimeout(resolve, 200));
          attempts++;
        }

        console.log('📊 Profile query result:', { profile, profileSource, attempts });

        // Handle profile creation if it doesn't exist
        if (!profile) {
          console.log('📝 Profile not found, creating...');
          const created = await upsertProfileForAuthUser(supabase, session.user)

          if (!created.profile) {
            console.error('❌ Profile creation error')
          }

          // New users go to plans page first (payment required before onboarding)
          console.log('✅ Redirecting new user to /onboarding/plans (payment required)');
          return NextResponse.redirect(`${requestUrl.origin}/onboarding/plans`);
        }

        // Determine redirect based on subscription and onboarding status
        const subscriptionStatus = profile?.subscription_status;
        const onboardingStatus = profile?.onboarding_status;
        const subscriptionPlan = profile?.subscription_plan;

        console.log('📊 User status:', { subscriptionStatus, onboardingStatus, subscriptionPlan });

        // ROUTING LOGIC (Payment Required First):
        // 1. No active subscription → Plans page (PhonePe payment required)
        // 2. Active subscription but onboarding not complete → Onboarding Step 1
        // 3. Active subscription + onboarding complete → Dashboard

        // If no active subscription, user MUST pay via PhonePe first
        if (subscriptionStatus !== 'active' || !subscriptionPlan) {
          console.log('✅ Redirecting to /onboarding/plans (payment required before onboarding)');
          return NextResponse.redirect(`${requestUrl.origin}/onboarding/plans`);
        }

        // User paid but hasn't completed onboarding - now they can access onboarding
        if (onboardingStatus !== 'active') {
          console.log('✅ Redirecting to /onboarding/session/step/1 (payment confirmed, starting onboarding)');
          return NextResponse.redirect(`${requestUrl.origin}/onboarding/session/step/1`);
        }

        // Fully onboarded user with active subscription
        console.log('✅ Redirecting to /dashboard (fully onboarded)');
        return NextResponse.redirect(`${requestUrl.origin}/dashboard`);
      }
    } catch (error) {
      console.error('❌ Auth callback error:', error);
      return NextResponse.redirect(`${requestUrl.origin}/login?error=auth_failed&reason=callback_error`);
    }
  }

  // If no code, redirect to login
  console.log('❌ No auth code found, redirecting to login');
  return NextResponse.redirect(`${requestUrl.origin}/login`);
}
