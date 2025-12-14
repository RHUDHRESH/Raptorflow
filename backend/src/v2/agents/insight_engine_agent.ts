import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class InsightEngineAgent extends BaseAgent {
  department = Department.ANALYTICS;
  name = 'insight_engine_agent';
  description = 'Finds surprising patterns ("Pattern Cards") in data and behavior';

  protected getSystemPrompt(): string {
    return `You are a senior data scientist and insight specialist with 15+ years experience in advanced analytics, pattern recognition, and behavioral analysis.

Your expertise includes:
- Statistical pattern recognition and anomaly detection
- Machine learning and clustering algorithms
- Behavioral segmentation and cohort analysis
- Correlation and causation analysis frameworks
- Data storytelling and insight communication

You understand:
1. Statistical significance and practical importance distinction
2. Data quality assessment and preprocessing techniques
3. Business context integration and insight relevance
4. Visualization and communication of complex patterns
5. Ethical data analysis and privacy considerations

Your role is to uncover actionable insights and surprising patterns that drive strategic business decisions and competitive advantage.

Focus on:
- Counterintuitive findings and unexpected relationships
- Business impact assessment and strategic implications
- Statistical rigor and methodological transparency
- Actionable recommendations and implementation guidance
- Pattern validation and robustness testing

You have discovered insights that led to billion-dollar strategic pivots and market opportunities across technology, retail, and financial services.`;
  }

  inputSchema = z.object({
    dataset: z.record(z.any()),
    analysis_objectives: z.array(z.string()),
    segment_definitions: z.record(z.any()),
    time_periods: z.array(z.string()),
    statistical_thresholds: z.record(z.number())
  });

  outputSchema = z.object({
    pattern_cards: z.array(z.object({
      pattern_title: z.string(),
      pattern_description: z.string(),
      statistical_significance: z.number(),
      affected_segments: z.array(z.string()),
      business_impact: z.string(),
      recommended_actions: z.array(z.string()),
      data_visualization: z.string()
    })),
    correlation_analysis: z.array(z.object({
      variables: z.array(z.string()),
      correlation_coefficient: z.number(),
      relationship_type: z.string(),
      practical_insights: z.array(z.string())
    })),
    anomaly_detection: z.array(z.object({
      anomaly_type: z.string(),
      affected_metric: z.string(),
      deviation_magnitude: z.number(),
      potential_causes: z.array(z.string()),
      investigation_priority: z.enum(['high', 'medium', 'low'])
    })),
    predictive_signals: z.array(z.object({
      signal_name: z.string(),
      leading_indicators: z.array(z.string()),
      prediction_accuracy: z.number(),
      actionable_timeframe: z.string()
    }))
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const prompt = `Discover hidden patterns and insights in marketing data using advanced analytics.`;
    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);
    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    return {
      pattern_cards: [],
      correlation_analysis: [],
      anomaly_detection: [],
      predictive_signals: []
    };
  }
}
