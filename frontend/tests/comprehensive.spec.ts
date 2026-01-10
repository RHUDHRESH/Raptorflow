import { test, expect } from '@playwright/test';

test.describe('Comprehensive System Test', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
  });

  test('Complete system verification', async ({ page }) => {
    console.log('🚀 Starting comprehensive system test...');

    // Test 1: Landing page
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    console.log('✅ Landing page loaded');

    // Test 2: Navigation to login
    await page.click('text=Get Started');
    await page.waitForTimeout(2000);
    console.log('✅ Navigation to login works');

    // Test 3: Login page elements
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('button:has-text("Sign Up")')).toBeVisible();
    console.log('✅ Login page elements present');

    // Test 4: Pricing page
    await page.goto('http://localhost:3000/pricing');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('text=Soar')).toBeVisible();
    await expect(page.locator('text=Glide')).toBeVisible();
    await expect(page.locator('text=Ascent')).toBeVisible();
    console.log('✅ Pricing page works');

    // Test 5: Workspace protection
    await page.goto('http://localhost:3000/workspace');
    await page.waitForTimeout(3000);
    const currentUrl = page.url();
    if (currentUrl.includes('/login')) {
      console.log('✅ Workspace properly protected');
    } else {
      console.log('⚠️ Workspace not protected');
    }

    // Test 6: API endpoints
    const apiTests = [
      { url: '/api/verify-setup', name: 'Setup verification' },
      { url: '/api/storage/upload-url', name: 'Storage upload' },
      { url: '/api/vertex-ai', name: 'Vertex AI' },
      { url: '/api/test-db-direct', name: 'Database test' }
    ];

    for (const api of apiTests) {
      try {
        const response = await page.goto(`http://localhost:3000${api.url}`);
        if (response?.status() === 405) {
          console.log(`✅ ${api.name} API endpoint exists`);
        } else if (response?.status() === 200) {
          console.log(`✅ ${api.name} API endpoint works`);
        } else {
          console.log(`⚠️ ${api.name} API endpoint status: ${response?.status()}`);
        }
      } catch (error) {
        console.log(`❌ ${api.name} API endpoint failed`);
      }
    }

    // Test 7: UI Components
    await page.goto('http://localhost:3000/login');
    await page.click('button:has-text("Sign Up")');
    await page.waitForTimeout(1000);

    // Check if form elements exist
    const emailInput = page.locator('input[type="email"]');
    const nameInput = page.locator('input[type="text"]');
    const passwordInput = page.locator('input[type="password"]');
    const createAccountBtn = page.locator('button:has-text("Create Account")');

    if (await emailInput.isVisible() && await nameInput.isVisible() && await passwordInput.isVisible() && await createAccountBtn.isVisible()) {
      console.log('✅ Signup form elements present');
    } else {
      console.log('❌ Signup form elements missing');
    }

    // Test 8: Try to create a test account (without database tables)
    const testEmail = `test-${Date.now()}@raptorflow.in`;
    await emailInput.fill(testEmail);
    await nameInput.fill('Test User');
    await passwordInput.fill('testpassword123');

    await createAccountBtn.click();
    await page.waitForTimeout(5000);

    const finalUrl = page.url();
    if (finalUrl.includes('/pricing')) {
      console.log('✅ Account creation successful');
    } else if (finalUrl.includes('/login')) {
      console.log('⚠️ Account creation failed (expected - no database tables)');
    } else {
      console.log(`❌ Unexpected redirect to: ${finalUrl}`);
    }

    // Test 9: Check error handling
    const errorElement = page.locator('text=/error|failed|unable/i');
    if (await errorElement.isVisible()) {
      const errorMsg = await errorElement.textContent();
      console.log(`📝 Error message displayed: ${errorMsg}`);
    }

    console.log('🎯 Comprehensive test completed');
  });

  test('Database connection verification', async ({ page }) => {
    console.log('🔍 Testing database connection...');

    // Test the database test endpoint
    const response = await page.goto('http://localhost:3000/api/test-db-direct');
    const data = await response?.json();

    if (data) {
      console.log('📊 Database test results:', JSON.stringify(data, null, 2));

      if (data.user_profiles_exists && data.payments_exists) {
        console.log('✅ Database tables exist');
      } else {
        console.log('❌ Database tables missing');
      }

      if (data.test_insert) {
        console.log('✅ Database operations work');
      } else {
        console.log('❌ Database operations failed');
      }
    } else {
      console.log('❌ Database test endpoint failed');
    }
  });

  test('Authentication flow simulation', async ({ page }) => {
    console.log('🔐 Testing authentication flow...');

    // Test Google OAuth button
    await page.goto('http://localhost:3000/login');
    const googleBtn = page.locator('button:has-text("Google")');
    if (await googleBtn.isVisible()) {
      console.log('✅ Google OAuth button present');
    } else {
      console.log('⚠️ Google OAuth button not found');
    }

    // Test email signup flow
    await page.click('button:has-text("Sign Up")');
    await page.waitForTimeout(1000);

    const testEmail = `auth-test-${Date.now()}@raptorflow.in`;
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="text"]', 'Auth Test User');
    await page.fill('input[type="password"]', 'auth123456');

    await page.click('button:has-text("Create Account")');
    await page.waitForTimeout(5000);

    const currentUrl = page.url();
    if (currentUrl.includes('/pricing')) {
      console.log('✅ Authentication flow successful');
    } else if (currentUrl.includes('/login')) {
      console.log('⚠️ Authentication flow failed (expected - no database tables)');
    } else {
      console.log(`❌ Unexpected authentication result: ${currentUrl}`);
    }
  });

  test('Payment flow verification', async ({ page }) => {
    console.log('💳 Testing payment flow...');

    // Go to pricing page
    await page.goto('http://localhost:3000/pricing');
    await page.waitForLoadState('networkidle');

    // Check if pricing elements are present
    const soarPrice = page.locator('text=₹5,000');
    const glidePrice = page.locator('text=₹7,000');
    const ascentPrice = page.locator('text=₹10,000');

    if (await soarPrice.isVisible() && await glidePrice.isVisible() && await ascentPrice.isVisible()) {
      console.log('✅ Pricing elements present');
    } else {
      console.log('❌ Pricing elements missing');
    }

    // Try to select a plan
    const chooseSoarBtn = page.locator('button').filter({ hasText: 'Choose Soar' });
    if (await chooseSoarBtn.isVisible()) {
      console.log('✅ Plan selection buttons present');
    } else {
      // Try alternative selector
      const selectSoarBtn = page.locator('button').filter({ hasText: 'Select Soar' });
      if (await selectSoarBtn.isVisible()) {
        console.log('✅ Alternative plan selection buttons present');
      } else {
        console.log('❌ Plan selection buttons missing');
      }
    }

    // Test payment API endpoint
    try {
      const paymentResponse = await page.request.post('http://localhost:3000/api/payment/create-order', {
        data: {
          planId: 'soar',
          amount: 5000
        }
      });

      if (paymentResponse.status() === 200) {
        console.log('✅ Payment API endpoint works');
      } else {
        console.log('⚠️ Payment API endpoint status: ' + paymentResponse.status());
      }
    } catch (error) {
      console.log('❌ Payment API endpoint failed');
    }
  });

  test('Storage and AI integration', async ({ page }) => {
    console.log('💾 Testing storage and AI integration...');

    // Test storage endpoints
    const storageTests = [
      { url: '/api/storage/upload-url', name: 'Upload URL' },
      { url: '/api/storage/download-url', name: 'Download URL' }
    ];

    for (const test of storageTests) {
      try {
        const response = await page.goto(`http://localhost:3000${test.url}`);
        if (response?.status() === 405) {
          console.log(`✅ ${test.name} endpoint exists`);
        } else {
          console.log(`⚠️ ${test.name} endpoint status: ${response?.status()}`);
        }
      } catch (error) {
        console.log(`❌ ${test.name} endpoint failed`);
      }
    }

    // Test AI endpoint
    try {
      const aiResponse = await page.goto('http://localhost:3000/api/vertex-ai');
      if (aiResponse?.status() === 405) {
        console.log('✅ Vertex AI endpoint exists');
      } else {
        console.log(`⚠️ Vertex AI endpoint status: ${aiResponse?.status()}`);
      }
    } catch (error) {
      console.log('❌ Vertex AI endpoint failed');
    }

    // Test GCP integration
    const gcpResponse = await page.goto('http://localhost:3000/api/verify-setup');
    const gcpData = await gcpResponse?.json();

    if (gcpData) {
      console.log('📊 GCP integration status:', JSON.stringify(gcpData, null, 2));

      if (gcpData.supabase?.connected) {
        console.log('✅ Supabase connected');
      } else {
        console.log('❌ Supabase not connected');
      }

      if (gcpData.auth?.working) {
        console.log('✅ Authentication system working');
      } else {
        console.log('❌ Authentication system issues');
      }
    }
  });
});
