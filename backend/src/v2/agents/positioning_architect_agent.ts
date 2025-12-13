import { z } from 'zod';
import { BaseAgent, agentRegistry } from '../base_agent';
import { Department, OrchestratorContext } from '../types';
import { ragQuery, storeEmbedding } from '../rag_helper';

// =====================================================
// POSITIONING ARCHITECT AGENT
// =====================================================

const PositioningArchitectInputSchema = z.object({
  company_name: z.string().describe("The company/product name"),
  category: z.string().describe("Current or desired market category"),
  competitors: z.array(z.string()).describe("Main competitors in the space"),
  target_audience: z.string().describe("Primary target audience description"),
  unique_mechanism: z.string().optional().describe("Unique mechanism or approach"),
  desired_positioning: z.enum(['leader', 'innovator', 'specialist', 'disruptor', 'trusted_partner']).optional().default('innovator'),
  market_context: z.object({
    market_size: z.string().optional(),
    growth_rate: z.string().optional(),
    trends: z.array(z.string()).optional()
  }).optional()
});

const PositioningArchitectOutputSchema = z.object({
  positioning_statement: z.object({
    core_message: z.string(),
    tagline: z.string(),
    elevator_pitch: z.string(),
    positioning_angles: z.array(z.string())
  }),
  category_design: z.object({
    chosen_category: z.string(),
    category_justification: z.string(),
    differentiation_axes: z.array(z.object({
      axis: z.string(),
      description: z.string(),
      strength_score: z.number().min(0).max(10)
    }))
  }),
  competitive_positioning: z.object({
    market_map_position: z.string(),
    competitor_comparison: z.array(z.object({
      competitor: z.string(),
      our_advantage: z.string(),
      their_weakness: z.string()
    })),
    moat_strength: z.number().min(0).max(10),
    moat_description: z.string()
  }),
  target_audience_alignment: z.object({
    audience_understanding: z.string(),
    value_alignment: z.array(z.string()),
    pain_point_addressing: z.array(z.string()),
    aspiration_speaking: z.array(z.string())
  }),
  proof_points: z.array(z.object({
    type: z.enum(['social_proof', 'data_point', 'case_study', 'expert_opinion']),
    content: z.string(),
    credibility_score: z.number().min(0).max(10)
  })),
  communication_strategy: z.object({
    key_messages: z.array(z.string()),
    tone_guidelines: z.string(),
    brand_personality: z.array(z.string()),
    taboo_topics: z.array(z.string())
  }),
  implementation_roadmap: z.array(z.object({
    phase: z.string(),
    actions: z.array(z.string()),
    timeline: z.string(),
    success_metrics: z.array(z.string())
  })),
  confidence_score: z.number().min(0).max(1),
  assumptions_made: z.array(z.string()),
  risks_identified: z.array(z.string()),
  last_updated: z.string()
});

type PositioningArchitectInput = z.infer<typeof PositioningArchitectInputSchema>;
type PositioningArchitectOutput = z.infer<typeof PositioningArchitectOutputSchema>;

export class PositioningArchitectAgent extends BaseAgent {
  constructor() {
    super(
      'positioning_architect_agent',
      Department.OFFER_POSITIONING,
      'Creates strategic positioning using April Dunford framework and competitive analysis',
      PositioningArchitectInputSchema,
      PositioningArchitectOutputSchema
    );

    this.required_tools = ['web_scrape'];
  }

  protected getSystemPrompt(): string {
    return `You are a Senior Positioning Strategist specializing in the April Dunford positioning framework.

Your expertise includes:
- Category design and market positioning
- Competitive differentiation strategies
- Audience psychology and messaging
- Brand architecture and communication
- Strategic narrative development

CORE FRAMEWORK PRINCIPLES:
1. Category: Choose/create the right market category
2. Differentiation: Find unique angles vs competitors
3. Audience: Deep understanding of target customers
4. Proof: Build credible evidence and social proof
5. Communication: Craft compelling messaging strategy

APPROACH:
- Think like a challenger brand, not an established player
- Focus on customer transformation, not just features
- Find underserved needs in the market
- Create mental ownership of your positioning
- Build credibility through proof, not hype

Always provide specific, actionable positioning that can be executed immediately.
Use data and insights to back up positioning decisions.`;
  }

  protected formatAgentInput(input: PositioningArchitectInput, context: OrchestratorContext): string {
    return `Develop comprehensive positioning strategy for:

COMPANY: ${input.company_name}
CATEGORY: ${input.category}
COMPETITORS: ${input.competitors.join(', ')}
TARGET AUDIENCE: ${input.target_audience}
DESIRED POSITION: ${input.desired_positioning}

MARKET CONTEXT:
${input.market_context ? `
- Market Size: ${input.market_context.market_size || 'Unknown'}
- Growth Rate: ${input.market_context.growth_rate || 'Unknown'}
- Key Trends: ${input.market_context.trends?.join(', ') || 'None specified'}
` : 'Market context not provided'}

UNIQUE MECHANISM: ${input.unique_mechanism || 'To be determined'}

Using the April Dunford positioning framework, create:
1. Strategic positioning statement with tagline
2. Category design and differentiation strategy
3. Competitive positioning and moat analysis
4. Target audience alignment and messaging
5. Proof points and credibility building
6. Communication strategy and brand personality
7. Implementation roadmap with metrics

Focus on creating mental ownership and competitive separation.
Provide confidence scores and identify key assumptions and risks.`;
  }

