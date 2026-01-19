import { test, expect } from '@playwright/test';

test.describe('Muse Vertex AI Integration', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/muse-vertex-ai');
  });

  test('should load Muse Vertex AI chat interface', async ({ page }) => {
    // Check if the page loads correctly
    await expect(page.locator('h3')).toContainText('Muse Vertex AI');
    
    // Check for connection status
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Check for welcome message
    await expect(page.locator('text=Welcome to Muse Vertex AI')).toBeVisible();
    await expect(page.locator('text=powered by Gemini 2.0 Flash')).toBeVisible();
  });

  test('should show quick action buttons', async ({ page }) => {
    // Wait for connection
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Check for quick action buttons
    await expect(page.locator('button:has-text("Blog")')).toBeVisible();
    await expect(page.locator('button:has-text("Email")')).toBeVisible();
  });

  test('should show suggested prompts', async ({ page }) => {
    // Wait for connection
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Check for suggested prompts
    await expect(page.locator('text=Try asking me:')).toBeVisible();
    await expect(page.locator('button:has-text("How can I improve my email marketing campaigns?")')).toBeVisible();
    await expect(page.locator('button:has-text("Create a social media content calendar")')).toBeVisible();
    await expect(page.locator('button:has-text("What are the best practices for landing page optimization?")')).toBeVisible();
  });

  test('should allow clicking suggested prompts', async ({ page }) => {
    // Wait for connection
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Click on a suggested prompt
    await page.locator('button:has-text("How can I improve my email marketing campaigns?")').click();
    
    // Check if the input is populated
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await expect(input).toHaveValue('How can I improve my email marketing campaigns?');
  });

  test('should send a message and receive response', async ({ page }) => {
    // Wait for connection
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Type and send a message
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await input.fill('Hello! Can you help me with marketing automation?');
    
    // Click send button
    await page.locator('button:has([data-lucide="Send"])').click();
    
    // Check if user message appears
    await expect(page.locator('text=Hello! Can you help me with marketing automation?')).toBeVisible();
    
    // Wait for AI response (this might take a few seconds)
    await expect(page.locator('text=Tokens:')).toBeVisible({ timeout: 30000 });
    
    // Check for AI response metadata
    await expect(page.locator('text=Cost:')).toBeVisible();
    await expect(page.locator('text=Model:')).toBeVisible();
  });

  test('should use quick content generation', async ({ page }) => {
    // Wait for connection
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Click the Blog quick action button
    await page.locator('button:has-text("Blog")').click();
    
    // Wait for content generation
    await expect(page.locator('text=Generated blog:')).toBeVisible({ timeout: 30000 });
    
    // Check for metadata
    await expect(page.locator('text=Tokens:')).toBeVisible();
    await expect(page.locator('text=Cost:')).toBeVisible();
    await expect(page.locator('text=SEO Score:')).toBeVisible();
  });

  test('should show suggestions after AI response', async ({ page }) => {
    // Wait for connection
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Send a message
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await input.fill('Tell me about content marketing');
    await page.locator('button:has([data-lucide="Send"])').click();
    
    // Wait for AI response
    await expect(page.locator('text=Tokens:')).toBeVisible({ timeout: 30000 });
    
    // Check for suggestions
    await expect(page.locator('text=Suggestions:')).toBeVisible();
    
    // Suggestions should be clickable
    const suggestions = page.locator('button:has-text("💡")');
    await expect(suggestions.first()).toBeVisible();
  });

  test('should handle API connection errors gracefully', async ({ page }) => {
    // This test would need to simulate API failure
    // For now, just check that the error state is handled
    await expect(page.locator('text=Connecting...')).toBeVisible({ timeout: 5000 });
    
    // Should eventually show either connected or error state
    await expect(page.locator('text=Connected to Gemini 2.0 Flash').or(page.locator('text=API Connection Error'))).toBeVisible({ timeout: 15000 });
  });

  test('should disable input when loading', async ({ page }) => {
    // Wait for connection
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Send a message
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await input.fill('Test message');
    await page.locator('button:has([data-lucide="Send"])').click();
    
    // Input should be disabled while loading
    await expect(input).toBeDisabled();
    
    // Send button should show stop icon while loading
    await expect(page.locator('button:has([data-lucide="StopCircle"])')).toBeVisible();
    
    // Wait for response to complete
    await expect(page.locator('text=Tokens:')).toBeVisible({ timeout: 30000 });
    
    // Input should be enabled again
    await expect(input).toBeEnabled();
    await expect(page.locator('button:has([data-lucide="Send"])')).toBeVisible();
  });

  test('should display cost and token information', async ({ page }) => {
    // Wait for connection
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Send a message
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await input.fill('What is the best marketing strategy?');
    await page.locator('button:has([data-lucide="Send"])').click();
    
    // Wait for response
    await expect(page.locator('text=Tokens:')).toBeVisible({ timeout: 30000 });
    
    // Check cost format (should be very small, like $0.000XXX)
    const costText = await page.locator('text=Cost:').textContent();
    expect(costText).toMatch(/\$0\.000\d+/);
    
    // Check tokens (should be a number)
    const tokensText = await page.locator('text=Tokens:').textContent();
    expect(tokensText).toMatch(/Tokens: \d+/);
  });
});

test.describe('Muse Vertex AI - Error Handling', () => {
  test('should handle network errors', async ({ page }) => {
    // Mock network failure by intercepting the API call
    await page.route('/api/v1/muse/status', route => {
      route.fulfill({ status: 500, body: '{"error": "API Error"}' });
    });
    
    await page.goto('/muse-vertex-ai');
    
    // Should show error state
    await expect(page.locator('text=API Connection Error')).toBeVisible({ timeout: 15000 });
    
    // Input should be disabled
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await expect(input).toBeDisabled();
  });

  test('should handle API rate limiting', async ({ page }) => {
    // Mock rate limit response
    await page.route('/api/v1/muse/chat', route => {
      route.fulfill({ 
        status: 429, 
        body: '{"success": false, "error": "Rate limit exceeded"}' 
      });
    });
    
    await page.goto('/muse-vertex-ai');
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Try to send a message
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await input.fill('Test message');
    await page.locator('button:has([data-lucide="Send"])').click();
    
    // Should show error message
    await expect(page.locator('text=encountered an error')).toBeVisible({ timeout: 10000 });
  });
});

test.describe('Muse Vertex AI - Performance', () => {
  test('should load within reasonable time', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/muse-vertex-ai');
    
    // Should connect within 15 seconds
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 15000 });
    
    const loadTime = Date.now() - startTime;
    expect(loadTime).toBeLessThan(15000); // 15 seconds max load time
  });

  test('should respond to messages within reasonable time', async ({ page }) => {
    await page.goto('/muse-vertex-ai');
    await expect(page.locator('text=Connected to Gemini 2.0 Flash')).toBeVisible({ timeout: 10000 });
    
    // Send a simple message
    const input = page.locator('input[placeholder*="Ask Muse"]');
    await input.fill('Hello');
    await page.locator('button:has([data-lucide="Send"])').click();
    
    // Should respond within 30 seconds
    const startTime = Date.now();
    await expect(page.locator('text=Tokens:')).toBeVisible({ timeout: 30000 });
    const responseTime = Date.now() - startTime;
    
    // Log response time for monitoring
    console.log(`AI Response Time: ${responseTime}ms`);
    
    // Should respond within 30 seconds (generous for AI)
    expect(responseTime).toBeLessThan(30000);
  });
});
