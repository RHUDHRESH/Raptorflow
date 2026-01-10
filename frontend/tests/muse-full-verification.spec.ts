import { test, expect } from '@playwright/test';

test.describe('Muse App - Full Feature Verification', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/muse');
    // Wait for the app to load
    await page.waitForSelector('[data-testid="muse-app"]', { timeout: 10000 });
  });

  test('1. Topic selector dropdown functionality', async ({ page }) => {
    // Test topic selector exists and opens
    await page.click('[data-testid="topic-selector"]');
    await expect(page.locator('[data-testid="topic-dropdown"]')).toBeVisible();

    // Test selecting a topic
    await page.click('[data-testid="topic-option"]:first-child');
    await expect(page.locator('[data-testid="selected-topic"]')).toContainText('selected');
  });

  test('2. Tag/type filter functionality', async ({ page }) => {
    // Test filter dropdown exists
    await page.click('[data-testid="filter-dropdown"]');
    await expect(page.locator('[data-testid="filter-options"]')).toBeVisible();

    // Test filtering by type
    await page.click('[data-testid="filter-type-email"]');
    await expect(page.locator('[data-testid="asset-card"]')).toHaveCount(0); // Assuming no email assets initially

    // Test tag pills
    await page.click('[data-testid="tag-pill"]:first-child');
    await expect(page.locator('[data-testid="active-filter"]')).toBeVisible();
  });

  test('3. Delete asset and bulk operations', async ({ page }) => {
    // First create an asset to delete
    await page.fill('[data-testid="command-input"]', 'Create a test asset');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Test individual delete
    await page.hover('[data-testid="asset-card"]:first-child');
    await page.click('[data-testid="delete-asset"]');
    await expect(page.locator('[data-testid="delete-modal"]')).toBeVisible();
    await page.click('[data-testid="confirm-delete"]');

    // Test bulk mode
    await page.click('[data-testid="bulk-mode-toggle"]');
    await expect(page.locator('[data-testid="bulk-controls"]')).toBeVisible();
    await page.click('[data-testid="select-all"]');
    await expect(page.locator('[data-testid="bulk-delete"]')).toBeEnabled();
  });

  test('4. Asset search functionality', async ({ page }) => {
    // Test search input exists
    await page.fill('[data-testid="search-input"]', 'test');
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();

    // Test real-time filtering
    await page.fill('[data-testid="search-input"]', 'nonexistent');
    await expect(page.locator('[data-testid="no-results"]')).toBeVisible();
  });

  test('5. Empty state CTA', async ({ page }) => {
    // Clear all assets first
    await page.click('[data-testid="bulk-mode-toggle"]');
    await page.click('[data-testid="select-all"]');
    await page.click('[data-testid="bulk-delete"]');
    await page.click('[data-testid="confirm-delete"]');

    // Test empty state
    await expect(page.locator('[data-testid="empty-state"]')).toBeVisible();
    await expect(page.locator('[data-testid="cta-input"]')).toBeFocused();
  });

  test('6. Keyboard shortcuts', async ({ page }) => {
    // Test Ctrl+K focuses input
    await page.keyboard.press('Control+k');
    await expect(page.locator('[data-testid="command-input"]')).toBeFocused();

    // Test Ctrl+E exports
    const downloadPromise = page.waitForEvent('download');
    await page.keyboard.press('Control+e');
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toContain('muse-export');

    // Test Escape closes modals
    await page.click('[data-testid="topic-selector"]');
    await page.keyboard.press('Escape');
    await expect(page.locator('[data-testid="topic-dropdown"]')).toBeHidden();
  });

  test('7. Versioning and history', async ({ page }) => {
    // Create an asset first
    await page.fill('[data-testid="command-input"]', 'Create a versioned asset');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(2000);

    // Open asset editor
    await page.click('[data-testid="asset-card"]:first-child');
    await expect(page.locator('[data-testid="asset-editor"]')).toBeVisible();

    // Test versioning tabs
    await page.click('[data-testid="history-tab"]');
    await expect(page.locator('[data-testid="version-list"]')).toBeVisible();

    // Create a new version
    await page.click('[data-testid="edit-tab"]');
    await page.fill('[data-testid="content-textarea"]', 'Updated content');
    await page.click('[data-testid="save-button"]');

    // Verify version was created
    await page.click('[data-testid="history-tab"]');
    await expect(page.locator('[data-testid="version-item"]')).toHaveCount(2);
  });

  test('8. Tone/length presets', async ({ page }) => {
    // Open asset editor
    await page.click('[data-testid="asset-card"]:first-child');
    await expect(page.locator('[data-testid="asset-editor"]')).toBeVisible();

    // Test tone presets
    await page.click('[data-testid="tone-confident"]');
    await expect(page.locator('[data-testid="content-textarea"]')).toContainText('[Tone: Confident]');

    // Test length presets
    await page.click('[data-testid="length-expand"]');
    await expect(page.locator('[data-testid="content-textarea"]')).toContainText('[Length: Expand]');
  });

  test('9. Persona brief functionality', async ({ page }) => {
    // Test persona brief bar
    await expect(page.locator('[data-testid="persona-brief-bar"]')).toBeVisible();

    // Open persona modal
    await page.click('[data-testid="edit-persona"]');
    await expect(page.locator('[data-testid="persona-modal"]')).toBeVisible();

    // Fill persona form
    await page.fill('[data-testid="audience-input"]', 'Enterprise CTOs');
    await page.fill('[data-testid="voice-input"]', 'Confident & authoritative');
    await page.fill('[data-testid="goal-input"]', 'Increase adoption');
    await page.click('[data-testid="add-goal"]');
    await page.click('[data-testid="save-persona"]');

    // Verify persona is saved
    await expect(page.locator('[data-testid="persona-brief-bar"]')).toContainText('Enterprise CTOs');
  });

  test('10. Export formats', async ({ page }) => {
    // Test export dropdown
    await page.click('[data-testid="export-dropdown"]');
    await expect(page.locator('[data-testid="export-options"]')).toBeVisible();

    // Test different export formats
    const formats = ['markdown', 'pdf', 'html', 'csv'];
    for (const format of formats) {
      const downloadPromise = page.waitForEvent('download');
      await page.click(`[data-testid="export-${format}"]`);
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toContain(format);
    }
  });

  test('11. Collaboration indicators', async ({ page }) => {
    // Test collaboration status (mock implementation)
    await expect(page.locator('[data-testid="collaboration-status"]')).toBeVisible();
    await expect(page.locator('[data-testid="active-users"]')).toBeVisible();
  });

  test('12. Undo/redo functionality', async ({ page }) => {
    // Open asset editor
    await page.click('[data-testid="asset-card"]:first-child');
    await expect(page.locator('[data-testid="asset-editor"]')).toBeVisible();

    // Make some changes
    const textarea = page.locator('[data-testid="content-textarea"]');
    await textarea.fill('Original content');
    await textarea.fill('Modified content');

    // Test undo
    await page.keyboard.press('Control+z');
    await expect(textarea).toHaveValue('Original content');

    // Test redo
    await page.keyboard.press('Control+Shift+z');
    await expect(textarea).toHaveValue('Modified content');
  });

  test('13. Asset templates gallery', async ({ page }) => {
    // Open templates gallery
    await page.click('[data-testid="templates-button"]');
    await expect(page.locator('[data-testid="templates-gallery"]')).toBeVisible();

    // Test template selection
    await page.click('[data-testid="template-card"]:first-child');
    await expect(page.locator('[data-testid="template-preview"]')).toBeVisible();

    // Apply template
    await page.click('[data-testid="apply-template"]');
    await expect(page.locator('[data-testid="content-textarea"]')).not.toBeEmpty();
  });

  test('14. Analytics sidebar', async ({ page }) => {
    // Open analytics
    await page.click('[data-testid="analytics-button"]');
    await expect(page.locator('[data-testid="analytics-sidebar"]')).toBeVisible();

    // Test analytics components
    await expect(page.locator('[data-testid="word-count-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="generation-frequency"]')).toBeVisible();
    await expect(page.locator('[data-testid="top-tags"]')).toBeVisible();
  });

  test('15. Voice input', async ({ page }) => {
    // Test voice input button
    await expect(page.locator('[data-testid="voice-input-button"]')).toBeVisible();

    // Note: Actual voice recording testing requires microphone permissions
    // This tests the UI elements only
    await page.click('[data-testid="voice-input-button"]');
    await expect(page.locator('[data-testid="voice-recording-indicator"]')).toBeVisible();
    await page.click('[data-testid="stop-recording"]');
  });

  test('16. File import', async ({ page }) => {
    // Test file import button
    await expect(page.locator('[data-testid="import-button"]')).toBeVisible();

    // Test file import dialog
    await page.click('[data-testid="import-button"]');
    await expect(page.locator('[data-testid="import-modal"]')).toBeVisible();

    // Test drag and drop area
    await expect(page.locator('[data-testid="drop-zone"]')).toBeVisible();
  });

  test('17. Theme toggle', async ({ page }) => {
    // Test theme toggle button
    await expect(page.locator('[data-testid="theme-toggle"]')).toBeVisible();

    // Test theme switching
    const htmlElement = page.locator('html');
    const initialTheme = await htmlElement.getAttribute('data-theme') || 'light';

    await page.click('[data-testid="theme-toggle"]');
    await expect(htmlElement).not.toHaveAttribute('data-theme', initialTheme);
  });

  test('18. Loading skeletons', async ({ page }) => {
    // Trigger loading state
    await page.fill('[data-testid="command-input"]', 'Generate a complex asset');
    await page.click('[data-testid="send-button"]');

    // Test skeleton states
    await expect(page.locator('[data-testid="loading-skeleton"]')).toBeVisible();
    await expect(page.locator('[data-testid="shimmer-effect"]')).toBeVisible();

    // Wait for completion
    await page.waitForSelector('[data-testid="asset-card"]', { timeout: 10000 });
    await expect(page.locator('[data-testid="loading-skeleton"]')).toBeHidden();
  });

  test('19. Onboarding tooltips', async ({ page }) => {
    // Test onboarding for first-time users
    await page.evaluate(() => {
      localStorage.removeItem('muse-onboarding-completed');
    });
    await page.reload();

    // Test tooltip visibility
    await expect(page.locator('[data-testid="onboarding-tooltip"]')).toBeVisible();
    await expect(page.locator('[data-testid="coach-mark"]')).toBeVisible();

    // Test tooltip navigation
    await page.click('[data-testid="next-tooltip"]');
    await expect(page.locator('[data-testid="tooltip-counter"]')).toContainText('2');

    // Complete onboarding
    await page.click('[data-testid="skip-onboarding"]');
    await expect(page.locator('[data-testid="onboarding-tooltip"]')).toBeHidden();
  });

  test('20. Settings panel', async ({ page }) => {
    // Open settings panel
    await page.click('[data-testid="settings-button"]');
    await expect(page.locator('[data-testid="settings-panel"]')).toBeVisible();

    // Test settings sections
    await expect(page.locator('[data-testid="auto-save-settings"]')).toBeVisible();
    await expect(page.locator('[data-testid="default-tone-settings"]')).toBeVisible();
    await expect(page.locator('[data-testid="shortcuts-settings"]')).toBeVisible();
    await expect(page.locator('[data-testid="export-preferences"]')).toBeVisible();

    // Test setting changes
    await page.click('[data-testid="auto-save-toggle"]');
    await expect(page.locator('[data-testid="save-indicator"]')).toBeVisible();
  });

  test('Integration test: Complete workflow', async ({ page }) => {
    // Test complete user workflow
    // 1. Set up persona
    await page.click('[data-testid="edit-persona"]');
    await page.fill('[data-testid="audience-input"]', 'Startup Founders');
    await page.fill('[data-testid="voice-input"]', 'Inspirational & direct');
    await page.fill('[data-testid="goal-input"]', 'Drive growth');
    await page.click('[data-testid="add-goal"]');
    await page.click('[data-testid="save-persona"]');

    // 2. Create asset with topic
    await page.click('[data-testid="topic-selector"]');
    await page.click('[data-testid="topic-growth"]');
    await page.fill('[data-testid="command-input"]', 'Create a growth strategy post');
    await page.click('[data-testid="send-button"]');
    await page.waitForTimeout(3000);

    // 3. Edit and refine asset
    await page.click('[data-testid="asset-card"]:first-child');
    await page.click('[data-testid="tone-confident"]');
    await page.click('[data-testid="save-button"]');

    // 4. Export in multiple formats
    await page.click('[data-testid="export-dropdown"]');
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-markdown"]');
    await downloadPromise;

    // 5. Verify version history
    await page.click('[data-testid="history-tab"]');
    await expect(page.locator('[data-testid="version-item"]')).toHaveCount(2);

    // 6. Test search and filter
    await page.click('[data-testid="close-editor"]');
    await page.fill('[data-testid="search-input"]', 'growth');
    await expect(page.locator('[data-testid="asset-card"]')).toHaveCount(1);

    // 7. Test bulk operations
    await page.click('[data-testid="bulk-mode-toggle"]');
    await page.click('[data-testid="select-all"]');
    await expect(page.locator('[data-testid="bulk-delete"]')).toBeEnabled();

    // Verify all features work together
    await expect(page.locator('[data-testid="persona-brief-bar"]')).toContainText('Startup Founders');
    await expect(page.locator('[data-testid="asset-card"]')).toBeVisible();
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
  });
});
