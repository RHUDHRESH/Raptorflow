import { test as base, expect } from '@playwright/test'

// Define test fixtures
export const test = base.extend({
  // Authenticated page fixture
  authenticatedPage: async ({ page }, use) => {
    // Complete authentication
    await page.goto('/login')
    await page.click('button:has-text("Continue with Google")')
    
    // Handle Google OAuth
    await page.fill('input[type="email"]', 'rhudhreshr@gmail.com')
    await page.click('button:has-text("Next")')
    await page.fill('input[type="password"]', process.env.GMAIL_PASSWORD!)
    await page.click('button:has-text("Next")')
    
    // Wait for redirect
    await page.waitForURL('**/dashboard')
    await use(page)
  },
  
  // Test user fixture
  testUser: async ({ page }, use) => {
    // Create test user via API
    const response = await page.request.post('/api/test/create-user', {
      data: {
        email: 'test@example.com',
        password: 'testpassword123'
      }
    })
    const userData = await response.json()
    await use(userData)
  }
})

export { expect }
