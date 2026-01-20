import { test, expect } from '@playwright/test';

const routes = [
  // Main routes
  '/',
  '/login',
  '/signup',
  '/signup-bypass',
  '/onboarding',
  '/pricing',
  '/workspace',
  '/setup',
  '/setup-complete',
  '/payment/success',
  '/payment/failed',
  '/test-gemini',

  // Shell routes
  '/dashboard',
  '/analytics',
  '/campaigns',
  '/campaigns/1',
  '/cohorts',
  '/daily-wins',
  '/blackbox',
  '/design',
  '/error',
  '/foundation',
  '/help',
  '/matrix',
  '/moves',
  '/moves/1',
  '/muse',
  '/notifications',
  '/payments',
  '/status',

  // Settings routes
  '/settings',
  '/settings/appearance',
  '/settings/billing',
  '/settings/notifications',
  '/settings/profile',
  '/settings/security',
  '/settings/workspace',

  // Onboarding step routes
  '/onboarding/session/step/1',
  '/onboarding/session/step/2',
  '/onboarding/session/step/3',
];

test.describe('Comprehensive Page Error Detection', () => {
  const errors: Array<{
    route: string;
    error: string;
    type: 'console' | 'network' | 'page' | 'timeout';
  }> = [];

  test.beforeEach(async ({ page }) => {
    // Capture console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push({
          route: page.url(),
          error: msg.text(),
          type: 'console'
        });
      }
    });

    // Capture network errors
    page.on('response', response => {
      if (response.status() >= 400) {
        errors.push({
          route: page.url(),
          error: `Network error: ${response.status()} ${response.url()}`,
          type: 'network'
        });
      }
    });

    // Capture page errors
    page.on('pageerror', error => {
      errors.push({
        route: page.url(),
        error: error.message,
        type: 'page'
      });
    });
  });

  test('Navigate through all pages and capture errors', async ({ page }) => {
    for (const route of routes) {
      try {
        console.log(`Testing route: ${route}`);

        // Navigate to the page
        const response = await page.goto(route, {
          waitUntil: 'domcontentloaded',
          timeout: 10000
        });

        if (!response) {
          errors.push({
            route,
            error: 'No response received',
            type: 'page'
          });
          continue;
        }

        // Check if page loaded successfully
        const status = response.status();
        if (status >= 400) {
          errors.push({
            route,
            error: `HTTP ${status} error`,
            type: 'page'
          });
          continue;
        }

        // Wait a bit for any dynamic content to load
        await page.waitForTimeout(2000);

        // Check for common error indicators
        const hasErrorContent = await page.locator('text=Error').count() > 0 ||
                               await page.locator('text=500').count() > 0 ||
                               await page.locator('text=404').count() > 0 ||
                               await page.locator('.error').count() > 0;

        if (hasErrorContent) {
          errors.push({
            route,
            error: 'Page contains error content',
            type: 'page'
          });
        }

        console.log(`✅ Route ${route} loaded successfully`);

      } catch (error) {
        errors.push({
          route,
          error: error instanceof Error ? error.message : String(error),
          type: 'timeout'
        });
        console.log(`❌ Route ${route} failed: ${error}`);
      }
    }

    // Print all errors at the end
    console.log('\n=== ERROR SUMMARY ===');
    if (errors.length === 0) {
      console.log('🎉 No errors found!');
    } else {
      console.log(`Found ${errors.length} errors:\n`);
      errors.forEach((error, index) => {
        console.log(`${index + 1}. Route: ${error.route}`);
        console.log(`   Type: ${error.type}`);
        console.log(`   Error: ${error.error}\n`);
      });
    }

    // Fail the test if there are critical errors
    const criticalErrors = errors.filter(e =>
      e.type === 'page' ||
      e.type === 'timeout' ||
      (e.type === 'network' && e.error.includes('500'))
    );

    if (criticalErrors.length > 0) {
      throw new Error(`Found ${criticalErrors.length} critical errors that need fixing`);
    }
  });
});
