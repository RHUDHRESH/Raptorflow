// Comprehensive Authentication Test
// Tests all authentication scenarios including API endpoints

const { chromium } = require('playwright');
const fetch = require('node-fetch');

async function runComprehensiveAuthTest() {
  console.log('🧪 Comprehensive Authentication Test\n');
  
  const results = {
    loginPage: { success: false, message: '', url: '' },
    forgotPasswordPage: { success: false, message: '', url: '' },
    resetPasswordPage: { success: false, message: '', url: '' },
    apiEndpoints: { success: false, message: '', tests: {} },
    emailDelivery: { success: false, message: '', tests: {} },
    overall: { success: false, message: '' }
  };
  
  // Test 1: API Endpoints
  console.log('🔍 Testing API Endpoints...');
  results.apiEndpoints = await testAPIEndpoints();
  
  // Test 2: Login Page
  console.log('\n🔐 Testing Login Page...');
  results.loginPage = await testLoginPage();
  
  // Test 3: Forgot Password Page
  console.log('\n📧 Testing Forgot Password Page...');
  results.forgotPasswordPage = await testForgotPasswordPage();
  
  // Test 4: Reset Password Page
  console.log('\n🔄 Testing Reset Password Page...');
  results.resetPasswordPage = await testResetPasswordPage();
  
  // Test 5: Email Delivery (simulated)
  console.log('\n📧 Testing Email Delivery...');
  results.emailDelivery = await testEmailDelivery();
  
  // Calculate overall result
  const allTests = [
    results.loginPage.success,
    results.forgotPasswordPage.success,
    results.resetPasswordPage.success,
    results.apiEndpoints.success,
    results.emailDelivery.success
  ];
  
  const successCount = allTests.filter(test => test).length;
  const totalCount = allTests.length;
  
  results.overall = {
    success: successCount === totalCount,
    message: `${successCount}/${totalCount} tests passed`
  };
  
  // Generate final report
  console.log('\n🎯 Comprehensive Authentication Test Results');
  console.log('=====================================');
  console.log(`Overall Result: ${results.overall.success ? '✅ SUCCESS' : '❌ FAILED'}`);
  console.log(`Message: ${results.overall.message}`);
  console.log('');
  console.log('Detailed Results:');
  console.log(`Login Page: ${results.loginPage.success ? '✅' : '❌'} - ${results.loginPage.message}`);
  console.log(`Forgot Password: ${results.forgotPasswordPage.success ? '✅' : '❌'} - ${results.forgotPasswordPage.message}`);
  console.log(`Reset Password: ${results.resetPasswordPage.success ? '✅' : '❌'} - ${results.resetPasswordPage.message}`);
  console.log(`API Endpoints: ${results.apiEndpoints.success ? '✅' : '❌'} - ${results.apiEndpoints.message}`);
  console.log(`Email Delivery: ${results.emailDelivery.success ? '✅' : '❌'} - ${results.emailDelivery.message}`);
  console.log('=====================================');
  
  return results;
}

async function testAPIEndpoints() {
  const tests = {};
  let success = true;
  let message = '';
  
  const endpoints = [
    { name: 'Forgot Password', url: '/api/auth/forgot-password', method: 'POST', data: { email: 'test@example.com' } },
    { name: 'Validate Token', url: '/api/auth/validate-reset-token-simple', method: 'POST', data: { token: 'test-token' } },
    { name: 'Reset Password', url: '/api/auth/reset-password-simple', method: 'POST', data: { token: 'test-token', newPassword: 'NewPassword123' } },
    { name: 'Health Check', url: '/api/health', method: 'GET', data: null }
  ];
  
  for (const endpoint of endpoints) {
    try {
      const options = {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json',
        }
      };
      
      if (endpoint.data) {
        options.body = JSON.stringify(endpoint.data);
      }
      
      const response = await fetch(`http://localhost:3000${endpoint.url}`, options);
      
      if (response.ok) {
        tests[endpoint.name] = { status: 'success', code: response.status };
        console.log(`✅ ${endpoint.name}: ${response.status} OK`);
      } else {
        tests[endpoint.name] = { status: 'failed', code: response.status };
        console.log(`❌ ${endpoint.name}: ${response.status} - ${response.statusText}`);
        success = false;
      }
    } catch (error) {
      tests[endpoint.name] = { status: 'error', error: error.message };
      console.log(`❌ ${endpoint.name}: Error - ${error.message}`);
      success = false;
    }
  }
  
  if (success) {
    message = 'All API endpoints responding correctly';
  } else {
    message = 'Some API endpoints failed';
  }
  
  return { success, message, tests };
}

