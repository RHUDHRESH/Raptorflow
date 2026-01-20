/**
 * 🔐 LOGOUT API ROUTE - Textbook Implementation
 * 
 * This is the most straightforward logout API possible.
 * No magic, no complexity, just pure textbook authentication.
 * 
 * 📚 TEXTBOOK EXAMPLE:
 * 1. Client requests logout
 * 2. Server clears auth cookie
 * 3. Server returns success response
 */

import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { createServerClient } from '@supabase/auth-helpers-nextjs';

type CookieOptions = Parameters<ReturnType<typeof NextResponse.json>['cookies']['set']>[2];
type PendingCookie = { name: string; value: string; options?: CookieOptions };

export async function POST(): Promise<Response> {
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
  await supabase.auth.signOut();
  const response = NextResponse.json({ success: true }, { status: 200 });
  pendingCookies.forEach(({ name, value, options }) => {
    response.cookies.set(name, value, options);
  });
  return response;
}
