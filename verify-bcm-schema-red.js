const { createClient } = require('@supabase/supabase-js')

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co'
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw'

const supabase = createClient(supabaseUrl, supabaseServiceKey)

async function verifyBcmEvents() {
  console.log('🔍 Verifying bcm_events table...')
  
  // Try to query the table
  const { data, error } = await supabase
    .from('bcm_events')
    .select('*')
    .limit(1)
    
  if (error) {
    if (error.code === 'PGRST116' || error.message.includes('does not exist') || error.message.includes('Could not find the table')) {
      console.log('✅ Red Phase Confirmed: bcm_events table does not exist yet.')
      process.exit(0)
    } else {
      console.error('❌ Unexpected error:', error.message)
      process.exit(1)
    }
  } else {
    console.log('⚠️ Warning: bcm_events table already exists.')
    if (data.length > 0) {
      console.log('Columns found:', Object.keys(data[0]))
    }
    process.exit(0)
  }
}

verifyBcmEvents()
