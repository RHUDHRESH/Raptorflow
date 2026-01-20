/**
 * 🔐 LOGIN API ROUTE - Textbook Implementation
 * 
 * This is the most straightforward login API possible.
 * No magic, no complexity, just pure textbook authentication.
 * 
 * 📚 TEXTBOOK EXAMPLE:
 * 1. Client sends email/password
 * 2. Server validates credentials
 * 3. Server creates JWT token
 * 4. Server sets HttpOnly cookie
 * 5. Server returns success response
 */

import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/auth-helpers-nextjs';

type CookieOptions = Parameters<ReturnType<typeof NextResponse.json>['cookies']['set']>[2];
type PendingCookie = { name: string; value: string; options?: CookieOptions };

export async function POST(request: Request): Promise<Response> {
  const { email, password } = await request.json();

  if (!email || !password) {
    return NextResponse.json({ error: 'Email and password are required' }, { status: 400 });
  }

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
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });

  if (error || !data.user) {
    const response = NextResponse.json({ error: error?.message || 'Login failed' }, { status: 401 });
    pendingCookies.forEach(({ name, value, options }) => {
      response.cookies.set(name, value, options);
    });
    return response;
  }

  const response = NextResponse.json({
    user: {
      userId: data.user.id,
      email: data.user.email
    }
  }, { status: 200 });
  pendingCookies.forEach(({ name, value, options }) => {
    response.cookies.set(name, value, options);
  });
  return response;
}
