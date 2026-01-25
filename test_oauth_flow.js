// Test OAuth flow directly
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function testOAuthFlow() {
  try {
    console.log('🔍 Testing OAuth flow...');
    
    // Test 1: Check if we can generate OAuth URL
    console.log('\n1. Testing OAuth URL generation...');
    const { data: urlData, error: urlError } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: 'http://localhost:3000/auth/callback',
        skipBrowserRedirect: true
      }
    });
    
    if (urlError) {
      console.error('❌ OAuth URL generation failed:', urlError);
      return;
    }
    
    console.log('✅ OAuth URL generated:', urlData.url);
    
    // Test 2: Simulate the callback with a test code
    console.log('\n2. Testing code exchange (this will fail without real code)...');
    
    // Extract the provider and test if we can at least call the exchange method
    const testCode = 'test_code_12345';
    const { data: sessionData, error: sessionError } = await supabase.auth.exchangeCodeForSession(testCode);
    
    if (sessionError) {
      console.log('Expected error with test code:', sessionError.message);
    }
    
    console.log('✅ OAuth flow test completed');
    
  } catch (error) {
    console.error('❌ OAuth test error:', error);
  }
}

testOAuthFlow();
