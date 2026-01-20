/**
 * 🔐 CURRENT USER API ROUTE - Textbook Implementation
 * 
 * This is the most straightforward user info API possible.
 * No magic, no complexity, just pure textbook authentication.
 * 
 * 📚 TEXTBOOK EXAMPLE:
 * 1. Client requests current user info
 * 2. Server checks auth cookie
 * 3. Server verifies JWT token
 * 4. Server returns user data if valid
 */

import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/auth-helpers-nextjs';

type CookieOptions = Parameters<ReturnType<typeof NextResponse.json>['cookies']['set']>[2];
type PendingCookie = { name: string; value: string; options?: CookieOptions };

export async function GET(): Promise<Response> {
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
    const response = NextResponse.json({ error: 'Not authenticated' }, { status: 401 });
    pendingCookies.forEach(({ name, value, options }) => {
      response.cookies.set(name, value, options);
    });
    return response;
  }

  const response = NextResponse.json({
    user: {
      userId: user.id,
      email: user.email
    }
  }, { status: 200 });
  pendingCookies.forEach(({ name, value, options }) => {
    response.cookies.set(name, value, options);
  });
  return response;
}
