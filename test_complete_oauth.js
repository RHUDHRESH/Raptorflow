// Test the complete OAuth flow with cookies
import { createBrowserClient } from '@supabase/ssr';
import { createServerClient } from '@supabase/ssr';
import dotenv from 'dotenv';

dotenv.config();

// Mock cookies storage
const mockCookies = new Map();

async function testCompleteOAuthFlow() {
  try {
    console.log('🔍 Testing complete OAuth flow with cookies...');

    // Step 1: Client-side OAuth initiation (like in OAuthButton)
    console.log('\n1. Testing client-side OAuth initiation...');

    const clientSupabase = createBrowserClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      {
        cookies: {
          get(name) {
            return mockCookies.get(name);
          },
          set(name, value, options) {
            console.log(`Client setting cookie: ${name} = ${value}`);
            mockCookies.set(name, value);
          },
          remove(name, options) {
            mockCookies.delete(name);
          },
        },
      }
    );

    const { data: oauthData, error: oauthError } = await clientSupabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: 'http://localhost:3000/auth/callback',
        skipBrowserRedirect: true
      }
    });

    if (oauthError) {
      console.error('❌ OAuth initiation failed:', oauthError);
      return;
    }

    console.log('✅ OAuth URL generated:', oauthData.url);

    // Step 2: Check what cookies were set
    console.log('\n2. Checking cookies set by OAuth initiation...');
    // Note: In real scenario, cookies would be set automatically

    // Step 3: Server-side callback (like in auth/callback route)
    console.log('\n3. Testing server-side callback with cookies...');

    const serverSupabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      {
        cookies: {
          get(name) {
            console.log(`Getting cookie: ${name} = ${mockCookies.get(name)}`);
            return mockCookies.get(name);
          },
          set(name, value, options) {
            console.log(`Setting cookie: ${name} = ${value}`);
            mockCookies.set(name, value);
          },
          remove(name, options) {
            console.log(`Removing cookie: ${name}`);
            mockCookies.delete(name);
          },
        },
      }
    );

    console.log('✅ Server client created with cookie handling');

    // Test with fake code (this will still fail but should show different error)
    const { data, error } = await serverSupabase.auth.exchangeCodeForSession('fake_code_12345');

    if (error) {
      if (error.code === 'pkce_code_verifier_not_found') {
        console.log('🔥 PKCE error still occurs - cookies not being shared between client and server');
        console.log('💡 Solution: Ensure both client and server use the same cookie domain and storage');
      } else {
        console.log('✅ Different error (expected with fake code):', error.message);
      }
    }

  } catch (error) {
    console.error('❌ Test error:', error);
  }
}

testCompleteOAuthFlow();
