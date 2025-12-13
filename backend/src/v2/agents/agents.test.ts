/**
 * Unit Tests for Orchestrator Agents
 *
 * Tests agent manifests, validation, and basic functionality.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { z } from 'zod';

// Mock dependencies
vi.mock('../llm/adapter', () => ({
  llmAdapter: {
    generate: vi.fn(),
  },
}));

vi.mock('../prompts/index', () => ({
  promptStore: {
    getRenderedPromptForAgent: vi.fn(),
  },
}));

vi.mock('../../services/redisMemory', () => ({
  redisMemory: {
    storeAgentMemory: vi.fn(),
    getAgentMemory: vi.fn(),
    delete: vi.fn(),
  },
}));

// Import after mocking
import { brandScriptAgent, taglineAgent, productDescriptionAgent, oneLinerAgent } from './index';
import { llmAdapter } from '../llm/adapter';
import { promptStore } from '../prompts/index';

describe('Orchestrator Agents', () => {
  const mockInput = {
    brandProfileId: 'test-brand-id',
    inputOverrides: {},
    contextSnapshot: {},
    jobId: 'test-job-id',
    userId: 'test-user-id',
  };

  const mockLLMResponse = {
    content: JSON.stringify({
      primaryTagline: 'Test Tagline',
      alternativeTaglines: ['Alt 1', 'Alt 2'],
      rationale: 'Test rationale',
      brandAlignment: 9,
      memorability: 8,
      uniqueness: 7,
    }),
    model: 'gemini-2.5-flash-preview-05-20',
    usage: {
      promptTokens: 100,
      completionTokens: 50,
      totalTokens: 150,
    },
    cost: 0.008,
    latency: 500,
    provider: 'vertex' as const,
  };

  beforeEach(() => {
    vi.clearAllMocks();

    // Setup default mocks
    vi.mocked(llmAdapter.generate).mockResolvedValue(mockLLMResponse);
    vi.mocked(promptStore.getRenderedPromptForAgent).mockResolvedValue('Mock rendered prompt');
  });

  describe('BrandScript Agent', () => {
    it('should have valid manifest', () => {
      expect(brandScriptAgent.manifest.name).toBe('BrandScript');
      expect(brandScriptAgent.manifest.category).toBe('brand');
      expect(brandScriptAgent.manifest.capabilities).toContain('Brand storytelling');
    });

    it('should validate input correctly', () => {
      const validInput = { ...mockInput };
      const { valid, errors } = brandScriptAgent['validateInput'](validInput);
      expect(valid).toBe(true);
      expect(errors).toHaveLength(0);
    });

    it('should reject invalid input', () => {
      const invalidInput = { ...mockInput, brandProfileId: undefined };
      const { valid, errors } = brandScriptAgent['validateInput'](invalidInput);
      expect(valid).toBe(false);
      expect(errors).toContain('Missing required input: brandProfileId');
    });

    it('should generate content successfully', async () => {
      const result = await brandScriptAgent.generate(mockInput);

      expect(result).toBeDefined();
      expect(result.content).toBeDefined();
      expect(result.metadata.model).toBe('gemini-2.5-flash-preview-05-20');
      expect(result.metadata.tokens).toBe(150);
      expect(result.metadata.cost).toBe(0.008);
    });

    it('should handle LLM errors gracefully', async () => {
      vi.mocked(llmAdapter.generate).mockRejectedValue(new Error('LLM service unavailable'));

      await expect(brandScriptAgent.generate(mockInput)).rejects.toThrow('LLM request failed');
    });
  });

  describe('Tagline Agent', () => {
    it('should have valid manifest', () => {
      expect(taglineAgent.manifest.name).toBe('Tagline');
      expect(taglineAgent.manifest.category).toBe('brand');
      expect(taglineAgent.manifest.capabilities).toContain('Memorable messaging');
    });

    it('should generate valid tagline output', async () => {
      const result = await taglineAgent.generate(mockInput);

      expect(result).toBeDefined();
      expect(result.content).toBeDefined();
      expect(result.metadata).toBeDefined();
    });

    it('should validate output schema', async () => {
      // Test that the output conforms to expected schema
      const result = await taglineAgent.generate(mockInput);
      const parsed = JSON.parse(result.content);

      expect(parsed).toHaveProperty('primaryTagline');
      expect(parsed).toHaveProperty('alternativeTaglines');
      expect(Array.isArray(parsed.alternativeTaglines)).toBe(true);
    });
  });

  describe('ProductDescription Agent', () => {
    it('should have valid manifest', () => {
      expect(productDescriptionAgent.manifest.name).toBe('ProductDescription');
      expect(productDescriptionAgent.manifest.category).toBe('content');
      expect(productDescriptionAgent.manifest.capabilities).toContain('Conversion optimization');
    });

    it('should generate product description', async () => {
      const result = await productDescriptionAgent.generate(mockInput);

      expect(result).toBeDefined();
      expect(result.content).toBeDefined();
      expect(result.metadata.tokens).toBeGreaterThan(0);
    });
  });

  describe('OneLiner Agent', () => {
    it('should have valid manifest', () => {
      expect(oneLinerAgent.manifest.name).toBe('OneLiner');
      expect(oneLinerAgent.manifest.category).toBe('content');
      expect(oneLinerAgent.manifest.capabilities).toContain('Concise messaging');
    });

    it('should generate one-liner content', async () => {
      const result = await oneLinerAgent.generate(mockInput);

      expect(result).toBeDefined();
      expect(result.content).toBeDefined();
      expect(result.metadata).toBeDefined();
    });
  });

  describe('Agent Manifest Validation', () => {
    it('should validate all agent manifests', () => {
      const agents = [brandScriptAgent, taglineAgent, productDescriptionAgent, oneLinerAgent];

      agents.forEach(agent => {
        const manifest = agent.manifest;

        // Required fields
        expect(manifest.name).toBeDefined();
        expect(manifest.description).toBeDefined();
        expect(manifest.version).toBeDefined();
        expect(manifest.category).toBeDefined();
        expect(manifest.inputs).toBeDefined();
        expect(manifest.outputs).toBeDefined();
        expect(manifest.capabilities).toBeDefined();

        // Input validation
        expect(manifest.inputs.required).toBeDefined();
        expect(Array.isArray(manifest.inputs.required)).toBe(true);
        expect(manifest.inputs.optional).toBeDefined();
        expect(Array.isArray(manifest.inputs.optional)).toBe(true);

        // Output validation
        expect(manifest.outputs.type).toBeDefined();
        expect(manifest.outputs.format).toBeDefined();
        expect(['text', 'json', 'markdown', 'html']).toContain(manifest.outputs.format);

        // Capabilities
        expect(Array.isArray(manifest.capabilities)).toBe(true);
        expect(manifest.capabilities.length).toBeGreaterThan(0);

        // Cost estimate
        expect(manifest.costEstimate).toBeDefined();
        expect(manifest.costEstimate.minTokens).toBeGreaterThan(0);
        expect(manifest.costEstimate.maxTokens).toBeGreaterThan(0);
        expect(manifest.costEstimate.estimatedCost).toBeGreaterThan(0);
      });
    });

    it('should validate manifest schema', () => {
      const agents = [brandScriptAgent, taglineAgent, productDescriptionAgent, oneLinerAgent];

      agents.forEach(agent => {
        const manifest = agent.manifest;

        // Version should be semver-like
        expect(manifest.version).toMatch(/^\d+\.\d+\.\d+$/);

        // Category should be valid
        expect(['brand', 'content', 'marketing', 'creative', 'technical']).toContain(manifest.category);

        // Complexity should be valid
        expect(['simple', 'medium', 'complex']).toContain(manifest.metadata.complexity);
      });
    });
  });

  describe('Agent Context Handling', () => {
    it('should handle context rendering', async () => {
      const contextInput = {
        ...mockInput,
        inputOverrides: { campaignGoal: 'Drive sales' },
        contextSnapshot: { previousResults: ['result1'] },
      };

      await brandScriptAgent.generate(contextInput);

      expect(promptStore.getRenderedPromptForAgent).toHaveBeenCalledWith(
        'BrandScript',
        expect.objectContaining({
          agentName: 'BrandScript',
          brandProfile: null, // Would be populated in real scenario
          inputOverrides: contextInput.inputOverrides,
          contextSnapshot: contextInput.contextSnapshot,
        }),
        undefined
      );
    });

    it('should store agent memory', async () => {
      await brandScriptAgent.generate(mockInput);

      // Should store memory for the job
      expect(brandScriptAgent['storeAgentMemory']).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should handle prompt rendering failures', async () => {
      vi.mocked(promptStore.getRenderedPromptForAgent).mockRejectedValue(new Error('Prompt not found'));

      await expect(brandScriptAgent.generate(mockInput)).rejects.toThrow();
    });

    it('should handle malformed LLM responses', async () => {
      vi.mocked(llmAdapter.generate).mockResolvedValue({
        ...mockLLMResponse,
        content: 'Invalid JSON',
      });

      // Should still return result but with raw content
      const result = await taglineAgent.generate(mockInput);
      expect(result).toBeDefined();
    });
  });

  describe('Performance Metrics', () => {
    it('should include performance metadata', async () => {
      const result = await brandScriptAgent.generate(mockInput);

      expect(result.metadata).toBeDefined();
      expect(result.metadata.latency).toBeDefined();
      expect(result.metadata.model).toBeDefined();
      expect(result.metadata.tokens).toBeDefined();
      expect(result.metadata.cost).toBeDefined();
    });

    it('should calculate costs correctly', async () => {
      const result = await brandScriptAgent.generate(mockInput);

      expect(result.metadata.cost).toBeGreaterThan(0);
      expect(typeof result.metadata.cost).toBe('number');
    });
  });

  describe('getSystemPrompt', () => {
    it('should return a non-empty string', () => {
      const prompt = brandScriptAgent.getSystemPrompt();
      expect(typeof prompt).toBe('string');
      expect(prompt.length).toBeGreaterThan(0);
    });

    it('should return a prompt containing relevant keywords', () => {
      const prompt = brandScriptAgent.getSystemPrompt();
      expect(prompt.toLowerCase()).toMatch(/brand|script|creative|director/);
    });
  });
});
