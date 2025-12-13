import { z } from 'zod';
import { BaseAgent, agentRegistry } from '../base_agent';
import { Department, OrchestratorContext } from '../types';
import { ragQuery, storeEmbedding } from '../rag_helper';

// =====================================================
// MESSAGE PILLAR AGENT
// =====================================================

const MessagePillarInputSchema = z.object({
  brand_name: z.string().describe("Company/brand name"),
  product_category: z.string().describe("Product/service category"),
  target_audience: z.string().describe("Primary target audience"),
  core_value_prop: z.string().describe("Core value proposition"),
  key_differentiators: z.array(z.string()).describe("Key points of differentiation"),
  brand_personality: z.array(z.string()).optional().describe("Brand personality traits"),
  competitor_messaging: z.array(z.object({
    competitor: z.string(),
    key_message: z.string(),
    weakness: z.string()
  })).optional().describe("Competitor messaging analysis"),
  campaign_goals: z.array(z.string()).optional().describe("Campaign objectives")
});

const MessagePillarOutputSchema = z.object({
  core_message_pillars: z.array(z.object({
    pillar_name: z.string(),
    headline: z.string(),
    description: z.string(),
    key_benefits: z.array(z.string()),
    target_audience: z.string(),
    proof_points: z.array(z.string()),
    emotional_hook: z.string(),
    call_to_action: z.string(),
    pillar_strength: z.number().min(0).max(10),
    usage_context: z.array(z.string())
  })),
  messaging_hierarchy: z.object({
    hero_message: z.string(),
    supporting_messages: z.array(z.string()),
    tactical_messages: z.array(z.string()),
    reinforcement_messages: z.array(z.string())
  }),
  audience_segmentation: z.array(z.object({
    segment_name: z.string(),
    characteristics: z.array(z.string()),
    primary_pillar: z.string(),
    secondary_pillars: z.array(z.string()),
    messaging_tone: z.string(),
    conversion_signals: z.array(z.string())
  })),
  competitive_differentiation: z.object({
    unique_positioning: z.string(),
    competitor_weaknesses: z.array(z.string()),
    messaging_gaps: z.array(z.string()),
    differentiation_opportunities: z.array(z.string())
  }),
  content_themes: z.array(z.object({
    theme_name: z.string(),
    description: z.string(),
    pillar_alignment: z.array(z.string()),
    content_types: z.array(z.string()),
    key_messages: z.array(z.string()),
    target_channels: z.array(z.string())
  })),
  objection_handling: z.array(z.object({
    common_objection: z.string(),
    pillar_response: z.string(),
    supporting_evidence: z.array(z.string()),
    follow_up_messaging: z.string()
  })),
  brand_voice_guidelines: z.object({
    primary_tone: z.string(),
    secondary_tones: z.array(z.string()),
    taboo_words: z.array(z.string()),
    power_words: z.array(z.string()),
    brand_voice_examples: z.array(z.object({
      context: z.string(),
      example_text: z.string(),
      voice_elements: z.array(z.string())
    }))
  }),
  implementation_framework: z.object({
    pillar_rollout: z.array(z.object({
      pillar: z.string(),
      rollout_order: z.number(),
      timeline: z.string(),
      success_metrics: z.array(z.string()),
      dependencies: z.array(z.string())
    })),
    content_calendar: z.object({
      monthly_themes: z.array(z.string()),
      pillar_rotation: z.string(),
      content_mix: z.record(z.number()),
      posting_schedule: z.string()
    }),
    testing_plan: z.array(z.object({
      test_type: z.string(),
      variables: z.array(z.string()),
      sample_size: z.string(),
      success_criteria: z.string()
    }))
  }),
  performance_tracking: z.object({
    key_metrics: z.array(z.object({
      metric_name: z.string(),
      pillar_alignment: z.array(z.string()),
      target_value: z.string(),
      measurement_method: z.string()
    })),
    reporting_cadence: z.string(),
    optimization_triggers: z.array(z.string()),
    pillar_performance_dashboard: z.array(z.string())
  }),
  confidence_score: z.number().min(0).max(1),
  assumptions: z.array(z.string()),
  risks: z.array(z.string()),
  last_updated: z.string()
});

type MessagePillarInput = z.infer<typeof MessagePillarInputSchema>;
type MessagePillarOutput = z.infer<typeof MessagePillarOutputSchema>;

