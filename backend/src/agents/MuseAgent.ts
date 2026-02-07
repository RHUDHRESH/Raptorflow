import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";
import type { ICP, ProtocolType, Asset, CreateAssetInput } from "../types";

// =====================================================
// INPUT/OUTPUT SCHEMAS
// =====================================================

export interface MuseGenerationInput {
  asset_type: string;
  move_context?: {
    name: string;
    description: string;
    protocol: ProtocolType;
    channels: string[];
  };
  icp: ICP;
  positioning: {
    value_proposition?: string;
    primary_target?: string;
    primary_problem?: string;
    primary_outcome?: string;
    differentiation?: string;
  };
  company: {
    name: string;
    industry?: string;
    product_name?: string;
  };
  additional_context?: Record<string, any>;
}

const contentOutputSchema = z.object({
  title: z.string(),
  content: z.string(),
  format: z.enum(["markdown", "html", "json"]),
  sections: z.array(z.object({
    heading: z.string(),
    content: z.string(),
    purpose: z.string()
  })).optional(),
  metadata: z.object({
    word_count: z.number(),
    reading_time_minutes: z.number(),
    tone: z.string(),
    cta: z.string().optional()
  }),
  variants: z.array(z.object({
    name: z.string(),
    hook: z.string(),
    angle: z.string()
  })).optional(),
  usage_notes: z.string()
});

export type MuseGenerationOutput = z.infer<typeof contentOutputSchema>;

// =====================================================
// ASSET TYPE TEMPLATES
// =====================================================

const ASSET_TEMPLATES: Record<string, {
  prompt_context: string;
  structure_guide: string;
  tone_guide: string;
}> = {
  pillar_webinar_script: {
    prompt_context: "Create a comprehensive webinar script that establishes thought leadership",
    structure_guide: `Structure:
1. Hook (30 seconds)
2. Introduction & credibility (2 minutes)
3. Problem framing (5 minutes)
4. Core content - 3 key insights (15 minutes)
5. Solution framework (5 minutes)
6. Case study / proof (3 minutes)
7. Call to action (2 minutes)
8. Q&A prompts`,
    tone_guide: "Expert, educational, conversational but authoritative"
  },
  linkedin_post: {
    prompt_context: "Create a high-engagement LinkedIn post that drives awareness",
    structure_guide: `Structure:
1. Hook line (pattern interrupt)
2. Personal story or observation
3. Key insight (the "aha")
4. Proof/example
5. Takeaway for reader
6. Call to engage (question or action)`,
    tone_guide: "Personal, insightful, conversational. First-person perspective."
  },
  email_sequence: {
    prompt_context: "Create a multi-email sequence that nurtures leads",
    structure_guide: `Structure for each email:
1. Subject line (curiosity or benefit)
2. Preview text
3. Opening hook
4. Value content
5. Soft CTA
6. PS line

Sequence arc: Educate → Build trust → Create urgency → Ask`,
    tone_guide: "Helpful, not salesy. Like a knowledgeable friend."
  },
  battlecard: {
    prompt_context: "Create a sales battlecard for competitive positioning",
    structure_guide: `Sections:
1. Quick win summary
2. Our strengths vs theirs
3. Their strengths (honest)
4. Landmines to plant
5. Objection handlers
6. Proof points to cite
7. Discovery questions
8. When we win / When we lose`,
    tone_guide: "Direct, factual, actionable. For internal use."
  },
  comparison_page: {
    prompt_context: "Create website comparison page content",
    structure_guide: `Sections:
1. Headline (position the comparison)
2. Quick comparison table
3. Our advantages (with proof)
4. Use case fit
5. Migration/switching info
6. FAQ
7. CTA`,
    tone_guide: "Fair but confident. Acknowledge competitor but show clear advantages."
  },
  case_study: {
    prompt_context: "Create a compelling customer case study",
    structure_guide: `Structure:
1. Headline with result
2. Customer profile
3. The challenge
4. Why they chose us
5. The solution
6. The results (specific metrics)
7. Customer quote
8. Key takeaways`,
    tone_guide: "Story-driven, specific, results-focused"
  },
  roi_calculator_spec: {
    prompt_context: "Create specifications for an ROI calculator tool",
    structure_guide: `Sections:
1. Calculator purpose
2. Input fields (with defaults)
3. Calculation logic
4. Output metrics
5. Assumptions
6. Messaging at each step
7. CTA after results`,
    tone_guide: "Clear, logical, focused on credible value demonstration"
  },
  onboarding_email: {
    prompt_context: "Create an onboarding email to drive activation",
    structure_guide: `Structure:
1. Welcome and context
2. What to do next (ONE action)
3. Why it matters (outcome)
4. How to do it (simple steps)
5. Help available
6. Clear CTA button`,
    tone_guide: "Warm, helpful, action-oriented. Reduce cognitive load."
  },
  churn_intercept_email: {
    prompt_context: "Create a churn prevention email using loss aversion",
    structure_guide: `Structure:
1. Acknowledge the situation
2. What they'll lose (specific)
3. What they've built (sunk cost)
4. Easy alternative (pause/downgrade)
5. Human touch offer
6. Final CTA`,
    tone_guide: "Empathetic but clear about stakes. Not desperate."
  }
};

