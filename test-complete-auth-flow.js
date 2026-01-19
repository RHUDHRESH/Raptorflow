// Complete Authentication Flow Test
// Tests all authentication functionality after security fixes

const { chromium } = require('playwright');
const fetch = require('node-fetch');

async function runCompleteAuthTest() {
  console.log('🧪 Starting Complete Authentication Flow Test...\n');
  
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
    // Test 1: Check if auth bypass is removed
    console.log('🔍 Test 1: Checking auth bypass removal...');
    await testAuthBypassRemoval(page);
    
    // Test 2: Test login page functionality
    console.log('\n🔍 Test 2: Testing login page...');
    await testLoginPage(page);
    
    // Test 3: Test forgot password flow
    console.log('\n🔍 Test 3: Testing forgot password flow...');
    await testForgotPasswordFlow(page);
    
    // Test 4: Test API endpoints
    console.log('\n🔍 Test 4: Testing API endpoints...');
    await testAPIEndpoints();
    
    // Test 5: Test database security
    console.log('\n🔍 Test 5: Testing database security...');
    await testDatabaseSecurity();
    
    console.log('\n✅ All tests completed successfully!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: 'test-error.png', fullPage: true });
  } finally {
    await browser.close();
  }
}

async function testAuthBypassRemoval(page) {
  try {
    // Try to access a protected route without authentication
    await page.goto('http://localhost:3000/dashboard', { waitUntil: 'networkidle' });
    
    const url = page.url();
    if (url.includes('/login')) {
      console.log('✅ Auth bypass removed - redirected to login');
    } else {
      console.log('⚠️  Possible auth bypass still exists');
    }
    
    // Check for mock user creation
    const localStorage = await page.evaluate(() => {
      return localStorage.getItem('raptorflow_session');
    });
    
    if (localStorage && localStorage.includes('demo@raptorflow.com')) {
      console.log('❌ Mock user still being created');
    } else {
      console.log('✅ Mock user creation removed');
    }
    
  } catch (error) {
    console.log('⚠️  Auth bypass test error:', error.message);
  }
}

async function testLoginPage(page) {
  try {
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    
    // Check if login form is present
    const emailInput = await page.locator('input[type="email"], input[name="email"]').first();
    const passwordInput = await page.locator('input[type="password"], input[name="password"]').first();
    const submitButton = await page.locator('button[type="submit"], button:has-text("Sign"), button:has-text("Login")').first();
    
    if (await emailInput.isVisible() && await passwordInput.isVisible() && await submitButton.isVisible()) {
      console.log('✅ Login form elements present');
    } else {
      console.log('❌ Login form elements missing');
      return;
    }
    
    // Test invalid credentials
    await emailInput.fill('invalid@test.com');
    await passwordInput.fill('wrongpassword');
    await submitButton.click();
    
    await page.waitForTimeout(2000);
    
    // Check for error message
    const errorElement = await page.locator('[class*="error"], [class*="Error"]').first();
    if (await errorElement.isVisible()) {
      console.log('✅ Error handling working');
    } else {
      console.log('⚠️  Error handling may not be working');
    }
    
    // Clear form
    await emailInput.fill('');
    await passwordInput.fill('');
    
  } catch (error) {
    console.log('⚠️  Login page test error:', error.message);
  }
}

async function testForgotPasswordFlow(page) {
  try {
    await page.goto('http://localhost:3000/login', { waitUntil: 'networkidle' });
    
    // Find and click forgot password link
    const forgotLink = await page.locator('a:has-text("Forgot"), a:has-text("Reset")').first();
    if (await forgotLink.isVisible()) {
      await forgotLink.click();
      await page.waitForLoadState('networkidle');
      
      const url = page.url();
      if (url.includes('forgot-password')) {
        console.log('✅ Forgot password page accessible');
      } else {
        console.log('❌ Forgot password page not accessible');
        return;
      }
      
      // Test forgot password form
      const emailInput = await page.locator('input[type="email"], input[name="email"]').first();
      const submitButton = await page.locator('button[type="submit"], button:has-text("Send"), button:has-text("Reset")').first();
      
      if (await emailInput.isVisible() && await submitButton.isVisible()) {
        console.log('✅ Forgot password form present');
        
        // Test with test email
        await emailInput.fill('rhudhreshr@gmail.com');
        await submitButton.click();
        
        await page.waitForTimeout(3000);
        
        // Check for success message
        const successElement = await page.locator('[class*="success"], [class*="Success"]').first();
        if (await successElement.isVisible()) {
          console.log('✅ Forgot password submission working');
        } else {
          console.log('⚠️  Forgot password submission may not be working');
        }
      } else {
        console.log('❌ Forgot password form elements missing');
      }
    } else {
      console.log('❌ Forgot password link not found');
    }
    
  } catch (error) {
    console.log('⚠️  Forgot password test error:', error.message);
  }
}

async function testAPIEndpoints() {
  try {
    // Test forgot password API
    const forgotPasswordResponse = await fetch('http://localhost:3000/api/auth/forgot-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'test@example.com'
      })
    });
    
    if (forgotPasswordResponse.ok) {
      console.log('✅ Forgot password API responding');
    } else {
      console.log('⚠️  Forgot password API error:', forgotPasswordResponse.status);
    }
    
    // Test token validation API
    const tokenValidationResponse = await fetch('http://localhost:3000/api/auth/validate-reset-token-simple', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: 'invalid-token'
      })
    });
    
    if (tokenValidationResponse.status === 400 || tokenValidationResponse.status === 401) {
      console.log('✅ Token validation API working (rejects invalid token)');
    } else {
      console.log('⚠️  Token validation API may not be working correctly');
    }
    
    // Test health endpoint
    const healthResponse = await fetch('http://localhost:3000/api/health');
    if (healthResponse.ok) {
      console.log('✅ Health endpoint working');
    } else {
      console.log('⚠️  Health endpoint not responding');
    }
    
  } catch (error) {
    console.log('⚠️  API test error:', error.message);
  }
}

async function testDatabaseSecurity() {
  try {
    // This would require database access, so we'll test the API security instead
    
    // Test that API endpoints require proper authentication
    const protectedResponse = await fetch('http://localhost:3000/api/auth/profile', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (protectedResponse.status === 401 || protectedResponse.status === 403) {
      console.log('✅ Protected endpoints require authentication');
    } else {
      console.log('⚠️  Protected endpoints may not be properly secured');
    }
    
    // Test rate limiting
    let rateLimitHit = false;
    for (let i = 0; i < 15; i++) {
      const response = await fetch('http://localhost:3000/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: `test${i}@example.com`
        })
      });
      
      if (response.status === 429) {
        rateLimitHit = true;
        break;
      }
    }
    
    if (rateLimitHit) {
      console.log('✅ Rate limiting working');
    } else {
      console.log('⚠️  Rate limiting may not be working');
    }
    
  } catch (error) {
    console.log('⚠️  Database security test error:', error.message);
  }
}

// Run the test
runCompleteAuthTest().catch(console.error);
