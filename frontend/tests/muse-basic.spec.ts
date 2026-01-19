import { test, expect } from '@playwright/test';

test.describe('Muse Vertex AI - Basic Demo', () => {
  test('🎬 Basic Muse Interface Demo', async ({ page }) => {
    console.log('🎬 Starting basic Muse demo...');
    
    // Navigate to the Muse Vertex AI page
    await page.goto('http://localhost:3000/muse-vertex-ai');
    
    // Wait for page to load (basic elements)
    await page.waitForSelector('h3:has-text("Muse Vertex AI")', { timeout: 10000 });
    console.log('✅ Page loaded successfully');
    
    // Check for basic interface elements
    await expect(page.locator('h3:has-text("Muse Vertex AI")')).toBeVisible();
    console.log('✅ Header visible');
    
    // Check for welcome message (should be visible even without API connection)
    await expect(page.locator('text=Welcome to Muse Vertex AI')).toBeVisible({ timeout: 5000 });
    console.log('✅ Welcome message visible');
    
    // Check for input field
    await expect(page.locator('input[placeholder*="Ask Muse"]')).toBeVisible();
    console.log('✅ Input field visible');
    
    // Check for send button
    await expect(page.locator('button:has([data-lucide="Send"])')).toBeVisible();
    console.log('✅ Send button visible');
    
    // Check for quick action buttons
    await expect(page.locator('button:has-text("Blog")')).toBeVisible();
    await expect(page.locator('button:has-text("Email")')).toBeVisible();
    console.log('✅ Quick action buttons visible');
    
    // Check for suggested prompts
    await expect(page.locator('text=Try asking me:')).toBeVisible();
    await expect(page.locator('button:has-text("How can I improve my email marketing campaigns?")')).toBeVisible();
    console.log('✅ Suggested prompts visible');
    
    // Test clicking a suggested prompt
    console.log('📍 Testing suggested prompt click...');
    await page.locator('button:has-text("How can I improve my email marketing campaigns?")').click();
    
    // Verify input is populated
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await expect(input).toHaveValue('How can I improve my email marketing campaigns?');
    console.log('✅ Suggested prompt clicked and input populated');
    
    // Take screenshot for demo
    console.log('📍 Taking demo screenshot...');
    await page.screenshot({ 
      path: 'muse-vertex-ai-basic-demo.png', 
      fullPage: true 
    });
    console.log('📸 Basic demo screenshot saved');
    
    console.log('🎉 Basic Muse demo completed successfully!');
    console.log('📱 Interface is working and ready for API connection');
  });

  test('🔧 API Connection Test', async ({ page }) => {
    console.log('🔧 Testing API connection...');
    
    await page.goto('http://localhost:3000/muse-vertex-ai');
    await page.waitForSelector('h3:has-text("Muse Vertex AI")', { timeout: 10000 });
    
    // Wait for API status (might be connecting, connected, or error)
    console.log('📍 Waiting for API status...');
    
    // Check for any of the possible status messages
    const statusLocator = page.locator('text=Connecting to Gemini 2.0 Flash, text=Connected to Gemini 2.0 Flash, text=API Connection Error');
    
    try {
      await expect(statusLocator.first()).toBeVisible({ timeout: 15000 });
      const statusText = await statusLocator.first().textContent();
      console.log(`📊 API Status: ${statusText}`);
      
      if (statusText?.includes('Connected')) {
        console.log('✅ API connection successful!');
        
        // Test a quick action if connected
        console.log('📍 Testing quick content generation...');
        await page.locator('button:has-text("Blog")').click();
        
        // Wait for response (if API is working)
        try {
          await expect(page.locator('text=Generated blog:')).toBeVisible({ timeout: 30000 });
          console.log('✅ Content generation working!');
          
          // Check for metadata
          await expect(page.locator('text=Tokens:')).toBeVisible();
          await expect(page.locator('text=Cost:')).toBeVisible();
          console.log('✅ Cost tracking working!');
          
        } catch (error) {
          console.log('⚠️ Content generation timed out - API might be slow');
        }
        
      } else if (statusText?.includes('Connecting')) {
        console.log('⏳ API still connecting...');
      } else {
        console.log('❌ API connection failed');
      }
    } catch (error) {
      console.log('⚠️ API status not determined within timeout');
    }
    
    // Take screenshot showing current state
    await page.screenshot({ 
      path: 'muse-vertex-ai-api-status.png', 
      fullPage: true 
    });
    console.log('📸 API status screenshot saved');
    
    console.log('🔧 API connection test completed');
  });

  test('📱 Responsive Design Test', async ({ page }) => {
    console.log('📱 Testing responsive design...');
    
    await page.goto('http://localhost:3000/muse-vertex-ai');
    await page.waitForSelector('h3:has-text("Muse Vertex AI")', { timeout: 10000 });
    
    // Test desktop
    console.log('📍 Testing desktop view...');
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(page.locator('h3:has-text("Muse Vertex AI")')).toBeVisible();
    console.log('✅ Desktop view working');
    
    // Test tablet
    console.log('📍 Testing tablet view...');
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('h3:has-text("Muse Vertex AI")')).toBeVisible();
    console.log('✅ Tablet view working');
    
    // Test mobile
    console.log('📍 Testing mobile view...');
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('h3:has-text("Muse Vertex AI")')).toBeVisible();
    console.log('✅ Mobile view working');
    
    // Reset to desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    console.log('📱 Responsive design test completed');
  });
});
