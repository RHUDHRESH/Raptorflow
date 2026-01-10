const { chromium } = require('playwright');

async function testAuthenticationFlow() {
  console.log('🎭 Starting Playwright Browser Test...\n');

  // Launch browser
  const browser = await chromium.launch({
    headless: false,  // Show the browser
    slowMo: 1000     // Slow down actions so we can see them
  });
  let page;
  try {
    const context = await browser.newContext();
    page = await context.newPage();

    console.log('🌐 Step 1: Opening login page...');
    await page.goto('http://localhost:3000/login');

    // Wait for page to load
    await page.waitForLoadState('networkidle');
    console.log('✅ Login page loaded');

    // Take a screenshot to see what's happening
    await page.screenshot({ path: 'login-page.png', fullPage: true });
    console.log('📸 Screenshot saved: login-page.png');

    // Check if we got the login page or an error
    const title = await page.title();
    console.log(`📄 Page title: ${title}`);

    const content = await page.content();
    if (content.includes('403') || content.includes('access denied')) {
      console.log('❌ Got 403 error page');
      console.log('📄 Page content preview:', content.substring(0, 500));
    } else {
      console.log('✅ Login page content loaded successfully');

      // Step 2: Switch to signup mode
      console.log('🔄 Step 2: Switching to signup mode...');

      // Look for the "REQUEST ACCESS" button
      const signupButton = await page.locator('text=REQUEST ACCESS').first();
      if (await signupButton.isVisible()) {
        await signupButton.click();
        console.log('✅ Clicked REQUEST ACCESS button');
        await page.waitForTimeout(1000);
      } else {
        console.log('❌ REQUEST ACCESS button not found');
        // Try alternative selectors
        const altButton = await page.locator('button:has-text("REQUEST")').first();
        if (await altButton.isVisible()) {
          await altButton.click();
          console.log('✅ Clicked alternative REQUEST button');
        }
      }

      // Step 3: Fill out the signup form
      console.log('📝 Step 3: Filling out signup form...');

      // Fill email
      await page.fill('input[type="email"]', 'testuser@gmail.com');
      console.log('✅ Filled email field');

      // Fill password
      await page.fill('input[type="password"]', 'password123');
      console.log('✅ Filled password field');

      // Fill full name (only visible in signup mode)
      const nameInput = await page.locator('input[placeholder*="Alex"], input[placeholder*="Jane"]').first();
      if (await nameInput.isVisible()) {
        await nameInput.fill('Test User');
        console.log('✅ Filled full name field');
      }

      // Step 4: Submit the form
      console.log('🚀 Step 4: Submitting signup form...');

      const submitButton = await page.locator('button:has-text("Create Account"), button:has-text("REQUEST"), button:has-text("Create Workspace"), button:has-text("Enter Workspace")').first();
      if (await submitButton.isVisible()) {
        await submitButton.click();
        console.log('✅ Clicked submit button');

        // Wait for navigation
        await page.waitForTimeout(3000);

        // Check where we ended up
        const currentUrl = page.url();
        console.log(`📍 Current URL after submit: ${currentUrl}`);

        if (currentUrl.includes('/workspace')) {
          console.log('🎉 SUCCESS! Redirected to workspace!');
          await page.screenshot({ path: 'workspace-success.png', fullPage: true });
        } else if (currentUrl.includes('/login')) {
          console.log('⚠️ Still on login page - checking for errors...');
          // Keep selector simple to avoid invalid CSS errors
          const errorElement = await page.locator('.error, [class*="error"], [class*="alert"], [role="alert"]').first();
          if (await errorElement.isVisible()) {
            const errorText = await errorElement.textContent();
            console.log('❌ Error message:', errorText?.trim());
          } else {
            console.log('❌ No visible error element found');
          }
        } else {
          console.log('🤔 Ended up at unexpected URL:', currentUrl);
        }
      } else {
        console.log('❌ Submit button not found');
      }

      // Take final screenshot
      await page.screenshot({ path: 'final-state.png', fullPage: true });
      console.log('📸 Final screenshot saved: final-state.png');
    }

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (page) {
      try { await page.screenshot({ path: 'error-state.png', fullPage: true }); } catch {}
    }
  } finally {
    // Keep browser open for 10 seconds so we can see what happened
    if (page) {
      console.log('⏰ Keeping browser open for 10 seconds...');
      await page.waitForTimeout(10000);
    }
    await browser.close();
    console.log('🔚 Browser closed');
  }
}

// Run the test
testAuthenticationFlow().catch(console.error);
