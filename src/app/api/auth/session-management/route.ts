import { NextResponse } from 'next/server';

// DEPRECATED: Custom session management removed (see ADR-0001-auth-unification.md).
// Session lifecycle is handled by Supabase Auth:
//   supabase.auth.getSession()    — current session
//   supabase.auth.signOut()       — revoke
//   supabase.auth.refreshSession() — extend
// This route returns 410 Gone to signal clients to migrate.

const GONE_RESPONSE = {
  error: 'This endpoint has been removed',
  migration: 'Use Supabase Auth session API (supabase.auth.getSession / signOut / refreshSession)',
  docs: 'https://supabase.com/docs/guides/auth/sessions',
};

export async function POST() {
  return NextResponse.json(GONE_RESPONSE, { status: 410 });
}

export async function GET() {
  return NextResponse.json(GONE_RESPONSE, { status: 410 });
}
