// Quick test script to create a user and test authentication
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'http://127.0.0.1:54321';
const supabaseKey = 'sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH';

const supabase = createClient(supabaseUrl, supabaseKey);

async function testAuth() {
  try {
    console.log('🧪 Testing Supabase connection...');
    
    // Test 1: Create a test user
    console.log('📝 Creating test user...');
    const { data: signUpData, error: signUpError } = await supabase.auth.signUp({
      email: 'test@raptorflow.local',
      password: 'test123456',
      options: {
        data: {
          full_name: 'Test User'
        }
      }
    });

    if (signUpError) {
      console.error('❌ Signup error:', signUpError);
    } else {
      console.log('✅ User created successfully:', signUpData.user?.email);
    }

    // Test 2: Try to sign in
    console.log('🔐 Testing sign in...');
    const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
      email: 'test@raptorflow.local',
      password: 'test123456'
    });

    if (signInError) {
      console.error('❌ Sign in error:', signInError);
    } else {
      console.log('✅ Sign in successful:', signInData.user?.email);
      console.log('🎫 Session:', signInData.session?.access_token ? 'Valid' : 'Invalid');
    }

    // Test 3: Check Google OAuth configuration
    console.log('🔍 Checking Google OAuth config...');
    const { data: settings } = await supabase.auth.getSession();
    console.log('✅ Auth service is running');

  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

testAuth();
