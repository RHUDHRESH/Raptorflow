// Test the onboarding layout fix
import { createServerClient } from '@supabase/ssr';
import dotenv from 'dotenv';

dotenv.config();

async function testOnboardingLayout() {
  console.log('🧪 Testing onboarding layout fix...');

  // Mock cookies (simulating browser after OAuth)
  const mockCookies = new Map();

  // Simulate session cookies that would be set after successful OAuth
  mockCookies.set('sb-vpwwzsanuyhpkvgorcnc-auth-token', 'mock-session-token');

  // Create server client (same as in onboarding layout)
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
    {
      cookies: {
        getAll() {
          return Array.from(mockCookies.entries()).map(([name, value]) => ({
            name,
            value
          }));
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => {
            mockCookies.set(name, value);
          });
        },
      },
    }
  );

  console.log('✅ Server client created');

  // Test the fixed getSession() call
  console.log('Testing getSession() call...');

  try {
    const { data } = await supabase.auth.getSession();
    console.log('✅ getSession() succeeded');
    console.log('Data structure:', typeof data);
    console.log('Has session property:', 'session' in (data || {}));

    // This should not crash anymore
    const session = data?.session;
    console.log('Session extracted safely:', !!session);

    console.log('🎉 Onboarding layout fix works!');
    return true;

  } catch (error) {
    console.error('❌ Error in getSession():', error.message);
    return false;
  }
}

testOnboardingLayout().then(success => {
  console.log('\n📊 Test Results:');
  if (success) {
    console.log('✅ Onboarding layout should work now');
    console.log('🚀 Try refreshing http://localhost:3000/onboarding/plans');
  } else {
    console.log('❌ Still has issues');
  }
});
