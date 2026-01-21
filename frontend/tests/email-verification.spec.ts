import { test, expect } from '@playwright/test';

test.describe('Email Verification Gate', () => {
  test('unverified user should be redirected to verify-email', async ({ page }) => {
    // 1. Mock the Supabase session response for an unverified user
    await page.route('**/auth/v1/user', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'unverified-user-id',
          email: 'unverified@example.com',
          email_confirmed_at: null, // This makes the user unverified
          user_metadata: { full_name: 'Unverified User' },
          aud: 'authenticated',
          role: 'authenticated'
        })
      });
    });

    // Mock session request
    await page.route('**/auth/v1/session', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'fake-token',
          token_type: 'bearer',
          expires_in: 3600,
          refresh_token: 'fake-refresh',
          user: {
            id: 'unverified-user-id',
            email: 'unverified@example.com',
            email_confirmed_at: null
          }
        })
      });
    });

    // 2. Attempt to navigate to dashboard
    await page.goto('http://localhost:3000/dashboard');

    // 3. Expect redirect to verify-email page
    // This is the failing part since we haven't implemented the gate or the page
    await expect(page).toHaveURL(/.*verify-email/);
  });

  test('verified user should NOT be redirected to verify-email', async ({ page }) => {
    // Mock verified user
    await page.route('**/auth/v1/user', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'verified-user-id',
          email: 'verified@example.com',
          email_confirmed_at: new Date().toISOString(),
          user_metadata: { full_name: 'Verified User' },
          aud: 'authenticated',
          role: 'authenticated'
        })
      });
    });

    await page.goto('http://localhost:3000/dashboard');

    // Should stay on dashboard
    await expect(page).toHaveURL(/.*dashboard/);
  });
});
