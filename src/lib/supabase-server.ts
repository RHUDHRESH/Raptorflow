import { createClient, SupabaseClient } from '@supabase/supabase-js';

/**
 * Creates a Supabase client lazily (on demand) to avoid build-time errors.
 * Environment variables are only accessed at runtime, not during Next.js build.
 */
export function getSupabaseClient(): SupabaseClient {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!url || !key) {
        throw new Error('Missing Supabase configuration. Check NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_KEY environment variables.');
    }

    return createClient(url, key);
}

/**
 * Creates a Supabase Admin client with service role key for privileged operations.
 * Should only be used in server-side API routes.
 */
export function getSupabaseAdminClient(): SupabaseClient {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!url || !key) {
        throw new Error('Missing Supabase admin configuration. Check NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables.');
    }

    return createClient(url, key);
}
