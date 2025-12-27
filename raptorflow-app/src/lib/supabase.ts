import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://dummy.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'dummy-key';

console.log('[Supabase] Initializing client with:', {
    url: supabaseUrl,
    keyLength: supabaseAnonKey?.length,
    isDummy: supabaseUrl.includes('dummy'),
    keyStart: supabaseAnonKey?.slice(0, 5) + '...'
});

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
