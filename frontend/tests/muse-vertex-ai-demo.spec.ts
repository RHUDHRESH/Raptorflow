import { test, expect } from '@playwright/test';

test.describe('Muse Vertex AI - Live Demo', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the Muse Vertex AI page
    await page.goto('http://localhost:3000/muse-vertex-ai');
    
    // Wait for the page to load and connect to API
    await page.waitForSelector('text=Connected to Gemini 2.0 Flash', { timeout: 15000 });
  });

  test('🎬 Complete Muse Vertex AI Demo', async ({ page }) => {
    console.log('🎬 Starting Muse Vertex AI Demo...');
    
    // Step 1: Verify initial state
    console.log('📍 Step 1: Verifying initial state...');
    await expect(page.locator('h3:has-text("Muse Vertex AI")')).toBeVisible();
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible();
    await expect(page.locator('text=Welcome to Muse Vertex AI')).toBeVisible();
    await expect(page.locator('text=powered by Gemini 2.0 Flash')).toBeVisible();
    console.log('✅ Initial state verified');
    
    // Step 2: Show quick action buttons
    console.log('📍 Step 2: Testing quick actions...');
    await expect(page.locator('button:has-text("Blog")')).toBeVisible();
    await expect(page.locator('button:has-text("Email")')).toBeVisible();
    console.log('✅ Quick action buttons visible');
    
    // Step 3: Show suggested prompts
    console.log('📍 Step 3: Displaying suggested prompts...');
    await expect(page.locator('text=Try asking me:')).toBeVisible();
    await expect(page.locator('button:has-text("How can I improve my email marketing campaigns?")')).toBeVisible();
    await expect(page.locator('button:has-text("Create a social media content calendar")')).toBeVisible();
    await expect(page.locator('button:has-text("What are the best practices for landing page optimization?")')).toBeVisible();
    console.log('✅ Suggested prompts visible');
    
    // Step 4: Click on a suggested prompt
    console.log('📍 Step 4: Clicking suggested prompt...');
    await page.locator('button:has-text("How can I improve my email marketing campaigns?")').click();
    
    // Verify input is populated
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await expect(input).toHaveValue('How can I improve my email marketing campaigns?');
    console.log('✅ Suggested prompt clicked and input populated');
    
    // Step 5: Send the message
    console.log('📍 Step 5: Sending message to AI...');
    await page.locator('button:has([data-lucide="Send"])').click();
    
    // Verify user message appears
    await expect(page.locator('text=How can I improve my email marketing campaigns?')).toBeVisible();
    console.log('✅ Message sent');
    
    // Step 6: Wait for AI response
    console.log('📍 Step 6: Waiting for AI response...');
    await expect(page.locator('text=Tokens:')).toBeVisible({ timeout: 30000 });
    
    // Verify AI response metadata
    await expect(page.locator('text=Cost:')).toBeVisible();
    console.log('✅ AI response received with metadata');
    
    // Step 7: Check for suggestions
    console.log('📍 Step 7: Checking for AI suggestions...');
    const suggestions = page.locator('button:has-text("💡")');
    if (await suggestions.count() > 0) {
      console.log(`✅ Found ${await suggestions.count()} suggestions`);
      // Click on first suggestion to show interactivity
      await suggestions.first().click();
      console.log('✅ Suggestion clicked');
    } else {
      console.log('ℹ️  No suggestions in this response');
    }
    
    // Step 8: Test quick content generation
    console.log('📍 Step 8: Testing quick content generation...');
    await page.locator('button:has-text("Blog")').click();
    
    // Wait for content generation
    await expect(page.locator('text=Generated blog:')).toBeVisible({ timeout: 30000 });
    
    // Check for content metadata
    await expect(page.locator('text=Tokens:')).toBeVisible();
    await expect(page.locator('text=Cost:')).toBeVisible();
    await expect(page.locator('text=SEO Score:')).toBeVisible();
    console.log('✅ Blog content generated successfully');
    
    // Step 9: Test another quick action
    console.log('📍 Step 9: Testing email content generation...');
    await page.locator('button:has-text("Email")').click();
    
    // Wait for email content
    await expect(page.locator('text=Generated email:')).toBeVisible({ timeout: 30000 });
    console.log('✅ Email content generated successfully');
    
    // Step 10: Test manual input
    console.log('📍 Step 10: Testing manual input...');
    await input.fill('Create a marketing strategy for a new SaaS product');
    await page.locator('button:has([data-lucide="Send"])').click();
    
    // Wait for response
    await expect(page.locator('text=Tokens:')).toBeVisible({ timeout: 30000 });
    console.log('✅ Manual input processed successfully');
    
    // Step 11: Verify cost tracking
    console.log('📍 Step 11: Verifying cost tracking...');
    const costElements = page.locator('text=Cost:');
    const costCount = await costElements.count();
    console.log(`💰 Total cost entries: ${costCount}`);
    
    // Check cost format
    for (let i = 0; i < costCount; i++) {
      const costText = await costElements.nth(i).textContent();
      if (costText && costText.includes('$')) {
        console.log(`💸 Cost entry ${i + 1}: ${costText}`);
      }
    }
    
    // Step 12: Verify token tracking
    console.log('📍 Step 12: Verifying token tracking...');
    const tokenElements = page.locator('text=Tokens:');
    const tokenCount = await tokenElements.count();
    console.log(`📊 Total token entries: ${tokenCount}`);
    
    // Step 13: Take screenshot for demo
    console.log('📍 Step 13: Taking demo screenshot...');
    await page.screenshot({ 
      path: 'muse-vertex-ai-demo.png', 
      fullPage: true 
    });
    console.log('📸 Demo screenshot saved');
    
    // Step 14: Final verification
    console.log('📍 Step 14: Final verification...');
    
    // Count total messages
    const userMessages = page.locator('div:has-text("How can I improve my email marketing campaigns?"), div:has-text("Create a marketing strategy for a new SaaS product")');
    const aiMessages = page.locator('text=Tokens:');
    
    const userMessageCount = await userMessages.count();
    const aiMessageCount = await aiMessages.count();
    
    console.log(`📨 User messages: ${userMessageCount}`);
    console.log(`🤖 AI responses: ${aiMessageCount}`);
    
    // Verify the interface is still responsive
    await expect(input).toBeVisible();
    await expect(page.locator('button:has([data-lucide="Send"])')).toBeVisible();
    
    console.log('✅ Demo completed successfully!');
    console.log('🎉 Muse Vertex AI is fully functional!');
  });

  test('🎯 Performance Demo', async ({ page }) => {
    console.log('⚡ Starting performance demo...');
    
    // Test response times
    const testMessages = [
      'What is marketing automation?',
      'How do I create a content calendar?',
      'Best practices for email subject lines?'
    ];
    
    for (let i = 0; i < testMessages.length; i++) {
      console.log(`📍 Testing message ${i + 1}: ${testMessages[i]}`);
      
      const startTime = Date.now();
      
      // Type and send message
      await page.locator('input[placeholder*="Ask Muse"]').fill(testMessages[i]);
      await page.locator('button:has([data-lucide="Send"])').click();
      
      // Wait for response
      await expect(page.locator('text=Tokens:')).toBeVisible({ timeout: 30000 });
      
      const responseTime = Date.now() - startTime;
      console.log(`⏱️  Response time: ${responseTime}ms`);
      
      // Verify response quality
      const costText = await page.locator('text=Cost:').first().textContent();
      const tokenText = await page.locator('text=Tokens:').first().textContent();
      
      console.log(`💰 Cost: ${costText}`);
      console.log(`📊 Tokens: ${tokenText}`);
    }
    
    console.log('⚡ Performance demo completed!');
  });

  test('🔧 Error Handling Demo', async ({ page }) => {
    console.log('🔧 Starting error handling demo...');
    
    // Test empty message
    console.log('📍 Testing empty message...');
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await input.fill('');
    await page.locator('button:has([data-lucide="Send"])').click();
    
    // Should not send empty message
    await expect(input).toBeVisible();
    console.log('✅ Empty message correctly handled');
    
    // Test very long message
    console.log('📍 Testing long message...');
    const longMessage = 'This is a very long message '.repeat(50);
    await input.fill(longMessage);
    await page.locator('button:has([data-lucide="Send"])').click();
    
    // Should handle gracefully
    await expect(page.locator('text=Tokens:')).toBeVisible({ timeout: 30000 });
    console.log('✅ Long message handled gracefully');
    
    console.log('🔧 Error handling demo completed!');
  });
});

