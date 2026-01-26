// Test the exact callback flow
import { createServerClient } from '@supabase/ssr';
import dotenv from 'dotenv';

dotenv.config();

async function testCallbackFlow() {
  try {
    console.log('🔍 Testing callback flow...');

    // Simulate the server client creation (like in callback route)
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      {
        cookies: {
          get(name) {
            return null; // No cookies in test
          },
          set(name, value, options) {
            console.log(`Setting cookie: ${name}`);
          },
          remove(name, options) {
            console.log(`Removing cookie: ${name}`);
          },
        },
      }
    );

    console.log('✅ Server client created');

    // Test with a fake code to see the exact error
    console.log('Testing code exchange with fake code...');
    const { data, error } = await supabase.auth.exchangeCodeForSession('fake_code_12345');

    if (error) {
      console.error('❌ Code exchange error:', {
        message: error.message,
        status: error.status,
        code: error.code
      });

      // This should give us the exact error we're seeing
      if (error.message === 'Invalid API key') {
        console.log('🔥 Found the issue: Invalid API key error');
        console.log('This suggests the anon key is not valid for this operation');
      }
    } else {
      console.log('Unexpected success with fake code');
    }

  } catch (error) {
    console.error('❌ Test error:', error);
  }
}

testCallbackFlow();
