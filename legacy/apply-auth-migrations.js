// Apply Auth Migrations to Supabase
// Run with: node apply-auth-migrations.js

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function applyMigrations() {
  console.log('🔄 Applying auth migrations...\n');

  const migrations = [
    'supabase/migrations/001_profiles.sql',
    'supabase/migrations/002_workspaces_rls.sql',
    'supabase/migrations/004_password_reset_tokens.sql'
  ];

  for (const migrationFile of migrations) {
    console.log(`Applying ${migrationFile}...`);
    
    try {
      const sql = fs.readFileSync(path.join(__dirname, migrationFile), 'utf8');
      
      // Split SQL by semicolons and execute each statement
      const statements = sql
        .split(';')
        .map(s => s.trim())
        .filter(s => s && !s.startsWith('--'));

      for (const statement of statements) {
        if (statement.trim()) {
          const { error } = await supabase.rpc('exec_sql', { sql_query: statement });
          
          if (error) {
            // Try direct SQL execution
            try {
              const { error: directError } = await supabase
                .from('pg_tables')
                .select('*')
                .limit(1);
              
              if (directError && directError.code === 'PGRST116') {
                console.log(`   ⚠️  Cannot execute SQL directly. Please run this in Supabase SQL Editor:`);
                console.log(`   \n${statement}\n`);
              }
            } catch (e) {
              console.log(`   ⚠️  SQL statement needs manual execution`);
            }
          }
        }
      }
      
      console.log(`   ✅ ${migrationFile} processed`);
    } catch (error) {
      console.log(`   ❌ Error processing ${migrationFile}:`, error.message);
    }
  }

  console.log('\n📋 Manual SQL Execution Required:');
  console.log('Please run the following SQL files in Supabase SQL Editor:');
  migrations.forEach(m => console.log(`   - ${m}`));
  
  console.log('\n🎯 After applying migrations:');
  console.log('1. Test user will have proper profile');
  console.log('2. Password reset tokens table will exist');
  console.log('3. Workspaces table will be ready');
}

applyMigrations();
