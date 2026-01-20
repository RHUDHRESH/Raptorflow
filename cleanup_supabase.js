const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseKey);

async function cleanup() {
    console.log('🚀 Starting Supabase cleanup...');

    // 1. Delete all users from auth
    console.log('Fetching users from auth...');
    const { data: { users }, error: listError } = await supabase.auth.admin.listUsers();
    
    if (listError) {
        console.error('Error listing users:', listError.message);
    } else {
        console.log(`Found ${users.length} users. Deleting...`);
        for (const user of users) {
            const { error: deleteError } = await supabase.auth.admin.deleteUser(user.id);
            if (deleteError) {
                console.error(`Error deleting user ${user.id}:`, deleteError.message);
            } else {
                console.log(`Deleted user ${user.id} (${user.email})`);
            }
        }
    }

    // 2. Clean up public tables
    const tables = ['workspaces', 'profiles', 'users', 'blackbox_strategies'];
    for (const table of tables) {
        console.log(`Cleaning table public.${table}...`);
        const { error } = await supabase.from(table).delete().neq('id', '00000000-0000-0000-0000-000000000000'); // Delete everything
        if (error) {
            console.error(`Error cleaning table ${table}:`, error.message);
        } else {
            console.log(`Table ${table} cleaned.`);
        }
    }

    console.log('✅ Cleanup complete.');
}

cleanup();
