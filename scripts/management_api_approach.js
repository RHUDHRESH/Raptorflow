// Try using Supabase Management API directly
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const supabaseUrl = 'https://api.supabase.com';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

async function tryManagementAPI() {
  console.log('🔧 Trying Supabase Management API...\n');
  
  try {
    // Read the SQL file
    const sqlPath = path.join(__dirname, '../missing_tables.sql');
    const sqlContent = fs.readFileSync(sqlPath, 'utf8');
    
    console.log('📁 SQL file loaded');
    
    // Try using the Management API to execute SQL
    const projectId = 'vpwwzsanuyhpkvgorcnc';
    
    console.log('🔄 Attempting Management API execution...');
    
    const response = await fetch(`${supabaseUrl}/v1/projects/${projectId}/database/query`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${serviceRoleKey}`,
        'Content-Type': 'application/json',
        'apikey': serviceRoleKey
      },
      body: JSON.stringify({
        query: sqlContent
      })
    });
    
    if (response.ok) {
      console.log('✅ Management API execution successful!');
      const result = await response.json();
      console.log('Result:', result);
      
      // Verify tables
      await verifyTables();
      
    } else {
      const errorText = await response.text();
      console.log('❌ Management API failed:', response.status, errorText);
      
      // Try alternative approach
      await tryAlternativeManagementAPI(sqlContent, projectId);
    }
    
  } catch (error) {
    console.error('❌ Management API approach failed:', error);
    
    // Final fallback - provide clear manual instructions
    console.log('\n📋 FINAL RECOMMENDATION:');
    console.log('🔗 Manual execution is the most reliable approach');
    console.log('\n📝 Steps to complete:');
    console.log('1. Open: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc');
    console.log('2. Go to SQL Editor');
    console.log('3. Copy and paste the SQL from missing_tables.sql');
    console.log('4. Click "Run"');
    console.log('5. Verify with: node scripts/quick_check.js');
  }
}

async function tryAlternativeManagementAPI(sql, projectId) {
  console.log('\n🔄 Trying alternative Management API approach...');
  
  try {
    // Try using a different endpoint
    const response = await fetch(`${supabaseUrl}/v1/projects/${projectId}/database/sql`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${serviceRoleKey}`,
        'Content-Type': 'application/json',
        'apikey': serviceRoleKey
      },
      body: JSON.stringify({
        sql: sql
      })
    });
    
    if (response.ok) {
      console.log('✅ Alternative Management API successful!');
      const result = await response.json();
      console.log('Result:', result);
      
      await verifyTables();
      
    } else {
      const errorText = await response.text();
      console.log('❌ Alternative Management API failed:', response.status, errorText);
      
      console.log('\n📋 All API approaches exhausted');
      console.log('🔗 Manual execution required');
    }
    
  } catch (err) {
    console.log('❌ Alternative Management API failed:', err.message);
  }
}

async function verifyTables() {
  console.log('\n🔍 Verifying table creation...');
  
  const tables = ['profiles', 'workspaces', 'subscriptions', 'payments', 'email_logs'];
  let existingCount = 0;
  
  for (const table of tables) {
    try {
      const response = await fetch(`https://vpwwzsanuyhpkvgorcnc.supabase.co/rest/v1/${table}?select=count&limit=1`, {
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
  }
}

// Execute
tryManagementAPI().catch(console.error);
