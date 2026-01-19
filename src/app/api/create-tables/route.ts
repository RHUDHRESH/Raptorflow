import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function POST() {
  const results: any = { success: false, steps: [] }

  try {
    // Create user_profiles table using raw SQL
    const createProfilesSQL = `
      CREATE TABLE IF NOT EXISTS public.user_profiles (
        id UUID REFERENCES auth.users(id) PRIMARY KEY,
        email TEXT NOT NULL,
        full_name TEXT,
        avatar_url TEXT,
        subscription_plan TEXT CHECK (subscription_plan IN ('soar', 'glide', 'ascent')),
        subscription_status TEXT CHECK (subscription_status IN ('active', 'cancelled', 'expired')),
        subscription_expires_at TIMESTAMPTZ,
        storage_quota_mb INTEGER DEFAULT 100,
        storage_used_mb INTEGER DEFAULT 0,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
      );

      ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

      DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
      DROP POLICY IF EXISTS "Users can update own profile" ON public.user_profiles;
      DROP POLICY IF EXISTS "Users can insert own profile" ON public.user_profiles;

      CREATE POLICY "Users can view own profile" ON public.user_profiles
        FOR SELECT USING (auth.uid() = id);
      CREATE POLICY "Users can update own profile" ON public.user_profiles
        FOR UPDATE USING (auth.uid() = id);
      CREATE POLICY "Users can insert own profile" ON public.user_profiles
        FOR INSERT WITH CHECK (auth.uid() = id);
    `

    // Create payments table using raw SQL
    const createPaymentsSQL = `
      CREATE TABLE IF NOT EXISTS public.payments (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users(id) NOT NULL,
        transaction_id TEXT UNIQUE NOT NULL,
        plan_id TEXT NOT NULL CHECK (plan_id IN ('soar', 'glide', 'ascent')),
        amount INTEGER NOT NULL,
        currency TEXT DEFAULT 'INR',
        status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
        payment_method TEXT DEFAULT 'phonepe',
        phonepe_transaction_id TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        verified_at TIMESTAMPTZ
      );

      ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

      DROP POLICY IF EXISTS "Users can view own payments" ON public.payments;
      CREATE POLICY "Users can view own payments" ON public.payments
        FOR SELECT USING (auth.uid() = user_id);
    `

    // Execute the SQL using Supabase's SQL editor endpoint
    // Since we can't execute arbitrary SQL directly, we'll use a workaround
    // by creating the tables through the Supabase dashboard

    results.steps.push('✅ SQL generated for user_profiles table')
    results.steps.push('✅ SQL generated for payments table')
    results.profiles_sql = createProfilesSQL
    results.payments_sql = createPaymentsSQL
    results.instructions = `
      1. Go to https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/sql
      2. Copy and paste the SQL from the profiles_sql field
      3. Click "Run" to execute
      4. Copy and paste the SQL from the payments_sql field
      5. Click "Run" to execute
    `

    results.success = true
    return NextResponse.json(results)

  } catch (error: any) {
    results.error = error.message
    return NextResponse.json(results, { status: 500 })
  }
}
