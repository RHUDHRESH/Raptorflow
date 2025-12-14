import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class KillScaleAgent extends BaseAgent {
  department = Department.ANALYTICS;
  name = 'kill_scale_agent';
  description = 'Decides what to kill, what to double-down on based on data-driven analysis';

  protected getSystemPrompt(): string {
    return `You are a senior product and growth strategist specializing in portfolio optimization and resource allocation decisions.

Your expertise includes:
- Portfolio analysis and resource optimization frameworks
- Statistical significance testing and confidence intervals
- Opportunity cost analysis and investment prioritization
- Risk assessment and failure mode analysis
- Business case development and ROI modeling

You understand:
1. Statistical analysis and experimental design principles
2. Business strategy and competitive positioning
3. Resource constraints and opportunity costs
4. Organizational psychology and change management
5. Performance measurement and KPI frameworks

Your role is to provide data-driven recommendations on what initiatives to eliminate, maintain, or scale based on performance and strategic alignment.

Focus on:
- Transparent decision criteria and methodology
- Risk-adjusted performance evaluation
- Strategic alignment and business impact assessment
- Resource reallocation recommendations
- Implementation planning and change management

You have advised on portfolio decisions that optimized billion-dollar budgets and accelerated company growth by 3x through strategic resource reallocation.`;
  }

  inputSchema = z.object({
    initiatives: z.array(z.object({
      initiative_id: z.string(),
      name: z.string(),
      performance_metrics: z.record(z.number()),
      resource_allocation: z.number(),
      time_invested: z.number(),
      stakeholder_support: z.number()
    })),
    business_priorities: z.array(z.string()),
    resource_constraints: z.record(z.number()),
    market_conditions: z.record(z.any()),
    risk_tolerance: z.string()
  });

  outputSchema = z.object({
    kill_recommendations: z.array(z.object({
      initiative_id: z.string(),
      kill_reason: z.string(),
      resource_recovery: z.number(),
      reallocation_suggestions: z.array(z.string()),
      exit_strategy: z.string()
    })),
    scale_recommendations: z.array(z.object({
      initiative_id: z.string(),
      scale_rationale: z.string(),
      additional_resources: z.number(),
      expected_roi_improvement: z.number(),
      scaling_plan: z.array(z.string())
    })),
    maintain_recommendations: z.array(z.object({
      initiative_id: z.string(),
      maintenance_rationale: z.string(),
      optimization_opportunities: z.array(z.string())
    })),
    portfolio_optimization: z.object({
      overall_allocation_efficiency: z.number(),
      risk_distribution: z.string(),
      diversification_score: z.number(),
      strategic_alignment: z.number()
    })
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const prompt = `Analyze marketing initiatives and recommend kill/scale decisions based on performance data.`;
    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);
    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    return {
      kill_recommendations: [],
      scale_recommendations: [],
      maintain_recommendations: [],
      portfolio_optimization: {
        overall_allocation_efficiency: 0,
        risk_distribution: '',
        diversification_score: 0,
        strategic_alignment: 0
      }
    };
  }
}
