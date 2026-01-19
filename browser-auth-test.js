// Browser Authentication Test using Playwright
// Run with: node browser-auth-test.js

const { chromium } = require('playwright');

async function runAuthTest() {
  console.log('🧪 Starting Browser Authentication Test...\n');
  
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Task 21: Navigate to login page
    console.log('Task 21: Navigating to login page...');
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');
    
    // Check if login page loaded
    const title = await page.title();
    console.log('Page title:', title);
    
    // Look for login form elements
    const emailInput = await page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"]').first();
    const submitButton = await page.locator('button[type="submit"]').first();
    
    if (await emailInput.isVisible() && await passwordInput.isVisible() && await submitButton.isVisible()) {
      console.log('✅ Login page loaded successfully');
    } else {
      console.log('❌ Login page elements not found');
      return;
    }

    // Task 22: Test login with credentials
    console.log('\nTask 22: Testing login with credentials...');
    await emailInput.fill('rhudhreshr@gmail.com');
    await passwordInput.fill('TestPassword123');
    
    // Click submit button
    await Promise.all([
      page.waitForNavigation(),
      submitButton.click()
    ]);
    
    // Task 23: Verify dashboard redirect
    console.log('\nTask 23: Verifying dashboard redirect...');
    const currentUrl = page.url();
    console.log('Current URL after login:', currentUrl);
    
    if (currentUrl.includes('/dashboard') || currentUrl.includes('/dash')) {
      console.log('✅ Successfully redirected to dashboard');
    } else {
      console.log('⚠️  Not redirected to dashboard, checking for other indicators...');
      
      // Look for user info or dashboard elements
      const userInfo = await page.locator('[data-testid="user-info"], .user-info, .dashboard').first();
      if (await userInfo.isVisible()) {
        console.log('✅ Dashboard elements found');
      } else {
        console.log('❌ Dashboard not found');
      }
    }

    // Take screenshot for verification
    await page.screenshot({ path: 'login-success.png', fullPage: true });
    console.log('📸 Screenshot saved: login-success.png');

    // Task 24: Test logout functionality
    console.log('\nTask 24: Testing logout functionality...');
    
    // Look for logout button or user profile
    const logoutButton = await page.locator('button:has-text("Sign Out"), button:has-text("Logout"), [data-testid="logout"]').first();
    const profileButton = await page.locator('button:has-text("Profile"), .user-profile, [data-testid="profile"]').first();
    
    if (await logoutButton.isVisible()) {
      await Promise.all([
        page.waitForNavigation(),
        logoutButton.click()
      ]);
      console.log('✅ Logout successful');
    } else if (await profileButton.isVisible()) {
      await profileButton.click();
      await page.waitForTimeout(1000);
      
      // Look for logout in dropdown
      const logoutInDropdown = await page.locator('button:has-text("Sign Out"), a:has-text("Logout")').first();
      if (await logoutInDropdown.isVisible()) {
        await Promise.all([
          page.waitForNavigation(),
          logoutInDropdown.click()
        ]);
        console.log('✅ Logout successful via profile menu');
      } else {
        console.log('❌ Logout option not found in profile menu');
      }
    } else {
      console.log('❌ Logout button not found');
    }

    // Check if redirected back to login
    const logoutUrl = page.url();
    if (logoutUrl.includes('/login')) {
      console.log('✅ Redirected to login after logout');
    } else {
      console.log('⚠️  Not redirected to login after logout');
    }

    // Task 25: Navigate to forgot password page
    console.log('\nTask 25: Navigating to forgot password page...');
    
    // Look for forgot password link
    const forgotLink = await page.locator('a:has-text("Forgot"), a:has-text("Reset"), [href*="forgot"]').first();
    if (await forgotLink.isVisible()) {
      await forgotLink.click();
      await page.waitForLoadState('networkidle');
      
      const forgotUrl = page.url();
      if (forgotUrl.includes('/forgot')) {
        console.log('✅ Navigated to forgot password page');
      } else {
        console.log('❌ Not on forgot password page');
      }
    } else {
      // Try direct navigation
      await page.goto('http://localhost:3000/forgot-password');
      await page.waitForLoadState('networkidle');
      
      const directForgotUrl = page.url();
      if (directForgotUrl.includes('/forgot')) {
        console.log('✅ Direct navigation to forgot password page successful');
      } else {
        console.log('❌ Could not navigate to forgot password page');
      }
    }

    // Task 26: Test forgot password form
    console.log('\nTask 26: Testing forgot password form...');
    
    const forgotEmailInput = await page.locator('input[type="email"], input[name="email"]').first();
    const forgotSubmitButton = await page.locator('button[type="submit"], button:has-text("Send")').first();
    
    if (await forgotEmailInput.isVisible() && await forgotSubmitButton.isVisible()) {
      await forgotEmailInput.fill('rhudhreshr@gmail.com');
      
      // Click submit button
      await forgotSubmitButton.click();
      
      // Wait for success message
      await page.waitForTimeout(2000);
      
      // Look for success message
      const successMessage = await page.locator('text=Reset Link Sent, text=success, .success-message').first();
      if (await successMessage.isVisible()) {
        console.log('✅ Forgot password form submitted successfully');
      } else {
        console.log('⚠️  Success message not immediately visible, checking page state...');
        
        // Take screenshot for debugging
        await page.screenshot({ path: 'forgot-password-result.png', fullPage: true });
        console.log('📸 Screenshot saved: forgot-password-result.png');
      }
    } else {
      console.log('❌ Forgot password form not found');
    }

    console.log('\n✅ Browser test completed!');
    console.log('📧 Check rhudhresh3697@gmail.com for reset email');
    console.log('🔗 Use the reset link to continue testing');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: 'error-screenshot.png', fullPage: true });
    console.log('📸 Error screenshot saved: error-screenshot.png');
  } finally {
    await browser.close();
  }
}

runAuthTest();
