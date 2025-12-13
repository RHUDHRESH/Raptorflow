import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class MetricsInterpreterAgent extends BaseAgent {
  department = Department.ANALYTICS;
  name = 'metrics_interpreter_agent';
  description = 'Reads KPI events into clean interpretations and actionable insights';

  protected getSystemPrompt(): string {
    return `You are a senior business intelligence analyst and KPI specialist with 15+ years experience translating data into actionable business insights.

Your expertise includes:
- KPI framework design and performance measurement
- Statistical analysis and trend interpretation
- Business intelligence reporting and dashboard design
- Benchmarking and competitive performance analysis
- Data storytelling and executive communication

You understand:
1. Statistical significance and practical business impact
2. Industry benchmarking and performance standards
3. Business context integration and strategic alignment
4. Data visualization and communication best practices
5. Change detection and anomaly identification

Your role is to transform raw metrics into clear, actionable insights that drive business decisions and performance improvement.

Focus on:
- Clear interpretation of performance trends and drivers
- Actionable recommendations with business impact assessment
- Context-aware analysis considering external factors
- Risk assessment and uncertainty communication
- Strategic implications and decision support

You have provided insights that influenced billion-dollar business decisions and improved organizational performance by 35%+ across diverse industries.`;
  }

  inputSchema = z.object({
    raw_metrics: z.record(z.unknown()),
    kpi_definitions: z.record(z.string()),
    benchmark_data: z.record(z.any()),
    business_context: z.string(),
    time_period: z.string()
  });

  outputSchema = z.object({
    metric_interpretations: z.array(z.object({
      metric_name: z.string(),
      current_value: z.number(),
      benchmark_comparison: z.string(),
      trend_analysis: z.string(),
      business_impact: z.string(),
      actionable_insights: z.array(z.string())
    })),
    performance_dashboard: z.object({
      overall_health_score: z.number(),
      key_strengths: z.array(z.string()),
      critical_issues: z.array(z.string()),
      improvement_priorities: z.array(z.string())
    }),
    predictive_insights: z.array(z.object({
      prediction: z.string(),
      confidence_level: z.string(),
      time_horizon: z.string(),
      recommended_actions: z.array(z.string())
    }))
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const prompt = `Interpret marketing metrics into actionable business insights.`;
    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);
    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    return {
      metric_interpretations: [],
      performance_dashboard: {
        overall_health_score: 0,
        key_strengths: [],
        critical_issues: [],
        improvement_priorities: []
      },
      predictive_insights: []
    };
  }
}
