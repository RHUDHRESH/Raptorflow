import { test, expect } from '@playwright/test';

const criticalRoutes = [
  '/',
  '/login',
  '/signup',
  '/dashboard',
  '/daily-wins',
  '/blackbox',
  '/campaigns',
  '/moves',
  '/muse',
  '/settings'
];

test.describe('Critical Page Error Detection', () => {
  test('Check critical pages for major errors', async ({ page }) => {
    const errors = [];

    // Listen for console errors
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push({ type: 'console', message: msg.text(), url: page.url() });
      }
    });

    // Listen for page errors
    page.on('pageerror', error => {
      errors.push({ type: 'page', message: error.message, url: page.url() });
    });

    for (const route of criticalRoutes) {
      try {
        console.log(`Testing: ${route}`);

        const response = await page.goto(`http://localhost:3001${route}`, {
          waitUntil: 'domcontentloaded',
          timeout: 8000
        });

        if (!response || response.status() >= 400) {
          errors.push({
            type: 'network',
            message: `HTTP ${response?.status || 'No response'}`,
            url: `http://localhost:3001${route}`
          });
        }

        // Check for error indicators
        const hasErrorContent = await page.locator('text=Error').count() > 0;
        if (hasErrorContent) {
          errors.push({ type: 'content', message: 'Page contains error content', url: `http://localhost:3001${route}` });
        }

        console.log(`✅ ${route} - OK`);

      } catch (error) {
        errors.push({
          type: 'navigation',
          message: error instanceof Error ? error.message : String(error),
          url: `http://localhost:3001${route}`
        });
        console.log(`❌ ${route} - ERROR: ${error}`);
      }
    }

    // Report results
    console.log('\n=== ERROR SUMMARY ===');
    if (errors.length === 0) {
      console.log('🎉 No critical errors found!');
    } else {
      console.log(`Found ${errors.length} errors:`);
      errors.forEach((error, i) => {
        console.log(`${i + 1}. ${error.url} - ${error.type}: ${error.message}`);
      });
    }

    // Fail test if critical errors exist
    const criticalErrors = errors.filter(e => e.type === 'page' || e.type === 'navigation');
    if (criticalErrors.length > 0) {
      throw new Error(`Found ${criticalErrors.length} critical errors that need fixing`);
    }
  });
});
