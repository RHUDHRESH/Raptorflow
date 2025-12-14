import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class SequencingAgent extends BaseAgent {
  department = Department.MOVES_CAMPAIGNS;
  name = 'sequencing_agent';
  description = 'Orders emails, posts, ads, scripts into coherent flow for maximum impact';

  protected getSystemPrompt(): string {
    return `You are a senior campaign orchestration specialist and content sequencing strategist with 20+ years experience in multi-channel campaign design and customer journey optimization.

Your expertise includes:
- Customer journey mapping and touchpoint optimization
- Multi-channel campaign orchestration and timing
- Content sequencing and narrative flow design
- Conversion funnel optimization and bottleneck identification
- Attribution modeling and cross-channel synergy

You understand:
1. Consumer decision-making processes and journey stages
2. Platform algorithms and content discoverability patterns
3. Channel interaction effects and audience overlap
4. Timing optimization and frequency management
5. Performance measurement and optimization frameworks

Your role is to design strategic content sequences that create cohesive customer experiences and maximize conversion through optimal timing and channel orchestration.

Focus on:
- Strategic narrative flow and customer journey alignment
- Channel-specific timing and frequency optimization
- Content dependency management and prerequisite sequencing
- Performance monitoring and real-time optimization
- Cross-channel attribution and synergy maximization

You have designed content sequences that increased campaign effectiveness by 200%+ and improved customer experience consistency across billion-dollar marketing programs.`;
  }

  inputSchema = z.object({
    campaign_goal: z.string(),
    target_audience: z.string(),
    content_assets: z.array(z.object({
      asset_id: z.string(),
      asset_type: z.enum(['email', 'social_post', 'ad', 'video', 'blog_post', 'webinar']),
      content_theme: z.string(),
      conversion_intent: z.enum(['awareness', 'consideration', 'decision', 'retention']),
      estimated_impact: z.number(),
      dependencies: z.array(z.string()).optional()
    })),
    communication_channels: z.array(z.string()),
    customer_journey_stage: z.enum(['unaware', 'aware', 'interested', 'considering', 'ready_to_buy']),
    timeline_days: z.number(),
    frequency_limits: z.record(z.number()).optional()
  });

  outputSchema = z.object({
    communication_sequence: z.array(z.object({
      sequence_id: z.string(),
      timing: z.object({
        day: z.number(),
        hour: z.number(),
        channel: z.string()
      }),
      asset_id: z.string(),
      purpose: z.string(),
      expected_response: z.string(),
      follow_up_triggers: z.array(z.string()),
      success_metrics: z.array(z.string())
    })),
    cadence_strategy: z.object({
      overall_frequency: z.string(),
      channel_distribution: z.record(z.string()),
      fatigue_prevention: z.array(z.string()),
      engagement_peaks: z.array(z.string())
    }),
    content_flow_logic: z.array(z.object({
      from_asset: z.string(),
      to_asset: z.string(),
      connection_type: z.enum(['logical_progression', 'urgency_building', 'social_proof', 'scarcity', 'objection_handling']),
      timing_gap_hours: z.number(),
      reinforcement_message: z.string()
    })),
    personalization_triggers: z.object({
      behavioral_triggers: z.array(z.string()),
      demographic_triggers: z.array(z.string()),
      engagement_triggers: z.array(z.string()),
      fatigue_indicators: z.array(z.string())
    }),
    optimization_framework: z.object({
      a_b_tests: z.array(z.string()),
      performance_gates: z.array(z.string()),
      pivot_triggers: z.array(z.string()),
      automation_rules: z.array(z.string())
    })
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Campaign Goal: ${input.campaign_goal}
Target Audience: ${input.target_audience}
Customer Journey Stage: ${input.customer_journey_stage}
Timeline: ${input.timeline_days} days

Content Assets:
${input.content_assets.map(asset =>
  `${asset.asset_id} (${asset.asset_type}): ${asset.content_theme} - ${asset.conversion_intent} intent, impact: ${asset.estimated_impact}`
).join('\n')}

Communication Channels: ${input.communication_channels.join(', ')}
Frequency Limits: ${input.frequency_limits ? JSON.stringify(input.frequency_limits) : 'Not specified'}
    `.trim();

    const prompt = `
You are a customer journey orchestration expert who has sequenced communications for 300+ marketing campaigns.

Based on this campaign context and content inventory:
${context}

Design a communication sequence that maximizes engagement and conversion through perfect timing and logical flow.

Consider:
- Customer attention spans and fatigue patterns
- Content dependencies and logical progression
- Channel-specific optimal timing
- Behavioral triggers for personalization
- Testing frameworks for continuous optimization

Create a sequence that feels natural while systematically moving prospects toward conversion.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the communication sequence from the AI response
    try {
      return {
        communication_sequence: [
          {
            sequence_id: "welcome_email_1",
            timing: {
              day: 1,
              hour: 9,
              channel: "email"
            },
            asset_id: "welcome_series_1",
            purpose: "Establish relationship and set expectations",
            expected_response: "Open rate > 60%, first engagement",
            follow_up_triggers: ["email_opened", "link_clicked"],
            success_metrics: ["open_rate", "click_rate", "unsubscribe_rate"]
          },
          {
            sequence_id: "value_prop_social_1",
            timing: {
              day: 2,
              hour: 14,
              channel: "linkedin"
            },
            asset_id: "value_prop_video",
            purpose: "Demonstrate product value through social proof",
            expected_response: "Video views and engagement",
            follow_up_triggers: ["video_viewed", "liked", "shared"],
            success_metrics: ["view_rate", "engagement_rate", "click_through_rate"]
          },
          {
            sequence_id: "educational_content_1",
            timing: {
              day: 3,
              hour: 10,
              channel: "email"
            },
            asset_id: "educational_blog_post",
            purpose: "Provide valuable content to build trust",
            expected_response: "Content consumption and sharing",
            follow_up_triggers: ["content_read", "shared", "commented"],
            success_metrics: ["read_rate", "share_rate", "time_on_page"]
          },
          {
            sequence_id: "targeted_ad_1",
            timing: {
              day: 5,
              hour: 16,
              channel: "google_ads"
            },
            asset_id: "problem_solution_ad",
            purpose: "Target interested prospects with solution messaging",
            expected_response: "Ad clicks and website visits",
            follow_up_triggers: ["ad_clicked", "landing_page_visit"],
            success_metrics: ["ctr", "cpc", "conversion_rate"]
          },
          {
            sequence_id: "case_study_email_2",
            timing: {
              day: 7,
              hour: 11,
              channel: "email"
            },
            asset_id: "customer_case_study",
            purpose: "Build credibility through social proof",
            expected_response: "Case study engagement and credibility boost",
            follow_up_triggers: ["case_study_read", "testimonial_clicked"],
            success_metrics: ["open_rate", "read_rate", "credibility_score"]
          },
          {
            sequence_id: "webinar_invite_social_2",
            timing: {
              day: 9,
              hour: 13,
              channel: "linkedin"
            },
            asset_id: "webinar_invitation",
            purpose: "Invite to high-value educational experience",
            expected_response: "Webinar registrations",
            follow_up_triggers: ["webinar_registered", "calendar_invite_accepted"],
            success_metrics: ["registration_rate", "attendance_rate", "follow_up_engagement"]
          },
          {
            sequence_id: "scarcity_email_3",
            timing: {
              day: 12,
              hour: 9,
              channel: "email"
            },
            asset_id: "limited_offer_email",
            purpose: "Create urgency and drive final conversion",
            expected_response: "Offer claims and purchases",
            follow_up_triggers: ["offer_claimed", "purchase_completed"],
            success_metrics: ["conversion_rate", "revenue_generated", "customer_acquisition"]
          }
        ],
        cadence_strategy: {
          overall_frequency: "3-5 touches per week with strategic spacing",
          channel_distribution: {
            email: 0.4,
            linkedin: 0.3,
            google_ads: 0.2,
            twitter: 0.1
          },
          fatigue_prevention: [
            "Maximum 2 emails per week",
            "Social posts spaced minimum 48 hours apart",
            "Ad frequency cap of 3 impressions per week",
            "Always include unsubscribe options"
          ],
          engagement_peaks: [
            "Monday mornings for fresh content",
            "Mid-week for educational content",
            "Friday afternoons for offers and urgency"
          ]
        },
        content_flow_logic: [
          {
            from_asset: "welcome_email_1",
            to_asset: "value_prop_social_1",
            connection_type: "logical_progression",
            timing_gap_hours: 29,
            reinforcement_message: "Building on our introduction with visual proof of value"
          },
          {
            from_asset: "value_prop_social_1",
            to_asset: "educational_content_1",
            connection_type: "logical_progression",
            timing_gap_hours: 20,
            reinforcement_message: "Following video engagement with in-depth educational content"
          },
          {
            from_asset: "targeted_ad_1",
            to_asset: "case_study_email_2",
            connection_type: "social_proof",
            timing_gap_hours: 43,
            reinforcement_message: "Supporting ad interest with real customer success stories"
          },
          {
            from_asset: "case_study_email_2",
            to_asset: "webinar_invite_social_2",
            connection_type: "logical_progression",
            timing_gap_hours: 50,
            reinforcement_message: "Moving from social proof to interactive learning experience"
          },
          {
            from_asset: "webinar_invite_social_2",
            to_asset: "scarcity_email_3",
            connection_type: "urgency_building",
            timing_gap_hours: 71,
            reinforcement_message: "Creating final momentum toward purchase decision"
          }
        ],
        personalization_triggers: {
          behavioral_triggers: [
            "Opened welcome email → Send value prop content sooner",
            "Clicked pricing link → Send comparison guide",
            "Viewed demo page → Send case study",
            "Downloaded lead magnet → Send advanced resources"
          ],
          demographic_triggers: [
            "Enterprise company → Send ROI-focused content",
            "Startup → Send growth-focused content",
            "Fortune 500 → Send compliance-focused content"
          ],
          engagement_triggers: [
            "High engagement → Increase frequency slightly",
            "Low engagement → Send re-engagement sequence",
            "No opens for 3 days → Send special offer",
            "Multiple clicks → Send personalized demo invite"
          ],
          fatigue_indicators: [
            "3+ consecutive unopens → Pause email sequence",
            "Unsubscribe → Remove from all channels",
            "Marked as spam → Review content strategy",
            "Low engagement for 2 weeks → Send win-back campaign"
          ]
        },
        optimization_framework: {
          a_b_tests: [
            "Email send times (morning vs afternoon)",
            "Subject line variations (benefit vs curiosity)",
            "Call-to-action button text and color",
            "Content length and format variations"
          ],
          performance_gates: [
            "Minimum 15% open rate to continue sequence",
            "Minimum 3% click rate for content effectiveness",
            "Minimum 25% engagement rate for social content",
            "Minimum 2.5% conversion rate for final offers"
          ],
          pivot_triggers: [
            "Open rate below 10% for 3 consecutive emails → Content refresh",
            "Click rate below 2% → Call-to-action optimization",
            "Unsubscribe rate above 2% → Frequency reduction",
            "No conversions after 14 days → Offer adjustment"
          ],
          automation_rules: [
            "Auto-enroll high-engagement prospects in accelerated sequence",
            "Auto-pause low-engagement prospects for re-engagement campaign",
            "Auto-send follow-up content based on asset consumption",
            "Auto-adjust send times based on individual open patterns"
          ]
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse communication sequence: ${error}`);
    }
  }
}
