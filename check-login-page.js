// Check Login Page Content
const { chromium } = require('playwright');

async function checkLoginPage() {
  console.log('🔍 Checking login page content...\n');
  
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    await page.goto('http://localhost:3000/login');
    await page.waitForLoadState('networkidle');
    
    // Get page content
    const title = await page.title();
    const url = page.url();
    
    console.log('Page Title:', title);
    console.log('Current URL:', url);
    
    // Get all input elements
    const inputs = await page.locator('input').all();
    console.log('\nInput elements found:');
    for (let i = 0; i < inputs.length; i++) {
      const input = inputs[i];
      const type = await input.getAttribute('type');
      const name = await input.getAttribute('name');
      const placeholder = await input.getAttribute('placeholder');
      console.log(`  ${i + 1}. Type: ${type}, Name: ${name}, Placeholder: ${placeholder}`);
    }
    
    // Get all buttons
    const buttons = await page.locator('button').all();
    console.log('\nButtons found:');
    for (let i = 0; i < buttons.length; i++) {
      const button = buttons[i];
      const text = await button.textContent();
      const type = await button.getAttribute('type');
      console.log(`  ${i + 1}. Text: "${text}", Type: ${type}`);
    }
    
    // Check for any error messages
    const errorElements = await page.locator('[class*="error"], [class*="Error"]').all();
    if (errorElements.length > 0) {
      console.log('\nError elements found:');
      for (let i = 0; i < errorElements.length; i++) {
        const error = errorElements[i];
        const text = await error.textContent();
        console.log(`  ${i + 1}. "${text}"`);
      }
    }
    
    // Take screenshot
    await page.screenshot({ path: 'login-page-debug.png', fullPage: true });
    console.log('\n📸 Screenshot saved: login-page-debug.png');
    
    // Get page HTML for debugging
    const bodyHTML = await page.locator('body').innerHTML();
    console.log('\nPage body HTML (first 500 chars):');
    console.log(bodyHTML.substring(0, 500) + '...');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
}

checkLoginPage();
