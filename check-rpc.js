const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function checkRpc() {
  console.log('🔍 Checking exec_sql RPC variations...');
  
  const queries = [
    { name: 'exec_sql(sql_query)', rpc: 'exec_sql', params: { sql_query: 'SELECT 1' } },
    { name: 'exec_sql(sql)', rpc: 'exec_sql', params: { sql: 'SELECT 1' } },
    { name: 'exec_sql(query)', rpc: 'exec_sql', params: { query: 'SELECT 1' } },
    { name: 'exec_sql() - no params', rpc: 'exec_sql', params: {} }
  ];
  
  for (const q of queries) {
    console.log(`Testing ${q.name}...`);
    const { data, error } = await supabase.rpc(q.rpc, q.params);
    if (error) {
      console.log(`❌ ${q.name} failed: ${error.message} (${error.code})`);
      if (error.details) console.log(`   Details: ${error.details}`);
    } else {
      console.log(`✅ ${q.name} worked! Result:`, data);
    }
  }
}

checkRpc();
