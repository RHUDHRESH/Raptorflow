import { z } from 'zod';
import { BaseAgent, agentRegistry } from '../base_agent';
import { Department, OrchestratorContext } from '../types';
import { ragQuery, storeEmbedding } from '../rag_helper';

// =====================================================
// VALUE PROPOSITION AGENT
// =====================================================

const ValuePropositionInputSchema = z.object({
  product_name: z.string().describe("Name of the product/service"),
  target_customer: z.string().describe("Primary target customer segment"),
  customer_job: z.string().describe("What the customer is trying to accomplish"),
  current_solution: z.string().optional().describe("How they currently solve this problem"),
  pain_points: z.array(z.string()).describe("Specific pain points they experience"),
  desired_outcomes: z.array(z.string()).describe("Outcomes they want to achieve"),
  emotional_drivers: z.array(z.string()).optional().describe("Emotional motivations and desires"),
  competitors: z.array(z.string()).optional().describe("Main competitors to differentiate from"),
  unique_mechanism: z.string().optional().describe("What makes your solution unique"),
  price_point: z.number().optional().describe("Target price point")
});

const ValuePropositionOutputSchema = z.object({
  core_value_prop: z.object({
    headline: z.string(),
    subheadline: z.string(),
    key_benefits: z.array(z.string()),
    transformation_promise: z.string(),
    unique_value: z.string()
  }),
  customer_understanding: z.object({
    job_to_be_done: z.string(),
    emotional_job: z.string(),
    social_job: z.string(),
    functional_job: z.string(),
    current_alternatives: z.array(z.string()),
    switching_triggers: z.array(z.string())
  }),
  value_quantification: z.object({
    time_saved: z.object({
      hours_per_week: z.number(),
      annual_value: z.string(),
      calculation: z.string()
    }),
    money_saved: z.object({
      amount: z.string(),
      timeframe: z.string(),
      calculation: z.string()
    }),
    risk_reduction: z.object({
      risk_type: z.string(),
      impact_value: z.string(),
      probability_reduction: z.string()
    }),
    opportunity_gained: z.object({
      opportunity: z.string(),
      value: z.string(),
      timeline: z.string()
    }),
    total_economic_value: z.string()
  }),
  differentiation_factors: z.array(z.object({
    factor: z.string(),
    description: z.string(),
    competitive_advantage: z.string(),
    customer_importance: z.number().min(1).max(10)
  })),
  proof_elements: z.array(z.object({
    type: z.enum(['data', 'testimonials', 'case_study', 'comparison', 'guarantee']),
    content: z.string(),
    source: z.string(),
    credibility_score: z.number().min(0).max(10)
  })),
  messaging_framework: z.object({
    hero_message: z.string(),
    supporting_points: z.array(z.string()),
    objection_responses: z.array(z.object({
      objection: z.string(),
      response: z.string(),
      proof: z.string()
    })),
    call_to_action: z.string()
  }),
  positioning_statement: z.object({
    for_statement: z.string(),
    who_statement: z.string(),
    our_statement: z.string(),
    that_statement: z.string(),
    unlike_statement: z.string(),
    our_competitive_advantage: z.string()
  }),
  validation_questions: z.array(z.object({
    question: z.string(),
    purpose: z.string(),
    expected_answer: z.string(),
    validation_method: z.string()
  })),
  implementation_priorities: z.array(z.object({
    element: z.string(),
    priority: z.enum(['critical', 'high', 'medium', 'low']),
    timeline: z.string(),
    dependencies: z.array(z.string()).optional(),
    success_metric: z.string()
  })),
  confidence_score: z.number().min(0).max(1),
  assumptions: z.array(z.string()),
  risks: z.array(z.string()),
  last_updated: z.string()
});

type ValuePropositionInput = z.infer<typeof ValuePropositionInputSchema>;
type ValuePropositionOutput = z.infer<typeof ValuePropositionOutputSchema>;

