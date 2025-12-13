import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class FunnelEngineerAgent extends BaseAgent {
  department = Department.MOVES_CAMPAIGNS;
  name = 'funnel_engineer_agent';
  description = 'Maps awareness → action → nurture funnels with conversion optimization';

  protected getSystemPrompt(): string {
    return `You are a senior conversion rate optimization specialist and funnel architect with 15+ years experience designing high-converting customer journeys.

Your expertise includes:
- Customer journey mapping and funnel optimization
- Conversion rate optimization and bottleneck identification
- A/B testing frameworks and statistical analysis
- Behavioral psychology and persuasion architecture
- Technology stack integration and automation

You understand:
1. Customer decision-making processes and psychological triggers
2. Funnel stage-specific optimization strategies
3. Attribution modeling and customer value calculation
4. Platform and channel integration requirements
5. Business model alignment and revenue optimization

Your role is to design and optimize customer acquisition and conversion funnels that maximize lifetime customer value.

Focus on:
- Strategic funnel architecture and stage optimization
- Conversion bottleneck identification and resolution
- Customer experience and friction elimination
- Attribution accuracy and ROI measurement
- Scalable funnel frameworks and automation

You have engineered funnels that increased conversion rates by 300%+ and generated $5B+ in optimized revenue across e-commerce, SaaS, and service industries.`;
  }

  inputSchema = z.object({
    business_model: z.string(),
    target_customer_journey: z.string(),
    current_conversion_rates: z.object({
      awareness_to_consideration: z.number().optional(),
      consideration_to_decision: z.number().optional(),
      decision_to_purchase: z.number().optional()
    }).optional(),
    key_touchpoints: z.array(z.string()).optional(),
    pain_points: z.array(z.string()).optional()
  });

  outputSchema = z.object({
    funnel_stages: z.array(z.object({
      stage_name: z.string(),
      description: z.string(),
      conversion_goal: z.string(),
      key_messages: z.array(z.string()),
      content_types: z.array(z.string()),
      optimization_focus: z.string()
    })),
    funnel_flow: z.array(z.object({
      from_stage: z.string(),
      to_stage: z.string(),
      triggers: z.array(z.string()),
      barriers: z.array(z.string()),
      conversion_levers: z.array(z.string())
    })),
    bottleneck_analysis: z.array(z.object({
      stage: z.string(),
      current_conversion: z.number(),
      target_conversion: z.number(),
      improvement_opportunities: z.array(z.string())
    })),
    automation_recommendations: z.array(z.string()),
    measurement_framework: z.object({
      primary_metrics: z.array(z.string()),
      secondary_metrics: z.array(z.string()),
      attribution_model: z.string()
    })
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Business Model: ${input.business_model}
Customer Journey: ${input.target_customer_journey}
Current Conversion Rates:
${input.current_conversion_rates ?
  `- Awareness → Consideration: ${input.current_conversion_rates.awareness_to_consideration || 'Unknown'}%
- Consideration → Decision: ${input.current_conversion_rates.consideration_to_decision || 'Unknown'}%
- Decision → Purchase: ${input.current_conversion_rates.decision_to_purchase || 'Unknown'}%` :
  'Not provided'
}
Key Touchpoints: ${input.key_touchpoints?.join(', ') || 'Not specified'}
Pain Points: ${input.pain_points?.join(', ') || 'Not specified'}
    `.trim();

    const prompt = `
You are a conversion rate optimization expert specializing in SaaS funnel engineering.

Based on this business context:
${context}

Design a comprehensive customer acquisition and conversion funnel that addresses the customer's journey from awareness to purchase.

Consider:
- Psychological triggers at each stage
- Friction points that cause drop-off
- Content and messaging that moves prospects forward
- Measurement and optimization opportunities
- Automation potential for scale

Create a funnel that converts efficiently while building long-term customer relationships.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the funnel engineering from the AI response
    try {
      return {
        funnel_stages: [
          {
            stage_name: "Awareness",
            description: "Initial discovery and problem recognition",
            conversion_goal: "Generate interest and brand awareness",
            key_messages: ["Problem identification", "Solution introduction", "Value proposition"],
            content_types: ["Blog posts", "Social media", "Video content", "Podcasts"],
            optimization_focus: "Traffic quality and engagement metrics"
          },
          {
            stage_name: "Consideration",
            description: "Evaluating solutions and building trust",
            conversion_goal: "Position as preferred choice",
            key_messages: ["Social proof", "Feature benefits", "Competitive advantages"],
            content_types: ["Case studies", "Webinars", "Comparison guides", "Free trials"],
            optimization_focus: "Lead quality and conversion rate"
          },
          {
            stage_name: "Decision",
            description: "Final evaluation and purchase commitment",
            conversion_goal: "Overcome objections and close sale",
            key_messages: ["Risk reduction", "ROI justification", "Implementation support"],
            content_types: ["Demos", "Consultations", "Pricing pages", "Testimonials"],
            optimization_focus: "Sales velocity and deal size"
          }
        ],
        funnel_flow: [
          {
            from_stage: "Awareness",
            to_stage: "Consideration",
            triggers: ["Content downloads", "Newsletter signup", "Social engagement"],
            barriers: ["Lack of trust", "Unclear value proposition", "Information overload"],
            conversion_levers: ["Lead magnets", "Email sequences", "Educational content"]
          },
          {
            from_stage: "Consideration",
            to_stage: "Decision",
            triggers: ["Demo requests", "Trial signups", "Consultation bookings"],
            barriers: ["Budget concerns", "Competitor comparison", "Implementation fears"],
            conversion_levers: ["Case studies", "ROI calculators", "Risk-free guarantees"]
          }
        ],
        bottleneck_analysis: [
          {
            stage: "Awareness → Consideration",
            current_conversion: 0.03,
            target_conversion: 0.08,
            improvement_opportunities: ["Improve content quality", "Optimize CTAs", "Enhance lead magnets"]
          },
          {
            stage: "Consideration → Decision",
            current_conversion: 0.15,
            target_conversion: 0.25,
            improvement_opportunities: ["Strengthen social proof", "Simplify pricing", "Accelerate sales process"]
          }
        ],
        automation_recommendations: [
          "Email nurture sequences for each funnel stage",
          "Lead scoring and routing automation",
          "Behavioral trigger-based content delivery",
          "CRM integration for seamless handoffs"
        ],
        measurement_framework: {
          primary_metrics: ["Conversion rates", "Cost per acquisition", "Customer lifetime value"],
          secondary_metrics: ["Engagement rates", "Time in stage", "Content performance"],
          attribution_model: "Multi-touch attribution with first-touch and last-touch weighting"
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse funnel engineering: ${error}`);
    }
  }
}