async function testLoginPage() {
  const browser = await chromium.launch({ 
    headless: false,
    args: [
      '--no-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage'
    ]
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 720 }
  });
  
  const page = await context.newPage();

  try {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
      });
    });
    
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    const url = page.url();
    
    // Check if we're on login page
    if (!url.includes('/login')) {
      return { success: false, message: 'Not on login page', url };
    }
    
    // Check for form elements
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="password"]').first();
    const submitButton = await page.locator('button:has-text("ACCESS TERMINAL")').first();
    
    const elementsFound = await emailInput.isVisible() && await passwordInput.isVisible() && await submitButton.isVisible();
    
    if (elementsFound) {
      return { success: true, message: 'Login form accessible', url };
    } else {
      return { success: false, message: 'Login form not fully accessible', url };
    }
    
  } catch (error) {
    return { success: false, error: error.message, url: '' };
  } finally {
    await browser.close();
  }
}

async function testForgotPasswordPage() {
  const browser = await chromium.launch({ 
    headless: false,
    args: [
      '--no-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage'
    ]
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 720 }
  });
  
  const page = await context.newPage();

  try {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
      });
    });
    
    // Try direct navigation to forgot password page
    await page.goto('http://localhost:3000/forgot-password', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    const url = page.url();
    
    if (url.includes('/forgot-password') || url.includes('/reset-password')) {
      // Check for form elements
      const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
      const submitButton = await page.locator('button[type="submit"], button:has-text("Send"), button:has-text("Reset")').first();
      
      const elementsFound = await emailInput.isVisible() && await submitButton.isVisible();
      
      if (elementsFound) {
        return { success: true, message: 'Forgot password form accessible', url };
      } else {
        return { success: false, message: 'Forgot password form not fully accessible', url };
      }
    } else {
      return { success: false, message: 'Forgot password page not accessible', url };
    }
    
  } catch (error) {
    return { success: false, error: error.message, url: '' };
  } finally {
    await browser.close();
  }
}

async function testResetPasswordPage() {
  const browser = await chromium.launch({ 
    headless: false,
    args: [
      '--no-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage'
    ]
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 720 }
  });
  
  const page = await context.newPage();

  try {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
      });
    });
    
    // Try direct navigation to reset password page
    await page.goto('http://localhost:3000/auth/reset-password?token=test-token', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    const url = page.url();
    
    if (url.includes('/reset-password')) {
      // Check for form elements
      const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="password"]').first();
      const confirmPasswordInput = await page.locator('input[name*="confirm"], input[placeholder*="confirm"]').first();
      const submitButton = await page.locator('button[type="submit"], button:has-text("Reset"), button:has-text("Submit")').first();
      
      const elementsFound = await passwordInput.isVisible() && await confirmPasswordInput.isVisible() && await submitButton.isVisible();
      
      if (elementsFound) {
        return { success: true, message: 'Reset password form accessible', url };
      } else {
        return { success: false, message: 'Reset password form not fully accessible', url };
      }
    } else {
      return { success: false, message: 'Reset password page not accessible', url };
    }
    
  } catch (error) {
    return { success: false, error: error.message, url: '' };
  } finally {
    await browser.close();
  }
}

async function testEmailDelivery() {
  const tests = {};
  let success = true;
  let message = '';
  
  // Simulate email delivery test
  try {
    // Test forgot password API to trigger email
    const response = await fetch('http://localhost:3000/api/auth/forgot-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'rhudhreshr@gmail.com'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      tests['forgotPassword'] = { status: 'success', data: data };
      console.log('✅ Forgot password API triggered email');
      
      // Check if token was created (simulated)
      if (data.token || data.message && data.message.includes('sent')) {
        tests['tokenCreation'] = { status: 'success', data: 'Token created' };
        console.log('✅ Token creation simulated success');
      } else {
        tests['tokenCreation'] = { status: 'failed', data: 'No token created' };
        console.log('⚠️  Token creation may have failed');
        success = false;
      }
    } else {
      tests['forgotPassword'] = { status: 'failed', error: response.statusText };
      console.log(`❌ Forgot password API failed: ${response.status}`);
      success = false;
    }
  } catch (error) {
    tests['forgotPassword'] = { status: 'error', error: error.message };
    console.log(`❌ Email delivery test error: ${error.message}`);
    success = false;
  }
  
  if (success) {
    message = 'Email delivery simulation successful';
  } else {
    message = 'Email delivery simulation failed';
  }
  
  return { success, message, tests };
}

// Run the comprehensive test
runComprehensiveAuthTest().catch(console.error);
