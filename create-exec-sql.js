const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://vpwwzsanuyhpkvgorcnc.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw';

const supabase = createClient(supabaseUrl, supabaseServiceKey);

const sql = `
CREATE OR REPLACE FUNCTION public.exec_sql(sql_query TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE sql_query;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

REVOKE ALL ON FUNCTION public.exec_sql(TEXT) FROM public;
GRANT EXECUTE ON FUNCTION public.exec_sql(TEXT) TO service_role;
`;

async function createFunction() {
  console.log('🚀 Attempting to create exec_sql function via RPC call to itself (hacky)...');
  
  // Try calling exec_sql to create exec_sql - this is a long shot but sometimes works if it's partially there
  const { error } = await supabase.rpc('exec_sql', { sql_query: sql });
  
  if (error) {
    console.error('❌ RPC Hack failed:', error.message);
    console.log('Trying alternative: searching for ANY way to run raw SQL...');
    
    // Some older versions of Supabase had a 'sql' or 'raw_sql' RPC
    const alternatives = ['sql', 'raw_sql', 'execute_sql', 'query'];
    for (const alt of alternatives) {
      console.log(`Checking alternative RPC: ${alt}...`);
      const { error: altError } = await supabase.rpc(alt, { query: 'SELECT 1' });
      if (!altError) {
        console.log(`✅ Found working alternative: ${alt}`);
        // Use this alternative to create exec_sql
        const { error: finalError } = await supabase.rpc(alt, { query: sql });
        if (!finalError) {
          console.log('✅ exec_sql created successfully via alternative!');
          return;
        }
      }
    }
    
    console.log('❌ No alternative RPCs found. Manual creation in Dashboard SQL Editor is required.');
  } else {
    console.log('✅ exec_sql created successfully!');
  }
}

createFunction();
