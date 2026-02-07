/**
 * ContentIdeaAgent - Generates specific content ideas from opportunities
 * 
 * Takes radar opportunities and creates detailed, executable content briefs
 */

import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

export interface ContentIdeaInput {
  opportunity_title: string;
  opportunity_description: string;
  trend_type: string;
  cohort_name: string;
  cohort_description: string;
  matching_tags: string[];
  format: 'image_post' | 'video' | 'carousel' | 'story' | 'reel' | 'thread' | 'blog' | 'email';
  platform: string;
  brand_voice?: string;
  brand_guidelines?: string;
}

const contentIdeaSchema = z.object({
  content_brief: z.object({
    headline: z.string().describe("Attention-grabbing headline/hook"),
    subheadline: z.string().nullable(),
    body_copy: z.string().describe("Main content/caption"),
    call_to_action: z.string(),
    hashtags: z.array(z.string()),
    
    // Visual direction
    visual_concept: z.string().describe("Description of visual/creative direction"),
    visual_style: z.enum(['minimalist', 'bold', 'playful', 'professional', 'emotional', 'meme', 'infographic']),
    color_suggestions: z.array(z.string()),
    
    // Copy variations
    variations: z.array(z.object({
      version: z.string(),
      headline: z.string(),
      body: z.string()
    })).describe("A/B test variations")
  }),
  
  // Execution details
  execution: z.object({
    estimated_time: z.string(),
    difficulty: z.enum(['quick', 'moderate', 'complex']),
    resources_needed: z.array(z.string()),
    approval_notes: z.string().nullable()
  }),
  
  // Performance prediction
  predictions: z.object({
    engagement_estimate: z.enum(['low', 'medium', 'high', 'viral']),
    best_posting_time: z.string(),
    expected_reach_multiplier: z.number(),
    reasoning: z.string()
  }),

  // Tie to moves/campaigns
  integration: z.object({
    suggested_move_type: z.string(),
    campaign_fit: z.string(),
    follow_up_content: z.array(z.string())
  })
});

export type ContentIdea = z.infer<typeof contentIdeaSchema>;

export class ContentIdeaAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    const agentName = 'ContentIdeaAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'reasoning', getModelForAgent(agentName));
    
    this.parser = StructuredOutputParser.fromZodSchema(contentIdeaSchema);
    
    this.prompt = new PromptTemplate({
      template: `You are a creative content strategist. Generate a detailed, ready-to-execute content brief.

## OPPORTUNITY
Title: {opportunity_title}
Description: {opportunity_description}
Trend Type: {trend_type}

## TARGET COHORT
Name: {cohort_name}
Description: {cohort_description}
Interest Tags: {matching_tags}

## FORMAT & PLATFORM
Format: {format}
Platform: {platform}

## BRAND GUIDELINES
Voice: {brand_voice}
Guidelines: {brand_guidelines}

## YOUR TASK

Create a complete content brief that:

1. **HOOKS IMMEDIATELY** - First 3 seconds/words must grab attention
2. **FEELS NATIVE** - Matches the platform's culture and your cohort's language
3. **RIDES THE TREND** - Clearly connects to what's happening now
4. **DRIVES ACTION** - Has a clear CTA that makes sense
5. **IS EXECUTABLE** - Can actually be created quickly

### HEADLINE RULES
- Under 10 words for social
- Use power words: "How", "Why", "Secret", "Finally", "Breaking"
- Reference the trend explicitly
- Speak directly to the cohort

### BODY COPY RULES
- Lead with the most interesting point
- Use short sentences
- Include one surprising fact/stat if relevant
- End with clear next step

### VISUAL RULES
- Describe exactly what the image/video should show
- Reference trending visual styles
- Consider what makes people stop scrolling

{format_instructions}`,
      inputVariables: [
        "opportunity_title", "opportunity_description", "trend_type",
        "cohort_name", "cohort_description", "matching_tags",
        "format", "platform", "brand_voice", "brand_guidelines"
      ],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() }
    });
  }

  async generateIdea(input: ContentIdeaInput): Promise<ContentIdea> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    
    return await chain.invoke({
      opportunity_title: input.opportunity_title,
      opportunity_description: input.opportunity_description,
      trend_type: input.trend_type,
      cohort_name: input.cohort_name,
      cohort_description: input.cohort_description,
      matching_tags: input.matching_tags.join(', '),
      format: input.format,
      platform: input.platform,
      brand_voice: input.brand_voice || 'Professional but approachable',
      brand_guidelines: input.brand_guidelines || 'No specific guidelines'
    });
  }

  /**
   * Generate multiple ideas for different platforms
   */
  async generateMultiPlatformIdeas(
    input: Omit<ContentIdeaInput, 'format' | 'platform'>,
    platforms: Array<{ format: ContentIdeaInput['format']; platform: string }>
  ): Promise<ContentIdea[]> {
    return Promise.all(
      platforms.map(p => this.generateIdea({
        ...input,
        format: p.format,
        platform: p.platform
      }))
    );
  }
}

