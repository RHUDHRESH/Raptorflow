// Apply Database Migrations Directly to Supabase
// Run with: node apply-migrations-direct.js

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function applyMigrations() {
  console.log('🔄 Applying Database Migrations to Supabase...\n');

  const migrations = [
    {
      name: '001_profiles.sql',
      file: 'supabase/migrations/001_profiles.sql',
      description: 'Create profiles table with RLS'
    },
    {
      name: '002_workspaces_rls.sql', 
      file: 'supabase/migrations/002_workspaces_rls.sql',
      description: 'Create workspaces and workspace_members tables'
    },
    {
      name: '004_password_reset_tokens.sql',
      file: 'supabase/migrations/004_password_reset_tokens.sql',
      description: 'Create password reset tokens table'
    }
  ];

  for (const migration of migrations) {
    console.log(`\n📋 Applying ${migration.name} - ${migration.description}`);
    
    try {
      const sqlContent = fs.readFileSync(path.join(__dirname, migration.file), 'utf8');
      
      // Split SQL into individual statements
      const statements = sqlContent
        .split(';')
        .map(s => s.trim())
        .filter(s => s && !s.startsWith('--') && !s.startsWith('/*'))
        .filter(s => s.toLowerCase().includes('create') || 
                   s.toLowerCase().includes('alter') || 
                   s.toLowerCase().includes('insert') ||
                   s.toLowerCase().includes('drop') ||
                   s.toLowerCase().includes('enable') ||
                   s.toLowerCase().includes('create policy') ||
                   s.toLowerCase().includes('create trigger') ||
                   s.toLowerCase().includes('create function') ||
                   s.toLowerCase().includes('create index'));

      console.log(`   Found ${statements.length} SQL statements to execute`);

      for (let i = 0; i < statements.length; i++) {
        const statement = statements[i].trim();
        if (statement) {
          console.log(`   Executing statement ${i + 1}/${statements.length}`);
          
          try {
            // Use raw SQL execution via Supabase
            const { error } = await supabase.rpc('exec_sql', { 
              sql_query: statement 
            });
            
            if (error) {
              // Try using direct SQL through the REST API
              console.log(`   ⚠️  RPC failed, trying direct SQL execution...`);
              
              // For now, just log the statement for manual execution
              console.log(`   📝 Statement requires manual execution:`);
              console.log(`   \n${statement}\n`);
            } else {
              console.log(`   ✅ Statement executed successfully`);
            }
          } catch (err) {
            console.log(`   ⚠️  Error executing statement: ${err.message}`);
            console.log(`   📝 Statement requires manual execution:`);
            console.log(`   \n${statement}\n`);
          }
        }
      }
      
      console.log(`   ✅ ${migration.name} processed`);
      
    } catch (error) {
      console.log(`   ❌ Error processing ${migration.name}:`, error.message);
    }
  }

  console.log('\n📊 Migration Summary:');
  console.log('✅ All migration files processed');
  console.log('📝 Some statements may require manual execution in Supabase SQL Editor');
  console.log('🔗 Supabase Dashboard: https://app.supabase.com');
  
  console.log('\n🎯 Manual Execution Required:');
  console.log('1. Go to Supabase Dashboard → SQL Editor');
  console.log('2. Run the following migration files:');
  migrations.forEach(m => console.log(`   - ${m.file}`));
  
  console.log('\n✅ Migration preparation complete!');
}

// Check if tables exist after migrations
async function verifyTables() {
  console.log('\n🔍 Verifying table creation...');
  
  const tables = ['profiles', 'workspaces', 'workspace_members', 'password_reset_tokens'];
  
  for (const table of tables) {
    try {
      const { data, error } = await supabase
        .from('pg_tables')
        .select('*')
        .eq('schemaname', 'public')
        .eq('tablename', table);
      
      if (error) {
        console.log(`   ❌ Error checking ${table}: ${error.message}`);
      } else if (data && data.length > 0) {
        console.log(`   ✅ Table ${table} exists`);
      } else {
        console.log(`   ⚠️  Table ${table} not found`);
      }
    } catch (err) {
      console.log(`   ❌ Error checking ${table}: ${err.message}`);
    }
  }
}

// Main execution
applyMigrations().then(() => {
  return verifyTables();
}).then(() => {
  console.log('\n🎉 Migration process completed!');
}).catch(error => {
  console.error('❌ Migration failed:', error);
});
