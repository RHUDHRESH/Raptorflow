import { z } from 'zod';
import { BaseAgent, agentRegistry } from '../base_agent';
import { Department, OrchestratorContext } from '../types';
import { ragQuery, storeEmbedding } from '../rag_helper';

// =====================================================
// REVENUE MODEL AGENT
// =====================================================

const RevenueModelInputSchema = z.object({
  product_name: z.string().describe("Name of the product/service"),
  business_model: z.enum(['subscription', 'one_time', 'freemium', 'commission', 'licensing', 'marketplace']).describe("Primary business model"),
  target_market_size: z.object({
    tam: z.number().describe("Total Addressable Market in dollars"),
    sam: z.number().describe("Serviceable Addressable Market in dollars"),
    som: z.number().describe("Serviceable Obtainable Market in dollars")
  }).describe("Market size estimates"),
  customer_acquisition: z.object({
    channels: z.array(z.string()).describe("Acquisition channels used"),
    estimated_cac: z.number().optional().describe("Current Customer Acquisition Cost"),
    conversion_rates: z.record(z.number()).optional().describe("Conversion rates by funnel stage")
  }).describe("Customer acquisition data"),
  pricing_strategy: z.object({
    current_price: z.number().optional().describe("Current price point"),
    target_price: z.number().optional().describe("Target price point"),
    competitor_prices: z.array(z.number()).optional().describe("Competitor price points")
  }).optional().describe("Current pricing information"),
  unit_economics: z.object({
    variable_costs: z.number().optional().describe("Variable costs per customer"),
    fixed_costs: z.number().optional().describe("Fixed costs allocation"),
    gross_margin_target: z.number().optional().describe("Target gross margin percentage")
  }).optional().describe("Cost structure"),
  growth_targets: z.object({
    monthly_revenue_target: z.number().optional().describe("Monthly recurring revenue target"),
    customer_growth_rate: z.number().optional().describe("Monthly customer growth rate"),
    churn_rate: z.number().optional().describe("Monthly churn rate")
  }).optional().describe("Business growth objectives")
});

const RevenueModelOutputSchema = z.object({
  optimal_pricing: z.object({
    recommended_price: z.number(),
    pricing_model: z.string(),
    price_justification: z.object({
      value_based: z.string(),
      competitive: z.string(),
      cost_plus: z.string(),
      psychological: z.string()
    }),
    price_elasticity: z.object({
      estimated_elasticity: z.number(),
      price_sensitivity: z.enum(['high', 'medium', 'low']),
      optimal_range: z.object({
        minimum: z.number(),
        maximum: z.number(),
        recommended: z.number()
      })
    }),
    tier_structure: z.array(z.object({
      tier_name: z.string(),
      price: z.number(),
      features: z.array(z.string()),
      target_customer: z.string(),
      expected_conversion: z.number()
    })).optional()
  }),
  unit_economics: z.object({
    customer_lifetime_value: z.object({
      clv_calculation: z.number(),
      assumptions: z.array(z.string()),
      sensitivity_analysis: z.array(z.object({
        variable: z.string(),
        impact: z.string(),
        breakeven_point: z.number()
      }))
    }),
    customer_acquisition_cost: z.object({
      cac_calculation: z.number(),
      channel_breakdown: z.record(z.number()),
      optimization_opportunities: z.array(z.string()),
      payback_period: z.object({
        months: z.number(),
        optimization_target: z.number()
      })
    }),
    profitability_metrics: z.object({
      gross_margin: z.number(),
      contribution_margin: z.number(),
      customer_profitability: z.number(),
      scalability_factor: z.number()
    }),
    break_even_analysis: z.object({
      monthly_break_even: z.number(),
      customer_break_even: z.number(),
      time_to_profitability: z.string(),
      risk_factors: z.array(z.string())
    })
  }),
  revenue_projections: z.object({
    monthly_recurring_revenue: z.array(z.object({
      month: z.number(),
      revenue: z.number(),
      customers: z.number(),
      churn_rate: z.number(),
      growth_rate: z.number()
    })),
    annual_run_rate: z.object({
      current: z.number(),
      projected_12_months: z.number(),
      confidence_level: z.enum(['high', 'medium', 'low'])
    }),
    revenue_mix: z.object({
      primary_revenue_stream: z.string(),
      secondary_streams: z.array(z.string()),
      diversification_index: z.number()
    })
  }),
  growth_strategies: z.array(z.object({
    strategy_name: z.string(),
    description: z.string(),
    revenue_impact: z.object({
      immediate: z.number(),
      year_1: z.number(),
      year_2: z.number()
    }),
    implementation_complexity: z.enum(['low', 'medium', 'high']),
    resource_requirements: z.array(z.string()),
    success_probability: z.number(),
    key_risks: z.array(z.string())
  })),
  risk_assessment: z.object({
    revenue_risks: z.array(z.object({
      risk: z.string(),
      probability: z.enum(['low', 'medium', 'high']),
      impact: z.enum(['low', 'medium', 'high']),
      mitigation_strategy: z.string()
    })),
    market_risks: z.array(z.object({
      risk: z.string(),
      probability: z.enum(['low', 'medium', 'high']),
      impact: z.enum(['low', 'medium', 'high']),
      mitigation_strategy: z.string()
    })),
    competitive_risks: z.array(z.object({
      risk: z.string(),
      probability: z.enum(['low', 'medium', 'high']),
      impact: z.enum(['low', 'medium', 'high']),
      mitigation_strategy: z.string()
    }))
  }),
  optimization_recommendations: z.array(z.object({
    recommendation: z.string(),
    expected_impact: z.object({
      revenue_increase: z.number(),
      timeline: z.string(),
      confidence: z.number()
    }),
    implementation_steps: z.array(z.string()),
    kpis_to_track: z.array(z.string()),
    priority: z.enum(['critical', 'high', 'medium', 'low'])
  })),
  financial_projections: z.object({
    year_1_revenue: z.number(),
    year_2_revenue: z.number(),
    year_3_revenue: z.number(),
    profitability_timeline: z.string(),
    funding_requirements: z.object({
      amount: z.number(),
      use_of_funds: z.array(z.string()),
      runway_extension: z.string()
    }),
    exit_valuation: z.object({
      conservative: z.number(),
      realistic: z.number(),
      optimistic: z.number(),
      valuation_method: z.string()
    })
  }),
  confidence_score: z.number().min(0).max(1),
  data_quality_assessment: z.object({
    data_completeness: z.number().min(0).max(1),
    data_accuracy: z.number().min(0).max(1),
    assumptions_validity: z.number().min(0).max(1),
    risk_adjustment_factor: z.number()
  }),
  assumptions: z.array(z.string()),
  limitations: z.array(z.string()),
  last_updated: z.string()
});

