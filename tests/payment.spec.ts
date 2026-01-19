import { test, expect } from '@playwright/test'

test.describe('PhonePe Payment Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Complete onboarding up to payment
    await completeOnboardingUntilPayment(page)
  })

  test('successful payment flow', async ({ page }) => {
    // Initiate payment
    await page.click('button:has-text("Pay ₹1,499")')
    
    // Verify PhonePe redirect
    await expect(page).toHaveURL(/phonepe/)
    
    // Complete test payment
    await page.fill('input[name="mobileNumber"]', '9999999999')
    await page.click('button:has-text("Pay")')
    
    // Handle OTP if needed
    if (await page.isVisible('input[name="otp"]')) {
      await page.fill('input[name="otp"]', '123456')
      await page.click('button:has-text("Verify")')
    }
    
    // Verify redirect back
    await page.waitForURL('**/dashboard?welcome=true')
    await expect(page.locator('.toast-success')).toContainText('Payment successful')
  })

  test('payment failure handling', async ({ page }) => {
    // Mock payment failure
    await page.route('**/api/payments/initiate', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Payment gateway error' })
      })
    })
    
    await page.click('button:has-text("Pay ₹1,499")')
    await expect(page.locator('.error-message')).toContainText('Payment failed')
  })

  test('payment verification after redirect', async ({ page }) => {
    // Mock payment verification
    await page.route('**/api/payments/verify', route => {
      route.fulfill({
        status: 200,
        body: JSON.stringify({ success: true })
      })
    })
    
    // Simulate returning from PhonePe
    await page.goto('/onboarding/payment?status=success&transactionId=test_txn_123')
    
    // Should redirect to dashboard
    await page.waitForURL('**/dashboard')
    await expect(page.locator('h1')).toContainText('Dashboard')
  })

  test('order summary displays correct pricing', async ({ page }) => {
    // Check monthly pricing
    await expect(page.locator('text=₹1,499/month')).toBeVisible()
    
    // Switch to yearly
    await page.click('button:has-text("Yearly")')
    
    // Check yearly pricing
    await expect(page.locator('text=₹14,990/year')).toBeVisible()
    await expect(page.locator('text=Billed as ₹14,990 per year')).toBeVisible()
    await expect(page.locator('text=₹1,249/month')).toBeVisible()
  })

  test('payment retry flow', async ({ page }) => {
    // Mock failed payment
    await page.route('**/api/payments/verify', route => {
      route.fulfill({
        status: 200,
        body: JSON.stringify({ success: false, error: 'Payment declined' })
      })
    })
    
    // Return from failed payment
    await page.goto('/onboarding/payment?status=failure&transactionId=test_txn_123')
    
    // Should show error and retry option
    await expect(page.locator('.error-message')).toContainText('Payment declined')
    await expect(page.locator('button:has-text("Try Again")')).toBeVisible()
    
    // Retry payment
    await page.click('button:has-text("Try Again")')
    await expect(page).toHaveURL(/phonepe/)
  })
})

async function completeOnboardingUntilPayment(page: any) {
  await page.goto('/')
  await page.click('[data-testid="auth-button"]')
  await page.click('button:has-text("Continue with Google")')
  
  // Handle Google login
  await page.fill('input[type="email"]', 'rhudhreshr@gmail.com')
  await page.click('button:has-text("Next")')
  await page.fill('input[type="password"]', process.env.GMAIL_PASSWORD!)
  await page.click('button:has-text("Next")')
  
  // Complete onboarding steps
  await page.fill('input#workspace-name', 'Payment Test Workspace')
  await page.click('button:has-text("Create Workspace")')
  
  await page.waitForSelector('text=Storage ready!')
  await page.click('[data-testid="plan-pro"]')
  await page.click('button:has-text("Continue to Payment")')
  
  await page.waitForURL('**/onboarding/payment')
}
