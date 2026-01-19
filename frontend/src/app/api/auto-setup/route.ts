import { NextResponse } from 'next/server';

export async function POST() {
  const results: any = {
    success: false,
    steps: [],
    instructions: [],
    status: 'pending'
  };

  try {
    // Step 1: Check if tables exist
    const profilesCheck = await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/user_profiles?select=count`, {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}`,
        'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        'Prefer': 'return=minimal'
      }
    });

    const paymentsCheck = await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/payments?select=count`, {
      headers: {
        'Authorization': `Bearer ${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY}`,
        'apikey': process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        'Prefer': 'return=minimal'
      }
    });

    if (profilesCheck.ok && paymentsCheck.ok) {
      results.steps.push('✅ Database tables exist and accessible');
      results.status = 'ready';
      results.success = true;
    } else {
      results.steps.push('❌ Database tables missing');
      results.status = 'needs_setup';

      // Provide clear instructions
      results.instructions = [
        "1. Go to: https://supabase.com/dashboard/project/vpwwzsanuyhpkvgorcnc/sql",
        "2. Copy this SQL and run it:",
        "",
        "CREATE TABLE IF NOT EXISTS public.user_profiles (",
        "  id UUID REFERENCES auth.users(id) PRIMARY KEY,",
        "  email TEXT NOT NULL,",
        "  full_name TEXT,",
        "  avatar_url TEXT,",
        "  subscription_plan TEXT CHECK (subscription_plan IN ('soar', 'glide', 'ascent')),",
        "  subscription_status TEXT CHECK (subscription_status IN ('active', 'cancelled', 'expired')),",
        "  subscription_expires_at TIMESTAMPTZ,",
        "  storage_quota_mb INTEGER DEFAULT 100,",
        "  storage_used_mb INTEGER DEFAULT 0,",
        "  created_at TIMESTAMPTZ DEFAULT NOW(),",
        "  updated_at TIMESTAMPTZ DEFAULT NOW()",
        ");",
        "",
        "ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;",
        "",
        "DROP POLICY IF EXISTS \"Users can view own profile\" ON public.user_profiles;",
        "DROP POLICY IF EXISTS \"Users can update own profile\" ON public.user_profiles;",
        "DROP POLICY IF EXISTS \"Users can insert own profile\" ON public.user_profiles;",
        "",
        "CREATE POLICY \"Users can view own profile\" ON public.user_profiles",
        "  FOR SELECT USING (auth.uid() = id);",
        "CREATE POLICY \"Users can update own profile\" ON public.user_profiles",
        "  FOR UPDATE USING (auth.uid() = id);",
        "CREATE POLICY \"Users can insert own profile\" ON public.user_profiles",
        "  FOR INSERT WITH CHECK (auth.uid() = id);",
        "",
        "CREATE TABLE IF NOT EXISTS public.payments (",
        "  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,",
        "  user_id UUID REFERENCES auth.users(id) NOT NULL,",
        "  transaction_id TEXT UNIQUE NOT NULL,",
        "  plan_id TEXT NOT NULL CHECK (plan_id IN ('soar', 'glide', 'ascent')),",
        "  amount INTEGER NOT NULL,",
        "  currency TEXT DEFAULT 'INR',",
        "  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),",
        "  payment_method TEXT DEFAULT 'phonepe',",
        "  phonepe_transaction_id TEXT,",
        "  created_at TIMESTAMPTZ DEFAULT NOW(),",
        "  verified_at TIMESTAMPTZ",
        ");",
        "",
        "ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;",
        "",
        "DROP POLICY IF EXISTS \"Users can view own payments\" ON public.payments;",
        "CREATE POLICY \"Users can view own payments\" ON public.payments",
        "  FOR SELECT USING (auth.uid() = user_id);",
        "",
        "3. Click 'Run' to execute",
        "4. After both tables are created, return here and click 'Test Again'",
        "",
        "⚠️ IMPORTANT: Make sure you're logged into the correct Supabase project!"
      ];
    }

    return NextResponse.json(results);

  } catch (error: any) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
      status: 'error'
    }, { status: 500 });
  }
}