type RevenueModelInput = z.infer<typeof RevenueModelInputSchema>;
type RevenueModelOutput = z.infer<typeof RevenueModelOutputSchema>;

export class RevenueModelAgent extends BaseAgent {
  constructor() {
    super(
      'revenue_model_agent',
      Department.OFFER_POSITIONING,
      'Calculates CAC/LTV metrics, optimizes pricing strategy, and builds financial projections',
      RevenueModelInputSchema,
      RevenueModelOutputSchema
    );

    this.required_tools = ['web_scrape'];
  }

  protected getSystemPrompt(): string {
    return `You are a Revenue Optimization Specialist who builds profitable, scalable business models.

Your expertise includes:
- Unit economics analysis and optimization
- Pricing strategy and price elasticity modeling
- Customer lifetime value calculations
- Financial projections and scenario planning
- Growth strategy evaluation and prioritization
- Risk assessment and mitigation planning
- Competitive positioning and market analysis

CORE FINANCIAL PRINCIPLES:
1. LTV > CAC (always): Customer lifetime value must exceed acquisition cost
2. Unit Economics: Focus on profitable customer cohorts, not vanity metrics
3. Scalability: Revenue models that improve with scale, not deteriorate
4. Risk-Adjusted: Conservative projections with clear assumption documentation
5. Market-Driven: Pricing based on value delivered, not costs incurred

ANALYSIS FRAMEWORK:
- Top-Down: Market size, competitive landscape, pricing power
- Bottom-Up: Unit economics, customer profitability, scalability factors
- Risk Analysis: Sensitivity testing, scenario planning, mitigation strategies
- Growth Modeling: Sustainable growth rates, market penetration, competitive dynamics

APPROACH:
- Start with unit economics, not revenue projections
- Build conservative financial models with clear assumptions
- Focus on sustainable profitability over rapid growth
- Price for value delivered, not cost-plus markup
- Optimize for long-term shareholder value, not short-term metrics

Always provide data-driven recommendations with clear risk assessments and implementation priorities.`;
  }

