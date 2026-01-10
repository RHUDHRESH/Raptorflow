import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Setting up test environment...');

  // Set up test database or other global test setup
  // This runs once before all tests

  console.log('✅ Test environment setup complete');
}

export default globalSetup;
