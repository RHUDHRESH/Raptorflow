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
      // Check profile for UCID and onboarding status
      const { data: profile } = await supabase
        .from('profiles')
        .select('ucid, onboarding_status')
        .eq('id', session.user.id)
        .single();

      // If no profile yet, or no UCID, or pending onboarding -> go to onboarding
      if (!profile || !profile.ucid || profile.onboarding_status === 'pending') {
        return NextResponse.redirect(`${requestUrl.origin}/onboarding`);
      }
    }
  }

  // URL to redirect to after sign in process completes
  return NextResponse.redirect(`${requestUrl.origin}${next}`);
}
