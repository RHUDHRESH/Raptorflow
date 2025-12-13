/**
 * OneLiner Agent
 *
 * Creates concise, impactful one-liner messages for various contexts.
 */

import { z } from 'zod';
import { BaseOrchestratorAgent, AgentManifest, AgentInput, AgentOutput } from './base';

const OneLinerSchema = z.object({
  oneLiner: z.string(),
  context: z.string(),
  tone: z.string(),
  impact: z.number().min(1).max(10),
  variations: z.array(z.string()),
});

const manifest: AgentManifest = {
  name: 'OneLiner',
  description: 'Creates concise, impactful one-liner messages',
  version: '1.0.0',
  category: 'content',
  inputs: {
    required: ['brandProfileId'],
    optional: ['inputOverrides', 'contextSnapshot'],
  },
  outputs: {
    type: 'OneLiner',
    format: 'json',
    schema: OneLinerSchema,
  },
  capabilities: [
    'Concise messaging',
    'Impact creation',
    'Context adaptation',
    'Brand voice capture',
    'Memorable communication',
  ],
  costEstimate: {
    minTokens: 150,
    maxTokens: 400,
    estimatedCost: 0.005,
  },
  connectors: [],
  metadata: {
    author: 'system',
    tags: ['content', 'messaging', 'concise', 'impact'],
    complexity: 'simple',
  },
};

export class OneLinerAgent extends BaseOrchestratorAgent {
  constructor() {
    super(manifest);
  }

  async generate(input: AgentInput): Promise<AgentOutput> {
    const validation = this.validateInput(input);
    if (!validation.valid) {
      throw new Error(`Invalid input: ${validation.errors.join(', ')}`);
    }

    const context = await this.getContext(input);
    const prompt = await this.renderPrompt(context, input);
    const { content, metadata } = await this.generateLLMRequest(prompt, input);
    const output = this.processOutput(content, metadata);

    return output;
  }
}

export const oneLinerAgent = new OneLinerAgent();
export { manifest as oneLinerManifest };
export type OneLinerOutput = z.infer<typeof OneLinerSchema>;

