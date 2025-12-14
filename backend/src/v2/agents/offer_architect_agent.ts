import { z } from 'zod';
import { BaseAgent, agentRegistry } from '../base_agent';
import { Department, OrchestratorContext } from '../types';
import { ragQuery, storeEmbedding } from '../rag_helper';

// =====================================================
// OFFER ARCHITECT AGENT
// =====================================================

const OfferArchitectInputSchema = z.object({
  product_name: z.string().describe("Name of the product/service"),
  product_type: z.enum(['saas', 'consulting', 'physical_product', 'digital_product', 'course', 'membership']).describe("Type of product"),
  target_customer: z.string().describe("Primary target customer profile"),
  customer_pain: z.string().describe("Main customer pain point to solve"),
  desired_outcome: z.string().describe("Desired customer outcome/transformation"),
  price_range: z.object({
    min: z.number().optional(),
    max: z.number().optional(),
    currency: z.string().default('USD')
  }).optional(),
  business_model: z.enum(['subscription', 'one_time', 'freemium', 'commission', 'licensing']).optional(),
  competitors_pricing: z.array(z.object({
    competitor: z.string(),
    price: z.number(),
    model: z.string()
  })).optional()
});

const OfferArchitectOutputSchema = z.object({
  core_offer: z.object({
    name: z.string(),
    headline: z.string(),
    subheadline: z.string(),
    description: z.string(),
    key_features: z.array(z.string()),
    transformation_promise: z.string()
  }),
  pricing_strategy: z.object({
    recommended_price: z.number(),
    pricing_model: z.string(),
    price_justification: z.string(),
    competitor_comparison: z.array(z.object({
      competitor: z.string(),
      their_price: z.number(),
      our_positioning: z.string(),
      differentiation: z.string()
    })),
    psychological_pricing: z.object({
      strategy: z.string(),
      reasoning: z.string(),
      expected_conversion_impact: z.string()
    })
  }),
  bonuses_and_incentives: z.array(z.object({
    name: z.string(),
    description: z.string(),
    value: z.string(),
    scarcity: z.string().optional(),
    urgency: z.string().optional()
  })),
  guarantees: z.array(z.object({
    type: z.enum(['money_back', 'results', 'satisfaction', 'support', 'custom']),
    description: z.string(),
    duration: z.string(),
    conditions: z.string(),
    credibility_impact: z.string()
  })),
  scarcity_elements: z.array(z.object({
    element: z.string(),
    implementation: z.string(),
    psychological_impact: z.string(),
    ethical_considerations: z.string()
  })),
  value_stack: z.object({
    core_value: z.string(),
    bonuses_value: z.string(),
    total_value: z.string(),
    perceived_value_ratio: z.number(),
    justification: z.string()
  }),
  objection_handling: z.array(z.object({
    common_objection: z.string(),
    response_strategy: z.string(),
    proof_point: z.string(),
    follow_up_action: z.string()
  })),
  implementation_plan: z.array(z.object({
    component: z.string(),
    description: z.string(),
    timeline: z.string(),
    dependencies: z.array(z.string()).optional(),
    success_criteria: z.string()
  })),
  conversion_optimization: z.object({
    key_copy_elements: z.array(z.string()),
    psychological_triggers: z.array(z.string()),
    risk_reversal_elements: z.array(z.string()),
    social_proof_suggestions: z.array(z.string())
  }),
  testing_recommendations: z.array(z.object({
    test_type: z.string(),
    variables: z.array(z.string()),
    expected_outcome: z.string(),
    sample_size: z.string()
  })),
  confidence_score: z.number().min(0).max(1),
  assumptions: z.array(z.string()),
  risks: z.array(z.string()),
  last_updated: z.string()
});

type OfferArchitectInput = z.infer<typeof OfferArchitectInputSchema>;
type OfferArchitectOutput = z.infer<typeof OfferArchitectOutputSchema>;