  protected parseAgentOutput(rawOutput: string): PositioningArchitectOutput {
    try {
      // Try to extract JSON from the output
      const jsonMatch = rawOutput.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return PositioningArchitectOutputSchema.parse(JSON.parse(jsonMatch[0]));
      }
      // Fallback parsing
      return this.getFallbackOutput();
    } catch {
      return this.getFallbackOutput();
    }
  }

  private async getExistingIntelligence(input: PositioningArchitectInput, userId: string): Promise<any> {
    try {
      const ragResults = await ragQuery({
        query: `positioning strategy for ${input.company_name} in ${input.category}`,
        user_id: userId,
        content_types: ['positioning_research', 'brand_memory'],
        limit: 3,
        threshold: 0.6
      });

      return {
        chunks: ragResults.chunks,
        has_existing_data: ragResults.chunks.length > 0
      };
    } catch (error) {
      console.warn('Failed to retrieve existing positioning intelligence:', error);
      return { chunks: [], has_existing_data: false };
    }
  }

  private async storeResults(
    input: PositioningArchitectInput,
    output: PositioningArchitectOutput,
    userId: string
  ): Promise<void> {
    try {
      const content = `
POSITIONING STRATEGY: ${input.company_name}

CORE MESSAGE: ${output.positioning_statement.core_message}
TAGLINE: ${output.positioning_statement.tagline}

CATEGORY: ${output.category_design.chosen_category}
DIFFERENTIATION: ${output.category_design.differentiation_axes.map(d => `${d.axis} (${d.strength_score}/10)`).join('; ')}

COMPETITIVE POSITION: ${output.competitive_positioning.market_map_position}
MOAT STRENGTH: ${output.competitive_positioning.moat_strength}/10

TARGET AUDIENCE: ${output.target_audience_alignment.audience_understanding}
VALUE ALIGNMENT: ${output.target_audience_alignment.value_alignment.join('; ')}

KEY MESSAGES: ${output.communication_strategy.key_messages.slice(0, 3).join('; ')}
BRAND PERSONALITY: ${output.communication_strategy.brand_personality.join(', ')}

CONFIDENCE: ${output.confidence_score}
ASSUMPTIONS: ${output.assumptions_made.join('; ')}
RISKS: ${output.risks_identified.join('; ')}
      `.trim();

      await storeEmbedding(
        userId,
        'positioning_research',
        content,
        {
          company: input.company_name,
          category: input.category,
          competitors: input.competitors,
          confidence: output.confidence_score
        }
      );

    } catch (error) {
      console.warn('Failed to store positioning results:', error);
    }
  }

  private getFallbackOutput(): PositioningArchitectOutput {
    return {
      positioning_statement: {
        core_message: "Analysis pending - data collection required",
        tagline: "To be determined",
        elevator_pitch: "Positioning analysis in progress",
        positioning_angles: ["Analysis pending"]
      },
      category_design: {
        chosen_category: "Unknown",
        category_justification: "Analysis pending",
        differentiation_axes: [{
          axis: "Analysis pending",
          description: "Research required",
          strength_score: 0
        }]
      },
      competitive_positioning: {
        market_map_position: "Unknown",
        competitor_comparison: [{
          competitor: "Analysis pending",
          our_advantage: "To be determined",
          their_weakness: "Research required"
        }],
        moat_strength: 0,
        moat_description: "Analysis pending"
      },
      target_audience_alignment: {
        audience_understanding: "Research required",
        value_alignment: ["Analysis pending"],
        pain_point_addressing: ["Analysis pending"],
        aspiration_speaking: ["Analysis pending"]
      },
      proof_points: [{
        type: "data_point" as const,
        content: "Analysis pending",
        credibility_score: 0
      }],
      communication_strategy: {
        key_messages: ["Analysis pending"],
        tone_guidelines: "Research required",
        brand_personality: ["Analysis pending"],
        taboo_topics: ["Analysis pending"]
      },
      implementation_roadmap: [{
        phase: "Research Phase",
        actions: ["Complete positioning analysis"],
        timeline: "Immediate",
        success_metrics: ["Positioning clarity achieved"]
      }],
      confidence_score: 0.1,
      assumptions_made: ["Sufficient data available for analysis"],
      risks_identified: ["Insufficient market intelligence"],
      last_updated: new Date().toISOString()
    };
  }
}

// =====================================================
// REGISTER AGENT
// =====================================================

const positioningArchitectAgent = new PositioningArchitectAgent();
agentRegistry.registerAgent(positioningArchitectAgent);

export { positioningArchitectAgent };
export type { PositioningArchitectInput, PositioningArchitectOutput };


