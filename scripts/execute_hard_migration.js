const { createClient } = require('@supabase/supabase-js')
const fs = require('fs')
const path = require('path')

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co'
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw'

const supabase = createClient(supabaseUrl, supabaseServiceKey)

async function runHardMigration() {
    try {
        console.log('🚀 Starting Hard Migration: Auth Consolidation & Cleanup')
        
        const sqlPath = path.join(process.cwd(), 'scripts', 'hard_migration_consolidated.sql')
        const sqlContent = fs.readFileSync(sqlPath, 'utf8')
        
        // Remove transaction blocks for individual execution if needed, 
        // but try to run them via RPC first.
        const statements = sqlContent
            .replace(/BEGIN;/g, '')
            .replace(/COMMIT;/g, '')
            .split(';')
            .map(s => s.trim())
            .filter(s => s && !s.startsWith('--'))

        console.log(`Found ${statements.length} statements to execute.`) // Corrected: Removed unnecessary escaping of backtick

        let success = 0
        let fail = 0

        for (let i = 0; i < statements.length; i++) {
            const stmt = statements[i]
            console.log(`[${i+1}/${statements.length}] Executing: ${stmt.substring(0, 50)}...`) // Corrected: Removed unnecessary escaping of backtick
            
            const { error } = await supabase.rpc('exec_sql', { sql_query: stmt + ';' })
            
            if (error) {
                console.error(`❌ Error: ${error.message}`) // Corrected: Removed unnecessary escaping of backtick
                fail++
            } else {
                success++
            }
        }

        console.log('\n=====================================') // Corrected: Removed unnecessary escaping of backtick
        console.log(`📊 Migration Result:`) // Corrected: Removed unnecessary escaping of backtick
        console.log(`✅ Success: ${success}`) // Corrected: Removed unnecessary escaping of backtick
        console.log(`❌ Failed: ${fail}`) // Corrected: Removed unnecessary escaping of backtick
        console.log('=====================================') // Corrected: Removed unnecessary escaping of backtick

    } catch (err) {
        console.error('Fatal error during migration execution:', err.message)
    }
}

runHardMigration()
