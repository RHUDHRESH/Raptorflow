// Simple Auth Test - No Bloat, Just Results
import { chromium } from 'playwright';

const TESTS = {
  // Core Auth Tests Only
  'LOGIN': {
    url: '/login',
    actions: ['fill email', 'fill password', 'click submit'],
    expected: 'redirect to dashboard'
  },
  'SIGNUP': {
    url: '/signup',
    actions: ['fill form', 'click submit'],
    expected: 'redirect to onboarding'
  },
  'LOGOUT': {
    url: '/dashboard',
    actions: ['click logout'],
    expected: 'redirect to login'
  }
};

async function runSimpleAuthTest() {
  console.log('🔥 Starting Simple Auth Test...');
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  try {
    // Test 1: Login Flow
    console.log('Testing LOGIN...');
    await page.goto('http://localhost:3000/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
    console.log('✅ LOGIN: PASSED');

    // Test 2: Logout Flow
    console.log('Testing LOGOUT...');
    await page.click('[data-testid="logout"]');
    await page.waitForURL('**/login');
    console.log('✅ LOGOUT: PASSED');

    // Test 3: Signup Flow
    console.log('Testing SIGNUP...');
    await page.goto('http://localhost:3000/signup');
    await page.fill('input[name="email"]', 'newuser@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.fill('input[name="confirmPassword"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/onboarding');
    console.log('✅ SIGNUP: PASSED');

  } catch (error) {
    console.log('❌ TEST FAILED:', error.message);
  } finally {
    await browser.close();
  }
}

// Database Test - Simple SQL Check
async function testDatabaseAuth() {
  console.log('🔍 Testing Database Auth Tables...');

  const tables = ['users', 'auth_sessions', 'user_profiles'];

  for (const table of tables) {
    try {
      const result = await supabase
        .from(table)
        .select('count')
        .limit(1);
      console.log(`✅ ${table}: EXISTS`);
    } catch (error) {
      console.log(`❌ ${table}: MISSING - ${error.message}`);
    }
  }
}

// Run all tests
async function main() {
  console.log('🚀 RAPTORFLOW AUTH TEST - NO BLOAT EDITION\n');

  await runSimpleAuthTest();
  await testDatabaseAuth();

  console.log('\n✨ TEST COMPLETE - If you see ✅ above, you\'re good to go!');
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export { runSimpleAuthTest, testDatabaseAuth };
