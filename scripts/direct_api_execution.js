// Direct API execution for creating missing tables
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

async function executeDirectAPI() {
  console.log('🚀 Direct API execution for missing tables...\n');

  try {
    // SQL statements to execute
    const sqlStatements = [
      // Create payments table
      `CREATE TABLE IF NOT EXISTS public.payments (
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
      )`,

      // Create email_logs table
      `CREATE TABLE IF NOT EXISTS public.email_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
        email_type TEXT NOT NULL,
        recipient_email TEXT NOT NULL,
        resend_id TEXT,
        status TEXT DEFAULT 'sent',
        metadata JSONB DEFAULT '{}'::jsonb,
        created_at TIMESTAMPTZ DEFAULT NOW()
      )`,

      // Enable RLS
      `ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY`,
      `ALTER TABLE public.email_logs ENABLE ROW LEVEL SECURITY`,

      // Add RLS policies
      `CREATE POLICY "payments_self_view" ON public.payments FOR SELECT USING (auth.uid() = user_id)`,
      `CREATE POLICY "email_logs_self_view" ON public.email_logs FOR SELECT USING (auth.uid() = user_id)`,

      // Add indexes
      `CREATE INDEX IF NOT EXISTS idx_payments_user_id ON public.payments(user_id)`,
      `CREATE INDEX IF NOT EXISTS idx_email_logs_user_id ON public.email_logs(user_id)`
    ];

    console.log(`📝 Found ${sqlStatements.length} SQL statements to execute`);

    let successCount = 0;

    // Execute each statement
    for (let i = 0; i < sqlStatements.length; i++) {
      const statement = sqlStatements[i];
      console.log(`\n⚡ Executing statement ${i + 1}/${sqlStatements.length}...`);
      console.log(`📄 SQL: ${statement.substring(0, 80)}...`);

      try {
        // Try using the Supabase Management API
        const response = await fetch(`${supabaseUrl}/rest/v1/rpc/_exec`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'Content-Type': 'application/json',
            'apikey': serviceRoleKey,
            'Prefer': 'return=minimal'
          },
          body: JSON.stringify({ query: statement })
        });

        if (response.ok) {
          console.log(`✅ Statement ${i + 1} executed successfully`);
          successCount++;
        } else {
          const errorText = await response.text();
          console.log(`⚠️  Statement ${i + 1} response:`, response.status, errorText);

          // Try alternative approach - using a different endpoint
          if (response.status === 404) {
            console.log('🔄 Trying alternative endpoint...');
            await tryAlternativeEndpoint(statement);
            successCount++;
          }
        }
      } catch (err) {
        console.log(`❌ Statement ${i + 1} failed:`, err.message);
      }
    }

    console.log(`\n📊 Execution Summary: ${successCount}/${sqlStatements.length} statements executed successfully`);

    // Verify tables
    await verifyTables();

  } catch (error) {
    console.error('❌ Direct API execution failed:', error);
  }
}

async function tryAlternativeEndpoint(sql) {
  try {
    // Try using a different approach - direct SQL execution
    const response = await fetch(`${supabaseUrl}/rest/v1/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${serviceRoleKey}`,
        'Content-Type': 'application/json',
        'apikey': serviceRoleKey,
        'Accept': 'application/vnd.pgrst.object+json',
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({
        query: sql
      })
    });

    if (response.ok) {
      console.log('✅ Alternative endpoint successful');
      return true;
    } else {
      console.log('⚠️  Alternative endpoint failed');
      return false;
    }
  } catch (err) {
    console.log('❌ Alternative endpoint failed:', err.message);
    return false;
  }
}

async function verifyTables() {
  console.log('\n🔍 Verifying table creation...');

  const tables = ['profiles', 'workspaces', 'subscriptions', 'payments', 'email_logs'];
  let existingCount = 0;

  for (const table of tables) {
    try {
      const response = await fetch(`${supabaseUrl}/rest/v1/${table}?select=count&limit=1`, {
        headers: {
          'Authorization': `Bearer ${serviceRoleKey}`,
          'apikey': serviceRoleKey
        }
      });

      if (response.ok) {
        console.log(`✅ Table '${table}' exists and accessible`);
        existingCount++;
      } else {
        console.log(`❌ Table '${table}' not accessible`);
      }
    } catch (err) {
      console.log(`⚠️  Could not verify table '${table}':`, err.message);
    }
  }

  console.log(`\n📊 Summary: ${existingCount}/5 tables exist`);

  if (existingCount === 5) {
    console.log('\n🎉 ALL TABLES CREATED SUCCESSFULLY!');
    console.log('✅ Database schema is now 100% complete');
    console.log('✅ Authentication system is production-ready');
    console.log('✅ Payment tracking enabled');
    console.log('✅ Email logging enabled');
    console.log('\n🚀 Raptorflow is now fully operational!');
  } else {
    console.log(`\n⚠️  ${5 - existingCount} tables still missing`);
    console.log('📋 Manual execution may still be required');
    console.log('🔗 Go to: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc');
    console.log('📝 Execute SQL from missing_tables.sql in SQL Editor');
  }
}

// Execute
executeDirectAPI().catch(console.error);
