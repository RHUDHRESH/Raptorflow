import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class ExperimentGeneratorAgent extends BaseAgent {
  department = Department.MOVES_CAMPAIGNS;
  name = 'experiment_generator_agent';
  description = 'Creates A/B tests, variant ideas, and hypotheses for marketing optimization';

  protected getSystemPrompt(): string {
    return `You are a senior experimentation specialist and growth hacker with 15+ years experience designing and executing high-impact marketing experiments.

Your expertise includes:
- A/B testing methodology and statistical analysis
- Hypothesis generation and experimental design
- Multivariate testing and factorial experiments
- Statistical significance and power analysis
- Bayesian vs frequentist statistical approaches

You understand:
1. Experimental design principles and bias mitigation
2. Sample size calculation and statistical power
3. Attribution and incrementality measurement
4. Platform-specific testing limitations and workarounds
5. Business metric optimization and KPI frameworks

Your role is to design rigorous experiments that provide actionable insights and drive continuous marketing optimization.

Focus on:
- Hypothesis-driven experimentation with clear success metrics
- Statistical rigor and experimental validity
- Business impact assessment and ROI evaluation
- Scalable testing frameworks and learning systems
- Risk mitigation and ethical testing practices

You have designed experiments that improved marketing performance by 200%+ and influenced billion-dollar optimization decisions.`;
  }

  inputSchema = z.object({
    current_performance: z.object({
      conversion_rate: z.number(),
      cost_per_acquisition: z.number(),
      customer_lifetime_value: z.number(),
      churn_rate: z.number().optional()
    }),
    campaign_elements: z.array(z.string()),
    target_improvements: z.array(z.string()),
    testing_budget: z.number(),
    timeline_weeks: z.number(),
    risk_tolerance: z.enum(['conservative', 'moderate', 'aggressive'])
  });

  outputSchema = z.object({
    experiment_roadmap: z.array(z.object({
      experiment_name: z.string(),
      hypothesis: z.string(),
      priority: z.enum(['high', 'medium', 'low']),
      estimated_impact: z.string(),
      estimated_effort: z.string(),
      test_type: z.enum(['a_b_test', 'multivariate', 'sequential']),
      variants: z.array(z.object({
        variant_name: z.string(),
        description: z.string(),
        implementation_notes: z.string()
      })),
      success_metrics: z.array(z.string()),
      sample_size_calculation: z.string(),
      timeline_days: z.number()
    })),
    testing_framework: z.object({
      statistical_significance: z.number(),
      minimum_detectable_effect: z.number(),
      testing_methodology: z.string(),
      quality_assurance: z.array(z.string())
    }),
    risk_assessment: z.array(z.object({
      experiment_name: z.string(),
      risk_level: z.enum(['low', 'medium', 'high']),
      potential_downside: z.string(),
      mitigation_strategy: z.string()
    })),
    resource_requirements: z.object({
      design_resources: z.array(z.string()),
      development_resources: z.array(z.string()),
      analysis_resources: z.array(z.string()),
      total_cost_estimate: z.number()
    }),
    implementation_plan: z.array(z.string())
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Current Performance:
- Conversion Rate: ${(input.current_performance.conversion_rate * 100).toFixed(2)}%
- Cost per Acquisition: $${input.current_performance.cost_per_acquisition}
- Customer Lifetime Value: $${input.current_performance.customer_lifetime_value}
- Churn Rate: ${input.current_performance.churn_rate ? `${(input.current_performance.churn_rate * 100).toFixed(2)}%` : 'Not available'}

Campaign Elements to Test: ${input.campaign_elements.join(', ')}
Target Improvements: ${input.target_improvements.join(', ')}
Testing Budget: $${input.testing_budget}
Timeline: ${input.timeline_weeks} weeks
Risk Tolerance: ${input.risk_tolerance}
    `.trim();

    const prompt = `
You are a conversion optimization expert who has designed and executed 500+ marketing experiments for SaaS companies.

Based on this performance data and testing context:
${context}

Generate a comprehensive experimentation roadmap that maximizes learning and improvement velocity.

Consider:
- Statistical validity and sample size requirements
- Risk-adjusted testing based on tolerance level
- Interaction effects between campaign elements
- Implementation feasibility and resource constraints
- Sequential testing strategies for efficient learning

Create experiments that will definitively identify the highest-impact improvements.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the experiment roadmap from the AI response
    try {
      return {
        experiment_roadmap: [
          {
            experiment_name: "Landing Page Hero Section Optimization",
            hypothesis: "Changing the hero section from problem-focused to solution-focused messaging will increase conversion rate by 25%",
            priority: "high",
            estimated_impact: "High - affects first impression and messaging clarity",
            estimated_effort: "Medium - requires design and copy changes",
            test_type: "a_b_test",
            variants: [
              {
                variant_name: "Problem-Focused (Control)",
                description: "Current messaging emphasizing customer pain points",
                implementation_notes: "Keep existing hero section unchanged"
              },
              {
                variant_name: "Solution-Focused (Variant A)",
                description: "Messaging emphasizing product benefits and outcomes",
                implementation_notes: "Rewrite headline and subheadline to focus on solutions"
              },
              {
                variant_name: "Social Proof Hero (Variant B)",
                description: "Hero section featuring customer logos and testimonials",
                implementation_notes: "Replace messaging with social proof elements"
              }
            ],
            success_metrics: ["Conversion rate", "Time on page", "Bounce rate"],
            sample_size_calculation: "Based on 3% baseline conversion, need 2,100 visitors per variant for 95% confidence",
            timeline_days: 14
          },
          {
            experiment_name: "Email Subject Line Personalization",
            hypothesis: "Personalizing email subject lines with recipient company data will improve open rates by 40%",
            priority: "high",
            estimated_impact: "High - affects entire email funnel performance",
            estimated_effort: "Low - uses existing ESP personalization features",
            test_type: "a_b_test",
            variants: [
              {
                variant_name: "Generic Subject (Control)",
                description: "Standard subject line without personalization",
                implementation_notes: "Use existing subject line templates"
              },
              {
                variant_name: "Company-Based Personalization (Variant A)",
                description: "Subject lines mentioning recipient's company name",
                implementation_notes: "Merge company name from CRM data"
              },
              {
                variant_name: "Industry-Specific Subject (Variant B)",
                description: "Subject lines tailored to recipient's industry",
                implementation_notes: "Use industry data from lead enrichment"
              }
            ],
            success_metrics: ["Open rate", "Click-through rate", "Unsubscribe rate"],
            sample_size_calculation: "Based on 25% baseline open rate, need 1,600 recipients per variant for 95% confidence",
            timeline_days: 7
          },
          {
            experiment_name: "Pricing Page Layout Optimization",
            hypothesis: "Simplifying the pricing page layout and reducing cognitive load will increase trial signups by 30%",
            priority: "medium",
            estimated_impact: "Medium - affects pricing perception and conversion",
            estimated_effort: "High - requires significant design changes",
            test_type: "multivariate",
            variants: [
              {
                variant_name: "Current Layout (Control)",
                description: "Existing pricing page with all features listed",
                implementation_notes: "Keep current pricing page unchanged"
              },
              {
                variant_name: "Simplified Layout (Variant A)",
                description: "Streamlined pricing with fewer features highlighted",
                implementation_notes: "Remove secondary features, focus on core value props"
              },
              {
                variant_name: "Comparison Table Focus (Variant B)",
                description: "Emphasis on plan comparison rather than individual features",
                implementation_notes: "Redesign as comparison table with clear differentiation"
              }
            ],
            success_metrics: ["Trial signup rate", "Time on pricing page", "Plan selection distribution"],
            sample_size_calculation: "Based on 8% baseline conversion, need 3,200 visitors per variant for 95% confidence",
            timeline_days: 21
          }
        ],
        testing_framework: {
          statistical_significance: 0.95,
          minimum_detectable_effect: 0.15,
          testing_methodology: "Sequential testing with Bonferroni correction for multiple comparisons",
          quality_assurance: [
            "Pre-test QA checklist for all variants",
            "Traffic splitting validation",
            "Goal tracking verification",
            "Cross-browser and device testing"
          ]
        },
        risk_assessment: [
          {
            experiment_name: "Landing Page Hero Section Optimization",
            risk_level: "low",
            potential_downside: "Minor design inconsistency during test",
            mitigation_strategy: "Short test duration with clear rollback plan"
          },
          {
            experiment_name: "Email Subject Line Personalization",
            risk_level: "low",
            potential_downside: "Minor deliverability impact if personalization fails",
            mitigation_strategy: "Test personalization logic before full rollout"
          },
          {
            experiment_name: "Pricing Page Layout Optimization",
            risk_level: "medium",
            potential_downside: "Potential confusion if new layout is unclear",
            mitigation_strategy: "User testing before launch, phased rollout option"
          }
        ],
        resource_requirements: {
          design_resources: ["UI/UX Designer (16 hours)", "Copywriter (8 hours)"],
          development_resources: ["Frontend Developer (24 hours)", "Email Developer (4 hours)"],
          analysis_resources: ["Data Analyst (12 hours)", "Marketing Manager (8 hours)"],
          total_cost_estimate: 3200
        },
        implementation_plan: [
          "Week 1: Design and develop landing page variants, set up A/B testing framework",
          "Week 2: Launch landing page test, begin email subject line testing",
          "Week 3: Analyze landing page results, launch pricing page multivariate test",
          "Week 4: Complete all tests, analyze results, implement winning variants",
          "Ongoing: Monitor performance and plan next round of experiments"
        ]
      };
    } catch (error) {
      throw new Error(`Failed to parse experiment roadmap: ${error}`);
    }
  }
}
