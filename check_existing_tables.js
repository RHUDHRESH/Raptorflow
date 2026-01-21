const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkTables() {
    console.log('Checking tables...');
    const tables = ['users', 'profiles', 'user_profiles', 'workspaces', 'subscriptions', 'payments', 'email_logs'];
    for (const table of tables) {
        const { data, error } = await supabase.from(table).select('*').limit(1);
        if (error) {
            console.log(`❌ Table '${table}' error: ${error.message}`);
        } else {
            console.log(`✅ Table '${table}' exists. Row count: ${data.length}`);
        }
    }
}

checkTables();
