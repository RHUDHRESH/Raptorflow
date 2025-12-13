/**
 * SocialMediaIdeas Agent
 *
 * Generates creative social media content ideas and campaigns.
 */

import { z } from 'zod';
import { BaseOrchestratorAgent, AgentManifest, AgentInput, AgentOutput } from './base';

const SocialMediaIdeaSchema = z.object({
  platform: z.string(),
  contentType: z.string(),
  idea: z.string(),
  caption: z.string(),
  hashtags: z.array(z.string()),
  engagement: z.number().min(1).max(10),
  timing: z.string(),
});

const SocialMediaIdeasSchema = z.object({
  campaignTheme: z.string(),
  ideas: z.array(SocialMediaIdeaSchema),
  contentCalendar: z.array(z.object({
    date: z.string(),
    platform: z.string(),
    content: z.string(),
  })),
});

const manifest: AgentManifest = {
  name: 'SocialMediaIdeas',
  description: 'Generates creative social media content ideas and campaigns',
  version: '1.0.0',
  category: 'marketing',
  inputs: {
    required: ['brandProfileId'],
    optional: ['inputOverrides', 'contextSnapshot'],
  },
  outputs: {
    type: 'SocialMediaIdeas',
    format: 'json',
    schema: SocialMediaIdeasSchema,
  },
  capabilities: [
    'Social media strategy',
    'Content ideation',
    'Platform optimization',
    'Engagement tactics',
    'Campaign planning',
  ],
  costEstimate: {
    minTokens: 400,
    maxTokens: 1000,
    estimatedCost: 0.012,
  },
  connectors: [],
  metadata: {
    author: 'system',
    tags: ['social', 'content', 'marketing', 'engagement'],
    complexity: 'medium',
  },
};

export class SocialMediaIdeasAgent extends BaseOrchestratorAgent {
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

export const socialMediaIdeasAgent = new SocialMediaIdeasAgent();
export { manifest as socialMediaIdeasManifest };
export type SocialMediaIdeasOutput = z.infer<typeof SocialMediaIdeasSchema>;

