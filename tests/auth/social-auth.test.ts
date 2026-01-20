import { test, expect, chromium, type Browser, type Page } from '@playwright/test';

test.describe('Social Authentication & Onboarding', () => {
  let browser: Browser;
  let page: Page;
  const baseUrl = process.env.TEST_BASE_URL || 'http://localhost:3000';

  test.beforeEach(async () => {
    browser = await chromium.launch({ headless: true });
    page = await browser.newPage();
  });

  test.afterEach(async () => {
    await browser.close();
  });

  test.describe('Social Login Providers', () => {
    test('should display Google and GitHub login options', async () => {
      await page.goto(`${baseUrl}/login`);
      
      // Debug: Print title and status
      console.log(`Page Title: ${await page.title()}`);
      
      // Check for Google login button
      const googleBtn = page.locator('button:has-text("Continue with Google")');
      try {
        await expect(googleBtn).toBeVisible({ timeout: 5000 });
      } catch (e) {
        console.log('Google button not found. Page content:');
        console.log(await page.content());
        throw e;
      }
      
      // Check for GitHub login button
      const githubBtn = page.locator('button:has-text("Continue with GitHub")');
      await expect(githubBtn).toBeVisible();
    });

    test('should redirect to Google OAuth on click', async () => {
      await page.goto(`${baseUrl}/login`);
      
      const googleBtn = page.locator('button:has-text("Continue with Google")');
      await googleBtn.click();
      
      // Check for loading state
      await expect(page.locator('text=ESTABLISHING UPLINK...')).toBeVisible();
    });

    test('should redirect to GitHub OAuth on click', async () => {
       await page.goto(`${baseUrl}/login`);
       
       const githubBtn = page.locator('button:has-text("Continue with GitHub")');
       await githubBtn.click();
       
       // Check for loading state - THIS SHOULD FAIL INITIALLY
       await expect(page.locator('text=ESTABLISHING UPLINK...')).toBeVisible();
    });
  });
});
