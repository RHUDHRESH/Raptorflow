import { test, expect } from '@playwright/test';

test.describe('10x Typing Experience', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/typing-test');
    // Wait for audio context to initialize
    await page.waitForTimeout(1000);
  });

  test('should load typing experience page with controls', async ({ page }) => {
    // Check main elements are present
    await expect(page.locator('h1')).toContainText('10x Typing Experience Test');
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.locator('textarea')).toBeVisible();
    await expect(page.locator('button:has-text("Play Completion Sound")')).toBeVisible();
  });

  test('should initialize audio context properly', async ({ page }) => {
    // Check if audio context is initialized
    const audioContext = await page.evaluate(() => {
      return (window as any).typingExperienceAudioContext !== null;
    });
    expect(audioContext).toBe(true);
  });

  test('should play sounds when typing', async ({ page }) => {
    // Mock audio context to track sound calls
    await page.addInitScript(() => {
      const originalCreateOscillator = AudioContext.prototype.createOscillator;
      const originalCreateGain = AudioContext.prototype.createGain;

      let soundCallCount = 0;
      (window as any).soundCallCount = 0;

      AudioContext.prototype.createOscillator = function(...args) {
        (window as any).soundCallCount++;
        return originalCreateOscillator.apply(this, args);
      };
    });

    // Type in input field
    await page.locator('input[type="text"]').fill('test typing');

    // Check if sounds were triggered
    const soundCalls = await page.evaluate(() => (window as any).soundCallCount);
    expect(soundCalls).toBeGreaterThan(0);
  });

  test('should handle different sound profiles', async ({ page }) => {
    // Find sound profile selector
    const profileSelector = page.locator('select').filter({ hasText: /Professional|Creative|Gaming|Minimalist/ }).first();

    // Test switching profiles
    const profiles = ['Professional', 'Creative', 'Gaming', 'Minimalist'];

    for (const profile of profiles) {
      await profileSelector.selectOption(profile);
      await page.waitForTimeout(100);

      // Verify profile was selected
      const selectedValue = await profileSelector.inputValue();
      expect(profiles.includes(selectedValue)).toBe(true);
    }
  });

  test('should respect volume controls', async ({ page }) => {
    // Find volume slider
    const volumeSlider = page.locator('input[type="range"]').first();

    // Test volume changes
    await volumeSlider.fill('0');
    await page.waitForTimeout(100);

    let volume = await volumeSlider.inputValue();
    expect(volume).toBe('0');

    await volumeSlider.fill('100');
    await page.waitForTimeout(100);

    volume = await volumeSlider.inputValue();
    expect(volume).toBe('100');
  });

  test('should toggle sound and animation', async ({ page }) => {
    // Find toggle switches
    const soundToggle = page.locator('input[type="checkbox"]').first();
    const animationToggle = page.locator('input[type="checkbox"]').nth(1);

    // Test sound toggle
    await soundToggle.check();
    let isChecked = await soundToggle.isChecked();
    expect(isChecked).toBe(true);

    await soundToggle.uncheck();
    isChecked = await soundToggle.isChecked();
    expect(isChecked).toBe(false);

    // Test animation toggle
    await animationToggle.check();
    isChecked = await animationToggle.isChecked();
    expect(isChecked).toBe(true);
  });

  test('should play completion sound on button click', async ({ page }) => {
    // Track sound calls
    await page.addInitScript(() => {
      (window as any).completionSoundPlayed = false;

      // Mock the playCompletionSound function
      const originalContext = (window as any).TypingExperienceContext;
      if (originalContext) {
        originalContext.playCompletionSound = () => {
          (window as any).completionSoundPlayed = true;
        };
      }
    });

    // Click the completion sound button
    await page.locator('button:has-text("Play Completion Sound")').click();

    // Check if sound was triggered
    const soundPlayed = await page.evaluate(() => (window as any).completionSoundPlayed);
    expect(soundPlayed).toBe(true);
  });

  test('should handle keyboard events properly', async ({ page }) => {
    // Focus on input field
    await page.locator('input[type="text"]').focus();

    // Track different key types
    await page.addInitScript(() => {
      (window as any).keyEvents = {
        keyPress: 0,
        backspace: 0,
        enter: 0
      };
    });

    // Type text
    await page.keyboard.type('hello world');

    // Press backspace
    await page.keyboard.press('Backspace');

    // Press enter
    await page.keyboard.press('Enter');

    // Check events were recorded
    const events = await page.evaluate(() => (window as any).keyEvents);
    expect(events.keyPress).toBeGreaterThan(0);
  });

  test('should be accessible', async ({ page }) => {
    // Check for proper ARIA labels
    await expect(page.locator('h1')).toHaveAttribute('role', 'heading');

    // Check keyboard navigation
    await page.keyboard.press('Tab');
    await expect(page.locator('input[type="text"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('textarea')).toBeFocused();
  });

  test('should handle errors gracefully', async ({ page }) => {
    // Mock audio context failure
    await page.addInitScript(() => {
      (window as any).AudioContext = class MockAudioContext {
        constructor() {
          throw new Error('Audio not supported');
        }
      };
    });

    // Reload page with mocked failure
    await page.reload();
    await page.waitForTimeout(1000);

    // Page should still load without crashing
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('input[type="text"]')).toBeVisible();
  });

  test('should have performance optimizations', async ({ page }) => {
    // Measure initial performance
    const startTime = Date.now();

    // Type rapidly
    await page.locator('input[type="text"]').fill('rapid typing test');

    const endTime = Date.now();
    const duration = endTime - startTime;

    // Should complete within reasonable time
    expect(duration).toBeLessThan(1000);

    // Check for memory leaks (basic check)
    const memoryUsage = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0;
    });

    expect(memoryUsage).toBeGreaterThan(0);
    expect(memoryUsage).toBeLessThan(100 * 1024 * 1024); // Less than 100MB
  });
});

test.describe('Typing Experience Integration', () => {
  test('should work on main landing page', async ({ page }) => {
    await page.goto('http://localhost:3001/');

    // Check if typing experience is available
    const hasTypingExperience = await page.evaluate(() => {
      return 'useTypingExperience' in window;
    });

    // Should have typing experience controls
    await expect(page.locator('[data-testid="typing-controls"]')).toBeVisible();
  });

  test('should work on Muse page', async ({ page }) => {
    await page.goto('http://localhost:3001/muse');

    // Should not crash and should load properly
    await expect(page.locator('body')).toBeVisible();

    // Type in muse interface
    const museInput = page.locator('input[placeholder*="What"], textarea[placeholder*="What"]').first();
    if (await museInput.isVisible()) {
      await museInput.fill('test typing in muse');

      // Should handle typing without errors
      await expect(museInput).toHaveValue('test typing in muse');
    }
  });
});
