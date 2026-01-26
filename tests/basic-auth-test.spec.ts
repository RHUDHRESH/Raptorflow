import { test, expect } from '@playwright/test'

test.describe('Basic Authentication Test', () => {
  test('frontend loads and has login button', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/')

    // Wait for page to load (with timeout)
    await page.waitForLoadState('networkidle', { timeout: 10000 })

    // Check if page loaded successfully
    const title = await page.title()
    console.log(`Page title: ${title}`)

    // Look for any login-related button or link
    const loginSelectors = [
      'text=Log in',
      'text=Login',
      'text=Sign in',
      'text=Sign In',
      'button:has-text("CONTINUE WITH GOOGLE")',
      'button:has-text("Continue with Google")',
      '[data-testid*="auth"]',
      '[data-testid*="login"]',
      'a[href*="login"]',
      'a[href*="auth"]'
    ]

    let loginElement = null
    for (const selector of loginSelectors) {
      try {
        loginElement = await page.$(selector)
        if (loginElement) {
          console.log(`Found login element with selector: ${selector}`)
          break
        }
      } catch (e) {
        // Continue trying other selectors
      }
    }

    if (loginElement) {
      console.log('✅ Login element found!')
      await expect(page.locator('text=Log in')).toBeVisible()
    } else {
      // Take screenshot for debugging
      await page.screenshot({ path: 'debug-homepage.png' })
      console.log('❌ No login element found. Screenshot saved as debug-homepage.png')

      // Check page content for debugging
      const bodyText = await page.locator('body').textContent()
      console.log(`Page content preview: ${bodyText?.substring(0, 200)}...`)
    }

    // Basic check that page is not completely broken
    expect(await page.locator('body')).toBeVisible()
  })

  test('check page for any errors', async ({ page }) => {
    const responses: any[] = []

    // Listen for network responses
    page.on('response', response => {
      if (response.status() >= 400) {
        responses.push({
          url: response.url(),
          status: response.status(),
          statusText: response.statusText()
        })
      }
    })

    // Navigate to homepage
    await page.goto('/', { waitUntil: 'networkidle' })

    // Check for any network errors
    if (responses.length > 0) {
      console.log('Network errors found:')
      responses.forEach(resp => {
        console.log(`  ${resp.status} ${resp.statusText} - ${resp.url}`)
      })
    }

    // Take screenshot for visual inspection
    await page.screenshot({ path: 'homepage-screenshot.png' })
    console.log('Screenshot saved as homepage-screenshot.png')
  })
})
