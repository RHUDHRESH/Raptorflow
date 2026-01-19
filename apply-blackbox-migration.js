const { createClient } = require('@supabase/supabase-js')
const fs = require('fs')
const path = require('path')

// Supabase configuration - using values from apply-migrations.js
const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co'
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw'

const supabase = createClient(supabaseUrl, supabaseServiceKey)

const migrationFile = '20260119_blackbox_resurrection.sql'

async function applyMigration() {
  try {
    console.log(`🚀 Applying Blackbox Resurrection migration: ${migrationFile}`)
    
    // Read migration file
    const migrationPath = path.join(__dirname, 'supabase', 'migrations', migrationFile)
    const migrationSQL = fs.readFileSync(migrationPath, 'utf8')
    
    // We use a simpler split here, but be careful with functions/triggers
    // For this specific migration, DO blocks and CREATE TABLE are handled by splitting on ";"
    // However, DO blocks contain ";" inside. 
    // Let's try to execute the whole block if possible, or use a more sophisticated parser.
    // Given the RPC 'exec_sql' likely exists:
    
    console.log('Sending migration to Supabase...')
    const { data, error } = await supabase.rpc('exec_sql', { sql: migrationSQL })
    
    if (error) {
      console.error('❌ RPC Error:', error.message)
      console.log('Trying to split statements as fallback...')
      
      const statements = migrationSQL
        .split(';')
        .map(stmt => stmt.trim())
        .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'))
        
      for (const statement of statements) {
        const { error: stmtError } = await supabase.rpc('exec_sql', { sql: statement })
        if (stmtError) {
          console.error(`  ⚠️ Statement failed: ${statement.substring(0, 50)}...`)
          console.error(`     Error: ${stmtError.message}`)
        } else {
          console.log(`  ✅ Success: ${statement.substring(0, 50)}...`)
        }
      }
    } else {
      console.log('✅ Successfully applied migration in one go!')
    }
    
    console.log('🎉 Done!')
  } catch (error) {
    console.error('❌ Critical Error:', error.message)
  }
}

applyMigration()