  protected formatAgentInput(input: RevenueModelInput, context: OrchestratorContext): string {
    return `Build comprehensive revenue model and financial projections for:

PRODUCT: ${input.product_name}
BUSINESS MODEL: ${input.business_model}

MARKET SIZE:
- TAM: $${input.target_market_size.tam.toLocaleString()}
- SAM: $${input.target_market_size.sam.toLocaleString()}
- SOM: $${input.target_market_size.som.toLocaleString()}

CUSTOMER ACQUISITION:
- Channels: ${input.customer_acquisition.channels.join(', ')}
- Estimated CAC: ${input.customer_acquisition.estimated_cac ? `$${input.customer_acquisition.estimated_cac}` : 'Unknown'}
- Conversion Rates: ${JSON.stringify(input.customer_acquisition.conversion_rates || {})}

PRICING:
- Current Price: ${input.pricing_strategy?.current_price ? `$${input.pricing_strategy.current_price}` : 'Not set'}
- Target Price: ${input.pricing_strategy?.target_price ? `$${input.pricing_strategy.target_price}` : 'Not set'}
- Competitor Prices: ${input.pricing_strategy?.competitor_prices?.map(p => `$${p}`).join(', ') || 'Unknown'}

COST STRUCTURE:
- Variable Costs: ${input.unit_economics?.variable_costs ? `$${input.unit_economics.variable_costs}` : 'Unknown'}
- Fixed Costs: ${input.unit_economics?.fixed_costs ? `$${input.unit_economics.fixed_costs}` : 'Unknown'}
- Target Margin: ${input.unit_economics?.gross_margin_target ? `${input.unit_economics.gross_margin_target}%` : 'Unknown'}

GROWTH TARGETS:
- Monthly Revenue: ${input.growth_targets?.monthly_revenue_target ? `$${input.growth_targets.monthly_revenue_target.toLocaleString()}` : 'Not set'}
- Customer Growth: ${input.growth_targets?.customer_growth_rate ? `${input.growth_targets.customer_growth_rate}% monthly` : 'Not set'}
- Churn Rate: ${input.growth_targets?.churn_rate ? `${input.growth_targets.churn_rate}% monthly` : 'Not set'}

Develop a complete revenue optimization framework including:
1. Optimal pricing strategy with tier structure
2. Unit economics analysis (LTV, CAC, margins)
3. Revenue projections and growth modeling
4. Risk assessment and mitigation strategies
5. Growth strategy prioritization
6. Financial projections and funding requirements

Focus on sustainable profitability and scalable unit economics.
Provide conservative estimates with clear assumptions and risk adjustments.`;
  }

