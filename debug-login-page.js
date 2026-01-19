// Debug Login Page - Find all interactive elements
const { chromium } = require('playwright');

async function debugLoginPage() {
  console.log('🔍 Debugging Login Page...\n');
  
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
    
    // Wait a bit for dynamic content
    await page.waitForTimeout(3000);
    
    console.log('📄 Page Analysis:');
    console.log(`Title: ${await page.title()}`);
    console.log(`URL: ${page.url()}`);
    
    // Find ALL buttons
    const allButtons = await page.locator('button').all();
    console.log(`\n🔘 All buttons found: ${allButtons.length}`);
    
    for (let i = 0; i < allButtons.length; i++) {
      const button = allButtons[i];
      const text = await button.textContent();
      const type = await button.getAttribute('type');
      const className = await button.getAttribute('class');
      const id = await button.getAttribute('id');
      
      console.log(`  ${i + 1}. Text: "${text}" | Type: ${type} | Class: ${className} | ID: ${id}`);
    }
    
    // Find ALL inputs
    const allInputs = await page.locator('input').all();
    console.log(`\n📝 All inputs found: ${allInputs.length}`);
    
    for (let i = 0; i < allInputs.length; i++) {
      const input = allInputs[i];
      const type = await input.getAttribute('type');
      const name = await input.getAttribute('name');
      const placeholder = await input.getAttribute('placeholder');
      const className = await input.getAttribute('class');
      const id = await input.getAttribute('id');
      
      console.log(`  ${i + 1}. Type: ${type} | Name: ${name} | Placeholder: ${placeholder} | Class: ${className} | ID: ${id}`);
    }
    
    // Find ALL forms
    const allForms = await page.locator('form').all();
    console.log(`\n📋 All forms found: ${allForms.length}`);
    
    for (let i = 0; i < allForms.length; i++) {
      const form = allForms[i];
      const action = await form.getAttribute('action');
      const method = await form.getAttribute('method');
      const className = await form.getAttribute('class');
      const id = await form.getAttribute('id');
      
      console.log(`  ${i + 1}. Action: ${action} | Method: ${method} | Class: ${className} | ID: ${id}`);
    }
    
    // Look for any elements with "submit", "login", "sign" in text
    const submitElements = await page.locator('*:has-text("Submit"), *:has-text("Login"), *:has-text("Sign"), *:has-text("Log in")').all();
    console.log(`\n🎯 Potential submit elements: ${submitElements.length}`);
    
    for (let i = 0; i < submitElements.length; i++) {
      const element = submitElements[i];
      const tagName = await element.evaluate(el => el.tagName.toLowerCase());
      const text = await element.textContent();
      const className = await element.getAttribute('class');
      
      console.log(`  ${i + 1}. Tag: ${tagName} | Text: "${text}" | Class: ${className}`);
    }
    
    // Take screenshot
    await page.screenshot({ path: 'login-page-debug.png', fullPage: true });
    console.log('\n📸 Screenshot saved: login-page-debug.png');
    
    // Try to find the actual submit button by looking for common patterns
    console.log('\n🔍 Attempting to find submit button...');
    
    // Try different selectors
    const selectors = [
      'button[type="submit"]',
      'button:has-text("Sign")',
      'button:has-text("Login")',
      'button:has-text("Log in")',
      'button:has-text("Submit")',
      'button.blueprint-button',
      '.blueprint-button',
      '[data-testid="submit"]',
      '[data-testid="login"]'
    ];
    
    for (const selector of selectors) {
      try {
        const element = await page.locator(selector).first();
        if (await element.isVisible()) {
          const text = await element.textContent();
          console.log(`✅ Found potential submit button with selector "${selector}": "${text}"`);
          
          // Try clicking it
          console.log('🖱️  Attempting to click...');
          await element.click();
          await page.waitForTimeout(2000);
          
          const newUrl = page.url();
          console.log(`URL after click: ${newUrl}`);
          
          if (newUrl !== 'http://localhost:3000/login') {
            console.log('✅ Button click caused navigation!');
            break;
          }
        }
      } catch (error) {
        // Continue to next selector
      }
    }
    
  } catch (error) {
    console.error('❌ Debug failed:', error.message);
  } finally {
    await browser.close();
  }
}

debugLoginPage().catch(console.error);
