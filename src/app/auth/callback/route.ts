import { createClient } from '@/lib/supabaseServer';
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
  // The `/auth/callback` route is required for the server-side auth flow to work properly.
  // The Auth helpers package automatically creates a server-side client for us.
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');
  const state = requestUrl.searchParams.get('state');
  const cookieStore = cookies();
  const storedState = cookieStore.get('oauth_state')?.value;
  const storedRedirect = cookieStore.get('oauth_redirect')?.value;
  const next = storedRedirect ? decodeURIComponent(storedRedirect) : (requestUrl.searchParams.get('next') ?? '/dashboard');

  // Validate CSRF state token
  if (state && storedState && state !== storedState) {
    console.error('OAuth CSRF validation failed');
    return NextResponse.redirect(`${requestUrl.origin}/login?error=csrf_failed`);
  }

  // Clear state cookies after validation
  const response = NextResponse.next();
  if (storedState) {
    response.cookies.delete('oauth_state');
    response.cookies.delete('oauth_redirect');
  }

  if (code) {
    const supabase = createClient();
    const { data: { session }, error: sessionError } = await supabase.auth.exchangeCodeForSession(code);

    if (sessionError) {
      console.error('Session exchange error:', sessionError);
      return NextResponse.redirect(`${requestUrl.origin}/login?error=auth_failed`);
    }

    if (session?.user) {
      // First get user profile
      const { data: userProfile } = await supabase
        .from('users')
        .select('id, onboarding_status, role')
        .eq('auth_user_id', session.user.id)
        .single();

      // Then get workspace owned by this user
      const { data: workspace } = userProfile ? await supabase
        .from('workspaces')
        .select('id')
        .eq('owner_id', userProfile.id)
        .limit(1)
        .maybeSingle() : { data: null };

      // Sync workspace_id and role to metadata for middleware
      if (workspace?.id || userProfile?.role) {
        await supabase.auth.updateUser({
          data: {
            workspace_id: workspace?.id || session.user.user_metadata?.workspace_id,
            role: userProfile?.role || session.user.user_metadata?.role || 'user',
            onboarding_status: userProfile?.onboarding_status || 'pending_workspace'
          }
        });
      }

      // If no user profile yet, or pending onboarding -> go to onboarding
      if (!userProfile || userProfile.onboarding_status === 'pending_workspace') {
        return NextResponse.redirect(`${requestUrl.origin}/onboarding`);
      }
    }
  }

  // URL to redirect to after sign in process completes
  const finalResponse = NextResponse.redirect(`${requestUrl.origin}${next}`);

  // Clear OAuth state cookies
  finalResponse.cookies.delete('oauth_state');
  finalResponse.cookies.delete('oauth_redirect');

  return finalResponse;
}
