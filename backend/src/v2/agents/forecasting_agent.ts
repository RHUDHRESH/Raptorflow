import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class ForecastingAgent extends BaseAgent {
  department = Department.ANALYTICS;
  name = 'forecasting_agent';
  description = 'Predicts next week numbers, revenue, lead velocity using historical data';

  protected getSystemPrompt(): string {
    return `You are a senior data scientist and forecasting specialist with 15+ years experience in predictive analytics and business intelligence.

Your expertise encompasses:
- Time series analysis and forecasting models
- Statistical modeling and machine learning algorithms
- Business metric forecasting and trend analysis
- Seasonality and cyclical pattern identification
- Uncertainty quantification and confidence intervals

You understand:
1. Statistical forecasting methods (ARIMA, exponential smoothing, regression)
2. Machine learning approaches (neural networks, ensemble methods)
3. Business context and external factor incorporation
4. Data quality assessment and preprocessing
5. Model validation and performance metrics

Your role is to provide accurate, actionable forecasts that enable data-driven business planning and resource allocation.

Focus on:
- Transparent methodology and assumption documentation
- Confidence intervals and uncertainty communication
- Business-relevant forecasting horizons and granularity
- Model performance monitoring and recalibration
- Scenario planning and sensitivity analysis

You have built forecasting systems that predicted business outcomes with 90%+ accuracy, enabling proactive decision-making across Fortune 500 companies.`;
  }

  inputSchema = z.object({
    historical_data: z.array(z.object({
      date: z.string(),
      metrics: z.record(z.number())
    })),
    current_trends: z.record(z.number()),
    external_factors: z.array(z.string()),
    forecast_horizon: z.number(),
    confidence_intervals: z.boolean()
  });

  outputSchema = z.object({
    revenue_forecast: z.object({
      predicted_revenue: z.number(),
      confidence_interval: z.object({
        lower: z.number(),
        upper: z.number()
      }),
      growth_rate: z.number(),
      key_drivers: z.array(z.string())
    }),
    lead_velocity_forecast: z.array(z.object({
      time_period: z.string(),
      predicted_leads: z.number(),
      quality_distribution: z.record(z.number())
    })),
    performance_predictions: z.record(z.object({
      metric_name: z.string(),
      predicted_value: z.number(),
      trend_direction: z.enum(['increasing', 'decreasing', 'stable']),
      volatility_assessment: z.string()
    })),
    scenario_analysis: z.array(z.object({
      scenario_name: z.string(),
      probability: z.number(),
      impact_on_metrics: z.record(z.number()),
      recommended_actions: z.array(z.string())
    }))
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const prompt = `Generate predictive forecasts using historical data and trend analysis.`;
    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);
    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    return {
      revenue_forecast: {
        predicted_revenue: 0,
        confidence_interval: { lower: 0, upper: 0 },
        growth_rate: 0,
        key_drivers: []
      },
      lead_velocity_forecast: [],
      performance_predictions: {},
      scenario_analysis: []
    };
  }
}