export class ValuePropositionAgent extends BaseAgent {
  constructor() {
    super(
      'value_proposition_agent',
      Department.OFFER_POSITIONING,
      'Maps customer outcomes to economic value and quantifies transformation impact',
      ValuePropositionInputSchema,
      ValuePropositionOutputSchema
    );

    this.required_tools = ['web_scrape'];
  }

  protected getSystemPrompt(): string {
    return `You are a Value Proposition Specialist who quantifies customer transformation and economic impact.

Your expertise includes:
- Jobs To Be Done (JTBD) analysis
- Economic value quantification
- Customer transformation mapping
- Competitive differentiation
- Value-based pricing foundations
- Proof and credibility building

CORE VALUE FRAMEWORK:
1. Functional Value: What the product does
2. Economic Value: Money/time saved or gained
3. Emotional Value: How it makes customers feel
4. Social Value: How it affects social standing
5. Strategic Value: Long-term competitive advantage

QUANTIFICATION PRINCIPLES:
- Calculate Total Economic Value (TEV)
- Use conservative, verifiable numbers
- Include risk reduction calculations
- Factor in opportunity costs
- Consider implementation costs vs. benefits

APPROACH:
- Start with customer jobs, not product features
- Quantify outcomes, not outputs
- Build credibility through specific numbers
- Create desire through transformation stories
- Differentiate through unique value delivery

Always provide specific, quantifiable value propositions that customers can immediately understand and act upon.`;
  }

  protected formatAgentInput(input: ValuePropositionInput, context: OrchestratorContext): string {
    return `Create a comprehensive value proposition analysis for:

PRODUCT: ${input.product_name}
TARGET CUSTOMER: ${input.target_customer}
CUSTOMER JOB: ${input.customer_job}

CURRENT SOLUTION: ${input.current_solution || 'Various alternatives'}

PAIN POINTS:
${input.pain_points.map(p => `- ${p}`).join('\n')}

DESIRED OUTCOMES:
${input.desired_outcomes.map(o => `- ${o}`).join('\n')}

EMOTIONAL DRIVERS:
${input.emotional_drivers?.map(e => `- ${e}`).join('\n') || 'Not specified'}

COMPETITORS: ${input.competitors?.join(', ') || 'Not specified'}
UNIQUE MECHANISM: ${input.unique_mechanism || 'To be determined'}
PRICE POINT: ${input.price_point ? `$${input.price_point}` : 'Not specified'}

Develop a complete value proposition including:
1. Core value proposition with quantified benefits
2. Customer job analysis (functional, emotional, social)
3. Economic value quantification (time, money, risk, opportunity)
4. Competitive differentiation factors
5. Proof elements and credibility building
6. Messaging framework and positioning statements
7. Validation questions and implementation priorities

Focus on creating undeniable economic and transformation value that makes the price seem insignificant.
Use specific numbers and calculations to build credibility.`;
  }

