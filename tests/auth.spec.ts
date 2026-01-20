import { test, expect } from '@playwright/test'

test.describe('Authentication & Onboarding', () => {
  test.beforeEach(async ({ page, request }) => {
    // Clear cookies and localStorage before each test
    await page.context().clearCookies()
    await page.goto('/')
    await page.evaluate(() => localStorage.clear())

    // Reset test user state
    await request.post('/api/test/reset-user', {
      data: { email: 'rhudhreshr@gmail.com' }
    })
  })

  test('complete user journey with real payment', async ({ page }) => {
    // Step 1: Navigate to app
    await page.goto('/')
    
    // Step 2: Click login/register
    await page.click('text=Log in')
    
    // Step 3: Login with Gmail
    await page.click('button:has-text("CONTINUE WITH GOOGLE")')
    
    // Step 4: Wait for redirect to onboarding (Mock Login auto-redirects)
    await page.waitForURL('**/onboarding')
    await expect(page.locator('h1')).toContainText('Create Your Workspace')
    
    // Step 7: Create workspace
    const workspaceName = `Test Workspace ${Date.now()}`
    await page.fill('input#workspace-name', workspaceName)
    await page.click('button:has-text("Create Workspace")')
    
    // Step 8: Wait for storage setup
    await page.waitForURL('**/onboarding/storage')
    await expect(page.locator('text=Storage ready!')).toBeVisible({ timeout: 30000 })
    
    // Step 9: Select plan
    await page.waitForURL('**/onboarding/plans')
    await page.click('[data-testid="plan-pro"]')
    await page.click('button:has-text("Continue to Payment")')
    
    // Step 10: Complete payment
    await page.waitForURL('**/onboarding/payment')
    await page.click('button:has-text("Pay")')
    
    // Step 11: Handle PhonePe redirect
    await page.waitForURL('**://phonepe**')
    await completePhonePePayment(page)
    
    // Step 12: Verify success
    await page.waitForURL('**/dashboard')
    await expect(page.locator('h1')).toContainText('Dashboard')
    
    // Step 13: Verify subscription active
    await page.click('[data-testid="account-menu"]')
    await page.click('a:has-text("Billing")')
    await expect(page.locator('text=Active Subscription')).toBeVisible()
  })

  test('login redirects existing user to dashboard', async ({ page }) => {
    // First, create a user and complete onboarding
    await createTestUser(page)
    
    // Logout
    await page.click('[data-testid="user-menu"]')
    await page.click('button:has-text("Sign out")')
    
    // Login again
    await page.goto('/login')
    await page.click('button:has-text("CONTINUE WITH GOOGLE")')
    
    // Should redirect to dashboard
    await page.waitForURL('**/dashboard')
    await expect(page.locator('h1')).toContainText('Dashboard')
  })

  test('onboarding progress is persistent', async ({ page }) => {
    // Start onboarding
    await page.goto('/')
    await page.click('text=Log in')
    await page.click('button:has-text("CONTINUE WITH GOOGLE")')
    
    // Complete workspace step
    await page.fill('input#workspace-name', 'Persistent Test')
    await page.click('button:has-text("Create Workspace")')
    
    // Reload page
    await page.reload()
    
    // Should be on storage step
    await page.waitForURL('**/onboarding/storage')
    await expect(page.locator('h1')).toContainText('Setting Up Your Storage')
  })

  test('invalid onboarding states redirect correctly', async ({ page }) => {
    // Create a user with pending_payment status
    await createTestUserWithStatus(page, 'pending_payment')
    
    // Try to access workspace creation
    await page.goto('/onboarding')
    
    // Should redirect to payment
    await page.waitForURL('**/onboarding/payment')
    await expect(page.locator('h1')).toContainText('Complete Your Purchase')
  })
})

async function completePhonePePayment(page: any) {
  // Complete payment in PhonePe UI
  await page.fill('input[name="mobileNumber"]', '9999999999')
  await page.click('button:has-text("Pay")')
  
  if (await page.isVisible('input[name="otp"]')) {
    await page.fill('input[name="otp"]', '123456')
    await page.click('button:has-text("Verify")')
  }
}

async function createTestUser(page: any) {
  // Helper to create a test user with completed onboarding
  await page.goto('/')
  await page.click('text=Log in')
  await page.click('button:has-text("CONTINUE WITH GOOGLE")')
  
  // Complete all onboarding steps
  await page.fill('input#workspace-name', `Test ${Date.now()}`)
  await page.click('button:has-text("Create Workspace")')
  
  await page.waitForSelector('text=Storage ready!')
  await page.click('[data-testid="plan-starter"]')
  await page.click('button:has-text("Continue to Payment")')
  
  // Mock successful payment
  await page.route('**/api/payments/initiate', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({
        redirectUrl: `${process.env.NEXT_PUBLIC_APP_URL}/onboarding/payment?status=success&transactionId=test_txn`,
        transactionId: 'test_txn'
      })
    })
  })
  
  await page.click('button:has-text("Pay")')
  await page.waitForURL('**/dashboard')
}

async function createTestUserWithStatus(page: any, status: string) {
  // Create user with specific status via API
  await page.evaluate(async ({ status }) => {
    const response = await fetch('/api/test/create-user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    })
    return response.json()
  }, { status })
}
