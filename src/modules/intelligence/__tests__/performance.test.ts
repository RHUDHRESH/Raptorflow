import { describe, test, expect } from 'vitest';
import { TitanDomain } from '../domain/TitanDomain';
import { BlackboxDomain } from '../domain/BlackboxDomain';
import { performance } from 'perf_hooks';

describe('Intelligence Performance Benchmarks', () => {
  test('Titan Multiplex Prompt Generation Speed', () => {
    const start = performance.now();
    for (let i = 0; i < 1000; i++) {
      TitanDomain.generateMultiplexPrompt('Quantum Computing in 2026');
    }
    const end = performance.now();
    const avg = (end - start) / 1000;
    console.log(`Titan Multiplex Prompt Avg: ${avg.toFixed(4)}ms`);
    expect(avg).toBeLessThan(0.1); // Should be very fast (pure string manipulation)
  });

  test('Blackbox Strategy Prompt Generation Speed', () => {
    const start = performance.now();
    for (let i = 0; i < 1000; i++) {
      BlackboxDomain.generateStrategyPrompt({
        workspace_id: 'ws1',
        objective: 'Market Expansion',
        risk_tolerance: 0.8
      });
    }
    const end = performance.now();
    const avg = (end - start) / 1000;
    console.log(`Blackbox Strategy Prompt Avg: ${avg.toFixed(4)}ms`);
    expect(avg).toBeLessThan(0.1);
  });
});
