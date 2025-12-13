/**
 * WebsiteWireframe Agent
 *
 * Generates website wireframes and page layouts for different purposes.
 */

import { z } from 'zod';
import { BaseOrchestratorAgent, AgentManifest, AgentInput, AgentOutput } from './base';

const WireframeSectionSchema = z.object({
  name: z.string(),
  type: z.string(),
  content: z.string(),
  layout: z.string(),
  priority: z.number().min(1).max(5),
});

const WebsiteWireframeSchema = z.object({
  pageType: z.string(),
  overallLayout: z.string(),
  sections: z.array(WireframeSectionSchema),
  navigation: z.array(z.string()),
  callToActions: z.array(z.string()),
  responsiveNotes: z.string(),
  userFlow: z.array(z.string()),
});

const manifest: AgentManifest = {
  name: 'WebsiteWireframe',
  description: 'Generates website wireframes and page layouts',
  version: '1.0.0',
  category: 'technical',
  inputs: {
    required: ['brandProfileId'],
    optional: ['inputOverrides', 'contextSnapshot'],
  },
  outputs: {
    type: 'WebsiteWireframe',
    format: 'json',
    schema: WebsiteWireframeSchema,
  },
  capabilities: [
    'UX design',
    'Information architecture',
    'Layout planning',
    'User flow design',
    'Responsive design',
  ],
  costEstimate: {
    minTokens: 400,
    maxTokens: 1200,
    estimatedCost: 0.014,
  },
  connectors: ['Figma'],
  metadata: {
    author: 'system',
    tags: ['website', 'wireframe', 'ux', 'design'],
    complexity: 'complex',
  },
};

export class WebsiteWireframeAgent extends BaseOrchestratorAgent {
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

export const websiteWireframeAgent = new WebsiteWireframeAgent();
export { manifest as websiteWireframeManifest };
export type WebsiteWireframeOutput = z.infer<typeof WebsiteWireframeSchema>;

