// Manual Login Test - Fill form and find submit button
const { chromium } = require('playwright');

async function testLoginManual() {
  console.log('🧪 Manual Login Test - Fill form and find submit button\n');
  
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
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    
    // Wait for page to fully load
    await page.waitForTimeout(3000);
    
    console.log('📄 Filling in login credentials...');
    
    // Find email input
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    if (await emailInput.isVisible()) {
      await emailInput.fill('rhudhreshr@gmail.com');
      console.log('✅ Email filled');
    } else {
      console.log('❌ Email input not found');
      return { success: false, error: 'Email input not found' };
    }
    
    // Find password input
    const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="password"]').first();
    if (await passwordInput.isVisible()) {
      await passwordInput.fill('TestPassword123');
      console.log('✅ Password filled');
    } else {
      console.log('❌ Password input not found');
      return { success: false, error: 'Password input not found' };
    }
    
    // Take screenshot before clicking
    await page.screenshot({ path: 'login-form-filled.png', fullPage: true });
    console.log('📸 Screenshot saved: login-form-filled.png');
    
    // Try to submit by pressing Enter on password field
    console.log('🔑 Trying to submit with Enter key...');
    await passwordInput.press('Enter');
    
    // Wait for navigation
    try {
      await page.waitForNavigation({ timeout: 5000 });
      const newUrl = page.url();
      console.log(`URL after Enter: ${newUrl}`);
      
      if (newUrl !== 'http://localhost:3000/login') {
        console.log('✅ Login successful with Enter key!');
        
        // Take screenshot after login
        await page.screenshot({ path: 'login-success.png', fullPage: true });
        console.log('📸 Screenshot saved: login-success.png');
        
        return { success: true, message: 'Login successful with Enter key', url: newUrl };
      }
    } catch (error) {
      console.log('⚠️  Enter key did not cause navigation');
    }
    
    // Try clicking different buttons
    console.log('🔘 Trying different submit buttons...');
    
    const buttonSelectors = [
      'button:has-text("ACCESS TERMINAL")',
      'button:has-text("SIGN")',
      'button:has-text("LOGIN")',
      'button:has-text("SUBMIT")',
      'button.blueprint-button',
      'form button',
      'form input[type="submit"]'
    ];
    
    for (const selector of buttonSelectors) {
      try {
        const button = await page.locator(selector).first();
        if (await button.isVisible()) {
          const buttonText = await button.textContent();
          console.log(`🔘 Trying button: "${buttonText}" with selector: ${selector}`);
          
          await button.click();
          await page.waitForTimeout(2000);
          
          const urlAfterClick = page.url();
          console.log(`URL after clicking "${buttonText}": ${urlAfterClick}`);
          
          if (urlAfterClick !== 'http://localhost:3000/login') {
            console.log(`✅ Login successful with button: "${buttonText}"!`);
            
            await page.screenshot({ path: 'login-success-button.png', fullPage: true });
            console.log('📸 Screenshot saved: login-success-button.png');
            
            return { success: true, message: `Login successful with button: ${buttonText}`, url: urlAfterClick };
          }
          
          // Go back to login page if needed
          if (urlAfterClick !== 'http://localhost:3000/login') {
            await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
            await page.waitForTimeout(2000);
            
            // Re-fill form
            await emailInput.fill('rhudhreshr@gmail.com');
            await passwordInput.fill('TestPassword123');
          }
        }
      } catch (error) {
        // Continue to next selector
      }
    }
    
    // Try form submit
    console.log('📋 Trying form submit...');
    const form = await page.locator('form').first();
    if (await form.isVisible()) {
      await form.submit();
      await page.waitForTimeout(2000);
      
      const urlAfterSubmit = page.url();
      console.log(`URL after form submit: ${urlAfterSubmit}`);
      
      if (urlAfterSubmit !== 'http://localhost:3000/login') {
        console.log('✅ Login successful with form submit!');
        
        await page.screenshot({ path: 'login-success-form.png', fullPage: true });
        console.log('📸 Screenshot saved: login-success-form.png');
        
        return { success: true, message: 'Login successful with form submit', url: urlAfterSubmit };
      }
    }
    
    console.log('❌ All login attempts failed');
    
    // Take final screenshot for debugging
    await page.screenshot({ path: 'login-failed-debug.png', fullPage: true });
    console.log('📸 Debug screenshot saved: login-failed-debug.png');
    
    return { success: false, error: 'All login attempts failed' };
    
  } catch (error) {
    console.error('❌ Manual login test failed:', error.message);
    await page.screenshot({ path: 'manual-login-error.png', fullPage: true });
    console.log('📸 Error screenshot saved: manual-login-error.png');
    
    return { success: false, error: error.message };
  } finally {
    await browser.close();
  }
}

// Run the test
testLoginManual().then(result => {
  console.log('\n🎯 Manual Login Test Complete');
  console.log('=====================================');
  console.log(`Result: ${result.success ? '✅ SUCCESS' : '❌ FAILED'}`);
  console.log(`Message: ${result.message}`);
  if (result.url) console.log(`Final URL: ${result.url}`);
  console.log('=====================================');
}).catch(console.error);
