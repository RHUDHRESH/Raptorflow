import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

// Lazy client creation to avoid build-time errors
function getSupabaseAdmin() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error('Missing Supabase configuration');
  }

  return createClient(url, key);
}

export async function GET() {
  const results: any = {}

  try {
    const supabaseAdmin = getSupabaseAdmin();

    // Direct table check with service role key
    const { data: profiles, error: profilesError } = await supabaseAdmin
      .from('user_profiles')
      .select('count')
      .limit(1)

    results.user_profiles_exists = !profilesError && profiles.length > 0

    const { data: payments, error: paymentsError } = await supabaseAdmin
      .from('payments')
      .select('count')
      .limit(1)

    results.payments_exists = !paymentsError && payments.length > 0

    // Test if we can create a test record
    const testId = `test-${Date.now()}`
    const { error: insertError } = await supabaseAdmin
      .from('user_profiles')
      .insert({
        id: testId,
        email: 'test@example.com',
        full_name: 'Test User',
        storage_quota_mb: 100,
        storage_used_mb: 0
      })

    results.test_insert = !insertError

    // Clean up
    if (!insertError) {
      await supabaseAdmin
        .from('user_profiles')
        .delete()
        .eq('id', testId)
    }

    return NextResponse.json(results)
  } catch (error: any) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 500 })
  }
}
