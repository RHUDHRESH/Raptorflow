const { createClient } = require('@supabase/supabase-js')

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co'
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw'

const supabase = createClient(supabaseUrl, supabaseServiceKey)

async function checkSchema() {
  console.log('🔍 Checking blackbox_strategies schema...')
  
  // Query information_schema.columns
  const { data, error } = await supabase
    .from('blackbox_strategies')
    .select('*')
    .limit(1)
    
  if (error) {
    console.error('❌ Error fetching data:', error.message)
  } else {
    console.log('✅ Successfully connected to blackbox_strategies')
    if (data.length > 0) {
      console.log('Columns in table:', Object.keys(data[0]))
    } else {
      console.log('Table is empty, trying to get columns via RPC if available...')
      // We know RPC exec_sql is missing, but maybe there's another way?
      // Actually, we can just try to insert a dummy record with only ID and see what happens?
      // Or try to select a known column.
    }
  }
  
  // Try to list tables
  const { data: tables, error: tablesError } = await supabase
    .from('pg_catalog.pg_tables')
    .select('tablename')
    .eq('schemaname', 'public')
    
  if (tablesError) {
    console.log('❌ Could not list tables via pg_catalog (normal for restricted roles)')
  } else {
    console.log('Tables in public schema:', tables.map(t => t.tablename))
  }
}

checkSchema()
