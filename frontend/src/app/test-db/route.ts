import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function GET() {
  const results: any = {}

  // Test basic connection
  try {
    const { data, error } = await supabase
      .from('_test_connection')
      .select('*')
      .limit(1)
    results.basic = { success: !error, error: error?.message }
  } catch (e: any) {
    results.basic = { success: false, error: e.message }
  }

  // Check if user_profiles exists
  try {
    const { data, error } = await supabase
      .from('user_profiles')
      .select('count')
      .limit(1)
    results.user_profiles = { exists: !error, error: error?.message }
  } catch (e: any) {
    results.user_profiles = { exists: false, error: e.message }
  }

  // Check if payments exists
  try {
    const { data, error } = await supabase
      .from('payments')
      .select('count')
      .limit(1)
    results.payments = { exists: !error, error: error?.message }
  } catch (e: any) {
    results.payments = { exists: false, error: e.message }
  }

  // List all tables
  try {
    const { data, error } = await supabase
      .rpc('get_tables')
    results.tables = data || error?.message
  } catch (e: any) {
    results.tables = e.message
  }

  // Check auth.users
  try {
    const { data, error } = await supabase.auth.admin.listUsers()
    results.auth_users = {
      count: data.users?.length || 0,
      error: error?.message
    }
  } catch (e: any) {
    results.auth_users = { error: e.message }
  }

  return NextResponse.json(results)
}
