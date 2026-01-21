const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseKey);

async function getColumns() {
    const tables = ['users', 'profiles', 'subscriptions', 'workspaces'];
    for (const table of tables) {
        console.log(`--- Table: ${table} ---`);
        const { data, error } = await supabase.from(table).select('*').limit(0);
        if (error) {
            console.error(`Error fetching columns for ${table}:`, error.message);
        } else {
            // This might not give columns if empty, but let's see.
            // Actually, we can use a RPC or just try to insert a dummy to see schema error?
            // Better: select * from pg_attribute where attrelid = 'public.table'::regclass
            const { data: cols, error: err } = await supabase.rpc('get_table_columns', { table_name: table });
            if (err) {
                 console.log(`RPC get_table_columns failed for ${table}: ${err.message}`);
                 // Fallback: try to select one row and see what keys we get
                 const { data: row } = await supabase.from(table).select('*').limit(1);
                 if (row && row.length > 0) {
                     console.log('Columns:', Object.keys(row[0]));
                 }
            } else {
                 console.log('Columns:', cols);
            }
        }
    }
}

getColumns();
