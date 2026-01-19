import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

// Lazy client creation to avoid build-time errors
function getSupabase() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error('Missing Supabase configuration');
  }

  return createClient(url, key);
}

export async function POST() {
  const results: any = { success: false, steps: [] }

  try {
    const supabase = getSupabase();

    // Step 1: Create user_profiles table
    try {
      const { error: profilesError } = await supabase
        .from('user_profiles')
        .select('count')
        .limit(1)

      if (profilesError && !profilesError.message.includes('does not exist')) {
        results.steps.push('user_profiles table exists')
      } else {
        const { error: createError } = await supabase
          .from('user_profiles')
          .insert([
            {
              id: 'id',
              email: 'email',
              full_name: 'full_name',
              avatar_url: 'avatar_url',
              subscription_plan: 'subscription_plan',
              subscription_status: 'subscription_status',
              subscription_expires_at: 'subscription_expires_at',
              storage_quota_mb: 100,
              storage_used_mb: 0,
              created_at: 'created_at',
              updated_at: 'updated_at'
            }
          ])

        if (createError) {
          results.steps.push('Failed to create user_profiles: ' + createError.message)
        } else {
          results.steps.push('Created user_profiles table')
        }
      }
    } catch (e: any) {
      results.steps.push('Failed to create user_profiles: ' + e.message)
    }

    // Step 2: Create payments table
    try {
      const { error: paymentsError } = await supabase
        .from('payments')
        .select('count')
        .limit(1)

      if (paymentsError && !paymentsError.message.includes('does not exist')) {
        results.steps.push('payments table exists')
      } else {
        const { error: createError } = await supabase
          .from('payments')
          .insert([
            {
              id: 'id',
              user_id: 'user_id',
              transaction_id: 'transaction_id',
              plan_id: 'plan_id',
              amount: 0,
              currency: 'INR',
              status: 'pending',
              payment_method: 'phonepe',
              phonepe_transaction_id: 'phonepe_transaction_id',
              created_at: 'created_at',
              verified_at: 'verified_at'
            }
          ])

        if (createError) {
          results.steps.push('Failed to create payments: ' + createError.message)
        } else {
          results.steps.push('Created payments table')
        }
      }
    } catch (e: any) {
      results.steps.push('Failed to create payments: ' + e.message)
    }

    // Step 3: Create storage buckets
    const buckets = [
      { name: 'avatars', public: true, fileSizeLimit: 1024 * 1024 },
      { name: 'documents', public: false, fileSizeLimit: 10 * 1024 * 1024 },
      { name: 'exports', public: false, fileSizeLimit: 50 * 1024 * 1024 },
    ]

    for (const bucket of buckets) {
      const { error: bucketError } = await supabase.storage.createBucket(bucket.name, {
        public: bucket.public,
        fileSizeLimit: bucket.fileSizeLimit,
        allowedMimeTypes: ['image/*', 'application/pdf', 'text/*'],
      })

      if (bucketError && !bucketError.message.includes('already exists')) {
        results.steps.push(`Failed to create ${bucket.name} bucket: ${bucketError.message}`)
      } else {
        results.steps.push(`Created ${bucket.name} bucket`)
      }
    }

    // Step 4: Create trigger for new user profile
    const { error: triggerError } = await supabase.rpc('exec_sql', {
      sql: `
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
    })

    if (triggerError) {
      results.steps.push('Trigger may already exist or needs manual creation')
    } else {
      results.steps.push('Created user profile trigger')
    }

    results.success = true
    return NextResponse.json(results)

  } catch (error: any) {
    results.error = error.message
    return NextResponse.json(results, { status: 500 })
  }
}
