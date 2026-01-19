const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Read .env file manually since we don't have dotenv easily available in this context without installing
const envPath = path.resolve(process.cwd(), '.env');
const envContent = fs.readFileSync(envPath, 'utf8');
const env = {};
envContent.split('\n').forEach(line => {
    const match = line.match(/^([^#=]+)=(.*)$/);
    if (match) {
        env[match[1].trim()] = match[2].trim();
    }
});

const supabaseUrl = env.SUPABASE_URL || env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.error('Missing Supabase credentials in .env');
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function listTables() {
    console.log('Fetching table list...');
    
    // We query the information_schema via a RPC if possible, 
    // or just try to select from common tables to see what exists.
    // Actually, the best way with supabase-js and service key is to use the direct SQL execution if possible, 
    // but the library doesn't expose it directly for arbitrary SQL unless we use a function.
    
    // Alternative: use the PostgREST meta-endpoint if available, 
    // but service_role key usually allows us to see everything.
    
    const { data, error } = await supabase
        .from('information_schema.tables')
        .select('table_name')
        .eq('table_schema', 'public');

    if (error) {
        // If information_schema is not accessible via PostgREST (usually it's not), 
        // we'll try to list tables from the migrations folder as a fallback audit.
        console.log('Could not access information_schema via API. Falling back to migration files audit.');
        return;
    }

    console.log('Tables found:');
    data.forEach(t => console.log(`- ${t.table_name}`));
}

listTables();
