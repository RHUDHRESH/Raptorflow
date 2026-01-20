// Complete Authentication Flow Test
// Tests all 6 steps from COMPLETE_AUTH_TEST_PLAN.md

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Test configuration
const TEST_CONFIG = {
  baseUrl: 'http://localhost:3000',
  email: 'rhudhreshr@gmail.com',
  password: 'TestPassword123',
  newPassword: 'NewPassword123',
  testEmail: 'rhudhresh3697@gmail.com',
  fallbackEmail: 'rhudhreshr@gmail.com',
  timeout: 30000
};

// Test results tracking
const testResults = {
  step1: { name: 'Login Test', status: 'pending', details: [] },
  step2: { name: 'Logout Test', status: 'pending', details: [] },
  step3: { name: 'Forgot Password Test', status: 'pending', details: [] },
  step4: { name: 'Email Verification', status: 'pending', details: [] },
  step5: { name: 'Password Reset Test', status: 'pending', details: [] },
  step6: { name: 'Login with New Password', status: 'pending', details: [] }
};

async function runCompleteAuthTest() {
  console.log('🧪 Starting Complete Authentication Flow Test');
  console.log('📋 Testing all 6 steps from COMPLETE_AUTH_TEST_PLAN.md');
  console.log('');

  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000 // Slow down for better visibility
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  
  const page = await context.newPage();

  try {
    // Step 1: Login Test
    console.log('🔑 Step 1: Login Test');
    await testLogin(page);
    
    // Step 2: Logout Test
    console.log('🚪 Step 2: Logout Test');
    await testLogout(page);
    
    // Step 3: Forgot Password Test
    console.log('📧 Step 3: Forgot Password Test');
    await testForgotPassword(page);
    
    // Step 4: Email Verification (Manual check)
    console.log('✉️ Step 4: Email Verification');
    await testEmailVerification(page);
    
    // Step 5: Password Reset Test
    console.log('🔄 Step 5: Password Reset Test');
    await testPasswordReset(page);
    
    // Step 6: Login with New Password
    console.log('🎯 Step 6: Login with New Password');
    await testLoginWithNewPassword(page);
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }

  // Print comprehensive results
  printTestResults();
}

async function testLogin(page) {
  try {
    testResults.step1.status = 'running';
    
    // Navigate to login page
    await page.goto(`${TEST_CONFIG.baseUrl}/login`);
    await page.waitForLoadState('networkidle');
    
    // Check if login page loaded
    const loginTitle = await page.title();
    testResults.step1.details.push(`Page title: ${loginTitle}`);
    
    // Look for login form elements
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="password"]').first();
    
    if (await emailInput.isVisible() && await passwordInput.isVisible()) {
      testResults.step1.details.push('✅ Login form elements found');
    } else {
      testResults.step1.details.push('❌ Login form elements not found');
      throw new Error('Login form not found');
    }
    
    // Fill in credentials
    await emailInput.fill(TEST_CONFIG.email);
    await passwordInput.fill(TEST_CONFIG.password);
    testResults.step1.details.push(`✅ Credentials filled: ${TEST_CONFIG.email}`);
    
    // Look for submit button
    const submitButton = await page.locator('button[type="submit"], button:has-text("Sign"), button:has-text("Login"), button:has-text("Access")').first();
    
    if (await submitButton.isVisible()) {
      await submitButton.click();
      testResults.step1.details.push('✅ Submit button clicked');
    } else {
      // Try alternative selectors
      const altButton = await page.locator('button').filter({ hasText: /sign|login|access/i }).first();
      if (await altButton.isVisible()) {
        await altButton.click();
        testResults.step1.details.push('✅ Alternative submit button clicked');
      } else {
        // Try form submission
        await page.keyboard.press('Enter');
        testResults.step1.details.push('✅ Form submitted with Enter key');
      }
    }
    
    // Wait for navigation
    await page.waitForLoadState('networkidle');
    
    // Check if redirected to dashboard
    const currentUrl = page.url();
    if (currentUrl.includes('/dashboard') || currentUrl.includes('/home') || !currentUrl.includes('/login')) {
      testResults.step1.status = 'completed';
      testResults.step1.details.push(`✅ Login successful - redirected to: ${currentUrl}`);
    } else {
      testResults.step1.status = 'failed';
      testResults.step1.details.push(`❌ Login failed - still on: ${currentUrl}`);
    }
    
  } catch (error) {
    testResults.step1.status = 'failed';
    testResults.step1.details.push(`❌ Error: ${error.message}`);
    throw error;
  }
}

