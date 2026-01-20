// Test Forgot Password Flow
const { chromium } = require('playwright');
const fetch = require('node-fetch');

async function testForgotPassword() {
  console.log('🧪 Step 3: Forgot Password Test\n');
  
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
    // Go to login page
    console.log('📍 Navigating to login page...');
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    console.log(`Current URL: ${page.url()}`);
    
    // Look for forgot password link
    console.log('🔍 Looking for forgot password link...');
    
    const forgotLinkSelectors = [
      'a:has-text("Forgot")',
      'a:has-text("Reset")',
      'a:has-text("Password")',
      'a[href*="forgot"]',
      'a[href*="reset"]',
      'button:has-text("Forgot")',
      'button:has-text("Reset")',
      'button:has-text("Password")'
    ];
    
    let forgotLinkFound = false;
    let forgotLinkElement = null;
    
    for (const selector of forgotLinkSelectors) {
      try {
        const element = await page.locator(selector).first();
        if (await element.isVisible()) {
          const text = await element.textContent();
          console.log(`✅ Found forgot password link: "${text}" with selector: ${selector}`);
          forgotLinkFound = true;
          forgotLinkElement = element;
          break;
        }
      } catch (error) {
        // Continue to next selector
      }
    }
    
    if (!forgotLinkFound) {
      console.log('❌ No forgot password link found');
      
      // Take screenshot for debugging
      await page.screenshot({ path: 'login-no-forgot-link.png', fullPage: true });
      console.log('📸 Debug screenshot saved: login-no-forgot-link.png');
      
      return { success: false, error: 'No forgot password link found' };
    }
    
    // Click forgot password link
    console.log('🔗 Clicking forgot password link...');
    await forgotLinkElement.click();
    
    // Wait for forgot password page to load
    await page.waitForTimeout(3000);
    
    const forgotUrl = page.url();
    console.log(`Forgot password page URL: ${forgotUrl}`);
    
    if (!forgotUrl.includes('forgot') && !forgotUrl.includes('reset')) {
      console.log('⚠️  May not have navigated to forgot password page');
    }
    
    // Take screenshot of forgot password page
    await page.screenshot({ path: 'forgot-password-page.png', fullPage: true });
    console.log('📸 Screenshot saved: forgot-password-page.png');
    
    // Look for forgot password form
    console.log('🔍 Looking for forgot password form...');
    
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    const submitButton = await page.locator('button[type="submit"], button:has-text("Send"), button:has-text("Reset"), button:has-text("Submit")').first();
    
    console.log(`Email input visible: ${await emailInput.isVisible()}`);
    console.log(`Submit button visible: ${await submitButton.isVisible()}`);
    
    if (!await emailInput.isVisible() || !await submitButton.isVisible()) {
      console.log('❌ Forgot password form not accessible');
      
      // Get page content for debugging
      const pageContent = await page.content();
      console.log('\n📄 Page content (first 500 chars):');
      console.log(pageContent.substring(0, 500));
      
      return { success: false, error: 'Forgot password form not accessible' };
    }
    
    // Fill in email
    console.log('📧 Filling in email: rhudhreshr@gmail.com');
    await emailInput.fill('rhudhreshr@gmail.com');
    
    // Take screenshot before submitting
    await page.screenshot({ path: 'forgot-form-filled.png', fullPage: true });
    console.log('📸 Screenshot saved: forgot-form-filled.png');
    
    // Submit the form
    console.log('📤 Submitting forgot password form...');
    await submitButton.click();
    
    // Wait for response
    await page.waitForTimeout(3000);
    
    // Check for success message
    const successElement = await page.locator('[class*="success"], [class*="Success"]').first();
    const errorElement = await page.locator('[class*="error"], [class*="Error"]').first();
    
    let message = '';
    let success = false;
    
    if (await successElement.isVisible()) {
      message = await successElement.textContent();
      console.log(`✅ Success message: ${message}`);
      success = true;
    } else if (await errorElement.isVisible()) {
      message = await errorElement.textContent();
      console.log(`❌ Error message: ${message}`);
      success = false;
    } else {
      console.log('⚠️  No success or error message visible');
      message = 'No response message visible';
      success = false;
    }
    
    // Take screenshot after submission
    await page.screenshot({ path: 'forgot-form-submitted.png', fullPage: true });
    console.log('📸 Screenshot saved: forgot-form-submitted.png');
    
    // Test API directly as well
    console.log('\n🔍 Testing forgot password API directly...');
    try {
      const apiResponse = await fetch('http://localhost:3000/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'rhudhreshr@gmail.com'
        })
      });
      
      if (apiResponse.ok) {
        const apiData = await apiResponse.json();
        console.log('✅ API response successful');
        console.log(`API Data: ${JSON.stringify(apiData, null, 2)}`);
      } else {
        console.log(`⚠️  API response failed: ${apiResponse.status}`);
      }
    } catch (error) {
      console.log(`❌ API test error: ${error.message}`);
    }
    
    return { 
      success, 
      message,
      url: forgotUrl,
      apiTest: 'completed'
    };
    
  } catch (error) {
    console.error('❌ Forgot password test failed:', error.message);
    await page.screenshot({ path: 'forgot-password-error.png', fullPage: true });
    console.log('📸 Error screenshot saved: forgot-password-error.png');
    
    return { success: false, error: error.message };
  } finally {
    await browser.close();
  }
}

// Run the test
testForgotPassword().then(result => {
  console.log('\n🎯 Forgot Password Test Complete');
  console.log('=====================================');
  console.log(`Result: ${result.success ? '✅ SUCCESS' : '❌ FAILED'}`);
  console.log(`Message: ${result.message}`);
  if (result.url) console.log(`Forgot Password URL: ${result.url}`);
  console.log('=====================================');
}).catch(console.error);
