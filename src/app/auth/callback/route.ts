import { createClient } from '@/lib/supabaseServer';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  // The `/auth/callback` route is required for the server-side auth flow to work properly.
  // The Auth helpers package automatically creates a server-side client for us.
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get('code');
  const next = requestUrl.searchParams.get('next') ?? '/dashboard';

  if (code) {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.exchangeCodeForSession(code);

    if (session?.user) {
      // Check profile and workspace to ensure session metadata is synced
      const [{ data: profile }, { data: workspace }] = await Promise.all([
        supabase
          .from('profiles')
          .select('ucid, onboarding_status, role')
          .eq('id', session.user.id)
          .single(),
        supabase
          .from('workspaces')
          .select('id')
          .or(`owner_id.eq.${session.user.id},user_id.eq.${session.user.id}`)
          .limit(1)
          .maybeSingle()
      ]);

      // Sync workspace_id and role to metadata for middleware
      if (workspace?.id || profile?.role) {
        await supabase.auth.updateUser({
          data: {
            workspace_id: workspace?.id || session.user.user_metadata?.workspace_id,
            role: profile?.role || session.user.user_metadata?.role || 'user',
            onboarding_status: profile?.onboarding_status || 'pending'
          }
        });
      }

      // If no profile yet, or no UCID, or pending onboarding -> go to onboarding
      if (!profile || !profile.ucid || profile.onboarding_status === 'pending') {
        return NextResponse.redirect(`${requestUrl.origin}/onboarding`);
      }
    }
  }

  // URL to redirect to after sign in process completes
  return NextResponse.redirect(`${requestUrl.origin}${next}`);
}