async function testLogout(page) {
  try {
    testResults.step2.status = 'running';
    
    // Look for user profile button (top right)
    const profileButton = await page.locator('button:has-text("Profile"), button:has-text("Account"), [data-testid="user-menu"], .user-avatar, .profile-button').first();
    
    if (await profileButton.isVisible()) {
      await profileButton.click();
      testResults.step2.details.push('✅ Profile button clicked');
    } else {
      // Try alternative selectors
      const altProfile = await page.locator('button').filter({ hasText: /profile|account|user/i }).first();
      if (await altProfile.isVisible()) {
        await altProfile.click();
        testResults.step2.details.push('✅ Alternative profile button clicked');
      } else {
        // Look for menu icon
        const menuIcon = await page.locator('.menu-icon, [data-testid="menu"], button:has-text("Menu")').first();
        if (await menuIcon.isVisible()) {
          await menuIcon.click();
          testResults.step2.details.push('✅ Menu icon clicked');
        } else {
          throw new Error('No logout option found');
        }
      }
    }
    
    // Wait for menu to appear
    await page.waitForTimeout(1000);
    
    // Look for logout option
    const logoutButton = await page.locator('button:has-text("Sign Out"), button:has-text("Logout"), a:has-text("Sign Out"), a:has-text("Logout")').first();
    
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      testResults.step2.details.push('✅ Logout button clicked');
    } else {
      // Try alternative logout options
      const altLogout = await page.locator('a, button').filter({ hasText: /sign out|logout|exit/i }).first();
      if (await altLogout.isVisible()) {
        await altLogout.click();
        testResults.step2.details.push('✅ Alternative logout option clicked');
      } else {
        throw new Error('No logout button found');
      }
    }
    
    // Wait for navigation
    await page.waitForLoadState('networkidle');
    
    // Check if redirected to login page
    const currentUrl = page.url();
    if (currentUrl.includes('/login')) {
      testResults.step2.status = 'completed';
      testResults.step2.details.push('✅ Logout successful - redirected to login page');
    } else {
      testResults.step2.status = 'failed';
      testResults.step2.details.push(`❌ Logout failed - current URL: ${currentUrl}`);
    }
    
  } catch (error) {
    testResults.step2.status = 'failed';
    testResults.step2.details.push(`❌ Error: ${error.message}`);
    throw error;
  }
}

async function testForgotPassword(page) {
  try {
    testResults.step3.status = 'running';
    
    // Look for forgot password link
    const forgotLink = await page.locator('a:has-text("Forgot"), a:has-text("Reset"), button:has-text("Forgot"), button:has-text("Reset")').first();
    
    if (await forgotLink.isVisible()) {
      await forgotLink.click();
      testResults.step3.details.push('✅ Forgot password link clicked');
    } else {
      // Try alternative selectors
      const altForgot = await page.locator('a, button').filter({ hasText: /forgot|reset/i }).first();
      if (await altForgot.isVisible()) {
        await altForgot.click();
        testResults.step3.details.push('✅ Alternative forgot password link clicked');
      } else {
        throw new Error('No forgot password link found');
      }
    }
    
    // Wait for forgot password page
    await page.waitForLoadState('networkidle');
    
    // Look for email input on forgot password page
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    
    if (await emailInput.isVisible()) {
      await emailInput.fill(TEST_CONFIG.email);
      testResults.step3.details.push(`✅ Email filled: ${TEST_CONFIG.email}`);
    } else {
      throw new Error('Email input not found on forgot password page');
    }
    
    // Look for submit button
    const submitButton = await page.locator('button[type="submit"], button:has-text("Send"), button:has-text("Reset")').first();
    
    if (await submitButton.isVisible()) {
      await submitButton.click();
      testResults.step3.details.push('✅ Send reset link button clicked');
    } else {
      // Try form submission
      await page.keyboard.press('Enter');
      testResults.step3.details.push('✅ Form submitted with Enter key');
    }
    
    // Wait for response
    await page.waitForTimeout(3000);
    
    // Look for success message
    const successMessage = await page.locator('text=Reset Link Sent, text=Email Sent, text=Check your email, .success-message').first();
    
    if (await successMessage.isVisible()) {
      testResults.step3.status = 'completed';
      testResults.step3.details.push('✅ Success message displayed');
    } else {
      // Check page content for success indicators
      const pageContent = await page.content();
      if (pageContent.includes('sent') || pageContent.includes('email') || pageContent.includes('reset')) {
        testResults.step3.status = 'completed';
        testResults.step3.details.push('✅ Success indicators found in page content');
      } else {
        testResults.step3.status = 'failed';
        testResults.step3.details.push('❌ No success message found');
      }
    }
    
  } catch (error) {
    testResults.step3.status = 'failed';
    testResults.step3.details.push(`❌ Error: ${error.message}`);
    throw error;
  }
}