export class OfferArchitectAgent extends BaseAgent {
  constructor() {
    super(
      'offer_architect_agent',
      Department.OFFER_POSITIONING,
      'Designs irresistible offers with pricing, bonuses, guarantees, and scarcity elements',
      OfferArchitectInputSchema,
      OfferArchitectOutputSchema
    );

    this.required_tools = ['web_scrape'];
  }

  protected getSystemPrompt(): string {
    return `You are a Master Offer Architect specializing in creating irresistible offers that drive conversions.

Your expertise includes:
- Value stacking and perceived value maximization
- Psychological pricing and scarcity engineering
- Risk reversal through guarantees and bonuses
- Competitive positioning in pricing
- Conversion optimization through copy and psychology
- Ethical offer design that builds trust

CORE OFFER DESIGN PRINCIPLES:
1. Value Stack: Core product + bonuses + guarantees > price paid
2. Risk Reversal: Remove all perceived risk from purchase
3. Scarcity & Urgency: Create FOMO without manipulation
4. Social Proof: Build credibility through testimonials and data
5. Objection Preemption: Handle concerns before they arise

APPROACH:
- Start with customer transformation, not features
- Use bonuses to increase perceived value dramatically
- Employ multiple guarantee types for complete risk removal
- Price based on value delivered, not costs incurred
- Test and optimize continuously

Always design offers that customers cannot refuse while maintaining ethical standards and building long-term trust.`;
  }

  protected formatAgentInput(input: OfferArchitectInput, context: OrchestratorContext): string {
    return `Design a comprehensive, irresistible offer for:

PRODUCT: ${input.product_name}
TYPE: ${input.product_type}
TARGET CUSTOMER: ${input.target_customer}
MAIN PAIN: ${input.customer_pain}
DESIRED OUTCOME: ${input.desired_outcome}

PRICING CONSTRAINTS:
${input.price_range ? `
- Min Price: ${input.price_range.currency} ${input.price_range.min || 'Not specified'}
- Max Price: ${input.price_range.currency} ${input.price_range.max || 'Not specified'}
- Currency: ${input.price_range.currency}
` : 'No pricing constraints specified'}

BUSINESS MODEL: ${input.business_model || 'Not specified'}

COMPETITOR PRICING:
${input.competitors_pricing?.map(c => `- ${c.competitor}: ${c.price} (${c.model})`).join('\n') || 'No competitor data provided'}

Create a complete offer architecture including:
1. Core offer with transformation promise
2. Strategic pricing with psychological elements
3. Bonuses and incentives that multiply value
4. Multiple guarantee types for risk reversal
5. Scarcity elements for urgency creation
6. Complete value stack analysis
7. Objection handling strategies
8. Implementation timeline and testing plan

Focus on creating an offer so compelling that customers feel they're getting an unfair advantage.
Use psychological principles ethically to maximize conversions while building trust.`;
  }

