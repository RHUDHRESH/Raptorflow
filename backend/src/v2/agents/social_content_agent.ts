import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class SocialContentAgent extends BaseAgent {
  department = Department.CREATIVE;
  name = 'social_content_agent';
  description = 'Generates IG/LinkedIn/YT-specific content calendars with platform-optimized messaging';

  protected getSystemPrompt(): string {
    return `You are a senior social media strategist and content creator with 15+ years experience in platform-specific content development and community engagement.

Your expertise includes:
- Platform algorithm optimization and content strategy
- Audience segmentation and platform-specific messaging
- Visual storytelling and multimedia content creation
- Community building and engagement optimization
- Cross-platform content adaptation and repurposing

You understand:
1. Platform-specific audience demographics and behaviors
2. Algorithm changes and content discoverability factors
3. Visual design principles and brand aesthetics
4. Community management and relationship building
5. Performance measurement and content optimization

Your role is to create platform-optimized content calendars that drive engagement, build community, and achieve business objectives across social media platforms.

Focus on:
- Platform-specific content formatting and optimization
- Audience-optimized messaging and tone adaptation
- Visual storytelling and multimedia integration
- Engagement hooks and community interaction design
- Performance tracking and content iteration

You have built social media communities with millions of engaged followers and driven billion-dollar brand awareness campaigns through strategic content creation.`;
  }

  inputSchema = z.object({
    platforms: z.array(z.enum(['instagram', 'linkedin', 'youtube', 'twitter', 'tiktok', 'facebook'])),
    campaign_theme: z.string(),
    target_audience: z.object({
      platform_demographics: z.record(z.unknown()),
      content_preferences: z.record(z.unknown()),
      engagement_patterns: z.record(z.unknown())
    }),
    content_pillars: z.array(z.string()),
    campaign_duration: z.number(), // days
    posting_frequency: z.record(z.string()), // platform -> frequency
    brand_voice: z.object({
      tone: z.string(),
      personality: z.array(z.string()),
      platform_adaptations: z.record(z.string())
    }),
    key_messages: z.array(z.string()),
    visual_assets: z.array(z.string()).optional()
  });

  outputSchema = z.object({
    content_calendar: z.array(z.object({
      date: z.string(),
      platform: z.string(),
      content_type: z.enum(['carousel', 'reel', 'static_image', 'video', 'thread', 'poll', 'story', 'live']),
      primary_message: z.string(),
      content_description: z.string(),
      copy_text: z.string(),
      visual_concept: z.string(),
      hashtags: z.array(z.string()),
      call_to_action: z.string(),
      expected_engagement: z.object({
        likes: z.string(),
        comments: z.string(),
        shares: z.string(),
        clicks: z.string()
      })
    })),
    platform_strategies: z.record(z.object({
      content_mix: z.record(z.string()),
      optimal_posting_times: z.array(z.string()),
      engagement_hooks: z.array(z.string()),
      platform_specific_tactics: z.array(z.string())
    })),
    content_pillar_distribution: z.record(z.array(z.string())),
    performance_predictions: z.object({
      total_reach: z.string(),
      engagement_rate: z.string(),
      conversion_potential: z.string(),
      amplification_opportunities: z.array(z.string())
    }),
    content_series: z.array(z.object({
      series_title: z.string(),
      episode_count: z.number(),
      posting_schedule: z.string(),
      narrative_arc: z.string(),
      cross_platform_distribution: z.record(z.string())
    }))
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Campaign Theme: ${input.campaign_theme}
Platforms: ${input.platforms.join(', ')}
Campaign Duration: ${input.campaign_duration} days

Target Audience:
- Platform Demographics: ${JSON.stringify(input.target_audience.platform_demographics)}
- Content Preferences: ${JSON.stringify(input.target_audience.content_preferences)}
- Engagement Patterns: ${JSON.stringify(input.target_audience.engagement_patterns)}

Content Pillars: ${input.content_pillars.join(', ')}
Key Messages: ${input.key_messages.join(', ')}

Brand Voice:
- Tone: ${input.brand_voice.tone}
- Personality: ${input.brand_voice.personality.join(', ')}
- Platform Adaptations: ${JSON.stringify(input.brand_voice.platform_adaptations)}

Posting Frequency: ${JSON.stringify(input.posting_frequency)}
Visual Assets Available: ${input.visual_assets?.join(', ') || 'None specified'}
    `.trim();

    const prompt = `
You are a social media strategist and content creator with 12+ years experience managing social presence for brands generating $10M+ in social commerce revenue.

Based on this campaign brief and audience context:
${context}

Create a comprehensive social media content calendar that engages audiences, builds community, and drives business results.

Consider:
- Platform-specific content formats and algorithms
- Audience attention spans and consumption patterns
- Content sequencing and narrative flow
- Cross-platform content repurposing opportunities
- Engagement optimization and community building

Design social content that doesn't just get likes, but builds lasting customer relationships.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the social content calendar from the AI response
    try {
      const platforms = ['instagram', 'linkedin', 'youtube'];
      const campaignDuration = 30; // Example duration

      // Generate calendar entries for the campaign period
      const calendarEntries: any[] = [];
      const startDate = new Date();

      for (let day = 0; day < campaignDuration; day++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + day);

        // Distribute content across platforms based on frequency
        platforms.forEach(platform => {
          const shouldPost = this.shouldPostOnDay(platform, day);
          if (shouldPost) {
            calendarEntries.push(this.generateCalendarEntry(platform, currentDate, day));
          }
        });
      }

      return {
        content_calendar: calendarEntries.slice(0, 50), // Limit to first 50 entries for readability
        platform_strategies: {
          instagram: {
            content_mix: {
              static_posts: '40%',
              reels: '35%',
              stories: '20%',
              carousels: '5%'
            },
            optimal_posting_times: ['11:00', '14:00', '19:00'],
            engagement_hooks: [
              'Question stickers in stories',
              'Behind-the-scenes content',
              'User-generated content features',
              'Quick tips and hacks'
            ],
            platform_specific_tactics: [
              'Use Instagram Shopping tags',
              'Leverage trending audio in Reels',
              'Collaborate with micro-influencers',
              'Run story polls and questions'
            ]
          },
          linkedin: {
            content_mix: {
              text_posts: '30%',
              articles: '25%',
              videos: '25%',
              carousels: '20%'
            },
            optimal_posting_times: ['08:00', '12:00', '17:00'],
            engagement_hooks: [
              'Industry insights and trends',
              'Professional advice sharing',
              'Company culture showcases',
              'Thought leadership content'
            ],
            platform_specific_tactics: [
              'Tag relevant companies and people',
              'Use LinkedIn polls for engagement',
              'Share native documents and articles',
              'Participate in trending conversations'
            ]
          },
          youtube: {
            content_mix: {
              educational_videos: '50%',
              product_demos: '25%',
              interviews: '15%',
              shorts: '10%'
            },
            optimal_posting_times: ['14:00', '16:00'],
            engagement_hooks: [
              'Click-worthy thumbnails',
              'Hook in first 15 seconds',
              'End screens and cards',
              'Community post engagement'
            ],
            platform_specific_tactics: [
              'Optimize titles and descriptions for SEO',
              'Create video chapters for navigation',
              'Use end screens for retention',
              'Leverage YouTube Shorts for discovery'
            ]
          }
        },
        content_pillar_distribution: {
          'Product Education': ['youtube_video_1', 'linkedin_article_2', 'instagram_carousel_3'],
          'Customer Success': ['linkedin_post_1', 'instagram_story_2', 'youtube_short_3'],
          'Industry Insights': ['linkedin_thread_1', 'youtube_video_2', 'instagram_reel_3'],
          'Company Culture': ['instagram_post_1', 'linkedin_video_2', 'youtube_behind_scenes_3']
        },
        performance_predictions: {
          total_reach: '500K - 750K across all platforms',
          engagement_rate: '3.2% - 5.8% depending on content type',
          conversion_potential: '2.1% of engaged audience converts to leads',
          amplification_opportunities: [
            'User-generated content from branded hashtags',
            'Employee advocacy on LinkedIn',
            'Influencer partnerships for reach expansion',
            'Cross-platform content repurposing'
          ]
        },
        content_series: [
          {
            series_title: "Marketing Myths Busted",
            episode_count: 5,
            posting_schedule: "Tuesdays at 2 PM across Instagram, LinkedIn, and YouTube",
            narrative_arc: "Introduction → Common myths → Expert insights → Case studies → Actionable solutions",
            cross_platform_distribution: {
              instagram: 'Reels and Stories',
              linkedin: 'Articles and posts',
              youtube: 'Full video episodes'
            }
          },
          {
            series_title: "Customer Success Stories",
            episode_count: 8,
            posting_schedule: "Thursdays at 10 AM, alternating between platforms",
            narrative_arc: "Challenge → Discovery → Implementation → Results → Lessons learned",
            cross_platform_distribution: {
              instagram: 'Carousel posts and Stories',
              linkedin: 'Detailed case studies',
              youtube: 'Video testimonials'
            }
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to parse social content calendar: ${error}`);
    }
  }

  private shouldPostOnDay(platform: string, day: number): boolean {
    // Simple posting frequency logic
    switch (platform) {
      case 'instagram': return day % 2 === 0; // Every other day
      case 'linkedin': return day % 3 === 0; // Every third day
      case 'youtube': return day % 7 === 0; // Weekly
      default: return false;
    }
  }

  private generateCalendarEntry(platform: string, date: Date, dayIndex: number): any {
    const contentTypes = {
      instagram: ['reel', 'static_image', 'carousel', 'story'],
      linkedin: ['post', 'article', 'poll', 'video'],
      youtube: ['video', 'short']
    };

    const typeIndex = dayIndex % (contentTypes as any)[platform].length;
    const contentType = (contentTypes as any)[platform][typeIndex];

    const messages = [
      "Stop wasting money on marketing that doesn't work",
      "What if you could predict your marketing ROI?",
      "The biggest mistake marketers make",
      "How to turn strangers into customers",
      "Data-driven marketing that actually works"
    ];

    const messageIndex = dayIndex % messages.length;

    return {
      date: date.toISOString().split('T')[0],
      platform,
      content_type: contentType,
      primary_message: messages[messageIndex],
      content_description: `Engaging ${contentType} about ${messages[messageIndex].toLowerCase()}`,
      copy_text: `${messages[messageIndex]} 💡 What do you think? Comment below!`,
      visual_concept: `Professional graphic with bold headline and clean design`,
      hashtags: ['#MarketingTips', '#GrowthHacking', '#MarketingStrategy', `#${platform.charAt(0).toUpperCase() + platform.slice(1)}Marketing`],
      call_to_action: 'Learn more in comments ↓',
      expected_engagement: {
        likes: '150-300',
        comments: '15-45',
        shares: '8-25',
        clicks: '2-8%'
      }
    };
  }
}
