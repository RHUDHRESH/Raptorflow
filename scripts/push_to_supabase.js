// Direct push to Supabase using REST API
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

async function pushToSupabase() {
  console.log('🚀 Pushing schema to Supabase...\n');
  
  try {
    // Read the SQL file
    const sqlPath = path.join(__dirname, '../schema_for_manual_execution.sql');
    const sqlContent = fs.readFileSync(sqlPath, 'utf8');
    
    console.log('📁 SQL file loaded successfully');
    console.log(`📏 SQL content length: ${sqlContent.length} characters`);
    
    // Split into manageable chunks (Supabase has limits on SQL execution size)
    const statements = sqlContent
      .split('-- ============================================================================')
      .filter(section => section.trim())
      .map(section => '-- ============================================================================' + section);
    
    console.log(`📝 Split into ${statements.length} sections for execution`);
    
    // Execute each section
    for (let i = 0; i < statements.length; i++) {
      const section = statements[i];
      console.log(`\n⚡ Executing section ${i + 1}/${statements.length}...`);
      
      try {
        const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${serviceRoleKey}`,
            'Content-Type': 'application/json',
            'apikey': serviceRoleKey,
            'Prefer': 'return=minimal'
          },
          body: JSON.stringify({ sql: section })
        });
        
        if (response.ok) {
          console.log(`✅ Section ${i + 1} executed successfully`);
        } else {
          const errorText = await response.text();
          console.log(`⚠️  Section ${i + 1} response:`, response.status, errorText);
          
          // Try alternative approach for DDL statements
          if (response.status === 400 || response.status === 500) {
            console.log('🔄 Trying direct SQL execution approach...');
            await tryDirectExecution(section);
          }
        }
      } catch (err) {
        console.log(`❌ Section ${i + 1} failed:`, err.message);
      }
    }
    
    console.log('\n🎉 Schema push completed!');
    await verifyDeployment();
    
  } catch (error) {
    console.error('❌ Push failed:', error);
    console.log('\n📋 Manual deployment required:');
    console.log('1. Open Supabase Dashboard: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc');
    console.log('2. Go to SQL Editor');
    console.log('3. Copy contents of schema_for_manual_execution.sql');
    console.log('4. Execute the SQL');
  }
}

async function tryDirectExecution(sql) {
  try {
    // Try using the _rpc endpoint with different approach
    const response = await fetch(`${supabaseUrl}/rest/v1/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${serviceRoleKey}`,
        'Content-Type': 'application/json',
        'apikey': serviceRoleKey,
        'Accept': 'application/vnd.pgrst.object+json'
      },
      body: JSON.stringify({
        query: sql
      })
    });
    
    if (response.ok) {
      console.log('✅ Direct execution successful');
    } else {
      console.log('⚠️  Direct execution failed, will need manual deployment');
    }
  } catch (err) {
    console.log('❌ Direct execution failed:', err.message);
  }
}

async function verifyDeployment() {
  console.log('\n🔍 Verifying deployment...');
  
  const tables = ['profiles', 'workspaces', 'subscriptions', 'payments', 'email_logs'];
  
  for (const table of tables) {
    try {
      const response = await fetch(`${supabaseUrl}/rest/v1/${table}?select=count&limit=1`, {
        headers: {
          'Authorization': `Bearer ${serviceRoleKey}`,
          'apikey': serviceRoleKey
        }
      });
      
      if (response.ok) {
        console.log(`✅ Table '${table}' accessible`);
      } else {
        console.log(`❌ Table '${table}' not accessible`);
      }
    } catch (err) {
      console.log(`⚠️  Could not verify table '${table}':`, err.message);
    }
  }
  
  console.log('\n📋 Deployment verification completed!');
  console.log('🔗 Check Supabase Dashboard: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc');
}

// Execute push
pushToSupabase().catch(console.error);