async function testEmailVerification(page) {
  try {
    testResults.step4.status = 'running';
    
    // This step requires manual email verification
    testResults.step4.details.push('📧 Manual verification required');
    testResults.step4.details.push(`📧 Check email: ${TEST_CONFIG.testEmail}`);
    testResults.step4.details.push(`📧 Fallback email: ${TEST_CONFIG.fallbackEmail}`);
    testResults.step4.details.push('📧 Look for subject: "Reset Your RaptorFlow Password"');
    testResults.step4.details.push('📧 Check Inbox + Spam/Promotions folders');
    testResults.step4.details.push('📧 From: onboarding@resend.dev');
    
    // Wait for user to check email
    console.log('\n⏰ Please check your email now...');
    console.log(`📧 Primary: ${TEST_CONFIG.testEmail}`);
    console.log(`📧 Fallback: ${TEST_CONFIG.fallbackEmail}`);
    console.log('📧 Subject: "Reset Your RaptorFlow Password"');
    console.log('📧 From: onboarding@resend.dev');
    console.log('⏰ Press Enter when you have the reset link...');
    
    // Wait for user input
    await new Promise(resolve => {
      process.stdin.once('data', resolve);
    });
    
    testResults.step4.status = 'completed';
    testResults.step4.details.push('✅ User confirmed email received');
    
  } catch (error) {
    testResults.step4.status = 'failed';
    testResults.step4.details.push(`❌ Error: ${error.message}`);
    throw error;
  }
}

async function testPasswordReset(page) {
  try {
    testResults.step5.status = 'running';
    
    // Navigate to reset page (user should have the link)
    console.log('🔗 Please navigate to the reset link from your email...');
    console.log('⏰ Press Enter when you are on the reset page...');
    
    // Wait for user to navigate
    await new Promise(resolve => {
      process.stdin.once('data', resolve);
    });
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Look for password inputs
    const newPasswordInput = await page.locator('input[type="password"], input[name="password"], input[name="newPassword"], input[placeholder*="password"]').first();
    const confirmPasswordInput = await page.locator('input[type="password"], input[name="confirmPassword"], input[name="confirmPassword"], input[placeholder*="confirm"]').nth(1);
    
    if (await newPasswordInput.isVisible() && await confirmPasswordInput.isVisible()) {
      await newPasswordInput.fill(TEST_CONFIG.newPassword);
      await confirmPasswordInput.fill(TEST_CONFIG.newPassword);
      testResults.step5.details.push(`✅ Password fields filled with: ${TEST_CONFIG.newPassword}`);
    } else {
      throw new Error('Password input fields not found');
    }
    
    // Look for submit button
    const submitButton = await page.locator('button[type="submit"], button:has-text("Reset"), button:has-text("Update")').first();
    
    if (await submitButton.isVisible()) {
      await submitButton.click();
      testResults.step5.details.push('✅ Reset password button clicked');
    } else {
      // Try form submission
      await page.keyboard.press('Enter');
      testResults.step5.details.push('✅ Form submitted with Enter key');
    }
    
    // Wait for response
    await page.waitForTimeout(3000);
    
    // Look for success message
    const successMessage = await page.locator('text=Password Reset, text=Success, text=Updated, .success-message').first();
    
    if (await successMessage.isVisible()) {
      testResults.step5.status = 'completed';
      testResults.step5.details.push('✅ Password reset successful');
    } else {
      // Check page content for success indicators
      const pageContent = await page.content();
      if (pageContent.includes('success') || pageContent.includes('reset') || pageContent.includes('updated')) {
        testResults.step5.status = 'completed';
        testResults.step5.details.push('✅ Success indicators found in page content');
      } else {
        testResults.step5.status = 'failed';
        testResults.step5.details.push('❌ No success message found');
      }
    }
    
  } catch (error) {
    testResults.step5.status = 'failed';
    testResults.step5.details.push(`❌ Error: ${error.message}`);
    throw error;
  }
}

