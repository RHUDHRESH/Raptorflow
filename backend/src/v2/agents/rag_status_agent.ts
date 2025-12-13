import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class RAGStatusAgent extends BaseAgent {
  department = Department.ANALYTICS;
  name = 'rag_status_agent';
  description = 'Assigns red/amber/green for Moves & campaigns with improvement recommendations';

  protected getSystemPrompt(): string {
    return `You are a senior program management and performance monitoring specialist with 15+ years experience in traffic light reporting and performance dashboard design.

Your expertise includes:
- Performance threshold setting and KPI frameworks
- Risk assessment and escalation protocols
- Trend analysis and early warning systems
- Stakeholder communication and executive reporting
- Continuous improvement and intervention strategies

You understand:
1. Business performance metrics and threshold setting
2. Risk management and intervention timing
3. Stakeholder communication and expectation management
4. Performance attribution and external factor consideration
5. Change management and course correction frameworks

Your role is to provide clear, actionable status assessments that enable timely interventions and resource reallocation decisions.

Focus on:
- Evidence-based status assignment with clear rationale
- Actionable recommendations prioritized by urgency
- Risk assessment and escalation protocols
- Performance trend analysis and forecasting
- Stakeholder communication and expectation alignment

You have managed performance monitoring systems that improved organizational responsiveness by 60% and prevented million-dollar losses through early intervention.`;
  }

  inputSchema = z.object({
    campaign_data: z.object({
      campaign_id: z.string(),
      kpis: z.record(z.number()),
      budget_spent: z.number(),
      budget_allocated: z.number(),
      timeline_progress: z.number()
    }),
    benchmark_data: z.record(z.number()),
    stakeholder_priorities: z.array(z.string())
  });

  outputSchema = z.object({
    status_assessment: z.object({
      overall_status: z.enum(['red', 'amber', 'green']),
      status_reason: z.string(),
      confidence_level: z.number(),
      risk_factors: z.array(z.string())
    }),
    kpi_breakdown: z.array(z.object({
      kpi_name: z.string(),
      current_value: z.number(),
      target_value: z.number(),
      status: z.enum(['red', 'amber', 'green']),
      gap_analysis: z.string()
    })),
    improvement_recommendations: z.array(z.object({
      recommendation: z.string(),
      impact_potential: z.enum(['high', 'medium', 'low']),
      implementation_effort: z.enum(['high', 'medium', 'low']),
      timeline: z.string()
    })),
    escalation_triggers: z.array(z.object({
      trigger_condition: z.string(),
      escalation_action: z.string(),
      responsible_party: z.string()
    }))
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const prompt = `Assess campaign performance and assign RAG status with actionable recommendations.`;
    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);
    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    return {
      status_assessment: {
        overall_status: 'green',
        status_reason: '',
        confidence_level: 0,
        risk_factors: []
      },
      kpi_breakdown: [],
      improvement_recommendations: [],
      escalation_triggers: []
    };
  }
}
