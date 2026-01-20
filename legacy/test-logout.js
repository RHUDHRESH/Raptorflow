// Test Logout Functionality from Dashboard
const { chromium } = require('playwright');

async function testLogout() {
  console.log('🧪 Step 2: Logout Test from Dashboard\n');
  
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
    // First, login to get to dashboard
    console.log('🔐 Logging in to get to dashboard...');
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // Fill login form
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="password"]').first();
    
    await emailInput.fill('rhudhreshr@gmail.com');
    await passwordInput.fill('TestPassword123');
    
    // Click login button
    const loginButton = await page.locator('button:has-text("ACCESS TERMINAL")').first();
    await loginButton.click();
    
    // Wait for dashboard to load
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await page.waitForTimeout(2000);
    
    console.log('✅ Successfully logged in to dashboard');
    console.log(`Current URL: ${page.url()}`);
    
    // Take screenshot of dashboard
    await page.screenshot({ path: 'dashboard-before-logout.png', fullPage: true });
    console.log('📸 Screenshot saved: dashboard-before-logout.png');
    
    // Look for logout functionality
    console.log('🔍 Looking for logout options...');
    
    // Look for user profile/logout buttons
    const logoutSelectors = [
      'button:has-text("Sign Out")',
      'button:has-text("Logout")',
      'button:has-text("Sign out")',
      'button:has-text("Log out")',
      'a:has-text("Sign Out")',
      'a:has-text("Logout")',
      'a:has-text("Sign out")',
      'a:has-text("Log out")',
      '[data-testid="logout"]',
      '[data-testid="signout"]',
      '.user-menu button',
      '.profile-menu button',
      '.avatar button',
      'button[aria-label*="logout"]',
      'button[aria-label*="signout"]'
    ];
    
    let logoutFound = false;
    let logoutElement = null;
    
    for (const selector of logoutSelectors) {
      try {
        const element = await page.locator(selector).first();
        if (await element.isVisible()) {
          const text = await element.textContent();
          console.log(`✅ Found logout element: "${text}" with selector: ${selector}`);
          logoutFound = true;
          logoutElement = element;
          break;
        }
      } catch (error) {
        // Continue to next selector
      }
    }
    
    if (!logoutFound) {
      // Look for any clickable elements that might be user menu
      console.log('🔍 Looking for user menu or profile elements...');
      
      const menuSelectors = [
        'button:has-text("Profile")',
        'button:has-text("Account")',
        'button:has-text("User")',
        '.user-avatar',
        '.profile-avatar',
        '.user-menu',
        '.profile-menu',
        'button[aria-label*="user"]',
        'button[aria-label*="profile"]',
        'button[aria-label*="account"]'
      ];
      
      for (const selector of menuSelectors) {
        try {
          const element = await page.locator(selector).first();
          if (await element.isVisible()) {
            const text = await element.textContent();
            console.log(`🔘 Found potential menu element: "${text}" with selector: ${selector}`);
            
            // Click it to see if it reveals logout options
            await element.click();
            await page.waitForTimeout(1000);
            
            // Look for logout options again
            for (const logoutSelector of logoutSelectors) {
              try {
                const logoutOption = await page.locator(logoutSelector).first();
                if (await logoutOption.isVisible()) {
                  const logoutText = await logoutOption.textContent();
                  console.log(`✅ Found logout option after clicking menu: "${logoutText}"`);
                  logoutFound = true;
                  logoutElement = logoutOption;
                  break;
                }
              } catch (error) {
                // Continue
              }
            }
            
            if (logoutFound) break;
            
            // If no logout found, close menu and continue
            await page.keyboard.press('Escape');
            await page.waitForTimeout(500);
          }
        } catch (error) {
          // Continue
        }
      }
    }
    
    if (!logoutFound) {
      // Try to find any button that might be logout by checking common patterns
      console.log('🔍 Searching for any logout-related buttons...');
      
      const allButtons = await page.locator('button').all();
      console.log(`Found ${allButtons.length} buttons on dashboard`);
      
      for (let i = 0; i < allButtons.length; i++) {
        const button = allButtons[i];
        const text = await button.textContent();
        const className = await button.getAttribute('class');
        
        if (text && (
          text.toLowerCase().includes('sign') ||
          text.toLowerCase().includes('log') ||
          text.toLowerCase().includes('out') ||
          text.toLowerCase().includes('exit')
        )) {
          console.log(`🔘 Found potential logout button: "${text}" | Class: ${className}`);
          logoutFound = true;
          logoutElement = button;
          break;
        }
      }
    }
    
    if (logoutFound && logoutElement) {
      console.log('🚪 Clicking logout button...');
      await logoutElement.click();
      
      // Wait for logout to complete
      try {
        await page.waitForURL('**/login', { timeout: 10000 });
        await page.waitForTimeout(2000);
        
        const finalUrl = page.url();
        console.log(`✅ Successfully logged out! Redirected to: ${finalUrl}`);
        
        // Take screenshot after logout
        await page.screenshot({ path: 'logout-success.png', fullPage: true });
        console.log('📸 Screenshot saved: logout-success.png');
        
        return { success: true, message: 'Logout successful', url: finalUrl };
        
      } catch (error) {
        console.log('⚠️  Logout button clicked but no redirect detected');
        
        // Check if we're still on dashboard or if there's a confirmation
        const currentUrl = page.url();
        console.log(`Current URL after logout click: ${currentUrl}`);
        
        // Look for confirmation dialog
        const confirmButton = await page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("OK")').first();
        if (await confirmButton.isVisible()) {
          console.log('🔘 Found confirmation button, clicking...');
          await confirmButton.click();
          await page.waitForTimeout(2000);
          
          const finalUrl = page.url();
          console.log(`URL after confirmation: ${finalUrl}`);
          
          if (finalUrl.includes('/login')) {
            console.log('✅ Logout successful after confirmation');
            return { success: true, message: 'Logout successful with confirmation', url: finalUrl };
          }
        }
        
        return { success: false, error: 'Logout button clicked but no redirect' };
      }
    } else {
      console.log('❌ No logout button found on dashboard');
      
      // Take screenshot for debugging
      await page.screenshot({ path: 'dashboard-no-logout.png', fullPage: true });
      console.log('📸 Debug screenshot saved: dashboard-no-logout.png');
      
      return { success: false, error: 'No logout button found' };
    }
    
  } catch (error) {
    console.error('❌ Logout test failed:', error.message);
    await page.screenshot({ path: 'logout-error.png', fullPage: true });
    console.log('📸 Error screenshot saved: logout-error.png');
    
    return { success: false, error: error.message };
  } finally {
    await browser.close();
  }
}

// Run the test
testLogout().then(result => {
  console.log('\n🎯 Logout Test Complete');
  console.log('=====================================');
  console.log(`Result: ${result.success ? '✅ SUCCESS' : '❌ FAILED'}`);
  console.log(`Message: ${result.message}`);
  if (result.url) console.log(`Final URL: ${result.url}`);
  console.log('=====================================');
}).catch(console.error);
