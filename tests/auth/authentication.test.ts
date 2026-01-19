import { describe, it, expect, beforeEach, afterEach } from '@playwright/test';
import { chromium, type Browser, type Page } from '@playwright/test';

describe('Authentication System Tests', () => {
  let browser: Browser;
  let page: Page;
  const baseUrl = process.env.TEST_BASE_URL || 'http://localhost:3000';

  beforeEach(async () => {
    browser = await chromium.launch({ headless: false });
    page = await browser.newPage();
  });

  afterEach(async () => {
    await browser.close();
  });

  describe('Login Page', () => {
    it('should load login page successfully', async () => {
      await page.goto(`${baseUrl}/login`);
      await expect(page).toHaveTitle(/RaptorFlow/);
      await expect(page.locator('h1')).toContainText('Sign In');
    });

    it('should show validation errors for empty fields', async () => {
      await page.goto(`${baseUrl}/login`);
      await page.click('button[type="submit"]');
      
      // Check for validation errors
      const emailError = page.locator('text=Email is required');
      const passwordError = page.locator('text=Password is required');
      
      await expect(emailError.or(passwordError)).toBeVisible();
    });

    it('should show error for invalid credentials', async () => {
      await page.goto(`${baseUrl}/login`);
      
      await page.fill('input[name="email"]', 'invalid@test.com');
      await page.fill('input[name="password"]', 'wrongpassword');
      await page.click('button[type="submit"]');
      
      // Wait for error message
      await expect(page.locator('text=Invalid credentials')).toBeVisible({ timeout: 5000 });
    });

    it('should login successfully with valid credentials', async () => {
      await page.goto(`${baseUrl}/login`);
      
      await page.fill('input[name="email"]', 'rhudhreshr@gmail.com');
      await page.fill('input[name="password"]', 'TestPassword123');
      await page.click('button[type="submit"]');
      
      // Should redirect to dashboard
      await expect(page).toHaveURL(`${baseUrl}/dashboard`);
      await expect(page.locator('text=Welcome back')).toBeVisible();
    });
  });

  describe('Signup Page', () => {
    it('should load signup page successfully', async () => {
      await page.goto(`${baseUrl}/signup`);
      await expect(page).toHaveTitle(/RaptorFlow/);
      await expect(page.locator('h1')).toContainText('Create Account');
    });

    it('should validate required fields', async () => {
      await page.goto(`${baseUrl}/signup`);
      await page.click('button[type="submit"]');
      
      const nameError = page.locator('text=Full name is required');
      const emailError = page.locator('text=Email is required');
      const passwordError = page.locator('text=Password is required');
      
      await expect(nameError.or(emailError).or(passwordError)).toBeVisible();
    });

    it('should validate email format', async () => {
      await page.goto(`${baseUrl}/signup`);
      
      await page.fill('input[name="fullName"]', 'Test User');
      await page.fill('input[name="email"]', 'invalid-email');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');
      
      await expect(page.locator('text=Invalid email format')).toBeVisible();
    });

    it('should validate password strength', async () => {
      await page.goto(`${baseUrl}/signup`);
      
      await page.fill('input[name="fullName"]', 'Test User');
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', '123');
      await page.click('button[type="submit"]');
      
      await expect(page.locator('text=Password must be at least 8 characters')).toBeVisible();
    });
  });

  describe('Forgot Password Flow', () => {
    it('should load forgot password page', async () => {
      await page.goto(`${baseUrl}/forgot-password`);
      await expect(page.locator('h1')).toContainText('Forgot Password');
    });

    it('should validate email input', async () => {
      await page.goto(`${baseUrl}/forgot-password`);
      await page.click('button[type="submit"]');
      
      await expect(page.locator('text=Email is required')).toBeVisible();
    });

    it('should send reset email for valid email', async () => {
      await page.goto(`${baseUrl}/forgot-password`);
      
      await page.fill('input[name="email"]', 'rhudhreshr@gmail.com');
      await page.click('button[type="submit"]');
      
      await expect(page.locator('text=Password reset instructions have been sent')).toBeVisible({ timeout: 10000 });
    });

    it('should show error for invalid email', async () => {
      await page.goto(`${baseUrl}/forgot-password`);
      
      await page.fill('input[name="email"]', 'nonexistent@test.com');
      await page.click('button[type="submit"]');
      
      await expect(page.locator('text=Email not found')).toBeVisible({ timeout: 5000 });
    });
  });

  describe('Password Reset Flow', () => {
    it('should validate reset token', async () => {
      const invalidToken = 'invalid-token-123';
      await page.goto(`${baseUrl}/auth/reset-password?token=${invalidToken}`);
      
      await expect(page.locator('text=Invalid or expired reset link')).toBeVisible();
    });

    it('should reset password with valid token', async () => {
      // First, get a valid token by requesting password reset
      await page.goto(`${baseUrl}/forgot-password`);
      await page.fill('input[name="email"]', 'rhudhreshr@gmail.com');
      await page.click('button[type="submit"]');
      
      // Wait for email to be sent (in real scenario, you'd extract token from email)
      await page.waitForTimeout(2000);
      
      // For testing, we'll use a mock token scenario
      // In real implementation, you'd need to extract the token from the email
      const validToken = 'test-reset-token-123';
      await page.goto(`${baseUrl}/auth/reset-password?token=${validToken}`);
      
      // Fill reset form
      await page.fill('input[name="password"]', 'NewPassword123');
      await page.fill('input[name="confirmPassword"]', 'NewPassword123');
      await page.click('button[type="submit"]');
      
      await expect(page.locator('text=Password reset successful')).toBeVisible({ timeout: 5000 });
    });

    it('should validate password confirmation', async () => {
      const validToken = 'test-reset-token-123';
      await page.goto(`${baseUrl}/auth/reset-password?token=${validToken}`);
      
      await page.fill('input[name="password"]', 'NewPassword123');
      await page.fill('input[name="confirmPassword"]', 'DifferentPassword');
      await page.click('button[type="submit"]');
      
      await expect(page.locator('text=Passwords do not match')).toBeVisible();
    });
  });

  describe('Security Tests', () => {
    it('should have security headers', async () => {
      const response = await page.goto(`${baseUrl}/login`);
      const headers = await response?.headers();
      
      expect(headers?.['x-frame-options']).toBe('DENY');
      expect(headers?.['x-content-type-options']).toBe('nosniff');
      expect(headers?.['x-xss-protection']).toContain('1; mode=block');
    });

    it('should prevent brute force attacks', async () => {
      await page.goto(`${baseUrl}/login`);
      
      // Attempt multiple failed logins
      for (let i = 0; i < 5; i++) {
        await page.fill('input[name="email"]', 'test@test.com');
        await page.fill('input[name="password"]', 'wrongpassword');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(1000);
      }
      
      // Should show rate limiting message
      await expect(page.locator('text=Too many attempts')).toBeVisible({ timeout: 5000 });
    });

    it('should sanitize input to prevent XSS', async () => {
      await page.goto(`${baseUrl}/login`);
      
      const xssPayload = '<script>alert("XSS")</script>';
      await page.fill('input[name="email"]', xssPayload);
      await page.fill('input[name="password"]', 'password123');
      await page.click('button[type="submit"]');
      
      // Should not execute script and show validation error
      await expect(page.locator('text=Invalid email format')).toBeVisible();
      
      // Check that no alert was triggered
      const alerts = page.context().alertMessages();
      expect(alerts).toHaveLength(0);
    });
  });

  describe('Performance Tests', () => {
    it('should load pages within performance budget', async () => {
      const pages = ['/login', '/signup', '/forgot-password'];
      
      for (const pagePath of pages) {
        const startTime = Date.now();
        await page.goto(`${baseUrl}${pagePath}`);
        await page.waitForLoadState('networkidle');
        const loadTime = Date.now() - startTime;
        
        expect(loadTime).toBeLessThan(3000); // 3 second budget
      }
    });

    it('should handle concurrent users', async () => {
      const concurrentUsers = 5;
      const pages: Page[] = [];
      
      // Create multiple pages
      for (let i = 0; i < concurrentUsers; i++) {
        pages.push(await browser.newPage());
      }
      
      // Simulate concurrent login attempts
      const loginPromises = pages.map(async (userPage, index) => {
        await userPage.goto(`${baseUrl}/login`);
        await userPage.fill('input[name="email"]', `user${index}@test.com`);
        await userPage.fill('input[name="password"]', 'password123');
        return userPage.click('button[type="submit"]');
      });
      
      await Promise.all(loginPromises);
      
      // Clean up
      for (const userPage of pages) {
        await userPage.close();
      }
    });
  });

  describe('Accessibility Tests', () => {
    it('should have proper semantic HTML', async () => {
      await page.goto(`${baseUrl}/login`);
      
      // Check for proper heading hierarchy
      const h1 = page.locator('h1');
      await expect(h1).toBeVisible();
      
      // Check for proper form labels
      const emailLabel = page.locator('label[for="email"]');
      const passwordLabel = page.locator('label[for="password"]');
      await expect(emailLabel).toBeVisible();
      await expect(passwordLabel).toBeVisible();
      
      // Check for proper button types
      const submitButton = page.locator('button[type="submit"]');
      await expect(submitButton).toBeVisible();
    });

    it('should be keyboard navigable', async () => {
      await page.goto(`${baseUrl}/login`);
      
      // Tab through form elements
      await page.keyboard.press('Tab');
      await expect(page.locator('input[name="email"]')).toBeFocused();
      
      await page.keyboard.press('Tab');
      await expect(page.locator('input[name="password"]')).toBeFocused();
      
      await page.keyboard.press('Tab');
      await expect(page.locator('button[type="submit"]')).toBeFocused();
    });

    it('should have sufficient color contrast', async () => {
      await page.goto(`${baseUrl}/login`);
      
      // Check button contrast
      const button = page.locator('button[type="submit"]');
      const buttonStyles = await button.evaluate((el) => {
        const styles = window.getComputedStyle(el);
        return {
          color: styles.color,
          backgroundColor: styles.backgroundColor
        };
      });
      
      // Basic contrast check (would need more sophisticated testing in real scenario)
      expect(buttonStyles.color).not.toBe(buttonStyles.backgroundColor);
    });
  });

  describe('API Tests', () => {
    it('should handle forgot password API correctly', async () => {
      const response = await page.request.post(`${baseUrl}/api/auth/forgot-password`, {
        data: { email: 'test@example.com' }
      });
      
      expect(response.status()).toBe(200);
      const responseBody = await response.json();
      expect(responseBody).toHaveProperty('message');
    });

    it('should validate API input', async () => {
      const response = await page.request.post(`${baseUrl}/api/auth/forgot-password`, {
        data: {}
      });
      
      expect(response.status()).toBe(400);
      const responseBody = await response.json();
      expect(responseBody).toHaveProperty('error');
    });

    it('should handle reset token validation', async () => {
      const response = await page.request.post(`${baseUrl}/api/auth/validate-reset-token-simple`, {
        data: { token: 'invalid-token' }
      });
      
      expect(response.status()).toBe(400);
      const responseBody = await response.json();
      expect(responseBody).toHaveProperty('valid', false);
    });
  });
});
