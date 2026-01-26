// Test the OAuth callback with service role key
import { createServerClient } from '@supabase/ssr';
import dotenv from 'dotenv';

dotenv.config();

async function testOAuthCallback() {
  console.log('🔍 Testing OAuth callback with service role key...');

  // Mock cookies storage (simulating browser cookies)
  const mockCookies = new Map();

  // Simulate the PKCE verifier being set (as would happen in real OAuth flow)
  mockCookies.set('sb-vpwwzsanuyhpkvgorcnc-auth-token-code-verifier', 'test-verifier-12345');

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
    {
      cookies: {
        get(name) {
          console.log(`Getting cookie: ${name} = ${mockCookies.get(name) || 'undefined'}`);
          return mockCookies.get(name);
        },
        set(name, value, options) {
          console.log(`Setting cookie: ${name} = ${value?.substring(0, 50)}...`);
          mockCookies.set(name, value);
        },
        remove(name, options) {
          console.log(`Removing cookie: ${name}`);
          mockCookies.delete(name);
        },
      },
    }
  );

  console.log('✅ Server client created with service role key');

  // Test with a fake OAuth code (this will still fail but should show different error)
  console.log('Testing code exchange with fake code...');
  const { data, error } = await supabase.auth.exchangeCodeForSession('fake-oauth-code-12345');

  if (error) {
    console.error('❌ Code exchange error:', {
      message: error.message,
      status: error.status,
      code: error.code
    });

    if (error.message === 'Invalid API key') {
      console.log('🔥 Still getting Invalid API key - service role key might be wrong');
    } else {
      console.log('✅ Different error (expected with fake code):', error.message);
    }
  } else {
    console.log('✅ Code exchange succeeded (unexpected with fake code)');
  }

  // Also test if the service role key works for other operations
  console.log('\nTesting service role key with other operations...');

  try {
    const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
    if (sessionError) {
      console.log('❌ Session check failed:', sessionError.message);
    } else {
      console.log('✅ Session check works');
    }
  } catch (e) {
    console.log('❌ Session check exception:', e.message);
  }
}

testOAuthCallback();
