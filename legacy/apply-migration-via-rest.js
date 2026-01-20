const fs = require('fs');
const path = require('path');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const migrationFile = 'supabase/migrations/20260119_blackbox_resurrection.sql';

async function applyMigration() {
  try {
    console.log(`🚀 Applying migration via REST: ${migrationFile}`);
    const sqlContent = fs.readFileSync(path.join(__dirname, migrationFile), 'utf8');

    // First, try to create the exec_sql function if it doesn't exist
    // Wait, if exec_sql doesn't exist, how can we execute SQL to create it?
    // Some projects have a "backdoor" or the Supabase dashboard was used.
    // Let's assume we can't create it if it doesn't exist.
    
    // However, maybe we can try to call it.
    const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${supabaseServiceKey}`,
        'Content-Type': 'application/json',
        'apikey': supabaseServiceKey,
        'Prefer': 'return=minimal'
      },
      body: JSON.stringify({ sql_query: sqlContent }) // Note: frontend used { sql: ... }, migration_manager used { sql: ... }
    });

    if (response.ok) {
      console.log('✅ Migration applied successfully!');
    } else {
      const error = await response.text();
      console.error('❌ Migration failed:', error);
      
      console.log('Retrying with "sql" parameter instead of "sql_query"...');
      const response2 = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${supabaseServiceKey}`,
          'Content-Type': 'application/json',
          'apikey': supabaseServiceKey,
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify({ sql: sqlContent })
      });
      
      if (response2.ok) {
        console.log('✅ Migration applied successfully (with "sql" param)!');
      } else {
        const error2 = await response2.text();
        console.error('❌ Migration failed again:', error2);
      }
    }
  } catch (error) {
    console.error('❌ Critical error:', error.message);
  }
}

applyMigration();
