const { createClient } = require('@supabase/supabase-js')
const fs = require('fs')
const path = require('path')

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co'
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw'

const supabase = createClient(supabaseUrl, supabaseServiceKey)

async function applyConsolidation() {
    try {
        const migrationFile = '20260119_auth_overhaul_consolidation.sql'
        console.log(`🚀 Applying consolidation migration: ${migrationFile}`)
        
        const migrationPath = path.join(__dirname, 'supabase', 'migrations', migrationFile)
        const migrationSQL = fs.readFileSync(migrationPath, 'utf8')
        
        // Split into individual statements, handling common PG blocks
        // Simple semicolon split for now, assuming statements are well-behaved
        const statements = migrationSQL
            .split(';')
            .map(stmt => stmt.trim())
            .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'))
        
        let successCount = 0
        let failCount = 0

        for (const statement of statements) {
            console.log(`Executing: ${statement.substring(0, 50)}...`)
            const { error } = await supabase.rpc('exec_sql', { sql_query: statement + ';' })
            
            if (error) {
                console.error(`❌ Error executing statement:`, error.message)
                failCount++
            } else {
                successCount++
            }
        }

        console.log('\n=====================================')
        console.log(`📊 Migration Summary:`)
        console.log(`✅ Successful: ${successCount}`)
        console.log(`❌ Failed: ${failCount}`)
        console.log('=====================================')

    } catch (error) {
        console.error('Fatal error:', error.message)
    }
}

applyConsolidation()
