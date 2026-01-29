import { NextResponse } from 'next/server';

export async function POST() {
  const results: any = { success: false, steps: [] };

  try {
    // Get the service role key - if it's a placeholder, we'll use a workaround
    const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!serviceRoleKey || serviceRoleKey === 'your-service-role-key-here') {
      results.steps.push('❌ Service role key not configured');
      results.steps.push('⚠️ Using alternative approach...');

      // Create a mock user profile table using the REST API
      try {
        // Try to create a test user profile directly
        const testUserId = '00000000-0000-0000-0000-000000000000';
        const response = await fetch(`${supabaseUrl}/rest/v1/user_profiles`, {
          method: 'POST',
          headers: {
            'apikey': anonKey || '',
            'Authorization': `Bearer ${anonKey || ''}`,
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
          } as HeadersInit,
          body: JSON.stringify({
            id: testUserId,
            email: 'test@raptorflow.in',
            full_name: 'Test User',
            storage_quota_mb: 100,
            storage_used_mb: 0
          })
        });

        if (response.status === 201) {
          results.steps.push('✅ Created test user profile successfully');
          results.steps.push('✅ Database is accessible');
          results.success = true;
        } else {
          const error = await response.text();
          results.steps.push('❌ Failed to create test profile: ' + error);
        }
      } catch (error: any) {
        results.steps.push('❌ Alternative approach failed: ' + error.message);
      }

      return NextResponse.json(results);
    }

    // If we have the service role key, use it to create tables
    results.steps.push('✅ Service role key available');

    // SQL to create tables
    const createTablesSQL = `
      CREATE TABLE IF NOT EXISTS public.user_profiles (
        id UUID REFERENCES auth.users(id) PRIMARY KEY,
        user_id TEXT UNIQUE,
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

      CREATE SEQUENCE IF NOT EXISTS public.user_profile_id_seq START 100000;

      ALTER TABLE public.user_profiles
        ADD COLUMN IF NOT EXISTS user_id TEXT;

      DO $$
      BEGIN
        IF NOT EXISTS (
          SELECT 1
          FROM pg_constraint
          WHERE conname = 'user_profiles_user_id_key'
            AND conrelid = 'public.user_profiles'::regclass
        ) THEN
          ALTER TABLE public.user_profiles
            ADD CONSTRAINT user_profiles_user_id_key UNIQUE (user_id);
        END IF;
      END $$;

      CREATE OR REPLACE FUNCTION public.assign_user_profile_id()
      RETURNS TRIGGER AS $$
      BEGIN
        IF NEW.user_id IS NULL OR NEW.user_id = '' THEN
          NEW.user_id := 'U' || nextval('public.user_profile_id_seq')::TEXT;
        END IF;
        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql;

      DROP TRIGGER IF EXISTS trg_assign_user_profile_id ON public.user_profiles;
      CREATE TRIGGER trg_assign_user_profile_id
        BEFORE INSERT ON public.user_profiles
        FOR EACH ROW EXECUTE FUNCTION public.assign_user_profile_id();

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
    `;

    // Try to execute SQL using Supabase REST API
    try {
      const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${serviceRoleKey}`,
          'Content-Type': 'application/json',
          'apikey': serviceRoleKey,
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify({ sql: createTablesSQL })
      });

      if (response.ok) {
        results.steps.push('✅ Database tables created successfully');
        results.success = true;
      } else {
        const error = await response.text();
        results.steps.push('❌ Failed to create tables: ' + error);
      }
    } catch (error: any) {
      results.steps.push('❌ SQL execution failed: ' + error.message);
    }

    return NextResponse.json(results);

  } catch (error: any) {
    results.error = error.message;
    results.steps.push('❌ Fatal error: ' + error.message);
    return NextResponse.json(results, { status: 500 });
  }
}
