import { test, expect } from '@playwright/test';

test.describe('Authentication Debug Test', () => {
  test('Debug authentication failure', async ({ page }) => {
    console.log('🔍 Debugging authentication failure...');

    // Step 1: Check current database status
    console.log('📊 Checking database status...');
    const dbResponse = await page.goto('http://localhost:3000/api/test-db-direct');
    const dbData = await dbResponse?.json();

    console.log('Database Status:', JSON.stringify(dbData, null, 2));

    if (!dbData.user_profiles_exists || !dbData.payments_exists) {
      console.log('❌ CONFIRMED: Database tables missing');
      console.log('🔧 SOLUTION: Create database tables');

      // Show the fix page
      await page.goto('http://localhost:3000/fix-auth');
      await page.waitForLoadState('networkidle');

      console.log('📋 Fix page loaded - user needs to execute SQL');
      console.log('📍 Next steps: Copy SQL → Open Supabase → Execute → Test');

      return;
    }

    // Step 2: Test authentication flow
    console.log('🧪 Testing authentication flow...');

    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');

    // Switch to signup
    await page.click('button:has-text("Sign Up")');
    await page.waitForTimeout(1000);

    // Fill form
    const testEmail = `debug-${Date.now()}@raptorflow.in`;
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="text"]', 'Debug Test User');
    await page.fill('input[type="password"]', 'debug123456');

    // Submit
    await page.click('button:has-text("Create Account")');
    await page.waitForTimeout(5000);

    const currentUrl = page.url();

    if (currentUrl.includes('/pricing')) {
      console.log('✅ Authentication SUCCESS - redirected to pricing');
    } else if (currentUrl.includes('/login')) {
      console.log('❌ Authentication FAILED - still on login page');

      // Check for error messages
      const errorElement = page.locator('text=/error|failed|unable/i');
      if (await errorElement.isVisible()) {
        const errorMsg = await errorElement.textContent();
        console.log('📝 Error message:', errorMsg);
      }

      // Check if there are any validation errors
      const emailError = page.locator('text=/email/i');
      const passwordError = page.locator('text=/password/i');

      if (await emailError.isVisible()) {
        console.log('📝 Email validation error present');
      }

      if (await passwordError.isVisible()) {
        console.log('📝 Password validation error present');
      }
    } else {
      console.log(`❌ Unexpected redirect to: ${currentUrl}`);
    }

    // Step 3: Test API directly
    console.log('🔌 Testing authentication API directly...');

    let apiData: any;

    try {
      const apiResponse = await page.request.post('http://localhost:3000/api/test-auth', {
        data: {
          email: testEmail,
          password: 'debug123456',
          fullName: 'Debug Test User'
        }
      });

      apiData = await apiResponse.json();
      console.log('API Response:', JSON.stringify(apiData, null, 2));

      if (apiData.success) {
        console.log('✅ API authentication SUCCESS');
      } else {
        console.log('❌ API authentication FAILED');
        console.log('Error:', apiData.error);
      }
    } catch (error: any) {
      console.log('❌ API request failed:', error.message);
    }

    // Step 4: Summary
    console.log('📋 DEBUG SUMMARY:');
    console.log('  Database Tables:', dbData.user_profiles_exists && dbData.payments_exists ? '✅ Exist' : '❌ Missing');
    console.log('  Frontend Auth:', currentUrl.includes('/pricing') ? '✅ Working' : '❌ Failed');
    console.log('  API Auth:', apiData?.success ? '✅ Working' : '❌ Failed');

    if (!dbData.user_profiles_exists || !dbData.payments_exists) {
      console.log('🔧 RECOMMENDATION: Create database tables first');
      console.log('📍 Go to: http://localhost:3000/fix-auth');
    }

    console.log('🎯 DEBUG TEST COMPLETE');
  });
});
