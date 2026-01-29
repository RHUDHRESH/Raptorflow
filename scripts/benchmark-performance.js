#!/usr/bin/env node

const { performance } = require('perf_hooks');

async function benchmarkAuth() {
  const start = performance.now();
  // Test auth endpoint
  const response = await fetch('/api/v1/auth/verify-profile');
  const end = performance.now();
  return end - start;
}

async function benchmarkBCM() {
  const start = performance.now();
  // Test BCM endpoint
  const response = await fetch('/api/v1/context/manifest');
  const end = performance.now();
  return end - start;
}

async function runBenchmarks() {
  console.log('🚀 Running performance benchmarks...');

  try {
    const authTime = await benchmarkAuth();
    const bcmTime = await benchmarkBCM();

    console.log(`Auth verification: ${authTime.toFixed(2)}ms (target: <1000ms)`);
    console.log(`BCM retrieval: ${bcmTime.toFixed(2)}ms (target: <200ms)`);

    if (authTime > 1000) {
      console.warn('⚠️ Auth verification is slower than target');
    }

    if (bcmTime > 200) {
      console.warn('⚠️ BCM retrieval is slower than target');
    }

    if (authTime <= 1000 && bcmTime <= 200) {
      console.log('✅ All performance benchmarks passed');
    }
  } catch (error) {
    console.error('❌ Performance benchmark failed:', error.message);
    process.exit(1);
  }
}

runBenchmarks().catch(console.error);
