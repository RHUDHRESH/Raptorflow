// Script to create password_reset_tokens table
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Load env from .env file
const envPath = path.join(__dirname, '..', '.env');
const envContent = fs.readFileSync(envPath, 'utf8');
envContent.split('\n').forEach(line => {
  const [key, ...valueParts] = line.split('=');
  if (key && valueParts.length) {
    process.env[key.trim()] = valueParts.join('=').trim();
  }
});

async function createTable() {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
  );

  console.log('Checking if password_reset_tokens table exists...');

  // First check if table exists by trying to query it
  const { data, error } = await supabase
    .from('password_reset_tokens')
    .select('*')
    .limit(1);

  if (error && error.code === '42P01') {
    console.log('Table does not exist. Please create it manually in Supabase Dashboard.');
    console.log('\nRun this SQL in Supabase SQL Editor:');
    console.log(`
CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  token TEXT UNIQUE NOT NULL,
  email TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON public.password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_email ON public.password_reset_tokens(email);

-- Disable RLS for service role access
ALTER TABLE public.password_reset_tokens ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "service_role_all" ON public.password_reset_tokens
  FOR ALL
  USING (true)
  WITH CHECK (true);
    `);
    return;
  }

  if (error) {
    console.log('Error checking table:', error.message);
    return;
  }

  console.log('Table exists! Current row count:', data?.length || 0);
}

createTable().catch(console.error);
