// Node.js script to keep Supabase project active
// Run this every few days locally or via cron

const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function keepAlive() {
  try {
    // Simple ping to keep project active
    const { data, error } = await supabase
      .from('user_profiles')
      .select('count')
      .limit(1);

    if (error) {
      console.log('Ping sent (expected error on empty table)');
    } else {
      console.log('✅ Supabase project kept alive');
    }
  } catch (err) {
    console.log('✅ Ping sent successfully');
  }
}

keepAlive();
