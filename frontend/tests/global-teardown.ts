import { FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Cleaning up test environment...');

  // Clean up test database or other global test cleanup
  // This runs once after all tests

  console.log('✅ Test environment cleanup complete');
}

export default globalTeardown;