export class MessagePillarAgent extends BaseAgent {
  constructor() {
    super(
      'message_pillar_agent',
      Department.OFFER_POSITIONING,
      'Creates 3-5 core messaging pillars that drive consistent, compelling communication',
      MessagePillarInputSchema,
      MessagePillarOutputSchema
    );

    this.required_tools = ['web_scrape'];
  }

  protected getSystemPrompt(): string {
    return `You are a Messaging Strategy Architect who creates compelling, differentiated communication frameworks.

Your expertise includes:
- Message pillar development and hierarchy
- Audience segmentation and targeting
- Competitive messaging analysis
- Brand voice and personality development
- Content theme creation and alignment
- Objection handling and conversion optimization
- Performance tracking and optimization

CORE MESSAGING PRINCIPLES:
1. Consistency: Same message across all touchpoints
2. Differentiation: Unique positioning vs competitors
3. Proof: Evidence-based claims, not hype
4. Emotion: Connect on human level, not just features
5. Action: Clear calls-to-action that drive behavior

PILLAR DEVELOPMENT FRAMEWORK:
- Hero Pillar: Main value proposition (1 pillar)
- Supporting Pillars: Key benefits/differentiators (2-3 pillars)
- Tactical Pillars: Specific use cases/features (1-2 pillars)

APPROACH:
- Start with audience problems, not product features
- Create emotional connection before logical arguments
- Use social proof and data to build credibility
- Differentiate from competitors, don't just be better
- Test and optimize messaging continuously

Always create messaging that resonates emotionally while delivering logical value. Focus on transformation stories over feature lists.`;
  }

  protected formatAgentInput(input: MessagePillarInput, context: OrchestratorContext): string {
    return `Develop comprehensive messaging pillars for:

BRAND: ${input.brand_name}
CATEGORY: ${input.product_category}
TARGET AUDIENCE: ${input.target_audience}

CORE VALUE PROPOSITION: ${input.core_value_prop}

KEY DIFFERENTIATORS:
${input.key_differentiators.map(d => `- ${d}`).join('\n')}

BRAND PERSONALITY: ${input.brand_personality?.join(', ') || 'Not specified'}

COMPETITOR MESSAGING:
${input.competitor_messaging?.map(c => `${c.competitor}: "${c.key_message}" (Weakness: ${c.weakness})`).join('\n') || 'Not provided'}

CAMPAIGN GOALS: ${input.campaign_goals?.join(', ') || 'Not specified'}

Create a complete messaging framework including:
1. 3-5 core message pillars with headlines, benefits, and proof points
2. Messaging hierarchy (hero, supporting, tactical messages)
3. Audience segmentation with pillar alignment
4. Competitive differentiation opportunities
5. Content themes and channel alignment
6. Objection handling strategies
7. Brand voice guidelines and examples
8. Implementation rollout plan
9. Performance tracking and optimization framework

Focus on creating messaging that cuts through noise, differentiates clearly, and drives action.
Ensure emotional resonance while maintaining credibility and proof.`;
  }