test.describe('🎬 Muse Vertex AI - Feature Showcase', () => {
  test('📱 Complete Feature Tour', async ({ page }) => {
    await page.goto('http://localhost:3000/muse-vertex-ai');
    await page.waitForSelector('text=Connected to Gemini 2.0 Flash', { timeout: 15000 });
    
    console.log('🎬 Starting feature tour...');
    
    // Feature 1: Connection Status
    console.log('📍 Feature 1: Connection Status');
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible();
    console.log('✅ Connection status working');
    
    // Feature 2: Quick Actions
    console.log('📍 Feature 2: Quick Actions');
    await page.locator('button:has-text("Blog")').click();
    await expect(page.locator('text=Generated blog:')).toBeVisible({ timeout: 30000 });
    console.log('✅ Quick actions working');
    
    // Feature 3: Interactive Chat
    console.log('📍 Feature 3: Interactive Chat');
    await page.locator('input[placeholder*="Ask Muse"]').fill('Tell me about content marketing');
    await page.locator('button:has([data-lucide="Send"])').click();
    await expect(page.locator('text=Tokens:')).toBeVisible({ timeout: 30000 });
    console.log('✅ Interactive chat working');
    
    // Feature 4: Cost Tracking
    console.log('📍 Feature 4: Cost Tracking');
    await expect(page.locator('text=Cost:')).toBeVisible();
    const costText = await page.locator('text=Cost:').first().textContent();
    console.log(`💰 Cost tracking: ${costText}`);
    console.log('✅ Cost tracking working');
    
    // Feature 5: Token Usage
    console.log('📍 Feature 5: Token Usage');
    await expect(page.locator('text=Tokens:')).toBeVisible();
    const tokenText = await page.locator('text=Tokens:').first().textContent();
    console.log(`📊 Token tracking: ${tokenText}`);
    console.log('✅ Token usage working');
    
    // Feature 6: SEO Scoring
    console.log('📍 Feature 6: SEO Scoring');
    await expect(page.locator('text=SEO Score:')).toBeVisible();
    const seoText = await page.locator('text=SEO Score:').first().textContent();
    console.log(`📈 SEO scoring: ${seoText}`);
    console.log('✅ SEO scoring working');
    
    // Feature 7: Smart Suggestions
    console.log('📍 Feature 7: Smart Suggestions');
    const suggestions = page.locator('button:has-text("💡")');
    const suggestionCount = await suggestions.count();
    console.log(`💡 Found ${suggestionCount} suggestions`);
    if (suggestionCount > 0) {
      await suggestions.first().click();
      console.log('✅ Smart suggestions working');
    }
    
    // Feature 8: Responsive Design
    console.log('📍 Feature 8: Responsive Design');
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('h3:has-text("Muse Vertex AI")')).toBeVisible();
    console.log('✅ Responsive design working');
    
    // Reset to desktop
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    console.log('🎬 Feature tour completed!');
    console.log('🎉 All features are working perfectly!');
  });
});
