import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export async function POST() {
  const results: any = { success: false, steps: [] }

  try {
    // Create buckets with service role key
    const buckets = [
      {
        name: 'user-avatars',
        public: true,
        fileSizeLimit: 2 * 1024 * 1024, // 2MB
        description: 'User profile pictures'
      },
      {
        name: 'user-documents',
        public: false,
        fileSizeLimit: 50 * 1024 * 1024, // 50MB
        description: 'User private documents'
      },
      {
        name: 'workspace-files',
        public: false,
        fileSizeLimit: 100 * 1024 * 1024, // 100MB
        description: 'Workspace file storage'
      },
      // GCS-mapped buckets
      {
        name: 'workspace-uploads',
        public: false,
        fileSizeLimit: 100 * 1024 * 1024, // 100MB
        description: 'Workspace uploads (replaces GCS uploads)'
      },
      {
        name: 'workspace-exports',
        public: false,
        fileSizeLimit: 200 * 1024 * 1024, // 200MB
        description: 'Workspace exports (replaces GCS exports)'
      },
      {
        name: 'workspace-backups',
        public: false,
        fileSizeLimit: 500 * 1024 * 1024, // 500MB
        description: 'Workspace backups (replaces GCS backups)'
      },
      {
        name: 'workspace-assets',
        public: true,
        fileSizeLimit: 50 * 1024 * 1024, // 50MB
        description: 'Workspace assets (replaces GCS assets)'
      },
      {
        name: 'workspace-temp',
        public: false,
        fileSizeLimit: 100 * 1024 * 1024, // 100MB
        description: 'Workspace temporary files (replaces GCS temp)'
      },
      {
        name: 'workspace-logs',
        public: false,
        fileSizeLimit: 50 * 1024 * 1024, // 50MB
        description: 'Workspace logs (replaces GCS logs)'
      },
      {
        name: 'intelligence-vault',
        public: false,
        fileSizeLimit: 10 * 1024 * 1024, // 10MB
        description: 'AI intelligence outputs (replaces GCS evidence vault)'
      },
      {
        name: 'user-data',
        public: false,
        fileSizeLimit: 100 * 1024 * 1024, // 100MB
        description: 'User data exports (GDPR compliance)'
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
          results.steps.push(`❌ Failed to create ${bucket.name}: ${error.message}`)
        } else {
          results.steps.push(`✅ Created ${bucket.name} bucket`)

          // Create storage policies based on bucket type
          const policyName = bucket.name.replace('-', '_')

          if (bucket.public) {
            // Public buckets - allow read access to all, write access only to authenticated users
            const { error: publicReadError } = await supabase.rpc('exec_sql', {
              sql: `
                CREATE POLICY "Public read access for ${bucket.name}" ON storage.objects
                  FOR SELECT USING (bucket_id = '${bucket.name}');
              `
            })

            const { error: userWriteError } = await supabase.rpc('exec_sql', {
              sql: `
                CREATE POLICY "Users can write to ${bucket.name}" ON storage.objects
                  FOR INSERT WITH CHECK (
                    bucket_id = '${bucket.name}' AND
                    auth.role() = 'authenticated'
                  );
              `
            })

            const { error: userUpdateError } = await supabase.rpc('exec_sql', {
              sql: `
                CREATE POLICY "Users can update their own files in ${bucket.name}" ON storage.objects
                  FOR UPDATE USING (
                    bucket_id = '${bucket.name}' AND
                    auth.uid()::text = (storage.foldername(name))[1]
                  );
              `
            })

            const { error: userDeleteError } = await supabase.rpc('exec_sql', {
              sql: `
                CREATE POLICY "Users can delete their own files in ${bucket.name}" ON storage.objects
                  FOR DELETE USING (
                    bucket_id = '${bucket.name}' AND
                    auth.uid()::text = (storage.foldername(name))[1]
                  );
              `
            })

            if (!publicReadError && !userWriteError && !userUpdateError && !userDeleteError) {
              results.steps.push(`✅ Created public policies for ${bucket.name}`)
            }
          } else {
            // Private buckets - users can only access their own folder
            const { error: privatePolicyError } = await supabase.rpc('exec_sql', {
              sql: `
                CREATE POLICY "Users can manage their own ${bucket.name}" ON storage.objects
                  FOR ALL USING (
                    bucket_id = '${bucket.name}' AND
                    auth.uid()::text = (storage.foldername(name))[1]
                  );
              `
            })

            if (!privatePolicyError) {
              results.steps.push(`✅ Created private policies for ${bucket.name}`)
            }
          }
        }
      } catch (e: any) {
        results.steps.push(`⚠️ ${bucket.name}: ${e.message}`)
      }
    }

    // Update user_profiles table with storage quotas based on plan
    const { error: quotaError } = await supabase.rpc('exec_sql', {
      sql: `
        ALTER TABLE public.user_profiles
        ADD COLUMN IF NOT EXISTS storage_quota_mb INTEGER DEFAULT 100,
        ADD COLUMN IF NOT EXISTS storage_used_mb INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS plan_features JSONB DEFAULT '{}';

        -- Create function to update storage quota based on plan
        CREATE OR REPLACE FUNCTION public.update_storage_quota()
        RETURNS TRIGGER AS $$
        BEGIN
          IF NEW.subscription_plan = 'soar' THEN
            NEW.storage_quota_mb = 1000; -- 1GB
          ELSIF NEW.subscription_plan = 'glide' THEN
            NEW.storage_quota_mb = 5000; -- 5GB
          ELSIF NEW.subscription_plan = 'ascent' THEN
            NEW.storage_quota_mb = 10000; -- 10GB
          ELSE
            NEW.storage_quota_mb = 100; -- 100MB free tier
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
      results.steps.push('✅ Updated storage quotas and features')
    } else {
      results.steps.push('⚠️ Storage quotas may need manual setup')
    }

    results.success = true
    return NextResponse.json(results)

  } catch (error: any) {
    results.error = error.message
    return NextResponse.json(results, { status: 500 })
  }
}
