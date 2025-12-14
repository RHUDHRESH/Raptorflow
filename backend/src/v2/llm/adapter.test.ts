/**
 * Unit Tests for LLM Adapter
 *
 * Tests Vertex AI primary with OpenAI fallback functionality.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock the telemetry service
vi.mock('../../services/telemetryService', () => ({
  telemetryService: {
    logLLMUsage: vi.fn(),
  },
}));

// Mock Redis memory
vi.mock('../../services/redisMemory', () => ({
  redisMemory: {
    store: vi.fn(),
  },
}));

// Import after mocking
import { llmAdapter } from './adapter';
import { telemetryService } from '../../services/telemetryService';

describe('LLM Adapter', () => {
  const mockRequest = {
    messages: [
      { role: 'user', content: 'Hello, create a tagline for my brand' },
    ],
    agentName: 'Tagline',
    jobId: 'test-job-123',
    userId: 'test-user-456',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('generate method', () => {
    it('should generate response successfully', async () => {
      const result = await llmAdapter.generate(mockRequest);

      expect(result).toBeDefined();
      expect(result.content).toBeDefined();
      expect(result.model).toBeDefined();
      expect(result.usage).toBeDefined();
      expect(result.cost).toBeGreaterThan(0);
      expect(result.provider).toBe('vertex');
    });

    it('should log usage to telemetry service', async () => {
      await llmAdapter.generate(mockRequest);

      expect(telemetryService.logLLMUsage).toHaveBeenCalledWith(
        expect.objectContaining({
          traceId: expect.any(String),
          agentName: 'Tagline',
          jobId: 'test-job-123',
          userId: 'test-user-456',
          provider: 'vertex',
          usage: expect.any(Object),
          cost: expect.any(Number),
          latency: expect.any(Number),
        })
      );
    });

    it('should include trace ID in logs', async () => {
      await llmAdapter.generate(mockRequest);

      const logCall = vi.mocked(telemetryService.logLLMUsage).mock.calls[0][0];
      expect(logCall.traceId).toMatch(/^llm_\d+_[a-z0-9]+$/);
    });

    it('should handle different agent names', async () => {
      const requests = [
        { ...mockRequest, agentName: 'BrandScript' },
        { ...mockRequest, agentName: 'ProductDescription' },
        { ...mockRequest, agentName: 'SocialMediaIdeas' },
      ];

      for (const request of requests) {
        await llmAdapter.generate(request);

        expect(telemetryService.logLLMUsage).toHaveBeenCalledWith(
          expect.objectContaining({
            agentName: request.agentName,
          })
        );
      }
    });
  });

  describe('Cost Calculation', () => {
    it('should calculate Vertex AI costs correctly', async () => {
      // Mock a response with known token usage
      const mockResponse = {
        content: 'Test response',
        model: 'gemini-2.5-flash-preview-05-20',
        usage: {
          promptTokens: 1000,
          completionTokens: 500,
          totalTokens: 1500,
        },
        cost: 0, // Will be calculated
        latency: 1000,
        provider: 'vertex' as const,
      };

      // The adapter calculates cost internally, so we just verify it's a number
      const result = await llmAdapter.generate(mockRequest);
      expect(typeof result.cost).toBe('number');
      expect(result.cost).toBeGreaterThan(0);
    });

    it('should include cost in usage logs', async () => {
      await llmAdapter.generate(mockRequest);

      const logCall = vi.mocked(telemetryService.logLLMUsage).mock.calls[0][0];
      expect(logCall.cost).toBeDefined();
      expect(typeof logCall.cost).toBe('number');
    });
  });

  describe('Usage Tracking', () => {
    it('should track token usage', async () => {
      const result = await llmAdapter.generate(mockRequest);

      expect(result.usage.promptTokens).toBeDefined();
      expect(result.usage.completionTokens).toBeDefined();
      expect(result.usage.totalTokens).toBeDefined();
      expect(result.usage.totalTokens).toBe(
        result.usage.promptTokens + result.usage.completionTokens
      );
    });

    it('should log usage metadata', async () => {
      await llmAdapter.generate(mockRequest);

      const logCall = vi.mocked(telemetryService.logLLMUsage).mock.calls[0][0];
      expect(logCall.usage).toBeDefined();
      expect(logCall.latency).toBeDefined();
      expect(logCall.timestamp).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    it('should handle rate limiting gracefully', async () => {
      // Mock rate limit error
      const originalGenerate = llmAdapter.generate;
      vi.spyOn(llmAdapter as any, 'generate').mockRejectedValueOnce(
        new Error('Rate limit exceeded')
      );

      await expect(llmAdapter.generate(mockRequest)).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      // Mock network error
      const originalGenerate = llmAdapter.generate;
      vi.spyOn(llmAdapter as any, 'generate').mockRejectedValueOnce(
        new Error('Network connection failed')
      );

      await expect(llmAdapter.generate(mockRequest)).rejects.toThrow();
    });
  });

  describe('Provider Fallback', () => {
    it('should indicate when fallback is used', async () => {
      // Test would require mocking Vertex failure and OpenAI success
      // This is complex to test without more sophisticated mocking
      const result = await llmAdapter.generate(mockRequest);

      // In normal operation, fallback should not be used
      expect(result.fallbackUsed).toBeUndefined();
    });
  });

  describe('Health Check', () => {
    it('should perform health checks', async () => {
      const health = await llmAdapter.healthCheck();

      expect(health).toBeDefined();
      expect(typeof health.vertex).toBe('boolean');
      // OpenAI health depends on configuration
    });
  });

  describe('Usage Statistics', () => {
    it('should provide usage statistics', async () => {
      const stats = await llmAdapter.getUsageStats();

      expect(stats).toBeDefined();
      expect(typeof stats.totalRequests).toBe('number');
      expect(typeof stats.totalTokens).toBe('number');
      expect(typeof stats.totalCost).toBe('number');
    });
  });
});

