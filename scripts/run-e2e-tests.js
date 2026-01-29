#!/usr/bin/env node

const { spawn } = require('child_process');

async function runE2ETests() {
  console.log('🧪 Running E2E tests...');

  // Start development server
  const devServer = spawn('npm', ['run', 'dev'], {
    stdio: 'inherit',
    env: { ...process.env, NODE_ENV: 'test' }
  });

  // Wait for server to start
  await new Promise(resolve => setTimeout(resolve, 5000));

  try {
    // Run Playwright tests
    const testProcess = spawn('npx', ['playwright', 'test'], {
      stdio: 'inherit'
    });

    await new Promise((resolve, reject) => {
      testProcess.on('close', resolve);
      testProcess.on('error', reject);
    });

    console.log('✅ E2E tests completed');
  } finally {
    // Cleanup
    devServer.kill();
  }
}

runE2ETests().catch(console.error);
