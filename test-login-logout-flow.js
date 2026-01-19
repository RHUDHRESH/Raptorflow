// Complete Login-Logout Flow Test
const { chromium } = require('playwright');

async function testLoginLogoutFlow() {
  console.log('🧪 Complete Login-Logout Flow Test\n');
  
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
    // Step 1: Login
    console.log('🔐 Step 1: Logging in...');
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // Fill login form
    const emailInput = await page.locator('input[type="email"], input[name="email"], input[placeholder*="email"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"], input[placeholder*="password"]').first();
    
    if (await emailInput.isVisible() && await passwordInput.isVisible()) {
      await emailInput.fill('rhudhreshr@gmail.com');
      await passwordInput.fill('TestPassword123');
      
      // Click login button
      const loginButton = await page.locator('button:has-text("ACCESS TERMINAL")').first();
      await loginButton.click();
      
      // Wait for dashboard
      await page.waitForURL('**/dashboard', { timeout: 10000 });
      await page.waitForTimeout(2000);
      
      console.log('✅ Successfully logged in to dashboard');
      console.log(`Dashboard URL: ${page.url()}`);
      
      // Take screenshot of dashboard
      await page.screenshot({ path: 'dashboard-after-login.png', fullPage: true });
      console.log('📸 Screenshot saved: dashboard-after-login.png');
      
      // Step 2: Look for logout
      console.log('\n🚪 Step 2: Looking for logout options...');
      
      // Look for logout buttons
      const logoutKeywords = ['sign out', 'logout', 'log out', 'signout', 'exit'];
      let logoutFound = false;
      let logoutElement = null;
      
      // Check all buttons
      const allButtons = await page.locator('button').all();
      console.log(`Found ${allButtons.length} buttons on dashboard`);
      
      for (let i = 0; i < allButtons.length; i++) {
        const button = allButtons[i];
        const text = await button.textContent();
        
        if (text) {
          const lowerText = text.toLowerCase();
          for (const keyword of logoutKeywords) {
            if (lowerText.includes(keyword)) {
              console.log(`✅ Found logout button: "${text}"`);
              logoutFound = true;
              logoutElement = button;
              break;
            }
          }
        }
      }
      
      // Check all links if no button found
      if (!logoutFound) {
        const allLinks = await page.locator('a').all();
        console.log(`Found ${allLinks.length} links on dashboard`);
        
        for (let i = 0; i < allLinks.length; i++) {
          const link = allLinks[i];
          const text = await link.textContent();
          
          if (text) {
            const lowerText = text.toLowerCase();
            for (const keyword of logoutKeywords) {
              if (lowerText.includes(keyword)) {
                console.log(`✅ Found logout link: "${text}"`);
                logoutFound = true;
                logoutElement = link;
                break;
              }
            }
          }
        }
      }
      
      // Look for user menu that might contain logout
      if (!logoutFound) {
        console.log('🔍 Looking for user menu...');
        
        const menuSelectors = [
          'button:has-text("Profile")',
          'button:has-text("Account")',
          'button:has-text("User")',
          '.user-avatar',
          '.profile-avatar',
          'button[aria-label*="user"]',
          'button[aria-label*="profile"]'
        ];
        
        for (const selector of menuSelectors) {
          try {
            const element = await page.locator(selector).first();
            if (await element.isVisible()) {
              const text = await element.textContent();
              console.log(`🔘 Found potential menu element: "${text}"`);
              
              // Click it to see if it reveals logout options
              await element.click();
              await page.waitForTimeout(1000);
              
              // Look for logout options again
              for (const keyword of logoutKeywords) {
                try {
                  const logoutOption = await page.locator(`*:has-text("${keyword}")`).first();
                  if (await logoutOption.isVisible()) {
                    const logoutText = await logoutOption.textContent();
                    console.log(`✅ Found logout option in menu: "${logoutText}"`);
                    logoutFound = true;
                    logoutElement = logoutOption;
                    break;
                  }
                } catch (error) {
                  // Continue
                }
              }
              
              if (logoutFound) break;
              
              // Close menu if no logout found
              await page.keyboard.press('Escape');
              await page.waitForTimeout(500);
            }
          } catch (error) {
            // Continue
          }
        }
      }
      
      // Step 3: Attempt logout
      if (logoutFound && logoutElement) {
        console.log('\n🚪 Step 3: Attempting logout...');
        await logoutElement.click();
        await page.waitForTimeout(2000);
        
        const urlAfterLogout = page.url();
        console.log(`URL after logout: ${urlAfterLogout}`);
        
        if (urlAfterLogout.includes('/login')) {
          console.log('✅ Successfully logged out!');
          
          await page.screenshot({ path: 'logout-success-complete.png', fullPage: true });
          console.log('📸 Screenshot saved: logout-success-complete.png');
          
          return { 
            success: true, 
            message: 'Complete login-logout flow successful',
            loginUrl: 'http://localhost:3000/dashboard',
            logoutUrl: urlAfterLogout
          };
        } else {
          // Look for confirmation dialog
          const confirmButton = await page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("OK")').first();
          if (await confirmButton.isVisible()) {
            console.log('🔘 Found confirmation button, clicking...');
            await confirmButton.click();
            await page.waitForTimeout(2000);
            
            const finalUrl = page.url();
            console.log(`URL after confirmation: ${finalUrl}`);
            
            if (finalUrl.includes('/login')) {
              console.log('✅ Logout successful after confirmation!');
              
              await page.screenshot({ path: 'logout-success-confirm.png', fullPage: true });
              console.log('📸 Screenshot saved: logout-success-confirm.png');
              
              return { 
                success: true, 
                message: 'Login-logout flow successful with confirmation',
                loginUrl: 'http://localhost:3000/dashboard',
                logoutUrl: finalUrl
              };
            }
          }
          
          return { success: false, error: 'Logout button clicked but no redirect' };
        }
      } else {
        console.log('❌ No logout functionality found');
        
        // Take screenshot for debugging
        await page.screenshot({ path: 'dashboard-no-logout-debug.png', fullPage: true });
        console.log('📸 Debug screenshot saved: dashboard-no-logout-debug.png');
        
        return { 
          success: false, 
          error: 'No logout functionality found',
          loginUrl: page.url()
        };
      }
      
    } else {
      console.log('❌ Login form not accessible');
      return { success: false, error: 'Login form not accessible' };
    }
    
  } catch (error) {
    console.error('❌ Login-logout flow test failed:', error.message);
    await page.screenshot({ path: 'flow-error.png', fullPage: true });
    console.log('📸 Error screenshot saved: flow-error.png');
    
    return { success: false, error: error.message };
  } finally {
    await browser.close();
  }
}

// Run the test
testLoginLogoutFlow().then(result => {
  console.log('\n🎯 Complete Login-Logout Flow Test');
  console.log('=====================================');
  console.log(`Result: ${result.success ? '✅ SUCCESS' : '❌ FAILED'}`);
  console.log(`Message: ${result.message}`);
  if (result.loginUrl) console.log(`Login URL: ${result.loginUrl}`);
  if (result.logoutUrl) console.log(`Logout URL: ${result.logoutUrl}`);
  console.log('=====================================');
}).catch(console.error);
