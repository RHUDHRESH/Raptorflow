// Test the anon key directly
import { createServerClient } from '@supabase/ssr';
import dotenv from 'dotenv';

dotenv.config();

async function testAnonKey() {
  console.log('Testing anon key directly...');
  
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        get() { return null; },
        set() {},
        remove() {}
      }
    }
  );

  try {
    // Test a simple API call
    const { data, error } = await supabase.from('profiles').select('count').single();
    
    if (error) {
      console.error('❌ Anon key test failed:', {
        message: error.message,
        status: error.status,
        code: error.code
      });
      
      // Try with service role key to see if it works
      console.log('\nTesting with service role key...');
      const serviceSupabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL,
        process.env.SUPABASE_SERVICE_ROLE_KEY,
        {
          cookies: {
            get() { return null; },
            set() {},
            remove() {}
          }
        }
      );
      
      const { data: serviceData, error: serviceError } = await serviceSupabase.from('profiles').select('count').single();
      
      if (serviceError) {
        console.error('❌ Service role key also failed:', serviceError.message);
      } else {
        console.log('✅ Service role key works! Anon key might be expired or invalid');
      }
    } else {
      console.log('✅ Anon key is valid');
    }
  } catch (error) {
    console.error('❌ Test error:', error);
  }
}

testAnonKey();