  protected parseAgentOutput(rawOutput: string): ValuePropositionOutput {
    try {
      // Try to extract JSON from the output
      const jsonMatch = rawOutput.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return ValuePropositionOutputSchema.parse(JSON.parse(jsonMatch[0]));
      }
      // Fallback parsing
      return this.getFallbackOutput();
    } catch {
      return this.getFallbackOutput();
    }
  }

  private async getExistingIntelligence(input: ValuePropositionInput, userId: string): Promise<any> {
    try {
      const ragResults = await ragQuery({
        query: `value proposition for ${input.product_name} targeting ${input.target_customer}`,
        user_id: userId,
        content_types: ['value_proposition', 'customer_research'],
        limit: 3,
        threshold: 0.6
      });

      return {
        chunks: ragResults.chunks,
        has_existing_data: ragResults.chunks.length > 0
      };
    } catch (error) {
      console.warn('Failed to retrieve existing value prop intelligence:', error);
      return { chunks: [], has_existing_data: false };
    }
  }

  private async storeResults(
    input: ValuePropositionInput,
    output: ValuePropositionOutput,
    userId: string
  ): Promise<void> {
    try {
      const content = `
VALUE PROPOSITION: ${input.product_name}

HEADLINE: ${output.core_value_prop.headline}
TRANSFORMATION: ${output.core_value_prop.transformation_promise}
UNIQUE VALUE: ${output.core_value_prop.unique_value}

ECONOMIC VALUE:
- Time Saved: ${output.value_quantification.time_saved.hours_per_week} hours/week
- Money Saved: ${output.value_quantification.money_saved.amount}
- Risk Reduction: ${output.value_quantification.risk_reduction.impact_value}
- Total Economic Value: ${output.value_quantification.total_economic_value}

CUSTOMER JOBS:
- Functional: ${output.customer_understanding.functional_job}
- Emotional: ${output.customer_understanding.emotional_job}
- Social: ${output.customer_understanding.social_job}

DIFFERENTIATION FACTORS: ${output.differentiation_factors.length} key factors
PROOF ELEMENTS: ${output.proof_elements.length} validation points

CONFIDENCE: ${output.confidence_score}
ASSUMPTIONS: ${output.assumptions.join('; ')}
RISKS: ${output.risks.join('; ')}
      `.trim();

      await storeEmbedding(
        userId,
        'value_proposition',
        content,
        {
          product: input.product_name,
          customer: input.target_customer,
          total_value: output.value_quantification.total_economic_value,
          confidence: output.confidence_score
        }
      );

    } catch (error) {
      console.warn('Failed to store value proposition results:', error);
    }
  }

  private getFallbackOutput(): ValuePropositionOutput {
    return {
      core_value_prop: {
        headline: "Analysis pending",
        subheadline: "Research required",
        key_benefits: ["Analysis pending"],
        transformation_promise: "To be determined",
        unique_value: "Research required"
      },
      customer_understanding: {
        job_to_be_done: "Analysis pending",
        emotional_job: "Research required",
        social_job: "To be determined",
        functional_job: "Analysis pending",
        current_alternatives: ["Research required"],
        switching_triggers: ["Analysis pending"]
      },
      value_quantification: {
        time_saved: {
          hours_per_week: 0,
          annual_value: "Analysis pending",
          calculation: "Research required"
        },
        money_saved: {
          amount: "Analysis pending",
          timeframe: "Research required",
          calculation: "To be determined"
        },
        risk_reduction: {
          risk_type: "Analysis pending",
          impact_value: "Research required",
          probability_reduction: "To be determined"
        },
        opportunity_gained: {
          opportunity: "Analysis pending",
          value: "Research required",
          timeline: "To be determined"
        },
        total_economic_value: "Analysis pending"
      },
      differentiation_factors: [{
        factor: "Analysis pending",
        description: "Research required",
        competitive_advantage: "To be determined",
        customer_importance: 5
      }],
      proof_elements: [{
        type: "data" as const,
        content: "Analysis pending",
        source: "Research required",
        credibility_score: 0
      }],
      messaging_framework: {
        hero_message: "Analysis pending",
        supporting_points: ["Research required"],
        objection_responses: [{
          objection: "Analysis pending",
          response: "Research required",
          proof: "To be determined"
        }],
        call_to_action: "Analysis pending"
      },
      positioning_statement: {
        for_statement: "Analysis pending",
        who_statement: "Research required",
        our_statement: "To be determined",
        that_statement: "Analysis pending",
        unlike_statement: "Research required",
        our_competitive_advantage: "To be determined"
      },
      validation_questions: [{
        question: "Analysis pending",
        purpose: "Research required",
        expected_answer: "To be determined",
        validation_method: "Analysis pending"
      }],
      implementation_priorities: [{
        element: "Value Proposition Development",
        priority: "critical" as const,
        timeline: "Immediate",
        dependencies: undefined,
        success_metric: "Value clarity achieved"
      }],
      confidence_score: 0.1,
      assumptions: ["Sufficient customer data available"],
      risks: ["Insufficient value intelligence"],
      last_updated: new Date().toISOString()
    };
  }
}

// =====================================================
// REGISTER AGENT
// =====================================================

const valuePropositionAgent = new ValuePropositionAgent();
agentRegistry.registerAgent(valuePropositionAgent);

export { valuePropositionAgent };
export type { ValuePropositionInput, ValuePropositionOutput };


