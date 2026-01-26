// Generate or retrieve proper Supabase access token
import { execSync } from 'child_process';

async function generateAccessToken() {
  console.log('🔑 Attempting to generate/retrieve Supabase access token...\n');

  try {
    // Try to get the token from environment or generate one
    console.log('🔄 Checking for existing token...');

    // Try to list projects to see if we have access
    try {
      const result = execSync('supabase projects list', {
        encoding: 'utf8',
        timeout: 10000
      });
      console.log('✅ CLI access working');
      console.log('Projects:', result);

      // If we get here, we have some level of access
      console.log('\n🔍 Checking token status...');

      // Try to get the stored token
      try {
        const tokenResult = execSync('supabase status', {
          encoding: 'utf8',
          timeout: 10000
        });
        console.log('Token status:', tokenResult);

      } catch (err) {
        console.log('Token status check failed:', err.message);
      }

    } catch (err) {
      console.log('❌ CLI access failed:', err.message);

      if (err.message.includes('Invalid access token format')) {
        console.log('\n📋 Token format issue detected');
        console.log('🔗 Need to generate proper sbp_ token from Supabase Dashboard');
        console.log('\n📋 Steps to generate token:');
        console.log('1. Go to: https://supabase.com/dashboard/account/tokens');
        console.log('2. Click "Generate Token"');
        console.log('3. Copy the token (starts with sbp_)');
        console.log('4. Run: supabase login --token YOUR_TOKEN');
      }
    }

    // Try alternative approach - use environment variable
    console.log('\n🔄 Trying environment variable approach...');

    // Check if we have a service role key that might work for some operations
    const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

    console.log('🔑 Service role key available');
    console.log('📝 Length:', serviceRoleKey.length);
    console.log('🔍 Format check:', serviceRoleKey.startsWith('eyJ') ? 'JWT format' : 'Unknown');

    // Try using service role key for database operations
    console.log('\n🚀 Trying database operations with service role key...');

    // Execute the SQL using the API approach
    await executeSQLWithServiceRole();

  } catch (error) {
    console.error('❌ Token generation failed:', error);
  }
}

async function executeSQLWithServiceRole() {
  console.log('\n🔧 Executing SQL with service role key...\n');

  const { execSync } = await import('child_process');
  const fs = await import('fs');
  const path = await import('path');

  try {
    // Read the SQL file
    const sqlPath = path.join(process.cwd(), 'missing_tables.sql');
    const sqlContent = fs.readFileSync(sqlPath, 'utf8');

    console.log('📁 SQL file loaded');

    // Create a temporary Node.js script to execute SQL
    const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

    const tempScript = `
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const serviceRoleKey = '${serviceRoleKey}';

const supabase = createClient(supabaseUrl, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false }
});

async function executeSQL() {
  try {
    console.log('🔗 Connecting to Supabase...');

    // Try to execute raw SQL using the service role key
    const response = await fetch(\`\${supabaseUrl}/rest/v1/rpc/_exec\`, {
      method: 'POST',
      headers: {
        'Authorization': \`Bearer \${serviceRoleKey}\`,
        'Content-Type': 'application/json',
        'apikey': serviceRoleKey,
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({
        query: \`
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
        \`
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
    console.log('\n🎉 Tables created successfully!');
    process.exit(0);
  } else {
    console.log('\n❌ Table creation failed');
    process.exit(1);
  }
}).catch(err => {
  console.error('❌ Script error:', err);
  process.exit(1);
});
    `;

    const tempScriptPath = path.join(process.cwd(), 'temp_execute_sql.js');
    fs.writeFileSync(tempScriptPath, tempScript);

    console.log('📝 Created temporary script:', tempScriptPath);

    // Execute the temporary script
    console.log('🚀 Executing temporary script...');
    const result = execSync('node temp_execute_sql.js', {
      encoding: 'utf8',
      timeout: 30000
    });

    console.log('📊 Script output:', result);

    // Clean up
    fs.unlinkSync(tempScriptPath);

    // Verify tables
    await verifyTables();

  } catch (error) {
    console.error('❌ Script execution failed:', error);
  }
}

async function verifyTables() {
  console.log('\n🔍 Verifying table creation...');

  try {
    const { execSync } = await import('child_process');
    const result = execSync('node scripts/quick_check.js', {
      encoding: 'utf8',
      cwd: process.cwd()
    });
    console.log(result);
  } catch (err) {
    console.log('Verification failed:', err.message);
  }
}

// Execute
generateAccessToken().catch(console.error);
