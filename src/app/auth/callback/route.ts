import { createClient } from '@/lib/supabaseServer';
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { sendWelcomeEmail } from '@/lib/email';

export async function GET(request: Request) {
  // The `/auth/callback` route is required for the server-side auth flow to work properly.
  // The Auth helpers package automatically creates a server-side client for us.
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');
  const state = requestUrl.searchParams.get('state');
  const cookieStore = await cookies();
  const storedState = cookieStore.get('oauth_state')?.value;
  const storedRedirect = cookieStore.get('oauth_redirect')?.value;
  const next = storedRedirect ? decodeURIComponent(storedRedirect) : (requestUrl.searchParams.get('next') ?? '/dashboard');

  // Validate CSRF state token
  if (state && storedState && state !== storedState) {
    console.error('OAuth CSRF validation failed');
    return NextResponse.redirect(`${requestUrl.origin}/signin?error=csrf_failed`);
  }

  // Clear state cookies after validation
  const response = NextResponse.next();
  if (storedState) {
    response.cookies.delete('oauth_state');
    response.cookies.delete('oauth_redirect');
  }

  if (code) {
    const supabase = await createClient();
    const { data: { session }, error: sessionError } = await supabase.auth.exchangeCodeForSession(code);

    if (sessionError) {
      console.error('Session exchange error:', sessionError);
      return NextResponse.redirect(`${requestUrl.origin}/signin?error=auth_failed`);
    }

    if (session?.user) {
      // First check if user profile exists
      const { data: userProfile } = await supabase
        .from('users')
        .select('id, onboarding_status, role, email, full_name')
        .eq('auth_user_id', session.user.id)
        .single();

      let isNewUser = false;
      let profileId = userProfile?.id;

      // Create profile if it doesn't exist (new user)
      if (!userProfile) {
        isNewUser = true;
        const userEmail = session.user.email || '';
        const userName = session.user.user_metadata?.full_name ||
                        session.user.user_metadata?.name ||
                        userEmail.split('@')[0] || 'User';
        const avatarUrl = session.user.user_metadata?.avatar_url ||
                         session.user.user_metadata?.picture || null;

        const { data: newProfile, error: createError } = await supabase
          .from('users')
          .insert({
            auth_user_id: session.user.id,
            email: userEmail,
            full_name: userName,
            avatar_url: avatarUrl,
            onboarding_status: 'pending_workspace',
            role: 'user',
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })
          .select('id')
          .single();

        if (createError) {
          console.error('Failed to create user profile:', createError);
        } else {
          profileId = newProfile?.id;

          // Send welcome email for new users
          try {
            await sendWelcomeEmail(userEmail, userName);
            console.log('Welcome email sent to:', userEmail);
          } catch (emailError) {
            console.error('Failed to send welcome email:', emailError);
            // Don't fail auth if email fails
          }
        }
      }

      // Get workspace owned by this user
      const { data: workspace } = profileId ? await supabase
        .from('workspaces')
        .select('id')
        .eq('owner_id', profileId)
        .limit(1)
        .maybeSingle() : { data: null };

      // Sync workspace_id and role to metadata for middleware
      const currentStatus = userProfile?.onboarding_status || 'pending_workspace';
      await supabase.auth.updateUser({
        data: {
          workspace_id: workspace?.id || session.user.user_metadata?.workspace_id,
          role: userProfile?.role || session.user.user_metadata?.role || 'user',
          onboarding_status: currentStatus
        }
      });

      // If no user profile yet, or pending onboarding -> go to onboarding
      if (isNewUser || !userProfile || userProfile.onboarding_status === 'pending_workspace') {
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