// =====================================================
// MUSE AGENT
// =====================================================

export class MuseAgent {
  private model;
  private parser;
  private basePrompt;

  constructor() {
    const agentName = 'MuseAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'reasoning', getModelForAgent(agentName));
    this.parser = StructuredOutputParser.fromZodSchema(contentOutputSchema);
    this.basePrompt = new PromptTemplate({
      template: `You are Muse, a world-class marketing copywriter and strategist. 

## Asset Type: {asset_type}
{asset_context}

## Target ICP: {icp_label}
Pain Points: {pain_points}
Motivations: {motivations}
Buying Constraints: {buying_constraints}
Messaging Angle: {messaging_angle}

## Company & Positioning
Company: {company_name}
Product: {product_name}
Value Proposition: {value_proposition}
Primary Target: {primary_target}
Key Differentiator: {differentiation}

## Protocol Context
{protocol_context}

## Structure Guide
{structure_guide}

## Tone Guide
{tone_guide}

## Additional Context
{additional_context}

## Your Task
Create compelling, ready-to-use content for this specific asset type. 

Requirements:
1. Speak directly to the ICP's pain points and motivations
2. Use the company's positioning and value proposition
3. Follow the structure guide closely
4. Match the tone guide
5. Include specific, actionable elements
6. Make it immediately usable without heavy editing

{format_instructions}`,
      inputVariables: [
        "asset_type", "asset_context", "icp_label", "pain_points", "motivations",
        "buying_constraints", "messaging_angle", "company_name", "product_name",
        "value_proposition", "primary_target", "differentiation", "protocol_context",
        "structure_guide", "tone_guide", "additional_context"
      ],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  /**
   * Generate an asset
   */
  async generate(input: MuseGenerationInput): Promise<MuseGenerationOutput> {
    const template = ASSET_TEMPLATES[input.asset_type] || {
      prompt_context: `Create ${input.asset_type} content`,
      structure_guide: "Use appropriate structure for this content type",
      tone_guide: "Professional and engaging"
    };

    const protocolContext = input.move_context?.protocol
      ? this.getProtocolContext(input.move_context.protocol)
      : "General marketing content";

    try {
      const chain = this.basePrompt.pipe(this.model).pipe(this.parser);
      const result = await chain.invoke({
        asset_type: input.asset_type,
        asset_context: template.prompt_context,
        icp_label: input.icp.label,
        pain_points: input.icp.psychographics?.pain_points?.join(', ') || 'Growth challenges',
        motivations: input.icp.psychographics?.motivations?.join(', ') || 'Better results',
        buying_constraints: input.icp.psychographics?.buying_constraints?.join(', ') || 'Budget and time',
        messaging_angle: input.icp.messaging_angle || 'Value-focused',
        company_name: input.company.name,
        product_name: input.company.product_name || input.company.name,
        value_proposition: input.positioning.value_proposition || 'Helping you succeed',
        primary_target: input.positioning.primary_target || input.icp.label,
        differentiation: input.positioning.differentiation || 'Unique approach',
        protocol_context: protocolContext,
        structure_guide: template.structure_guide,
        tone_guide: template.tone_guide,
        additional_context: JSON.stringify(input.additional_context || {})
      });
      
      return result as MuseGenerationOutput;
    } catch (error: any) {
      console.error('MuseAgent error:', error);
      return this.getFallbackContent(input);
    }
  }

  /**
   * Generate multiple variants of an asset
   */
  async generateWithVariants(input: MuseGenerationInput, numVariants: number = 3): Promise<MuseGenerationOutput[]> {
    const variants: MuseGenerationOutput[] = [];
    
    // Generate main version
    const main = await this.generate(input);
    variants.push(main);
    
    // Generate additional variants with different angles
    const angles = [
      'Focus on fear of missing out',
      'Lead with the biggest transformation',
      'Start with a controversial take'
    ];
    
    for (let i = 1; i < numVariants && i < angles.length; i++) {
      const variantInput = {
        ...input,
        additional_context: {
          ...input.additional_context,
          angle_override: angles[i]
        }
      };
      
      try {
        const variant = await this.generate(variantInput);
        variants.push(variant);
      } catch (error) {
        console.error(`Failed to generate variant ${i}:`, error);
      }
    }
    
    return variants;
  }

  /**
   * Convert output to database-ready format
   */
  toCreateInput(output: MuseGenerationOutput, input: MuseGenerationInput, moveId?: string, campaignId?: string): CreateAssetInput {
    return {
      name: output.title,
      asset_type: input.asset_type,
      content: output.content,
      content_format: output.format,
      move_id: moveId,
      campaign_id: campaignId,
      icp_id: input.icp.id,
      protocol: input.move_context?.protocol
    };
  }

  /**
   * Get protocol-specific context
   */
  private getProtocolContext(protocol: ProtocolType): string {
    const contexts: Record<ProtocolType, string> = {
      A_AUTHORITY_BLITZ: "Building thought leadership and awareness. Focus on education and insights.",
      B_TRUST_ANCHOR: "Building trust through proof and validation. Focus on evidence and credibility.",
      C_COST_OF_INACTION: "Creating urgency through consequences. Focus on what they lose by waiting.",
      D_HABIT_HARDCODE: "Driving activation and habit formation. Focus on quick wins and progress.",
      E_ENTERPRISE_WEDGE: "Enabling expansion and upsells. Focus on additional value and team benefits.",
      F_CHURN_INTERCEPT: "Preventing churn through intervention. Focus on value delivered and alternatives."
    };
    
    return contexts[protocol] || "General marketing context";
  }

  /**
   * Fallback content when LLM fails
   */
  private getFallbackContent(input: MuseGenerationInput): MuseGenerationOutput {
    const icp = input.icp;
    const company = input.company;
    const painPoint = icp.psychographics?.pain_points?.[0] || 'growth challenges';
    
    return {
      title: `${input.asset_type.replace(/_/g, ' ')} for ${icp.label}`,
      content: `# For ${icp.label}s struggling with ${painPoint}

## The Challenge
${icp.summary || `Companies like yours face significant challenges when it comes to ${painPoint}.`}

## How ${company.name} Helps
${input.positioning.value_proposition || `We help ${icp.label}s overcome ${painPoint} and achieve better results.`}

## Key Benefits
- Address your core pain points
- Designed for your specific needs
- Proven results with companies like yours

## Next Steps
Learn how ${company.name} can help you achieve your goals.

[Contact us to learn more]`,
      format: 'markdown',
      metadata: {
        word_count: 150,
        reading_time_minutes: 1,
        tone: 'professional',
        cta: 'Contact us'
      },
      usage_notes: 'This is a basic template. Customize with specific details and proof points.'
    };
  }

  /**
   * Get available asset types with descriptions
   */
  getAvailableAssetTypes(): Array<{ type: string; description: string; category: string }> {
    return [
      { type: 'pillar_webinar_script', description: 'Full webinar script for thought leadership', category: 'pillar' },
      { type: 'pillar_whitepaper', description: 'Long-form educational content', category: 'pillar' },
      { type: 'linkedin_post', description: 'High-engagement LinkedIn post', category: 'micro' },
      { type: 'twitter_thread', description: 'Twitter/X thread format', category: 'micro' },
      { type: 'email_sequence', description: 'Multi-email nurture sequence', category: 'lifecycle' },
      { type: 'onboarding_email', description: 'Activation-focused email', category: 'lifecycle' },
      { type: 'churn_intercept_email', description: 'Retention-focused email', category: 'lifecycle' },
      { type: 'battlecard', description: 'Sales competitive battlecard', category: 'sales' },
      { type: 'comparison_page', description: 'Website comparison content', category: 'sales' },
      { type: 'case_study', description: 'Customer success story', category: 'sales' },
      { type: 'roi_calculator_spec', description: 'ROI calculator specifications', category: 'tools' }
    ];
  }
}

