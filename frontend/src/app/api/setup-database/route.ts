import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

// Lazy client creation to avoid build-time errors
function getSupabaseAdmin() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !key) {
    throw new Error('Missing Supabase configuration');
  }

  return createClient(url, key);
}

export async function POST() {
  const results: any = { success: false, steps: [], error: null }

  try {
    const supabaseAdmin = getSupabaseAdmin();

    // SQL to create user_profiles table
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

    // SQL to create payments table
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

    // SQL to create trigger function
    const createTriggerSQL = `
      CREATE OR REPLACE FUNCTION public.handle_new_user()
      RETURNS TRIGGER AS $$
      BEGIN
        INSERT INTO public.user_profiles (id, email, full_name)
        VALUES (
          NEW.id,
          NEW.email,
          NEW.raw_user_meta_data->>'full_name'
        );
        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql SECURITY DEFINER;

      DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
      CREATE TRIGGER on_auth_user_created
        AFTER INSERT ON auth.users
        FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
    `

    const executeSQL = async (sql: string) => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/rpc/exec`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.SUPABASE_SERVICE_ROLE_KEY}`,
          'Content-Type': 'application/json',
          'apikey': process.env.SUPABASE_SERVICE_ROLE_KEY!,
        },
        body: JSON.stringify({ query: sql })
      })

      if (!response.ok) {
        const error = await response.text()
        throw new Error(`SQL execution failed: ${error}`)
      }

      return await response.json()
    }

    try {
      results.steps.push('Executing user_profiles table creation...')
      await executeSQL(createProfilesSQL)
      results.steps.push('user_profiles table created successfully')
    } catch (error: any) {
      results.steps.push(`user_profiles table creation failed: ${error.message}`)
    }

    try {
      results.steps.push('Executing payments table creation...')
      await executeSQL(createPaymentsSQL)
      results.steps.push('payments table created successfully')
    } catch (error: any) {
      results.steps.push(`payments table creation failed: ${error.message}`)
    }

    try {
      results.steps.push('Creating trigger function...')
      await executeSQL(createTriggerSQL)
      results.steps.push('Trigger function created successfully')
    } catch (error: any) {
      results.steps.push(`Trigger creation failed: ${error.message}`)
    }

    results.success = true
    results.steps.push('Database setup completed!')

    return NextResponse.json(results)

  } catch (error: any) {
    results.error = error.message
    results.steps.push(`Setup failed: ${error.message}`)
    return NextResponse.json(results, { status: 500 })
  }
}
