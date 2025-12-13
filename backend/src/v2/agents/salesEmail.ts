/**
 * SalesEmail Agent
 *
 * Creates persuasive sales emails for different stages of the funnel.
 */

import { z } from 'zod';
import { BaseOrchestratorAgent, AgentManifest, AgentInput, AgentOutput } from './base';

const SalesEmailSchema = z.object({
  subject: z.string(),
  preheader: z.string(),
  greeting: z.string(),
  body: z.string(),
  callToAction: z.string(),
  closing: z.string(),
  funnelStage: z.enum(['awareness', 'consideration', 'decision', 'retention']),
  personalization: z.array(z.string()),
  keyBenefits: z.array(z.string()),
});

const manifest: AgentManifest = {
  name: 'SalesEmail',
  description: 'Creates persuasive sales emails for different funnel stages',
  version: '1.0.0',
  category: 'marketing',
  inputs: {
    required: ['brandProfileId'],
    optional: ['inputOverrides', 'contextSnapshot'],
  },
  outputs: {
    type: 'SalesEmail',
    format: 'json',
    schema: SalesEmailSchema,
  },
  capabilities: [
    'Email marketing',
    'Sales copywriting',
    'Funnel optimization',
    'Personalization',
    'Conversion psychology',
  ],
  costEstimate: {
    minTokens: 350,
    maxTokens: 900,
    estimatedCost: 0.011,
  },
  connectors: ['SES'],
  metadata: {
    author: 'system',
    tags: ['email', 'sales', 'marketing', 'conversion'],
    complexity: 'medium',
  },
};

export class SalesEmailAgent extends BaseOrchestratorAgent {
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

export const salesEmailAgent = new SalesEmailAgent();
export { manifest as salesEmailManifest };
export type SalesEmailOutput = z.infer<typeof SalesEmailSchema>;

