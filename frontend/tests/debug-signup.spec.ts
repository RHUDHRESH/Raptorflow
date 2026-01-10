import { test, expect } from '@playwright/test';

test('debug signup flow', async ({ page }) => {
  // Listen for console errors
  page.on('console', msg => {
    if (msg.type() === 'error') console.log('PAGE ERROR:', msg.text());
    if (msg.type() === 'log') console.log('PAGE LOG:', msg.text());
  });

  // Listen for network requests
  page.on('request', request => {
    if (request.url().includes('supabase')) {
      console.log('SUPABASE REQUEST:', request.method(), request.url());
    }
  });

  page.on('response', response => {
    if (response.url().includes('supabase')) {
      console.log('SUPABASE RESPONSE:', response.status(), response.url());
    }
  });

  // Navigate to login
  await page.goto('http://localhost:3000/login');
  await page.waitForLoadState('networkidle');

  // Click Sign Up
  await page.click('button:has-text("Sign Up")');
  await page.waitForTimeout(1000);

  // Fill form
  const testEmail = `test${Date.now()}@example.com`;
  await page.fill('input[type="email"]', testEmail);
  await page.fill('input[type="text"]', 'Test User');
  await page.fill('input[type="password"]', 'testpassword123');

  // Submit
  await page.click('button:has-text("Create Account")');

  // Wait and see what happens
  await page.waitForTimeout(5000);

  // Check current URL
  console.log('Final URL:', page.url());

  // Check for any error messages
  const errorElement = page.locator('text=/error|failed|unable/i');
  if (await errorElement.isVisible()) {
    console.log('Error message:', await errorElement.textContent());
  }
});
