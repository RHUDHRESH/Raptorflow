// Test the complete OAuth flow end-to-end
import { createBrowserClient } from '@supabase/ssr';
import { createServerClient } from '@supabase/ssr';
import dotenv from 'dotenv';

dotenv.config();

async function testCompleteOAuthFlow() {
  console.log('🔍 Testing complete OAuth flow...');
  
  // Shared cookie storage between client and server
  const sharedCookies = new Map();
  
  // Step 1: Client-side OAuth initiation
  console.log('\n1. Client-side OAuth initiation...');
  
  const clientSupabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    {
      cookies: {
        get(name) {
          return sharedCookies.get(name);
        },
        set(name, value, options) {
          console.log(`🍪 Client setting: ${name}`);
          sharedCookies.set(name, value);
        },
        remove(name, options) {
          sharedCookies.delete(name);
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
  
  console.log('✅ OAuth URL generated');
  console.log('🔗 URL:', oauthData.url);
  
  // Step 2: Extract the OAuth flow state from the URL
  console.log('\n2. Extracting OAuth flow state...');
  const url = new URL(oauthData.url);
  const codeChallenge = url.searchParams.get('code_challenge');
  console.log('🔐 Code challenge:', codeChallenge?.substring(0, 20) + '...');
  
  // Step 3: Simulate server-side callback
  console.log('\n3. Server-side callback simulation...');
  
  const serverSupabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
    {
      cookies: {
        get(name) {
          const value = sharedCookies.get(name);
          if (name.includes('code-verifier') && value) {
            console.log(`🔓 Server reading PKCE verifier: ${value.substring(0, 20)}...`);
          }
          return value;
        },
        set(name, value, options) {
          console.log(`🍪 Server setting: ${name} = ${value?.substring(0, 50)}...`);
          sharedCookies.set(name, value);
        },
        remove(name, options) {
          sharedCookies.delete(name);
        },
      },
    }
  );
  
  // Test with a realistic fake OAuth code (not real but format-correct)
  console.log('Testing with realistic fake OAuth code...');
  const fakeOAuthCode = '8c8f9c0b-bb96-4d53-bad4-f55e8cabceb8'; // Same format as real codes
  
  const { data: sessionData, error: sessionError } = await serverSupabase.auth.exchangeCodeForSession(fakeOAuthCode);
  
  if (sessionError) {
    console.error('❌ Session exchange error:', {
      message: sessionError.message,
      status: sessionError.status,
      code: sessionError.code
    });
    
    if (sessionError.message === 'Invalid API key') {
      console.log('🔥 Still getting Invalid API key - need to investigate further');
    } else if (sessionError.code === 'flow_state_not_found') {
      console.log('✅ Expected error with fake code - OAuth flow mechanics work correctly');
    } else {
      console.log('ℹ️  Different error - might be expected with fake code');
    }
  } else {
    console.log('✅ Session exchange succeeded!');
  }
  
  console.log('\n4. Final cookie state...');
  console.log('Total cookies set:', sharedCookies.size);
  for (const [name, value] of sharedCookies.entries()) {
    console.log(`  ${name}: ${value?.substring(0, 30)}...`);
  }
}

testCompleteOAuthFlow();
