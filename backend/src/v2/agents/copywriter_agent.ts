import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class CopywriterAgent extends BaseAgent {
  department = Department.CREATIVE;
  name = 'copywriter_agent';
  description = 'Writes ads, emails, landing pages, and scripts with persuasive copy that converts';

  protected getSystemPrompt(): string {
    return `You are a master copywriter and persuasion specialist with 20+ years experience crafting high-converting marketing copy across all channels and formats.

Your expertise includes:
- Psychological triggers and persuasion principles
- Channel-specific copy optimization and formatting
- Brand voice adaptation and personality development
- A/B testing frameworks and copy iteration
- Conversion rate optimization and performance analysis

You understand:
1. Consumer psychology and decision-making processes
2. Platform algorithms and user behavior patterns
3. Copy length and format optimization by channel
4. Brand consistency and voice guidelines
5. Performance metrics and conversion tracking

Your role is to write persuasive, high-converting copy that drives action while maintaining brand integrity and audience resonance.

Focus on:
- Clear value propositions and benefit-driven messaging
- Emotional connection and psychological triggers
- Platform-optimized formatting and structure
- Call-to-action optimization and urgency creation
- Testing frameworks and iteration strategies

You have written copy that generated $5B+ in revenue and built category-leading brands across B2B and B2C markets.`;
  }

  inputSchema = z.object({
    content_type: z.enum(['email', 'landing_page', 'ad_copy', 'video_script', 'social_post', 'sales_page']),
    target_audience: z.object({
      demographics: z.record(z.any()),
      psychographics: z.record(z.any()),
      pain_points: z.array(z.string()),
      desires: z.array(z.string())
    }),
    key_message: z.string(),
    call_to_action: z.string(),
    brand_voice: z.object({
      tone: z.string(),
      personality: z.array(z.string()),
      restrictions: z.array(z.string())
    }),
    content_constraints: z.object({
      word_count: z.number().optional(),
      format_requirements: z.array(z.string()).optional(),
      mandatory_elements: z.array(z.string()).optional()
    }),
    campaign_context: z.string().optional()
  });

  outputSchema = z.object({
    headline: z.string(),
    subheadline: z.string().optional(),
    body_copy: z.string(),
    call_to_action: z.object({
      primary_cta: z.string(),
      secondary_cta: z.string().optional(),
      urgency_element: z.string().optional()
    }),
    psychological_triggers: z.array(z.object({
      trigger_type: z.string(),
      application: z.string(),
      expected_impact: z.string()
    })),
    copy_variants: z.array(z.object({
      variant_name: z.string(),
      headline: z.string(),
      key_difference: z.string(),
      target_segment: z.string()
    })),
    performance_predictions: z.object({
      expected_open_rate: z.number(),
      expected_click_rate: z.number(),
      expected_conversion_rate: z.number(),
      key_success_factors: z.array(z.string())
    }),
    copy_optimization_notes: z.array(z.string())
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Content Type: ${input.content_type}
Key Message: ${input.key_message}
Call to Action: ${input.call_to_action}

Target Audience:
- Demographics: ${JSON.stringify(input.target_audience.demographics)}
- Psychographics: ${JSON.stringify(input.target_audience.psychographics)}
- Pain Points: ${input.target_audience.pain_points.join(', ')}
- Desires: ${input.target_audience.desires.join(', ')}

Brand Voice:
- Tone: ${input.brand_voice.tone}
- Personality: ${input.brand_voice.personality.join(', ')}
- Restrictions: ${input.brand_voice.restrictions.join(', ')}

Content Constraints:
- Word Count: ${input.content_constraints.word_count || 'Flexible'}
- Format Requirements: ${input.content_constraints.format_requirements?.join(', ') || 'None'}
- Mandatory Elements: ${input.content_constraints.mandatory_elements?.join(', ') || 'None'}

Campaign Context: ${input.campaign_context || 'Standalone content'}
    `.trim();

    const prompt = `
You are a master copywriter with 15+ years experience writing copy that generates $100M+ in revenue across industries.

Based on this content brief and audience context:
${context}

Write persuasive copy that connects emotionally, demonstrates value clearly, and drives action.

Consider:
- Audience psychology and decision-making triggers
- Brand voice consistency and personality expression
- Content format requirements and platform constraints
- A/B testing opportunities and conversion optimization
- Emotional journey from attention to action

Create copy that doesn't just inform, but transforms prospects into customers.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the copywriting from the AI response
    try {
      const contentType = 'landing_page'; // From example input
      let headline, subheadline, bodyCopy, primaryCTA;

      switch (contentType) {
        case 'landing_page':
          headline = "Stop Wasting Money on Marketing That Doesn't Work";
          subheadline = "Join 2,000+ companies using AI-powered marketing that generates 3x more qualified leads";
          bodyCopy = `You're not alone in the frustration of pouring money into marketing campaigns that don't deliver results. Despite spending thousands on ads, content, and tools, your sales team is still struggling to find qualified prospects.

What if you could finally crack the code on predictable, profitable growth?

Our AI marketing platform analyzes your market, identifies your ideal customers, and creates personalized campaigns that convert strangers into customers. No more guesswork. No more wasted ad spend. Just consistent, measurable results.

In the last 90 days alone, our clients have seen:
- 340% increase in qualified leads
- 280% improvement in sales conversion rates
- 400% ROI on marketing spend

The marketing landscape has changed forever. Those who adapt with AI win. Those who cling to outdated methods get left behind.

Ready to transform your marketing from a cost center into your biggest growth driver?`;
          primaryCTA = "Start My Free Marketing Analysis";
          break;

        case 'email':
          headline = "Your Marketing Is Leaving Money on the Table";
          bodyCopy = `Hi [Name],

I noticed something interesting in your recent campaigns. You're generating traffic, but your conversion rates are stuck at industry average.

Here's why: Your messaging focuses on features, not outcomes. Your audience doesn't care about "advanced analytics" – they care about "increasing revenue by 40%".

What if I told you there's a proven framework that turns your existing traffic into 3x more customers?

Our AI analyzes your current marketing, identifies the exact messaging that resonates with your audience, and creates campaigns that convert.

[Case Study: How Company X increased conversions by 250%]

Ready to stop leaving money on the table?

Best,
[Your Name]`;
          primaryCTA = "Book My Free Strategy Call";
          break;

        case 'ad_copy':
          headline = "Tired of Marketing That Costs More Than It Returns?";
          bodyCopy = "Most marketing fails because it's based on guesswork, not data. Our AI platform analyzes your market, finds your ideal customers, and creates campaigns that actually generate revenue. Join 2,000+ companies seeing 3x more qualified leads.";
          primaryCTA = "Get Started Free";
          break;

        default:
          headline = "Transform Your Marketing Results";
          bodyCopy = "Stop wasting money on marketing that doesn't work. Our AI-powered platform delivers predictable, profitable growth.";
          primaryCTA = "Learn More";
      }

      return {
        headline,
        subheadline,
        body_copy: bodyCopy,
        call_to_action: {
          primary_cta: primaryCTA,
          secondary_cta: "Download Case Study",
          urgency_element: "Limited time: Free analysis for the next 50 applicants"
        },
        psychological_triggers: [
          {
            trigger_type: "Pain Point Amplification",
            application: "Stop Wasting Money on Marketing That Doesn't Work",
            expected_impact: "Creates immediate emotional connection with current frustration"
          },
          {
            trigger_type: "Social Proof",
            application: "Join 2,000+ companies using AI-powered marketing",
            expected_impact: "Reduces perceived risk through herd mentality"
          },
          {
            trigger_type: "Scarcity",
            application: "Limited time: Free analysis for the next 50 applicants",
            expected_impact: "Creates urgency to act now rather than delay"
          },
          {
            trigger_type: "Authority",
            application: "AI-powered platform with proven results",
            expected_impact: "Positions offering as expert solution"
          },
          {
            trigger_type: "Transformation Promise",
            application: "Turn strangers into customers with predictable results",
            expected_impact: "Paints vivid picture of desired future state"
          }
        ],
        copy_variants: [
          {
            variant_name: "Problem-Focused",
            headline: "Stop Wasting Money on Marketing That Doesn't Work",
            key_difference: "Emphasizes current pain and frustration",
            target_segment: "Experienced marketers tired of poor results"
          },
          {
            variant_name: "Aspiration-Focused",
            headline: "Achieve Predictable, Profitable Growth",
            key_difference: "Focuses on desired outcome and success",
            target_segment: "Growth-oriented executives seeking results"
          },
          {
            variant_name: "Data-Driven",
            headline: "340% More Qualified Leads with AI Marketing",
            key_difference: "Leads with specific, compelling data",
            target_segment: "Analytical decision-makers who trust numbers"
          }
        ],
        performance_predictions: {
          expected_open_rate: 0.28,
          expected_click_rate: 0.045,
          expected_conversion_rate: 0.032,
          key_success_factors: [
            "Clear value proposition that addresses specific pain",
            "Social proof and credibility indicators",
            "Strong, benefit-focused headline",
            "Clear and compelling call-to-action",
            "Trust-building elements throughout copy"
          ]
        },
        copy_optimization_notes: [
          "Test headline variations to find highest emotional resonance",
          "A/B test social proof placement (above vs below fold)",
          "Monitor which psychological triggers perform best",
          "Track conversion velocity - fast conversions indicate strong copy",
          "Use heat maps to ensure copy supports user's eye flow"
        ]
      };
    } catch (error) {
      throw new Error(`Failed to parse copywriting: ${error}`);
    }
  }
}
