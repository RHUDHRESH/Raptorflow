import { NextResponse } from 'next/server';

export async function POST() {
  const results: any = { success: false, steps: [] };

  try {
    // Get the service role key from environment
    const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;

    if (!serviceRoleKey || serviceRoleKey === 'your-service-role-key-here') {
      results.steps.push('❌ Service role key not configured');
      results.steps.push('Please update SUPABASE_SERVICE_ROLE_KEY in .env.local');
      return NextResponse.json(results);
    }

    // SQL to create user_profiles table
    const profilesSQL = `
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
    `;

    // SQL to create payments table
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

    // Execute SQL using Supabase REST API
    const executeSQL = async (sql: string, description: string) => {
      try {
        const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'Content-Type': 'application/json',
            'apikey': serviceRoleKey,
            'Prefer': 'return=minimal'
          },
          body: JSON.stringify({ sql })
        });

        if (response.ok) {
          results.steps.push(`✅ ${description}`);
          return true;
        } else {
          const error = await response.text();
          results.steps.push(`❌ ${description}: ${error}`);
          return false;
        }
      } catch (error: any) {
        results.steps.push(`❌ ${description}: ${error.message}`);
        return false;
      }
    };

    // Execute the SQL statements
    const profilesSuccess = await executeSQL(profilesSQL, 'Created user_profiles table');
    const paymentsSuccess = await executeSQL(paymentsSQL, 'Created payments table');

    // Test if tables were created
    const testTable = async (tableName: string) => {
      try {
        const response = await fetch(`${supabaseUrl}/rest/v1/${tableName}?select=count`, {
          headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'apikey': serviceRoleKey,
            'Prefer': 'return=minimal'
          }
        });
        return response.ok;
      } catch {
        return false;
      }
    };

    const profilesExist = await testTable('user_profiles');
    const paymentsExist = await testTable('payments');

    if (profilesExist) {
      results.steps.push('✅ user_profiles table verified');
    } else {
      results.steps.push('❌ user_profiles table not accessible');
    }

    if (paymentsExist) {
      results.steps.push('✅ payments table verified');
    } else {
      results.steps.push('❌ payments table not accessible');
    }

    // Overall success
    if (profilesSuccess && paymentsSuccess && profilesExist && paymentsExist) {
      results.success = true;
      results.steps.push('🎉 All tables created successfully!');
    } else {
      results.steps.push('⚠️ Some issues occurred - check logs above');
    }

    return NextResponse.json(results);

  } catch (error: any) {
    results.error = error.message;
    results.steps.push(`❌ Fatal error: ${error.message}`);
    return NextResponse.json(results, { status: 500 });
  }
}
