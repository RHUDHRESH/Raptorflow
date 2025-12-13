/**
 * ProductName Agent
 *
 * Generates creative and memorable product names.
 */

import { z } from 'zod';
import { BaseOrchestratorAgent, AgentManifest, AgentInput, AgentOutput } from './base';

const ProductNameSchema = z.object({
  primaryName: z.string(),
  alternativeNames: z.array(z.string()),
  rationale: z.string(),
  brandFit: z.number().min(1).max(10),
  memorability: z.number().min(1).max(10),
  marketability: z.number().min(1).max(10),
});

const manifest: AgentManifest = {
  name: 'ProductName',
  description: 'Generates creative and memorable product names',
  version: '1.0.0',
  category: 'brand',
  inputs: {
    required: ['brandProfileId'],
    optional: ['inputOverrides', 'contextSnapshot'],
  },
  outputs: {
    type: 'ProductName',
    format: 'json',
    schema: ProductNameSchema,
  },
  capabilities: ['Naming strategy', 'Brand alignment', 'Market research', 'Trademark consideration'],
  costEstimate: { minTokens: 200, maxTokens: 500, estimatedCost: 0.007 },
  connectors: [],
  metadata: { author: 'system', tags: ['product', 'naming', 'brand'], complexity: 'medium' },
};

export class ProductNameAgent extends BaseOrchestratorAgent {
  constructor() { super(manifest); }
  async generate(input: AgentInput): Promise<AgentOutput> {
    const validation = this.validateInput(input);
    if (!validation.valid) throw new Error(`Invalid input: ${validation.errors.join(', ')}`);
    const context = await this.getContext(input);
    const prompt = await this.renderPrompt(context, input);
    const { content, metadata } = await this.generateLLMRequest(prompt, input);
    return this.processOutput(content, metadata);
  }
}

export const productNameAgent = new ProductNameAgent();
export { manifest as productNameManifest };
export type ProductNameOutput = z.infer<typeof ProductNameSchema>;

