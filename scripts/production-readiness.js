#!/usr/bin/env node

const checks = [
  {
    name: 'Environment Variables',
    check: () => require('./validate-environment.js')
  },
  {
    name: 'Performance Benchmarks',
    check: () => require('./benchmark-performance.js')
  },
  {
    name: 'Security Verification',
    check: () => require('./verify-security.js')
  },
  {
    name: 'E2E Tests',
    check: () => require('./run-e2e-tests.js')
  }
];

async function runProductionReadiness() {
  console.log('🏁 Running production readiness checks...\n');

  for (const { name, check } of checks) {
    console.log(`Running ${name}...`);
    try {
      await check();
      console.log(`✅ ${name} passed\n`);
    } catch (error) {
      console.error(`❌ ${name} failed\n`);
      process.exit(1);
    }
  }

  console.log('🎉 All production readiness checks passed!');
  console.log('RaptorFlow is ready for deployment! 🚀');
}

runProductionReadiness().catch(console.error);
