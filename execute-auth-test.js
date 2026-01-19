// Execute Authentication Test - Step 1: Login Test
// Tests login with rhudhreshr@gmail.com / TestPassword123

const { chromium } = require('playwright');
const fetch = require('node-fetch');

async function executeLoginTest() {
  console.log('🧪 Step 1: Login Test - rhudhreshr@gmail.com / TestPassword123\n');
  
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

  // Remove webdriver property
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined,
    });
  });

  try {
    // Navigate to login page
    console.log('📍 Navigating to login page...');
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    
    // Check if login page loaded
    const title = await page.title();
    const url = page.url();
    
    console.log(`Page Title: ${title}`);
    console.log(`Current URL: ${url}`);
    
    if (!url.includes('/login')) {
      console.log('⚠️  Not on login page, checking for redirects...');
      
      // Look for login link on home page
      const loginLink = await page.locator('a:has-text("Login"), a:has-text("Sign In"), [href*="login"]').first();
      if (await loginLink.isVisible()) {
        await loginLink.click();
        await page.waitForLoadState('networkidle');
        console.log('✅ Navigated to login via home page');
      } else {
        console.log('❌ Login link not found, trying direct access');
        await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
      }
    }
    
    // Take screenshot of login page
    await page.screenshot({ path: 'login-page-test.png', fullPage: true });
    console.log('📸 Screenshot saved: login-page-test.png');
    
    // Check for login form elements
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="password"]').first();
    const submitButton = await page.locator('button[type="submit"], button:has-text("Sign"), button:has-text("Login")').first();
    
    console.log('\n🔍 Checking login form elements:');
    console.log(`Email input visible: ${await emailInput.isVisible()}`);
    console.log(`Password input visible: ${await passwordInput.isVisible()}`);
    console.log(`Submit button visible: ${await submitButton.isVisible()}`);
    
    if (!await emailInput.isVisible() || !await passwordInput.isVisible() || !await submitButton.isVisible()) {
      console.log('❌ Login form elements not found');
      
      // Get page content for debugging
      const pageContent = await page.content();
      console.log('\n📄 Page content (first 500 chars):');
      console.log(pageContent.substring(0, 500) + '...');
      
      return { success: false, error: 'Login form not accessible' };
    }
    
    // Fill in login credentials
    console.log('\n🔐 Filling in login credentials...');
    await emailInput.fill('rhudhreshr@gmail.com');
    await passwordInput.fill('TestPassword123');
    
    // Check for any form validation
    await page.waitForTimeout(1000);
    
    // Submit the form
    console.log('📤 Submitting login form...');
    await Promise.all([
      page.waitForNavigation({ timeout: 10000 }),
      submitButton.click()
    ]);
    
    // Check if login was successful
    const currentUrlAfterLogin = page.url();
    console.log(`URL after login: ${currentUrlAfterLogin}`);
    
    // Look for dashboard indicators
    const dashboardElements = await page.locator('[class*="dashboard"], [class*="Dashboard"], h1:has-text("Dashboard"), h2:has-text("Dashboard")').all();
    const userElements = await page.locator('[class*="user"], [class*="profile"], [class*="account"]').all();
    
    console.log(`Dashboard elements found: ${dashboardElements.length}`);
    console.log(`User elements found: ${userElements.length}`);
    
    // Take screenshot after login
    await page.screenshot({ path: 'after-login-test.png', fullPage: true });
    console.log('📸 Screenshot saved: after-login-test.png');
    
    // Check for success indicators
    let loginSuccess = false;
    let loginMessage = '';
    
    if (currentUrlAfterLogin.includes('/dashboard') || currentUrlAfterLogin.includes('/dash')) {
      loginSuccess = true;
      loginMessage = 'Successfully redirected to dashboard';
    } else if (dashboardElements.length > 0) {
      loginSuccess = true;
      loginMessage = 'Dashboard elements found';
    } else if (userElements.length > 0) {
      loginSuccess = true;
      loginMessage = 'User profile elements found';
    } else {
      // Check for error messages
      const errorElements = await page.locator('[class*="error"], [class*="Error"]').all();
      if (errorElements.length > 0) {
        const errorText = await errorElements[0].textContent();
        loginMessage = `Login error: ${errorText}`;
      } else {
        loginMessage = 'Login completed but destination unclear';
      }
    }
    
    console.log(`\n📊 Login Test Result:`);
    console.log(`Success: ${loginSuccess}`);
    console.log(`Message: ${loginMessage}`);
    
    // Test API health as well
    console.log('\n🔍 Testing API health...');
    try {
      const healthResponse = await fetch('http://localhost:3000/api/health');
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        console.log('✅ Health endpoint working');
        console.log(`Services status: ${JSON.stringify(healthData.services, null, 2)}`);
      } else {
        console.log('⚠️  Health endpoint not responding');
      }
    } catch (error) {
      console.log('⚠️  Health endpoint error:', error.message);
    }
    
    return { 
      success: loginSuccess, 
      message: loginMessage,
      url: currentUrlAfterLogin,
      dashboardElements: dashboardElements.length,
      userElements: userElements.length
    };
    
  } catch (error) {
    console.error('❌ Login test failed:', error.message);
    await page.screenshot({ path: 'login-test-error.png', fullPage: true });
    console.log('📸 Error screenshot saved: login-test-error.png');
    
    return { success: false, error: error.message };
  } finally {
    await browser.close();
  }
}

// Run the test
executeLoginTest().then(result => {
  console.log('\n🎯 Step 1 Login Test Complete');
  console.log('=====================================');
  console.log(`Result: ${result.success ? '✅ SUCCESS' : '❌ FAILED'}`);
  console.log(`Message: ${result.message}`);
  if (result.url) console.log(`Final URL: ${result.url}`);
  if (result.dashboardElements) console.log(`Dashboard elements: ${result.dashboardElements}`);
  if (result.userElements) console.log(`User elements: ${result.userElements}`);
  console.log('=====================================');
}).catch(console.error);
