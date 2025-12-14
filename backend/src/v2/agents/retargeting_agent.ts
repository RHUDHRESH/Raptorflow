import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class RetargetingAgent extends BaseAgent {
  department = Department.DISTRIBUTION;
  name = 'retargeting_agent';
  description = 'Builds retargeting loops + messaging for website visitors and engaged prospects';

  protected getSystemPrompt(): string {
    return `You are a senior retargeting and conversion optimization specialist with 15+ years experience in customer re-engagement and lifecycle marketing.

Your expertise includes:
- Behavioral segmentation and retargeting strategy design
- Cross-device and cross-platform audience tracking
- Frequency capping and ad fatigue prevention
- Dynamic creative optimization and personalization
- Attribution modeling and incremental lift measurement

You understand:
1. Consumer journey and conversion funnel optimization
2. Platform-specific retargeting capabilities and limitations
3. Privacy regulations and data protection requirements
4. Creative fatigue and audience saturation patterns
5. Performance measurement and ROI optimization

Your role is to design sophisticated retargeting campaigns that convert engaged prospects into customers while maximizing efficiency and minimizing ad waste.

Focus on:
- Strategic audience segmentation and journey mapping
- Platform-optimized creative and messaging sequences
- Frequency management and audience refresh strategies
- Performance attribution and incremental measurement
- Privacy compliance and data protection integration

You have designed retargeting programs that increased conversion rates by 400%+ and improved ROAS by 3x across e-commerce and lead generation campaigns.`;
  }

  inputSchema = z.object({
    audience_segments: z.array(z.string()),
    conversion_funnel: z.array(z.string()),
    retargeting_goals: z.array(z.string()),
    platform_capabilities: z.array(z.string())
  });

  outputSchema = z.object({
    retargeting_sequences: z.array(z.object({
      sequence_name: z.string(),
      trigger_event: z.string(),
      audience_segment: z.string(),
      ad_frequency: z.number(),
      messaging_progression: z.array(z.string()),
      platforms: z.array(z.string())
    })),
    creative_adaptation: z.object({
      dynamic_creatives: z.array(z.string()),
      messaging_pillars: z.array(z.string()),
      urgency_elements: z.array(z.string())
    }),
    frequency_optimization: z.object({
      frequency_caps: z.record(z.number()),
      cooldown_periods: z.record(z.string()),
      fatigue_indicators: z.array(z.string())
    })
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const prompt = `Create retargeting loops and messaging sequences.`;
    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);
    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    return {
      retargeting_sequences: [],
      creative_adaptation: {
        dynamic_creatives: [],
        messaging_pillars: [],
        urgency_elements: []
      },
      frequency_optimization: {
        frequency_caps: {},
        cooldown_periods: {},
        fatigue_indicators: []
      }
    };
  }
}