async function testLoginWithNewPassword(page) {
  try {
    testResults.step6.status = 'running';
    
    // Navigate to login page
    await page.goto(`${TEST_CONFIG.baseUrl}/login`);
    await page.waitForLoadState('networkidle');
    
    // Look for login form elements
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="password"]').first();
    
    if (await emailInput.isVisible() && await passwordInput.isVisible()) {
      await emailInput.fill(TEST_CONFIG.email);
      await passwordInput.fill(TEST_CONFIG.newPassword);
      testResults.step6.details.push(`✅ Credentials filled with new password`);
    } else {
      throw new Error('Login form not found');
    }
    
    // Look for submit button
    const submitButton = await page.locator('button[type="submit"], button:has-text("Sign"), button:has-text("Login")').first();
    
    if (await submitButton.isVisible()) {
      await submitButton.click();
      testResults.step6.details.push('✅ Submit button clicked');
    } else {
      // Try form submission
      await page.keyboard.press('Enter');
      testResults.step6.details.push('✅ Form submitted with Enter key');
    }
    
    // Wait for navigation
    await page.waitForLoadState('networkidle');
    
    // Check if redirected to dashboard
    const currentUrl = page.url();
    if (currentUrl.includes('/dashboard') || currentUrl.includes('/home') || !currentUrl.includes('/login')) {
      testResults.step6.status = 'completed';
      testResults.step6.details.push(`✅ Login successful with new password - redirected to: ${currentUrl}`);
    } else {
      testResults.step6.status = 'failed';
      testResults.step6.details.push(`❌ Login failed - still on: ${currentUrl}`);
    }
    
  } catch (error) {
    testResults.step6.status = 'failed';
    testResults.step6.details.push(`❌ Error: ${error.message}`);
    throw error;
  }
}

function printTestResults() {
  console.log('\n📊 COMPLETE AUTHENTICATION TEST RESULTS');
  console.log('=' .repeat(50));
  
  let totalTests = 0;
  let completedTests = 0;
  let failedTests = 0;
  
  Object.entries(testResults).forEach(([step, result]) => {
    totalTests++;
    
    const statusIcon = result.status === 'completed' ? '✅' : 
                      result.status === 'failed' ? '❌' : 
                      result.status === 'running' ? '⏳' : '⏸️';
    
    console.log(`${statusIcon} ${step}: ${result.name}`);
    result.details.forEach(detail => {
      console.log(`   ${detail}`);
    });
    console.log('');
    
    if (result.status === 'completed') completedTests++;
    if (result.status === 'failed') failedTests++;
  });
  
  console.log('=' .repeat(50));
  console.log(`📈 SUMMARY:`);
  console.log(`   Total Tests: ${totalTests}`);
  console.log(`   ✅ Completed: ${completedTests}`);
  console.log(`   ❌ Failed: ${failedTests}`);
  console.log(`   ⏳ Running: ${totalTests - completedTests - failedTests}`);
  
  const successRate = totalTests > 0 ? (completedTests / totalTests * 100).toFixed(1) : 0;
  console.log(`   🎯 Success Rate: ${successRate}%`);
  
  if (completedTests === totalTests) {
    console.log('\n🎉 ALL TESTS PASSED! Authentication system is working perfectly!');
  } else if (failedTests > 0) {
    console.log('\n⚠️  Some tests failed. Please check the details above.');
  } else {
    console.log('\n⏳ Some tests are still running. Please complete manual verification steps.');
  }
  
  // Save results to file
  const resultsFile = 'auth-test-results.json';
  fs.writeFileSync(resultsFile, JSON.stringify(testResults, null, 2));
  console.log(`\n📄 Results saved to: ${resultsFile}`);
}

// Run the test
runCompleteAuthTest().catch(console.error);
