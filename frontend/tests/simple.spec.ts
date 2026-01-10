import { test, expect } from '@playwright/test';

test('basic page load', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.waitForLoadState('networkidle');

  // Check if page loaded
  const title = await page.title();
  console.log('Page title:', title);

  // Look for any content
  const body = await page.locator('body').textContent();
  console.log('Body content preview:', body?.substring(0, 200));
});
