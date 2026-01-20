const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseKey);

async function listAll() {
    console.log('Fetching all tables from database...');
    
    // We'll use a direct query via the REST API to information_schema
    // Note: PostgREST doesn't expose information_schema by default, 
    // but we can try to guess tables or use the 'rpc' method if 'exec_sql' exists.
    
    const { data, error } = await supabase.rpc('exec_sql', { 
        sql_query: "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'" 
    });

    if (error) {
        console.log('exec_sql failed, trying variations...');
        const { data: data2, error: error2 } = await supabase.rpc('exec_sql', { 
            sql: "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'" 
        });
        
        if (error2) {
            console.error('All RPC attempts failed.');
            console.log('Falling back to direct table probing...');
            const commonTables = ['users', 'profiles', 'workspaces', 'system_settings', 'api_keys', 'usage_records'];
            for (const table of commonTables) {
                const { error: probeError } = await supabase.from(table).select('*').limit(1);
                if (!probeError) {
                    console.log(`✅ Table exists: ${table}`);
                } else {
                    console.log(`❌ Table missing or error: ${table} (${probeError.message})`);
                }
            }
            return;
        }
        console.log('Tables:', data2);
    } else {
        console.log('Tables:', data);
    }
}

listAll();
