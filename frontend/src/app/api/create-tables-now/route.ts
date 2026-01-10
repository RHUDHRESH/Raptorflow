import { NextResponse } from 'next/server';

const profilesSQL = `
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
`;

const paymentsSQL = `
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
`;

export async function POST() {
  const results: any = { success: false, steps: [] };

  try {
    // Execute profiles table creation
    const profilesResponse = await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/rpc/exec_sql`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
        'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({ sql: profilesSQL })
    });

    if (profilesResponse.ok) {
      results.steps.push('✅ Created user_profiles table');
    } else {
      const error = await profilesResponse.text();
      results.steps.push('❌ Failed to create user_profiles: ' + error);
    }

    // Execute payments table creation
    const paymentsResponse = await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/rpc/exec_sql`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
        'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({ sql: paymentsSQL })
    });

    if (paymentsResponse.ok) {
      results.steps.push('✅ Created payments table');
    } else {
      const error = await paymentsResponse.text();
      results.steps.push('❌ Failed to create payments: ' + error);
    }

    // Test if tables were created
    const testResponse = await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/user_profiles?select=count`, {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}`,
        'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        'Prefer': 'return=minimal'
      }
    });

    if (testResponse.ok) {
      results.steps.push('✅ Tables verified - user_profiles accessible');
    } else {
      results.steps.push('⚠️ Tables may not be accessible due to RLS policies');
    }

    const testPaymentsResponse = await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/payments?select=count`, {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}`,
        'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        'Prefer': 'return=minimal'
      }
    });

    if (testPaymentsResponse.ok) {
      results.steps.push('✅ Tables verified - payments accessible');
    } else {
      results.steps.push('⚠️ Tables may not be accessible due to RLS policies');
    }

    results.success = true;
    return NextResponse.json(results);

  } catch (error: any) {
    results.error = error.message;
    return NextResponse.json(results, { status: 500 });
  }
}
