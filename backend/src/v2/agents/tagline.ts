/**
 * Tagline Agent
 *
 * Creates memorable, impactful taglines that capture brand essence.
 */

import { z } from 'zod';
import { BaseOrchestratorAgent, AgentManifest, AgentInput, AgentOutput } from './base';

const TaglineSchema = z.object({
  primaryTagline: z.string(),
  alternativeTaglines: z.array(z.string()),
  rationale: z.string(),
  brandAlignment: z.string(),
  memorability: z.number().min(1).max(10),
  uniqueness: z.number().min(1).max(10),
});

const manifest: AgentManifest = {
  name: 'Tagline',
  description: 'Creates memorable taglines that capture brand essence',
  version: '1.0.0',
  category: 'brand',
  inputs: {
    required: ['brandProfileId'],
    optional: ['inputOverrides', 'contextSnapshot'],
  },
  outputs: {
    type: 'Tagline',
    format: 'json',
    schema: TaglineSchema,
  },
  capabilities: [
    'Brand positioning',
    'Memorable messaging',
    'Emotional resonance',
    'Market differentiation',
    'Brand voice capture',
  ],
  costEstimate: {
    minTokens: 200,
    maxTokens: 600,
    estimatedCost: 0.008,
  },
  connectors: [],
  metadata: {
    author: 'system',
    tags: ['brand', 'tagline', 'messaging', 'positioning'],
    complexity: 'medium',
  },
};

export class TaglineAgent extends BaseOrchestratorAgent {
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

    return output;
  }
}

// Export singleton instance
export const taglineAgent = new TaglineAgent();

// Export manifest for registry
export { manifest as taglineManifest };

// Export types
export type TaglineOutput = z.infer<typeof TaglineSchema>;

