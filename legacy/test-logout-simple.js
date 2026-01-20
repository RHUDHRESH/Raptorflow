// Simple Logout Test - Start from dashboard
const { chromium } = require('playwright');

async function testLogoutSimple() {
  console.log('🧪 Step 2: Logout Test - Starting from Dashboard\n');
  
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
    // Go directly to dashboard (assuming we're already logged in)
    console.log('📍 Going directly to dashboard...');
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    const currentUrl = page.url();
    console.log(`Current URL: ${currentUrl}`);
    
    if (currentUrl.includes('/login')) {
      console.log('❌ Not logged in - redirected to login page');
      return { success: false, error: 'Not logged in' };
    }
    
    console.log('✅ Successfully accessed dashboard');
    
    // Take screenshot of dashboard
    await page.screenshot({ path: 'dashboard-current.png', fullPage: true });
    console.log('📸 Screenshot saved: dashboard-current.png');
    
    // Look for logout functionality
    console.log('🔍 Looking for logout options...');
    
    // Try to find any logout-related elements
    const logoutKeywords = ['sign out', 'logout', 'log out', 'signout', 'exit'];
    let logoutFound = false;
    
    // Check all buttons
    const allButtons = await page.locator('button').all();
    console.log(`Found ${allButtons.length} buttons`);
    
    for (let i = 0; i < allButtons.length; i++) {
      const button = allButtons[i];
      const text = await button.textContent();
      
      if (text) {
        const lowerText = text.toLowerCase();
        for (const keyword of logoutKeywords) {
          if (lowerText.includes(keyword)) {
            console.log(`✅ Found logout button: "${text}"`);
            logoutFound = true;
            
            // Click the logout button
            console.log('🚪 Clicking logout button...');
            await button.click();
            await page.waitForTimeout(2000);
            
            const urlAfterClick = page.url();
            console.log(`URL after logout click: ${urlAfterClick}`);
            
            if (urlAfterClick.includes('/login')) {
              console.log('✅ Successfully logged out!');
              
              await page.screenshot({ path: 'logout-success-simple.png', fullPage: true });
              console.log('📸 Screenshot saved: logout-success-simple.png');
              
              return { success: true, message: 'Logout successful', url: urlAfterClick };
            }
            
            break;
          }
        }
      }
    }
    
    // Check all links
    if (!logoutFound) {
      const allLinks = await page.locator('a').all();
      console.log(`Found ${allLinks.length} links`);
      
      for (let i = 0; i < allLinks.length; i++) {
        const link = allLinks[i];
        const text = await link.textContent();
        
        if (text) {
          const lowerText = text.toLowerCase();
          for (const keyword of logoutKeywords) {
            if (lowerText.includes(keyword)) {
              console.log(`✅ Found logout link: "${text}"`);
              logoutFound = true;
              
              // Click the logout link
              console.log('🔗 Clicking logout link...');
              await link.click();
              await page.waitForTimeout(2000);
              
              const urlAfterClick = page.url();
              console.log(`URL after logout click: ${urlAfterClick}`);
              
              if (urlAfterClick.includes('/login')) {
                console.log('✅ Successfully logged out via link!');
                
                await page.screenshot({ path: 'logout-success-link.png', fullPage: true });
                console.log('📸 Screenshot saved: logout-success-link.png');
                
                return { success: true, message: 'Logout successful via link', url: urlAfterClick };
              }
              
              break;
            }
          }
        }
      }
    }
    
    // Look for user menu/profile that might contain logout
    if (!logoutFound) {
      console.log('🔍 Looking for user menu or profile...');
      
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
        'button[aria-label*="account"]',
        'div:has-text("Profile")',
        'div:has-text("Account")',
        'div:has-text("User")'
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
            for (const keyword of logoutKeywords) {
              try {
                const logoutOption = await page.locator(`*:has-text("${keyword}")`).first();
                if (await logoutOption.isVisible()) {
                  const logoutText = await logoutOption.textContent();
                  console.log(`✅ Found logout option after clicking menu: "${logoutText}"`);
                  
                  await logoutOption.click();
                  await page.waitForTimeout(2000);
                  
                  const urlAfterClick = page.url();
                  console.log(`URL after logout option: ${urlAfterClick}`);
                  
                  if (urlAfterClick.includes('/login')) {
                    console.log('✅ Successfully logged out via menu!');
                    
                    await page.screenshot({ path: 'logout-success-menu.png', fullPage: true });
                    console.log('📸 Screenshot saved: logout-success-menu.png');
                    
                    return { success: true, message: 'Logout successful via menu', url: urlAfterClick };
                  }
                  break;
                }
              } catch (error) {
                // Continue
              }
            }
            
            if (page.url().includes('/login')) {
              break;
            }
            
            // Close menu and continue
            await page.keyboard.press('Escape');
            await page.waitForTimeout(500);
          }
        } catch (error) {
          // Continue
        }
      }
    }
    
    if (!logoutFound) {
      console.log('❌ No logout functionality found');
      
      // Take screenshot for debugging
      await page.screenshot({ path: 'dashboard-no-logout-simple.png', fullPage: true });
      console.log('📸 Debug screenshot saved: dashboard-no-logout-simple.png');
      
      // Get page content for analysis
      const pageContent = await page.content();
      console.log('\n📄 Page content analysis (first 1000 chars):');
      console.log(pageContent.substring(0, 1000));
      
      return { success: false, error: 'No logout functionality found' };
    }
    
  } catch (error) {
    console.error('❌ Simple logout test failed:', error.message);
    await page.screenshot({ path: 'logout-simple-error.png', fullPage: true });
    console.log('📸 Error screenshot saved: logout-simple-error.png');
    
    return { success: false, error: error.message };
  } finally {
    await browser.close();
  }
}

// Run the test
testLogoutSimple().then(result => {
  console.log('\n🎯 Simple Logout Test Complete');
  console.log('=====================================');
  console.log(`Result: ${result.success ? '✅ SUCCESS' : '❌ FAILED'}`);
  console.log(`Message: ${result.message}`);
  if (result.url) console.log(`Final URL: ${result.url}`);
  console.log('=====================================');
}).catch(console.error);