  protected parseAgentOutput(rawOutput: string): RevenueModelOutput {
    try {
      // Try to extract JSON from the output
      const jsonMatch = rawOutput.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return RevenueModelOutputSchema.parse(JSON.parse(jsonMatch[0]));
      }
      // Fallback parsing
      return this.getFallbackOutput();
    } catch {
      return this.getFallbackOutput();
    }
  }

  private async getExistingIntelligence(input: RevenueModelInput, userId: string): Promise<any> {
    try {
      const ragResults = await ragQuery({
        query: `revenue model and pricing for ${input.product_name} ${input.business_model}`,
        user_id: userId,
        content_types: ['revenue_model', 'pricing_strategy', 'financial_projections'],
        limit: 3,
        threshold: 0.6
      });

      return {
        chunks: ragResults.chunks,
        has_existing_data: ragResults.chunks.length > 0
      };
    } catch (error) {
      console.warn('Failed to retrieve existing revenue intelligence:', error);
      return { chunks: [], has_existing_data: false };
    }
  }

  private async storeResults(
    input: RevenueModelInput,
    output: RevenueModelOutput,
    userId: string
  ): Promise<void> {
    try {
      const content = `
REVENUE MODEL: ${input.product_name}

OPTIMAL PRICING: $${output.optimal_pricing.recommended_price}
MODEL: ${output.optimal_pricing.pricing_model}

UNIT ECONOMICS:
- CLV: $${output.unit_economics.customer_lifetime_value.clv_calculation}
- CAC: $${output.unit_economics.customer_acquisition_cost.cac_calculation}
- Gross Margin: ${output.unit_economics.profitability_metrics.gross_margin}%
- Payback Period: ${output.unit_economics.customer_acquisition_cost.payback_period.months} months

REVENUE PROJECTIONS:
- Year 1: $${output.financial_projections.year_1_revenue.toLocaleString()}
- Year 2: $${output.financial_projections.year_2_revenue.toLocaleString()}
- Year 3: $${output.financial_projections.year_3_revenue.toLocaleString()}

GROWTH STRATEGIES: ${output.growth_strategies.length} recommended
OPTIMIZATION RECS: ${output.optimization_recommendations.length} identified

CONFIDENCE: ${output.confidence_score}
DATA QUALITY: ${output.data_quality_assessment.data_completeness * 100}% complete
ASSUMPTIONS: ${output.assumptions.join('; ')}
      `.trim();

      await storeEmbedding(
        userId,
        'revenue_model',
        content,
        {
          product: input.product_name,
          clv: output.unit_economics.customer_lifetime_value.clv_calculation,
          cac: output.unit_economics.customer_acquisition_cost.cac_calculation,
          year_1_revenue: output.financial_projections.year_1_revenue,
          confidence: output.confidence_score
        }
      );

    } catch (error) {
      console.warn('Failed to store revenue model results:', error);
    }
  }

  private getFallbackOutput(): RevenueModelOutput {
    return {
      optimal_pricing: {
        recommended_price: 0,
        pricing_model: "Analysis pending",
        price_justification: {
          value_based: "Research required",
          competitive: "Analysis pending",
          cost_plus: "To be determined",
          psychological: "Research required"
        },
        price_elasticity: {
          estimated_elasticity: 0,
          price_sensitivity: "medium" as const,
          optimal_range: {
            minimum: 0,
            maximum: 0,
            recommended: 0
          }
        },
        tier_structure: [{
          tier_name: "Basic",
          price: 0,
          features: ["Analysis pending"],
          target_customer: "Research required",
          expected_conversion: 0
        }]
      },
      unit_economics: {
        customer_lifetime_value: {
          clv_calculation: 0,
          assumptions: ["Analysis pending"],
          sensitivity_analysis: [{
            variable: "Churn rate",
            impact: "High",
            breakeven_point: 0
          }]
        },
        customer_acquisition_cost: {
          cac_calculation: 0,
          channel_breakdown: {},
          optimization_opportunities: ["Analysis pending"],
          payback_period: {
            months: 0,
            optimization_target: 12
          }
        },
        profitability_metrics: {
          gross_margin: 0,
          contribution_margin: 0,
          customer_profitability: 0,
          scalability_factor: 0
        },
        break_even_analysis: {
          monthly_break_even: 0,
          customer_break_even: 0,
          time_to_profitability: "Analysis pending",
          risk_factors: ["Insufficient data"]
        }
      },
      revenue_projections: {
        monthly_recurring_revenue: Array.from({ length: 12 }, (_, i) => ({
          month: i + 1,
          revenue: 0,
          customers: 0,
          churn_rate: 0,
          growth_rate: 0
        })),
        annual_run_rate: {
          current: 0,
          projected_12_months: 0,
          confidence_level: "low" as const
        },
        revenue_mix: {
          primary_revenue_stream: "Analysis pending",
          secondary_streams: [],
          diversification_index: 0
        }
      },
      growth_strategies: [{
        strategy_name: "Market penetration",
        description: "Analysis pending",
        revenue_impact: {
          immediate: 0,
          year_1: 0,
          year_2: 0
        },
        implementation_complexity: "medium" as const,
        resource_requirements: ["Analysis pending"],
        success_probability: 0.5,
        key_risks: ["Insufficient data"]
      }],
      risk_assessment: {
        revenue_risks: [{
          risk: "Insufficient data for analysis",
          probability: "high" as const,
          impact: "high" as const,
          mitigation_strategy: "Complete market research"
        }],
        market_risks: [{
          risk: "Market analysis pending",
          probability: "medium" as const,
          impact: "medium" as const,
          mitigation_strategy: "Conduct market research"
        }],
        competitive_risks: [{
          risk: "Competitive analysis pending",
          probability: "medium" as const,
          impact: "medium" as const,
          mitigation_strategy: "Complete competitor analysis"
        }]
      },
      optimization_recommendations: [{
        recommendation: "Complete unit economics analysis",
        expected_impact: {
          revenue_increase: 0,
          timeline: "3 months",
          confidence: 0.8
        },
        implementation_steps: ["Gather cost data", "Calculate LTV/CAC", "Optimize pricing"],
        kpis_to_track: ["Gross margin", "Customer profitability"],
        priority: "critical" as const
      }],
      financial_projections: {
        year_1_revenue: 0,
        year_2_revenue: 0,
        year_3_revenue: 0,
        profitability_timeline: "Analysis pending",
        funding_requirements: {
          amount: 0,
          use_of_funds: ["Analysis pending"],
          runway_extension: "Research required"
        },
        exit_valuation: {
          conservative: 0,
          realistic: 0,
          optimistic: 0,
          valuation_method: "Analysis pending"
        }
      },
      confidence_score: 0.1,
      data_quality_assessment: {
        data_completeness: 0.1,
        data_accuracy: 0.5,
        assumptions_validity: 0.3,
        risk_adjustment_factor: 0.5
      },
      assumptions: ["Sufficient financial data available", "Market conditions stable"],
      limitations: ["Limited historical data", "Market assumptions unvalidated"],
      last_updated: new Date().toISOString()
    };
  }
}

// =====================================================
// REGISTER AGENT
// =====================================================

const revenueModelAgent = new RevenueModelAgent();
agentRegistry.registerAgent(revenueModelAgent);

export { revenueModelAgent };
export type { RevenueModelInput, RevenueModelOutput };


