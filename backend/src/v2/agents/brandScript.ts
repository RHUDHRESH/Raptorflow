/**
 * BrandScript Agent
 *
 * Generates compelling brand scripts for marketing campaigns and storytelling.
 */

import { z } from 'zod';
import { BaseOrchestratorAgent, AgentManifest, AgentInput, AgentOutput } from './base';

const BrandScriptSchema = z.object({
  title: z.string(),
  script: z.string(),
  keyMessages: z.array(z.string()),
  tone: z.string(),
  estimatedDuration: z.string(),
  targetAudience: z.string(),
});

const manifest: AgentManifest = {
  name: 'BrandScript',
  description: 'Master brand storyteller creating compelling scripts for campaigns',
  version: '1.0.0',
  category: 'brand',
  inputs: {
    required: ['brandProfileId'],
    optional: ['inputOverrides', 'contextSnapshot'],
  },
  outputs: {
    type: 'BrandScript',
    format: 'json',
    schema: BrandScriptSchema,
  },
  capabilities: [
    'Brand storytelling',
    'Emotional connection',
    'Campaign messaging',
    'Audience engagement',
    'Brand voice consistency',
  ],
  costEstimate: {
    minTokens: 500,
    maxTokens: 1500,
    estimatedCost: 0.015,
  },
  connectors: [],
  metadata: {
    author: 'system',
    tags: ['brand', 'storytelling', 'marketing', 'campaigns'],
    complexity: 'complex',
  },
};

export class BrandScriptAgent extends BaseOrchestratorAgent {
  constructor() {
    super(manifest);
  }

  async generate(input: AgentInput): Promise<AgentOutput> {
    // Validate input
    const validation = this.validateInput(input);
    if (!validation.valid) {
      throw new Error(`Invalid input: ${validation.errors.join(', ')}`);
    }

    // Get context
    const context = await this.getContext(input);

    // Render prompt
    const prompt = await this.renderPrompt(context, input);

    // Generate LLM request
    const { content, metadata } = await this.generateLLMRequest(prompt, input);

    // Process and validate output
    const output = this.processOutput(content, metadata);

    // Store in agent memory for future reference
    if (input.jobId) {
      await this.storeAgentMemory(input.jobId, {
        script: output.content,
        generatedAt: new Date().toISOString(),
      });
    }

    return output;
  }
}

// Export singleton instance
export const brandScriptAgent = new BrandScriptAgent();

// Export manifest for registry
export { manifest as brandScriptManifest };

// Export types
export type BrandScriptOutput = z.infer<typeof BrandScriptSchema>;

