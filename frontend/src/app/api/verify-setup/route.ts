import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

export async function GET() {
  const results: any = {
    supabase: { connected: false, error: null },
    tables: { user_profiles: false, payments: false },
    auth: { working: false },
    storage: { buckets: [] }
  }

  try {
    // Test Supabase connection
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    )

    // Test basic connection
    const { data: { session }, error: sessionError } = await supabase.auth.getSession()
    if (!sessionError) {
      results.supabase.connected = true
    } else {
      results.supabase.error = sessionError.message
    }

    // Test tables
    try {
      const { data: profiles, error: profilesError } = await supabase
        .from('user_profiles')
        .select('count')
        .limit(1)
      results.tables.user_profiles = !profilesError
    } catch (e) {
      results.tables.user_profiles = false
    }

    try {
      const { data: payments, error: paymentsError } = await supabase
        .from('payments')
        .select('count')
        .limit(1)
      results.tables.payments = !paymentsError
    } catch (e) {
      results.tables.payments = false
    }

    // Test auth
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: 'http://localhost:3000' }
      })
      results.auth.working = !error
    } catch (e) {
      results.auth.working = false
    }

    // Check storage buckets (if service role key available)
    if (process.env.SUPABASE_SERVICE_ROLE_KEY && process.env.SUPABASE_SERVICE_ROLE_KEY !== 'your-service-role-key-here') {
      const adminClient = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.SUPABASE_SERVICE_ROLE_KEY!
      )

      try {
        const { data: buckets } = await adminClient.storage.listBuckets()
        results.storage.buckets = buckets || []
      } catch (e) {
        results.storage.buckets = []
      }
    }

  } catch (error: any) {
    results.error = error.message
  }

  return NextResponse.json(results)
}
