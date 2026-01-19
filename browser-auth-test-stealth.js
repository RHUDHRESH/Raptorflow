// Browser Authentication Test with Stealth Mode
const { chromium } = require('playwright');

async function runStealthAuthTest() {
  console.log('🧪 Starting Stealth Browser Authentication Test...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: [
      '--no-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage',
      '--disable-web-security',
      '--disable-features=VizDisplayCompositor'
    ]
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 720 },
    locale: 'en-US'
  });
  
  const page = await context.newPage();

  // Remove webdriver property
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined,
    });
  });

  try {
    // Task 21: Navigate to login page
    console.log('Task 21: Navigating to login page...');
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    
    // Wait a bit for any dynamic content
    await page.waitForTimeout(2000);
    
    // Get page content
    const title = await page.title();
    const url = page.url();
    
    console.log('Page Title:', title);
    console.log('Current URL:', url);
    
    // Check if we got the login page or an error
    const bodyText = await page.locator('body').textContent();
    if (bodyText.includes('Forbidden') || bodyText.includes('403')) {
      console.log('❌ Access forbidden by middleware');
      console.log('Trying direct access to home page first...');
      
      await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
      await page.waitForTimeout(2000);
      
      const homeUrl = page.url();
      console.log('Home page URL:', homeUrl);
      
      // Look for navigation to login
      const loginLink = await page.locator('a:has-text("Login"), a:has-text("Sign In"), [href*="login"]').first();
      if (await loginLink.isVisible()) {
        await loginLink.click();
        await page.waitForLoadState('networkidle');
        console.log('✅ Navigated to login via home page');
      } else {
        console.log('❌ Login link not found on home page');
      }
    }
    
    // Take screenshot of current state
    await page.screenshot({ path: 'login-page-current.png', fullPage: true });
    console.log('📸 Screenshot saved: login-page-current.png');
    
    // Check for login form elements again
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="password"]').first();
    const submitButton = await page.locator('button[type="submit"], button:has-text("Sign"), button:has-text("Login")').first();
    
    console.log('\nChecking for login elements...');
    console.log('Email input visible:', await emailInput.isVisible());
    console.log('Password input visible:', await passwordInput.isVisible());
    console.log('Submit button visible:', await submitButton.isVisible());
    
    if (await emailInput.isVisible() && await passwordInput.isVisible()) {
      console.log('✅ Login form found');
      
      // Task 22: Test login with credentials
      console.log('\nTask 22: Testing login with credentials...');
      await emailInput.fill('rhudhreshr@gmail.com');
      await passwordInput.fill('TestPassword123');
      
      // Look for any form validation or error messages before submitting
      await page.waitForTimeout(1000);
      
      // Submit the form
      if (await submitButton.isVisible()) {
        await Promise.all([
          page.waitForNavigation({ timeout: 10000 }),
          submitButton.click()
        ]);
        
        // Task 23: Verify dashboard redirect
        console.log('\nTask 23: Verifying dashboard redirect...');
        const currentUrlAfterLogin = page.url();
        console.log('URL after login:', currentUrlAfterLogin);
        
        if (currentUrlAfterLogin.includes('/dashboard') || currentUrlAfterLogin.includes('/dash')) {
          console.log('✅ Successfully redirected to dashboard');
        } else {
          console.log('⚠️  Not redirected to dashboard, checking content...');
          
          // Look for dashboard indicators
          const dashboardElements = await page.locator('[class*="dashboard"], [class*="Dashboard"], h1:has-text("Dashboard")').all();
          if (dashboardElements.length > 0) {
            console.log('✅ Dashboard elements found');
          } else {
            console.log('❌ Dashboard not found');
          }
        }
        
        // Take screenshot after login
        await page.screenshot({ path: 'after-login.png', fullPage: true });
        console.log('📸 Screenshot saved: after-login.png');
        
      } else {
        console.log('❌ Submit button not found');
      }
    } else {
      console.log('❌ Login form not found');
      
      // Debug: Get all form elements
      const allInputs = await page.locator('input').all();
      console.log('All inputs found:', allInputs.length);
      
      const allButtons = await page.locator('button').all();
      console.log('All buttons found:', allButtons.length);
      
      // Get page content for debugging
      const pageContent = await page.content();
      console.log('Page content length:', pageContent.length);
      
      // Save page content to file
      require('fs').writeFileSync('page-content.html', pageContent);
      console.log('📄 Page content saved to page-content.html');
    }

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: 'error-stealth.png', fullPage: true });
    console.log('📸 Error screenshot saved: error-stealth.png');
  } finally {
    await browser.close();
  }
}

runStealthAuthTest();
