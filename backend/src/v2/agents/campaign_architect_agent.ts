import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class CampaignArchitectAgent extends BaseAgent {
  department = Department.MOVES_CAMPAIGNS;
  name = 'campaign_architect_agent';
  description = 'Builds 30/60/90-day arcs + budget paths for marketing campaigns';

  protected getSystemPrompt(): string {
    return `You are a master campaign strategist and architect with 20+ years experience building billion-dollar marketing campaigns across industries.

Your expertise spans:
- Strategic campaign planning and objective setting
- Multi-channel orchestration and timing optimization
- Budget allocation and resource optimization
- Customer journey mapping and conversion funnel design
- Performance measurement and KPI frameworks

You have deep knowledge of:
1. Campaign lifecycle management and phasing strategies
2. Channel synergy and cross-platform optimization
3. Budget pacing and investment timing
4. Risk assessment and contingency planning
5. Stakeholder management and campaign governance

Your role is to design comprehensive campaign architectures that deliver measurable business results through strategic timing, resource allocation, and multi-channel integration.

Focus on:
- Clear campaign phases with measurable milestones
- Budget optimization and resource allocation
- Risk mitigation and contingency planning
- Performance tracking and optimization frameworks
- Scalability and long-term campaign evolution

You have designed campaigns that generated $10B+ in revenue and built market-leading brands across technology, consumer goods, and B2B sectors.`;
  }

  inputSchema = z.object({
    business_goal: z.string(),
    target_audience: z.string(),
    budget_range: z.string(),
    timeline_months: z.number(),
    current_positioning: z.string().optional(),
    competitor_activity: z.array(z.string()).optional()
  });

  outputSchema = z.object({
    campaign_arc: z.object({
      month_1: z.object({
        focus: z.string(),
        key_moves: z.array(z.string()),
        budget_allocation: z.number(),
        success_metrics: z.array(z.string())
      }),
      month_2: z.object({
        focus: z.string(),
        key_moves: z.array(z.string()),
        budget_allocation: z.number(),
        success_metrics: z.array(z.string())
      }),
      month_3: z.object({
        focus: z.string(),
        key_moves: z.array(z.string()),
        budget_allocation: z.number(),
        success_metrics: z.array(z.string())
      })
    }),
    budget_breakdown: z.object({
      content_creation: z.number(),
      advertising: z.number(),
      tools_software: z.number(),
      team_resources: z.number(),
      testing_optimization: z.number()
    }),
    risk_assessment: z.array(z.string()),
    contingency_plans: z.array(z.string())
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Business Goal: ${input.business_goal}
Target Audience: ${input.target_audience}
Budget Range: ${input.budget_range}
Timeline: ${input.timeline_months} months
Current Positioning: ${input.current_positioning || 'Not specified'}
Competitor Activity: ${input.competitor_activity?.join(', ') || 'Not analyzed yet'}
    `.trim();

    const prompt = `
You are a senior campaign architect with 15+ years experience building high-converting marketing campaigns for SaaS companies.

Based on this context:
${context}

Design a comprehensive 30/60/90-day campaign arc that maximizes growth within the given constraints.

Consider:
- Realistic ramp-up time for each channel
- Budget pacing and allocation efficiency
- Measurable milestones and pivot points
- Risk mitigation strategies
- Competitive positioning advantages

Output a detailed campaign architecture that a CMO would approve.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the campaign architecture from the AI response
    // This would include proper parsing logic for the structured output
    try {
      // For now, return a structured mock response
      return {
        campaign_arc: {
          month_1: {
            focus: "Foundation & Awareness",
            key_moves: ["Brand positioning", "Lead magnet creation", "Initial content calendar"],
            budget_allocation: 0.3,
            success_metrics: ["Website traffic +50%", "Lead magnet downloads", "Social following growth"]
          },
          month_2: {
            focus: "Lead Generation & Conversion",
            key_moves: ["Paid advertising launch", "Email nurture sequences", "Content amplification"],
            budget_allocation: 0.4,
            success_metrics: ["MQL generation", "Conversion rate improvement", "Cost per acquisition"]
          },
          month_3: {
            focus: "Optimization & Scale",
            key_moves: ["Performance analysis", "Budget reallocation", "Advanced retargeting"],
            budget_allocation: 0.3,
            success_metrics: ["LTV/CAC ratio", "Revenue attribution", "Customer acquisition cost"]
          }
        },
        budget_breakdown: {
          content_creation: 0.25,
          advertising: 0.45,
          tools_software: 0.15,
          team_resources: 0.10,
          testing_optimization: 0.05
        },
        risk_assessment: [
          "Budget pacing may exceed projections if early results are strong",
          "Competitor response could affect channel effectiveness",
          "Seasonal market changes may impact conversion rates"
        ],
        contingency_plans: [
          "Weekly budget monitoring with 20% buffer",
          "A/B testing framework for rapid optimization",
          "Competitor monitoring and response strategy"
        ]
      };
    } catch (error) {
      throw new Error(`Failed to parse campaign architecture: ${error}`);
    }
  }
}
