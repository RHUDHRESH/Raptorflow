// Manual OAuth Flow Test
// Run this with: node test-auth-flow.js

import { chromium } from 'playwright';

async function testOAuthFlow() {
  console.log('🔍 Testing OAuth Flow...');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate to login page
    console.log('📍 Navigating to login page...');
    await page.goto('http://localhost:3000/login');
    
    // Wait for page to load
    await page.waitForSelector('button', { timeout: 5000 });
    
    // Check if Google OAuth button is available
    const googleButton = await page.$('button');
    if (googleButton) {
      console.log('✅ Google OAuth button found');
      
      // Click Google OAuth button
      console.log('🖱️ Clicking Google OAuth button...');
      await googleButton.click();
      
      // Wait for redirect (OAuth will redirect to Google)
      console.log('⏳ Waiting for OAuth redirect...');
      await page.waitForNavigation({ timeout: 10000 });
      
      // Check current URL
      const currentUrl = page.url();
      console.log('📍 Current URL:', currentUrl);
      
      if (currentUrl.includes('accounts.google.com')) {
        console.log('✅ Redirected to Google OAuth');
        
        // Wait for user to complete OAuth (manual step)
        console.log('⏸️ Please complete Google OAuth in the browser...');
        console.log('⏸️ After authentication, you should be redirected back to the app');
        
        // Wait for redirect back to app
        await page.waitForNavigation({ timeout: 60000 });
        
        const finalUrl = page.url();
        console.log('📍 Final URL after OAuth:', finalUrl);
        
        if (finalUrl.includes('localhost:3000')) {
          console.log('✅ OAuth completed successfully');
          
          // Wait a bit for session to be established
          await page.waitForTimeout(2000);
          
          // Check if user is authenticated
          const authDebug = await page.$('.fixed.top-4.right-4');
          if (authDebug) {
            const debugText = await authDebug.textContent();
            console.log('🔍 Auth Debug Info:', debugText);
          }
          
          // Navigate to plans page
          console.log('📍 Navigating to plans page...');
          await page.goto('http://localhost:3000/onboarding/plans');
          
          // Wait for plans to load
          await page.waitForSelector('.text-4xl', { timeout: 5000 });
          
          // Check if pricing cards are loaded
          const pricingCards = await page.$$('.text-4xl');
          console.log(`💰 Found ${pricingCards.length} pricing cards`);
          
          // Try to select a plan
          const firstPlan = await page.$('button');
          if (firstPlan) {
            console.log('🎯 Clicking first plan button...');
            await firstPlan.click();
            
            // Wait for response
            await page.waitForTimeout(3000);
            
            // Check for any error messages
            const errorElement = await page.$('.text-red-600');
            if (errorElement) {
              const errorText = await errorElement.textContent();
              console.log('❌ Error:', errorText);
            } else {
              console.log('✅ Plan selection successful!');
            }
          }
          
        } else {
          console.log('❌ OAuth did not redirect back to app');
        }
      } else {
        console.log('❌ Did not redirect to Google OAuth');
      }
    } else {
      console.log('❌ Google OAuth button not found');
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await browser.close();
  }
}

// Only run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  testOAuthFlow();
}