  protected parseAgentOutput(rawOutput: string): MessagePillarOutput {
    try {
      // Try to extract JSON from the output
      const jsonMatch = rawOutput.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return MessagePillarOutputSchema.parse(JSON.parse(jsonMatch[0]));
      }
      // Fallback parsing
      return this.getFallbackOutput();
    } catch {
      return this.getFallbackOutput();
    }
  }

  private async getExistingIntelligence(input: MessagePillarInput, userId: string): Promise<any> {
    try {
      const ragResults = await ragQuery({
        query: `messaging strategy and pillars for ${input.brand_name} in ${input.product_category}`,
        user_id: userId,
        content_types: ['messaging_strategy', 'brand_voice', 'content_themes'],
        limit: 3,
        threshold: 0.6
      });

      return {
        chunks: ragResults.chunks,
        has_existing_data: ragResults.chunks.length > 0
      };
    } catch (error) {
      console.warn('Failed to retrieve existing messaging intelligence:', error);
      return { chunks: [], has_existing_data: false };
    }
  }

  private async storeResults(
    input: MessagePillarInput,
    output: MessagePillarOutput,
    userId: string
  ): Promise<void> {
    try {
      const content = `
MESSAGING PILLARS: ${input.brand_name}

CORE PILLARS: ${output.core_message_pillars.map(p => p.pillar_name).join(', ')}

HERO MESSAGE: ${output.messaging_hierarchy.hero_message}

BRAND VOICE: ${output.brand_voice_guidelines.primary_tone}
POWER WORDS: ${output.brand_voice_guidelines.power_words.slice(0, 5).join(', ')}
TABOO WORDS: ${output.brand_voice_guidelines.taboo_words.join(', ')}

AUDIENCE SEGMENTS: ${output.audience_segmentation.length} defined
CONTENT THEMES: ${output.content_themes.length} developed
OBJECTION HANDLING: ${output.objection_handling.length} strategies

CONFIDENCE: ${output.confidence_score}
ASSUMPTIONS: ${output.assumptions.join('; ')}
RISKS: ${output.risks.join('; ')}
      `.trim();

      await storeEmbedding(
        userId,
        'messaging_strategy',
        content,
        {
          brand: input.brand_name,
          pillars: output.core_message_pillars.length,
          audience_segments: output.audience_segmentation.length,
          confidence: output.confidence_score
        }
      );

    } catch (error) {
      console.warn('Failed to store messaging pillar results:', error);
    }
  }

  private getFallbackOutput(): MessagePillarOutput {
    return {
      core_message_pillars: [{
        pillar_name: "Analysis pending",
        headline: "Research required",
        description: "Messaging analysis in progress",
        key_benefits: ["To be determined"],
        target_audience: "Analysis pending",
        proof_points: ["Research required"],
        emotional_hook: "To be determined",
        call_to_action: "Analysis pending",
        pillar_strength: 0,
        usage_context: ["Analysis pending"]
      }],
      messaging_hierarchy: {
        hero_message: "Analysis pending",
        supporting_messages: ["Research required"],
        tactical_messages: ["To be determined"],
        reinforcement_messages: ["Analysis pending"]
      },
      audience_segmentation: [{
        segment_name: "Analysis pending",
        characteristics: ["Research required"],
        primary_pillar: "To be determined",
        secondary_pillars: [],
        messaging_tone: "Analysis pending",
        conversion_signals: ["Research required"]
      }],
      competitive_differentiation: {
        unique_positioning: "Analysis pending",
        competitor_weaknesses: ["Research required"],
        messaging_gaps: ["To be determined"],
        differentiation_opportunities: ["Analysis pending"]
      },
      content_themes: [{
        theme_name: "Analysis pending",
        description: "Research required",
        pillar_alignment: [],
        content_types: ["To be determined"],
        key_messages: ["Analysis pending"],
        target_channels: ["Research required"]
      }],
      objection_handling: [{
        common_objection: "Analysis pending",
        pillar_response: "Research required",
        supporting_evidence: ["To be determined"],
        follow_up_messaging: "Analysis pending"
      }],
      brand_voice_guidelines: {
        primary_tone: "Analysis pending",
        secondary_tones: [],
        taboo_words: ["Research required"],
        power_words: ["To be determined"],
        brand_voice_examples: [{
          context: "Analysis pending",
          example_text: "Research required",
          voice_elements: ["To be determined"]
        }]
      },
      implementation_framework: {
        pillar_rollout: [{
          pillar: "Analysis pending",
          rollout_order: 1,
          timeline: "Research required",
          success_metrics: ["To be determined"],
          dependencies: []
        }],
        content_calendar: {
          monthly_themes: ["Analysis pending"],
          pillar_rotation: "Research required",
          content_mix: {},
          posting_schedule: "To be determined"
        },
        testing_plan: [{
          test_type: "Messaging Test",
          variables: ["pillar_variants"],
          sample_size: "100+ responses",
          success_criteria: "15%+ conversion improvement"
        }]
      },
      performance_tracking: {
        key_metrics: [{
          metric_name: "Conversion Rate",
          pillar_alignment: ["All pillars"],
          target_value: "15%+ improvement",
          measurement_method: "A/B testing"
        }],
        reporting_cadence: "Weekly",
        optimization_triggers: ["5% performance drop"],
        pillar_performance_dashboard: ["Conversion by pillar", "Engagement metrics"]
      },
      confidence_score: 0.1,
      assumptions: ["Sufficient audience data available"],
      risks: ["Insufficient messaging intelligence"],
      last_updated: new Date().toISOString()
    };
  }
}

// =====================================================
// REGISTER AGENT
// =====================================================

const messagePillarAgent = new MessagePillarAgent();
agentRegistry.registerAgent(messagePillarAgent);

export { messagePillarAgent };
export type { MessagePillarInput, MessagePillarOutput };


