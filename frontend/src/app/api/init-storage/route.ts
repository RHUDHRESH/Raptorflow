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

    // Create buckets with service role key
    const buckets = [
      {
        name: 'user-avatars',
        public: true,
        fileSizeLimit: 2 * 1024 * 1024,
        description: 'User profile pictures'
      },
      {
        name: 'user-documents',
        public: false,
        fileSizeLimit: 50 * 1024 * 1024,
        description: 'User private documents'
      },
      {
        name: 'workspace-files',
        public: false,
        fileSizeLimit: 100 * 1024 * 1024,
        description: 'Workspace file storage'
      }
    ]

    for (const bucket of buckets) {
      try {
        const { error } = await supabase.storage.createBucket(bucket.name, {
          public: bucket.public,
          fileSizeLimit: bucket.fileSizeLimit,
          allowedMimeTypes: [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/webp',
            'application/pdf',
            'text/plain',
            'text/csv',
            'application/json',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          ]
        })

        if (error && !error.message.includes('already exists')) {
          results.steps.push(`Failed to create ${bucket.name}: ${error.message}`)
        } else {
          results.steps.push(`Created ${bucket.name} bucket`)

          const { error: policyError } = await supabase.rpc('exec_sql', {
            sql: `
              CREATE POLICY "Users can manage their ${bucket.name}" ON storage.objects
                FOR ALL USING (
                  bucket_id = '${bucket.name}' AND
                  auth.uid()::text = (storage.foldername(name))[1]
                );
            `
          })

          if (!policyError) {
            results.steps.push(`Created policy for ${bucket.name}`)
          }
        }
      } catch (e: any) {
        results.steps.push(`${bucket.name}: ${e.message}`)
      }
    }

    // Update user_profiles table with storage quotas
    const { error: quotaError } = await supabase.rpc('exec_sql', {
      sql: `
        ALTER TABLE public.user_profiles
        ADD COLUMN IF NOT EXISTS storage_quota_mb INTEGER DEFAULT 100,
        ADD COLUMN IF NOT EXISTS storage_used_mb INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS plan_features JSONB DEFAULT '{}';

        CREATE OR REPLACE FUNCTION public.update_storage_quota()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.subscription_plan = 'soar' THEN
            NEW.storage_quota_mb = 1000;
          ELSIF NEW.subscription_plan = 'glide' THEN
            NEW.storage_quota_mb = 5000;
          ELSIF NEW.subscription_plan = 'ascent' THEN
            NEW.storage_quota_mb = 10000;
          ELSE
            NEW.storage_quota_mb = 100;
          END IF;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS update_storage_quota_trigger ON public.user_profiles;
        CREATE TRIGGER update_storage_quota_trigger
          BEFORE UPDATE OF subscription_plan ON public.user_profiles
          FOR EACH ROW EXECUTE FUNCTION public.update_storage_quota();
      `
    })

    if (!quotaError) {
      results.steps.push('Updated storage quotas and features')
    } else {
      results.steps.push('Storage quotas may need manual setup')
    }

    results.success = true
    return NextResponse.json(results)

  } catch (error: any) {
    results.error = error.message
    return NextResponse.json(results, { status: 500 })
  }
}
