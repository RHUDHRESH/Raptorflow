/**
 * ProductDescription Agent
 *
 * Generates compelling product descriptions that drive conversions.
 */

import { z } from 'zod';
import { BaseOrchestratorAgent, AgentManifest, AgentInput, AgentOutput } from './base';

const ProductDescriptionSchema = z.object({
  shortDescription: z.string(),
  longDescription: z.string(),
  keyFeatures: z.array(z.string()),
  benefits: z.array(z.string()),
  callToAction: z.string(),
  seoKeywords: z.array(z.string()),
});

const manifest: AgentManifest = {
  name: 'ProductDescription',
  description: 'Creates compelling product descriptions that drive conversions',
  version: '1.0.0',
  category: 'content',
  inputs: {
    required: ['brandProfileId'],
    optional: ['inputOverrides', 'contextSnapshot'],
  },
  outputs: {
    type: 'ProductDescription',
    format: 'json',
    schema: ProductDescriptionSchema,
  },
  capabilities: [
    'Product storytelling',
    'Benefit communication',
    'Conversion optimization',
    'SEO optimization',
    'Brand voice alignment',
  ],
  costEstimate: {
    minTokens: 300,
    maxTokens: 800,
    estimatedCost: 0.010,
  },
  connectors: [],
  metadata: {
    author: 'system',
    tags: ['product', 'description', 'conversion', 'seo'],
    complexity: 'medium',
  },
};

export class ProductDescriptionAgent extends BaseOrchestratorAgent {
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

export const productDescriptionAgent = new ProductDescriptionAgent();
export { manifest as productDescriptionManifest };
export type ProductDescriptionOutput = z.infer<typeof ProductDescriptionSchema>;

