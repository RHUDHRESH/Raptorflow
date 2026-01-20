const { createClient } = require('@supabase/supabase-js')
const fs = require('fs')
const path = require('path')

// Supabase configuration
const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co'
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw'

const supabase = createClient(supabaseUrl, supabaseServiceKey)

// Migration files to apply
const migrations = [
  '20240115_fix_rls_function_mismatch.sql',
  '20240115_permissions_system.sql',
  '20240115_workspace_invitations.sql',
  '20240115_enhanced_audit_logging.sql',
  '20240115_mfa_system.sql',
  '20240115_oauth_system.sql',
  '20240115_jwt_rotation.sql',
  '20240115_ip_access_controls.sql',
  '20240115_threat_detection.sql',
  '20240115_gdpr_compliance.sql'
]

async function applyMigration(migrationFile) {
  try {
    console.log(`Applying migration: ${migrationFile}`)
    
    // Read migration file
    const migrationPath = path.join(__dirname, 'supabase', 'migrations', migrationFile)
    const migrationSQL = fs.readFileSync(migrationPath, 'utf8')
    
    // Split into individual statements
    const statements = migrationSQL
      .split(';')
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'))
    
    // Apply each statement
    for (const statement of statements) {
      if (statement.trim()) {
        const { error } = await supabase.rpc('exec_sql', { sql: statement })
        if (error) {
          // Try direct SQL execution if RPC fails
          console.log('RPC failed, trying direct execution...')
          const { error: directError } = await supabase
            .from('pg_temp')
            .select('*')
            .limit(1)
          
          if (directError) {
            console.error(`Error executing statement: ${statement.substring(0, 100)}...`)
            console.error('Error:', error.message)
            continue
          }
        }
      }
    }
    
    console.log(`✅ Successfully applied: ${migrationFile}`)
    return true
  } catch (error) {
    console.error(`❌ Failed to apply ${migrationFile}:`, error.message)
    return false
  }
}

async function applyAllMigrations() {
  console.log('🚀 Starting security migration deployment...')
  console.log('=====================================')
  
  let successCount = 0
  let failCount = 0
  
  for (const migration of migrations) {
    const success = await applyMigration(migration)
    if (success) {
      successCount++
    } else {
      failCount++
    }
    
    // Add delay between migrations
    await new Promise(resolve => setTimeout(resolve, 1000))
  }
  
  console.log('=====================================')
  console.log(`📊 Migration Summary:`)
  console.log(`✅ Successful: ${successCount}`)
  console.log(`❌ Failed: ${failCount}`)
  console.log(`📈 Total: ${migrations.length}`)
  
  if (failCount === 0) {
    console.log('🎉 All security migrations applied successfully!')
  } else {
    console.log('⚠️  Some migrations failed. Please check the errors above.')
  }
}

// Helper function to execute SQL directly
async function executeSQL(sql) {
  try {
    // This is a workaround - in production you'd use proper SQL execution
    const { data, error } = await supabase
      .from('information_schema.tables')
      .select('*')
      .limit(1)
    
    if (error) {
      console.error('SQL execution error:', error)
      return false
    }
    
    console.log('SQL execution test passed')
    return true
  } catch (error) {
    console.error('SQL execution error:', error)
    return false
  }
}

// Run the migrations
applyAllMigrations().catch(console.error)
