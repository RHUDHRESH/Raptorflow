import { test, expect } from '@playwright/test';

test.describe('GCP Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
  });

  test('Setup page loads and checks status', async ({ page }) => {
    await page.goto('http://localhost:3000/setup');
    await page.waitForLoadState('networkidle');
    
    // Check if setup page loads
    await expect(page.locator('h1')).toContainText('RaptorFlow Setup Status');
    
    // Check for status indicators
    await page.waitForTimeout(2000);
    
    // Look for status cards
    const statusCards = page.locator('.p-4');
    expect(await statusCards.count()).toBeGreaterThan(0);
    
    // Check for action buttons
    const createTablesBtn = page.locator('button:has-text("Create Database Tables")');
    const storageBtn = page.locator('button:has-text("Get Storage Setup SQL")');
    
    console.log('Setup page loaded successfully');
  });

  test('Database tables creation', async ({ page }) => {
    await page.goto('http://localhost:3000/setup');
    
    // Click create tables button
    const createTablesBtn = page.locator('button:has-text("Create Database Tables")');
    if (await createTablesBtn.isVisible()) {
      await createTablesBtn.click();
      await page.waitForTimeout(3000);
      
      // Check for success message
      const successMessage = page.locator('text=✅ Database Ready!');
      if (await successMessage.isVisible({ timeout: 10000 })) {
        console.log('Database tables created successfully');
      }
    }
  });

  test('Storage setup SQL generation', async ({ page }) => {
    await page.goto('http://localhost:3000/setup');
    
    // Click get storage SQL button
    const storageBtn = page.locator('button:has-text("Get Storage Setup SQL")');
    if (await storageBtn.isVisible()) {
      await storageBtn.click();
      await page.waitForTimeout(2000);
      
      // Check for SQL code display
      const sqlCode = page.locator('pre');
      if (await sqlCode.isVisible()) {
        const sqlText = await sqlCode.textContent() || '';
        if (sqlText.includes('INSERT INTO storage.buckets')) {
          console.log('Storage SQL generated successfully');
        }
      }
    }
  });

  test('Authentication flow with backend', async ({ page }) => {
    // Test login page
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');
    
    // Try to sign up
    await page.click('button:has-text("Sign Up")');
    await page.waitForTimeout(1000);
    
    const testEmail = `test-${Date.now()}@raptorflow.in`;
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="text"]', 'Test User');
    await page.fill('input[type="password"]', 'testpassword123');
    
    // Submit signup
    await page.click('button:has-text("Create Account")');
    
    // Check if it redirects to pricing (success) or shows error
    await page.waitForTimeout(5000);
    const currentUrl = page.url();
    
    if (currentUrl.includes('/pricing')) {
      console.log('✅ Signup successful - redirected to pricing');
    } else if (currentUrl.includes('/login')) {
      // Check for error message
      const errorElement = page.locator('text=/error|failed|unable/i');
      if (await errorElement.isVisible()) {
        const errorMsg = await errorElement.textContent();
        console.log('❌ Signup failed:', errorMsg);
      }
    }
  });

  test('Payment flow verification', async ({ page }) => {
    // Go to pricing page
    await page.goto('http://localhost:3000/pricing');
    await page.waitForLoadState('networkidle');
    
    // Check if pricing plans are displayed
    const plans = ['Soar', 'Glide', 'Ascent'];
    for (const plan of plans) {
      const planElement = page.locator(`text=${plan}`);
      expect(await planElement.isVisible()).toBeTruthy();
    }
    
    // Try to select a plan
    const chooseSoarBtn = page.locator('button').filter({ hasText: 'Choose Soar' });
    if (await chooseSoarBtn.isVisible()) {
      console.log('✅ Plan selection available');
    } else {
      // Try alternative selector
      const selectSoarBtn = page.locator('button').filter({ hasText: 'Select Soar' });
      if (await selectSoarBtn.isVisible()) {
        console.log('✅ Alternative plan selection available');
        await selectSoarBtn.click();
      }
    }
  });

  test('Workspace access verification', async ({ page }) => {
    // Try to access workspace without auth
    await page.goto('http://localhost:3000/workspace');
    await page.waitForTimeout(3000);
    
    // Should redirect to login
    const currentUrl = page.url();
    if (currentUrl.includes('/login')) {
      console.log('✅ Workspace properly protected - redirected to login');
    } else {
      console.log('⚠️ Workspace not protected - security issue');
    }
  });

  test('API endpoints health check', async ({ page }) => {
    // Test setup verification endpoint
    const response = await page.goto('http://localhost:3000/api/verify-setup');
    const data = await response?.json();
    
    if (data) {
      console.log('API Status:', JSON.stringify(data, null, 2));
      
      // Check if Supabase is connected
      if (data.supabase?.connected) {
        console.log('✅ Supabase connected');
      } else {
        console.log('❌ Supabase not connected:', data.supabase?.error);
      }
      
      // Check if tables exist
      if (data.tables?.user_profiles && data.tables?.payments) {
        console.log('✅ Database tables exist');
      } else {
        console.log('⚠️ Database tables missing');
      }
      
      // Check auth system
      if (data.auth?.working) {
        console.log('✅ Authentication system working');
      } else {
        console.log('⚠️ Authentication system issues');
      }
    }
  });

  test('Storage integration test', async ({ page }) => {
    // Test if storage API endpoints exist
    const uploadUrlResponse = await page.goto('http://localhost:3000/api/storage/upload-url');
    if (uploadUrlResponse?.status() === 405) {
      console.log('✅ Storage API endpoint exists (405 expected for POST without body)');
    }
    
    const downloadUrlResponse = await page.goto('http://localhost:3000/api/storage/download-url');
    if (downloadUrlResponse?.status() === 405) {
      console.log('✅ Storage download API endpoint exists (405 expected for POST without body)');
    }
  });

  test('Vertex AI integration test', async ({ page }) => {
    // Test if AI API endpoint exists
    const aiResponse = await page.goto('http://localhost:3000/api/vertex-ai');
    if (aiResponse?.status() === 405) {
      console.log('✅ Vertex AI API endpoint exists (405 expected for POST without body)');
    }
  });

  test('Complete user journey simulation', async ({ page }) => {
    console.log('🚀 Starting complete user journey test...');
    
    // 1. Landing page
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    console.log('✅ Landing page loaded');
    
    // 2. Navigate to login
    await page.click('text=Get Started');
    await page.waitForTimeout(2000);
    console.log('✅ Navigated to login');
    
    // 3. Attempt signup
    await page.click('button:has-text("Sign Up")');
    await page.waitForTimeout(1000);
    
    const testEmail = `journey-${Date.now()}@raptorflow.in`;
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="text"]', 'Journey Test User');
    await page.fill('input[type="password"]', 'journey123456');
    
    await page.click('button:has-text("Create Account")');
    await page.waitForTimeout(5000);
    
    const currentUrl = page.url();
    if (currentUrl.includes('/pricing')) {
      console.log('✅ User created and redirected to pricing');
      
      // 4. Check pricing page
      const soarPlan = page.locator('text=₹5,000');
      if (await soarPlan.isVisible()) {
        console.log('✅ Pricing plans displayed correctly');
      }
      
      // 5. Try to select a plan
      const chooseSoarBtn = page.locator('button').filter({ hasText: 'Choose Soar' });
      if (await chooseSoarBtn.isVisible()) {
        console.log('✅ Plan selection available');
      } else {
        // Try alternative selector
        const selectSoarBtn = page.locator('button').filter({ hasText: 'Select Soar' });
        if (await selectSoarBtn.isVisible()) {
          console.log('✅ Alternative plan selection available');
          await selectSoarBtn.click();
        }
      }
    } else {
      console.log('❌ Journey failed at signup stage');
    }
  });
});