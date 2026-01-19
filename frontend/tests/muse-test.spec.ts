import { test, expect } from '@playwright/test';

test('🎬 Simple Muse Test Page', async ({ page }) => {
  console.log('🎬 Testing simple Muse page...');
  
  // Navigate to the test page
  await page.goto('http://localhost:3000/muse-test');
  
  // Check if page loads
  await expect(page.locator('h1:has-text("Muse Vertex AI Test Page")')).toBeVisible({ timeout: 10000 });
  console.log('✅ Test page loaded successfully');
  
  // Check for content
  await expect(page.locator('text=Status: Testing')).toBeVisible();
  await expect(page.locator('button:has-text("Test Button")')).toBeVisible();
  console.log('✅ Page content visible');
  
  console.log('🎉 Simple test page working!');
});
