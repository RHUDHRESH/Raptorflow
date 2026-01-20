import { describe, test, expect } from 'vitest';
import { TitanDomain } from '../domain/TitanDomain';
import { BlackboxDomain } from '../domain/BlackboxDomain';
import { TitanMode } from '../types';

describe('Intelligence Domains', () => {
  describe('TitanDomain', () => {
    test('should return correct settings for DEEP mode', () => {
      const settings = TitanDomain.getResearchSettings(TitanMode.DEEP);
      expect(settings.recursion_depth).toBe(3);
      expect(settings.parallel_scrapers).toBe(10);
    });

    test('should generate multiplex prompt', () => {
      const prompt = TitanDomain.generateMultiplexPrompt('AI Chips');
      expect(prompt).toContain('AI Chips');
    });
  });

  describe('BlackboxDomain', () => {
    test('should generate bold strategy prompt for high risk', () => {
      const prompt = BlackboxDomain.generateStrategyPrompt({
        workspace_id: '1',
        objective: 'Market Entry',
        risk_tolerance: 0.9
      });
      expect(prompt).toContain('Aggressive/Bold');
    });

    test('should validate boldness', () => {
      const moves = [{ impact: 'high' }, { impact: 'high' }];
      expect(BlackboxDomain.isStrategyBoldEnough(moves, 0.9)).toBe(true);
      
      const weakMoves = [{ impact: 'low' }];
      expect(BlackboxDomain.isStrategyBoldEnough(weakMoves, 0.9)).toBe(false);
    });
  });
});
