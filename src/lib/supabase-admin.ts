/**
 * Supabase Admin Client - Lazy Initialization
 * 
 * This utility creates the Supabase admin client lazily to avoid
 * build-time errors when environment variables are not yet available.
 */

import { createClient, SupabaseClient } from '@supabase/supabase-js';

let supabaseAdmin: SupabaseClient | null = null;

/**
 * Get the Supabase admin client.
 * Creates the client on first call (lazy initialization).
 */
export function getSupabaseAdmin(): SupabaseClient {
    if (!supabaseAdmin) {
        const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
        const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

        if (!url || !key) {
            throw new Error('Missing Supabase environment variables');
        }

        supabaseAdmin = createClient(url, key);
    }

    return supabaseAdmin;
}
