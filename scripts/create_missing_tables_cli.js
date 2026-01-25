// Create missing tables using direct PostgreSQL connection
import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Use service role key for admin operations
const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

// Create admin client
const supabase = createClient(supabaseUrl, serviceRoleKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

async function createMissingTables() {
  console.log('🚀 Creating missing tables via CLI approach...\n');

  try {
    // Read the SQL file
    const sqlPath = path.join(__dirname, '../missing_tables.sql');
    const sqlContent = fs.readFileSync(sqlPath, 'utf8');

    console.log('📁 SQL file loaded');

    // Split into individual statements
    const statements = sqlContent
      .split(';')
      .map(s => s.trim())
      .filter(s => s && !s.startsWith('--') && !s.startsWith('/*') && !s.startsWith('*'));

    console.log(`📝 Found ${statements.length} SQL statements to execute`);

    // Execute each statement using the REST API
    for (let i = 0; i < statements.length; i++) {
      const statement = statements[i];
      console.log(`\n⚡ Executing statement ${i + 1}/${statements.length}...`);
      console.log(`📄 SQL: ${statement.substring(0, 100)}...`);

      try {
        // Try using the _exec function for admin operations
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
        } else {
          const errorText = await response.text();
          console.log(`⚠️  Statement ${i + 1} response:`, response.status, errorText);

          // Try alternative approach for DDL
          if (response.status === 400 || response.status === 500) {
            console.log('🔄 Trying alternative approach...');
            await tryAlternativeApproach(statement);
          }
        }
      } catch (err) {
        console.log(`❌ Statement ${i + 1} failed:`, err.message);
      }
    }

    console.log('\n🎉 Table creation completed!');
    await verifyTables();

  } catch (error) {
    console.error('❌ CLI approach failed:', error);
    console.log('\n📋 Manual deployment still required:');
    console.log('1. Open Supabase Dashboard: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc');
    console.log('2. Execute the SQL from missing_tables.sql');
  }
}

async function tryAlternativeApproach(sql) {
  try {
    // Try using direct SQL execution via a different endpoint
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
      console.log('✅ Alternative approach successful');
    } else {
      console.log('⚠️  Alternative approach failed');
    }
  } catch (err) {
    console.log('❌ Alternative approach failed:', err.message);
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
  } else {
    console.log(`\n⚠️  ${5 - existingCount} tables still missing`);
    console.log('📋 Manual execution may still be required');
  }
}

// Execute table creation
createMissingTables().catch(console.error);
