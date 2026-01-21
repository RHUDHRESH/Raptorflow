const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseKey);

async function compareTables() {
    const { data: users } = await supabase.from('users').select('*');
    const { data: profiles } = await supabase.from('profiles').select('*');

    console.log('--- USERS ---');
    console.log(JSON.stringify(users, null, 2));
    console.log('--- PROFILES ---');
    console.log(JSON.stringify(profiles, null, 2));
}

compareTables();
