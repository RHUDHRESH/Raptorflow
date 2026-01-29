import { createBrowserClient } from '@supabase/ssr';

// Supabase client configuration
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );
}

// Alias for backward compatibility
export const getSupabaseClient = createClient;
