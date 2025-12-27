import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://dummy.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'dummy-key';

console.log('[Supabase] Initializing client with:', {
    url: supabaseUrl,
    keyLength: supabaseAnonKey?.length,
    isDummy: supabaseUrl.includes('dummy')
});

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export const isSupabaseConfigured = () => {
    return !supabaseUrl.includes('dummy') && supabaseAnonKey !== 'dummy-key';
};
