import { NextResponse } from 'next/server'

// DEPRECATED: Custom MFA setup is removed (see ADR-0001-auth-unification.md).
// MFA is now handled exclusively via Supabase Auth MFA API:
//   supabase.auth.mfa.enroll()   — setup
//   supabase.auth.mfa.verify()   — verify
//   supabase.auth.mfa.unenroll() — disable
// This route returns 410 Gone to signal clients to migrate.

const GONE_RESPONSE = {
  error: 'This endpoint has been removed',
  migration: 'Use Supabase Auth MFA API (supabase.auth.mfa.*) instead',
  docs: 'https://supabase.com/docs/guides/auth/auth-mfa',
}

export async function POST() {
  return NextResponse.json(GONE_RESPONSE, { status: 410 })
}

export async function PUT() {
  return NextResponse.json(GONE_RESPONSE, { status: 410 })
}

export async function DELETE() {
  return NextResponse.json(GONE_RESPONSE, { status: 410 })
}