  protected parseAgentOutput(rawOutput: string): OfferArchitectOutput {
    try {
      // Try to extract JSON from the output
      const jsonMatch = rawOutput.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return OfferArchitectOutputSchema.parse(JSON.parse(jsonMatch[0]));
      }
      // Fallback parsing
      return this.getFallbackOutput();
    } catch {
      return this.getFallbackOutput();
    }
  }

  private async getExistingIntelligence(input: OfferArchitectInput, userId: string): Promise<any> {
    try {
      const ragResults = await ragQuery({
        query: `offer design and pricing for ${input.product_name} ${input.product_type}`,
        user_id: userId,
        content_types: ['offer_research', 'pricing_strategy'],
        limit: 3,
        threshold: 0.6
      });

      return {
        chunks: ragResults.chunks,
        has_existing_data: ragResults.chunks.length > 0
      };
    } catch (error) {
      console.warn('Failed to retrieve existing offer intelligence:', error);
      return { chunks: [], has_existing_data: false };
    }
  }

  private async storeResults(
    input: OfferArchitectInput,
    output: OfferArchitectOutput,
    userId: string
  ): Promise<void> {
    try {
      const content = `
OFFER ARCHITECTURE: ${input.product_name}

CORE OFFER: ${output.core_offer.name}
HEADLINE: ${output.core_offer.headline}
PRICE: ${output.pricing_strategy.recommended_price}
MODEL: ${output.pricing_strategy.pricing_model}

VALUE STACK:
- Core Value: ${output.value_stack.core_value}
- Bonuses Value: ${output.value_stack.bonuses_value}
- Total Value: ${output.value_stack.total_value}
- Value Ratio: ${output.value_stack.perceived_value_ratio}x

GUARANTEES: ${output.guarantees.map(g => g.type).join(', ')}
BONUSES: ${output.bonuses_and_incentives.length} bonuses
SCARCITY ELEMENTS: ${output.scarcity_elements.length} elements

CONFIDENCE: ${output.confidence_score}
ASSUMPTIONS: ${output.assumptions.join('; ')}
RISKS: ${output.risks.join('; ')}
      `.trim();

      await storeEmbedding(
        userId,
        'offer_research',
        content,
        {
          product: input.product_name,
          type: input.product_type,
          price: output.pricing_strategy.recommended_price,
          confidence: output.confidence_score
        }
      );

    } catch (error) {
      console.warn('Failed to store offer results:', error);
    }
  }

  private getFallbackOutput(): OfferArchitectOutput {
    return {
      core_offer: {
        name: "Analysis pending",
        headline: "To be determined",
        subheadline: "Research required",
        description: "Offer analysis in progress",
        key_features: ["Analysis pending"],
        transformation_promise: "To be determined"
      },
      pricing_strategy: {
        recommended_price: 0,
        pricing_model: "Analysis pending",
        price_justification: "Research required",
        competitor_comparison: [{
          competitor: "Analysis pending",
          their_price: 0,
          our_positioning: "Research required",
          differentiation: "Analysis pending"
        }],
        psychological_pricing: {
          strategy: "Analysis pending",
          reasoning: "Research required",
          expected_conversion_impact: "Unknown"
        }
      },
      bonuses_and_incentives: [{
        name: "Analysis pending",
        description: "Research required",
        value: "To be determined",
        scarcity: undefined,
        urgency: undefined
      }],
      guarantees: [{
        type: "money_back" as const,
        description: "Analysis pending",
        duration: "Research required",
        conditions: "To be determined",
        credibility_impact: "Unknown"
      }],
      scarcity_elements: [{
        element: "Analysis pending",
        implementation: "Research required",
        psychological_impact: "Unknown",
        ethical_considerations: "Analysis pending"
      }],
      value_stack: {
        core_value: "Analysis pending",
        bonuses_value: "Research required",
        total_value: "To be determined",
        perceived_value_ratio: 0,
        justification: "Research required"
      },
      objection_handling: [{
        common_objection: "Analysis pending",
        response_strategy: "Research required",
        proof_point: "To be determined",
        follow_up_action: "Analysis pending"
      }],
      implementation_plan: [{
        component: "Offer Design",
        description: "Complete offer architecture analysis",
        timeline: "Immediate",
        dependencies: undefined,
        success_criteria: "Offer clarity achieved"
      }],
      conversion_optimization: {
        key_copy_elements: ["Analysis pending"],
        psychological_triggers: ["Research required"],
        risk_reversal_elements: ["Analysis pending"],
        social_proof_suggestions: ["To be determined"]
      },
      testing_recommendations: [{
        test_type: "Pricing Test",
        variables: ["price_points"],
        expected_outcome: "Optimal price identification",
        sample_size: "100+ conversions"
      }],
      confidence_score: 0.1,
      assumptions: ["Sufficient market data available"],
      risks: ["Insufficient offer intelligence"],
      last_updated: new Date().toISOString()
    };
  }
}

// =====================================================
// REGISTER AGENT
// =====================================================

const offerArchitectAgent = new OfferArchitectAgent();
agentRegistry.registerAgent(offerArchitectAgent);

export { offerArchitectAgent };
export type { OfferArchitectInput, OfferArchitectOutput };


