
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false }
});

async function executeSQL() {
  try {
    console.log('🔗 Connecting to Supabase...');

    // Try to execute raw SQL using the service role key
    const response = await fetch(`${supabaseUrl}/rest/v1/rpc/_exec`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${serviceRoleKey}`,
        'Content-Type': 'application/json',
        'apikey': serviceRoleKey,
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({
        query: `
          -- Create payments table
          CREATE TABLE IF NOT EXISTS public.payments (
              id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
              user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
              transaction_id TEXT UNIQUE NOT NULL,
              phonepe_transaction_id TEXT,
              amount INTEGER NOT NULL,
              currency TEXT DEFAULT 'INR',
              status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
              plan_id TEXT CHECK (plan_id IN ('ascent', 'glide', 'soar')),
              invoice_url TEXT,
              metadata JSONB DEFAULT '{}'::jsonb,
              created_at TIMESTAMPTZ DEFAULT NOW(),
              verified_at TIMESTAMPTZ
          );

          -- Create email_logs table
          CREATE TABLE IF NOT EXISTS public.email_logs (
              id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
              user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
              email_type TEXT NOT NULL,
              recipient_email TEXT NOT NULL,
              resend_id TEXT,
              status TEXT DEFAULT 'sent',
              metadata JSONB DEFAULT '{}'::jsonb,
              created_at TIMESTAMPTZ DEFAULT NOW()
          );

          -- Enable RLS
          ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
          ALTER TABLE public.email_logs ENABLE ROW LEVEL SECURITY;

          -- Add RLS policies
          CREATE POLICY "payments_self_view" ON public.payments FOR SELECT USING (auth.uid() = user_id);
          CREATE POLICY "email_logs_self_view" ON public.email_logs FOR SELECT USING (auth.uid() = user_id);

          -- Add indexes
          CREATE INDEX IF NOT EXISTS idx_payments_user_id ON public.payments(user_id);
          CREATE INDEX IF NOT EXISTS idx_email_logs_user_id ON public.email_logs(user_id);
        `
      })
    });

    if (response.ok) {
      console.log('✅ SQL executed successfully!');
      console.log('Response:', await response.text());
      return true;
    } else {
      console.log('❌ SQL execution failed:', response.status);
      console.log('Error:', await response.text());
      return false;
    }
  } catch (error) {
    console.error('❌ SQL execution error:', error);
    return false;
  }
}

executeSQL().then(success => {
  if (success) {
    console.log('
🎉 Tables created successfully!');
    process.exit(0);
  } else {
    console.log('
❌ Table creation failed');
    process.exit(1);
  }
}).catch(err => {
  console.error('❌ Script error:', err);
  process.exit(1);
});
