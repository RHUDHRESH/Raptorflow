// Quick check of current Supabase state
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const serviceRoleKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false }
});

async function quickCheck() {
  console.log('⚡ Quick Supabase Status Check\n');
  
  const tables = ['profiles', 'workspaces', 'subscriptions', 'payments', 'email_logs'];
  const results = {};
  
  for (const table of tables) {
    try {
      const { data, error } = await supabase
        .from(table)
        .select('count')
        .limit(1);
      
      if (error && error.code === 'PGRST116') {
        results[table] = '❌ NOT FOUND';
      } else if (error) {
        results[table] = `⚠️ ERROR: ${error.message}`;
      } else {
        results[table] = '✅ EXISTS';
      }
    } catch (err) {
      results[table] = `❌ FAILED: ${err.message}`;
    }
  }
  
  console.log('📋 Table Status:');
  Object.entries(results).forEach(([table, status]) => {
    console.log(`  ${status} ${table}`);
  });
  
  const existing = Object.values(results).filter(s => s.includes('✅')).length;
  const missing = Object.values(results).filter(s => s.includes('❌')).length;
  
  console.log(`\n📊 Summary: ${existing}/5 tables exist, ${missing}/5 missing`);
  
  if (missing > 0) {
    console.log('\n🔧 Next: Execute SQL from MANUAL_DEPLOYMENT_STEPS.md');
  } else {
    console.log('\n🎉 All tables exist! Test authentication flow.');
  }
  
  // Test the critical workspace query
  console.log('\n🧪 Testing workspace query...');
  try {
    const { data, error } = await supabase
      .from('workspaces')
      .select('id, owner_id')
      .eq('owner_id', '00000000-0000-0000-0000-000000000000')
      .limit(1);
    
    if (error && error.message.includes('user_id')) {
      console.log('❌ Workspace query still has user_id reference');
    } else {
      console.log('✅ Workspace query works correctly');
    }
  } catch (err) {
    console.log('⚠️ Workspace query test inconclusive');
  }
}

quickCheck().catch(console.error);
