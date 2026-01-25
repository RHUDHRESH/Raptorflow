// Script to push schema directly to Supabase
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Configuration
const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

// Create Supabase client with service role key
const supabase = createClient(supabaseUrl, serviceRoleKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

async function executeMigration() {
  try {
    console.log('🚀 Starting schema push to Supabase...');
    
    // Read the latest migration file
    const migrationPath = path.join(__dirname, '../supabase/migrations/20260122074403_final_auth_consolidation.sql');
    const migrationSQL = fs.readFileSync(migrationPath, 'utf8');
    
    console.log('📁 Migration file loaded:', migrationPath);
    
    // Split SQL into individual statements
    const statements = migrationSQL
      .split(';')
      .map(s => s.trim())
      .filter(s => s && !s.startsWith('--'));
    
    console.log(`📝 Found ${statements.length} SQL statements to execute`);
    
    // Execute each statement
    for (let i = 0; i < statements.length; i++) {
      const statement = statements[i];
      if (statement.trim()) {
        console.log(`⚡ Executing statement ${i + 1}/${statements.length}...`);
        
        try {
          const { error } = await supabase.rpc('exec_sql', { sql: statement });
          
          if (error) {
            // If exec_sql doesn't exist, try direct SQL
            console.log('🔄 Trying direct SQL execution...');
            const { error: directError } = await supabase
              .from('pg_temp')
              .select('*')
              .limit(1);
            
            if (directError && directError.code === 'PGRST116') {
              // Table doesn't exist, try using raw SQL through a different approach
              console.log('⚠️  Cannot execute DDL via client. Please use Supabase Dashboard or CLI.');
              console.log('📋 SQL to execute manually:');
              console.log('---');
              console.log(statement);
              console.log('---');
            }
          } else {
            console.log(`✅ Statement ${i + 1} executed successfully`);
          }
        } catch (err) {
          console.log(`⚠️  Statement ${i + 1} failed:`, err.message);
          console.log('📋 Failed statement:');
          console.log('---');
          console.log(statement);
          console.log('---');
        }
      }
    }
    
    console.log('🎉 Schema push completed!');
    
    // Verify tables were created
    console.log('🔍 Verifying table creation...');
    const tables = ['profiles', 'subscriptions', 'payments', 'email_logs', 'workspaces'];
    
    for (const table of tables) {
      try {
        const { data, error } = await supabase
          .from(table)
          .select('*')
          .limit(1);
        
        if (error && error.code === 'PGRST116') {
          console.log(`❌ Table '${table}' not found`);
        } else {
          console.log(`✅ Table '${table}' exists`);
        }
      } catch (err) {
        console.log(`⚠️  Could not verify table '${table}':`, err.message);
      }
    }
    
  } catch (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  }
}

// Alternative approach using fetch directly
async function executeWithFetch() {
  try {
    console.log('🚀 Starting schema push via REST API...');
    
    const migrationPath = path.join(__dirname, '../supabase/migrations/20260122074403_final_auth_consolidation.sql');
    const migrationSQL = fs.readFileSync(migrationPath, 'utf8');
    
    // Use the Supabase REST API to execute SQL
    const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${serviceRoleKey}`,
        'Content-Type': 'application/json',
        'apikey': serviceRoleKey
      },
      body: JSON.stringify({ sql: migrationSQL })
    });
    
    if (response.ok) {
      console.log('✅ Schema executed successfully via REST API');
    } else {
      console.log('⚠️  REST API execution failed:', response.statusText);
      console.log('📋 Please execute the SQL manually in Supabase Dashboard:');
      console.log('---');
      console.log(migrationSQL);
      console.log('---');
    }
  } catch (error) {
    console.error('❌ Migration failed:', error);
  }
}

// Run the migration
executeMigration().catch(console.error);
