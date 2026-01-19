const { createClient } = require('@supabase/supabase-js')
const fs = require('fs')
const path = require('path')

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co'
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw'

const supabase = createClient(supabaseUrl, supabaseServiceKey)

async function applyPricing() {
    try {
        console.log('🚀 Applying Pricing Update: Ascent(5k), Glide(7k), Soar(10k)')
        
        const sqlPath = path.join(process.cwd(), 'scripts', 'fix_plans_pricing.sql')
        const sqlContent = fs.readFileSync(sqlPath, 'utf8')
        
        const statements = sqlContent
            .replace(/BEGIN;/g, '')
            .replace(/COMMIT;/g, '')
            .split(';')
            .map(s => s.trim())
            .filter(s => s && !s.startsWith('--'))

        let success = 0
        let fail = 0

        for (let i = 0; i < statements.length; i++) {
            const stmt = statements[i]
            console.log(`[${i+1}/${statements.length}] Executing: ${stmt.substring(0, 50)}...`)
            
            // Try different RPC names based on project history
            const { error } = await supabase.rpc('exec_sql', { sql_query: stmt + ';' })
            
            if (error) {
                console.error(`❌ Error: ${error.message}`)
                fail++
            } else {
                success++
            }
        }

        console.log('\n=====================================')
        console.log(`📊 Result:`)
        console.log(`✅ Success: ${success}`)
        console.log(`❌ Failed: ${fail}`)
        console.log('=====================================')
        
        if (fail > 0) {
            console.log('\n⚠️  ACTION REQUIRED: Some statements failed via API.')
            console.log('Please copy scripts/fix_plans_pricing.sql and run it in Supabase SQL Editor.')
        }

    } catch (err) {
        console.error('Fatal error:', err.message)
    }
}

applyPricing()
