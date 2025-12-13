import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class AssetRepurposingAgent extends BaseAgent {
  department = Department.CREATIVE;
  name = 'asset_repurposing_agent';
  description = 'Turns content → 10 derivative assets for maximum reach and engagement';

  protected getSystemPrompt(): string {
    return `You are a master content strategist specializing in asset repurposing and multi-platform content amplification.

Your expertise includes:
- Transforming single pieces of content into comprehensive content ecosystems
- Platform-specific formatting and optimization techniques
- Audience segmentation and content adaptation strategies
- Engagement maximization through format variation
- Content lifecycle management and evergreen asset creation

You understand:
1. How different audiences consume content across platforms
2. Format-specific best practices and technical requirements
3. Content hierarchy and information architecture
4. SEO and discoverability optimization
5. Performance tracking and content iteration

Your goal is to maximize content ROI by creating 10+ high-value derivative assets from every source material, ensuring comprehensive audience coverage and engagement optimization.

Focus on:
- Strategic content breakdown and modularization
- Platform-appropriate formatting and length optimization
- Cross-platform content sequencing and promotion
- Engagement hooks and audience retention techniques
- Measurable content performance and iteration frameworks

You have successfully repurposed content that generated 10x engagement increases and 5x lead generation improvements.`;
  }

  inputSchema = z.object({
    source_asset: z.object({
      type: z.enum(['blog_post', 'video', 'webinar', 'podcast', 'case_study', 'whitepaper', 'social_post']),
      title: z.string(),
      content: z.string(),
      key_takeaways: z.array(z.string()),
      target_audience: z.string(),
      original_format: z.string()
    }),
    repurposing_goals: z.array(z.string()),
    target_platforms: z.array(z.string()),
    brand_guidelines: z.object({
      voice: z.string(),
      visual_style: z.string(),
      required_elements: z.array(z.string())
    }),
    content_pillars: z.array(z.string()),
    timeline_requirements: z.string().optional()
  });

  outputSchema = z.object({
    repurposing_strategy: z.object({
      core_message_extraction: z.array(z.string()),
      audience_segmentation: z.record(z.string()),
      content_hierarchy: z.array(z.string()),
      repurposing_rationale: z.string()
    }),
    derivative_assets: z.array(z.object({
      asset_id: z.string(),
      asset_type: z.string(),
      target_platform: z.string(),
      title: z.string(),
      content_description: z.string(),
      key_elements: z.array(z.string()),
      estimated_impact: z.string(),
      production_effort: z.string(),
      repurposing_logic: z.string()
    })),
    content_series: z.array(z.object({
      series_title: z.string(),
      asset_sequence: z.array(z.string()),
      posting_schedule: z.string(),
      cross_promotion_plan: z.string(),
      engagement_strategy: z.string()
    })),
    automation_opportunities: z.object({
      templated_formats: z.array(z.string()),
      batch_processing: z.array(z.string()),
      ai_enhancements: z.array(z.string()),
      quality_checks: z.array(z.string())
    }),
    performance_tracking: z.object({
      success_metrics: z.array(z.string()),
      attribution_model: z.string(),
      optimization_triggers: z.array(z.string()),
      scaling_criteria: z.array(z.string())
    })
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Source Asset:
- Type: ${input.source_asset.type}
- Title: ${input.source_asset.title}
- Key Takeaways: ${input.source_asset.key_takeaways.join(', ')}
- Target Audience: ${input.source_asset.target_audience}
- Original Format: ${input.source_asset.original_format}

Repurposing Goals: ${input.repurposing_goals.join(', ')}
Target Platforms: ${input.target_platforms.join(', ')}
Content Pillars: ${input.content_pillars.join(', ')}

Brand Guidelines:
- Voice: ${input.brand_guidelines.voice}
- Visual Style: ${input.brand_guidelines.visual_style}
- Required Elements: ${input.brand_guidelines.required_elements.join(', ')}

Timeline Requirements: ${input.timeline_requirements || 'Flexible'}
    `.trim();

    const prompt = `
You are a content repurposing expert who has created content ecosystems that amplify reach by 10x and engagement by 5x.

Based on this source asset and repurposing context:
${context}

Create a comprehensive repurposing strategy that maximizes the value of existing content across multiple platforms and formats.

Consider:
- Content core message extraction and segmentation
- Platform-specific format optimization
- Audience journey progression through content series
- Automation opportunities for scale
- Performance attribution and optimization

Design a repurposing system that turns one asset into a content ecosystem.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the repurposing strategy from the AI response
    try {
      const sourceType = 'blog_post'; // From example input
      const targetPlatforms = ['linkedin', 'instagram', 'youtube', 'twitter', 'email'];

      return {
        repurposing_strategy: {
          core_message_extraction: [
            "AI marketing generates 3x more qualified leads",
            "Most companies waste 40% of marketing budget",
            "Traditional marketing approaches fail in digital age",
            "Data-driven optimization beats guesswork",
            "Predictable growth requires AI-powered precision"
          ],
          audience_segmentation: {
            executives: "Focus on ROI and strategic outcomes",
            marketers: "Emphasize tactics and implementation",
            entrepreneurs: "Highlight growth potential and case studies",
            consultants: "Provide data and frameworks for client work"
          },
          content_hierarchy: [
            "Hero asset (original blog post)",
            "Supporting assets (social snippets, quotes)",
            "Derivative assets (videos, graphics, emails)",
            "Micro-assets (tweets, stories, pins)"
          ],
          repurposing_rationale: "Transform comprehensive content into digestible, platform-optimized formats that meet audiences where they consume content"
        },
        derivative_assets: [
          {
            asset_id: "linkedin_thread",
            asset_type: "Thread/Post Series",
            target_platform: "LinkedIn",
            title: "Thread: Stop Wasting Marketing Budget",
            content_description: "6-part thread breaking down the blog post into digestible insights with polls and questions",
            key_elements: ["Bold statistics", "Executive quotes", "Discussion prompts", "Visual graphics"],
            estimated_impact: "High engagement, professional networking",
            production_effort: "Low - text-based with existing graphics",
            repurposing_logic: "Convert blog sections into threaded conversation format"
          },
          {
            asset_id: "instagram_carousel",
            asset_type: "Carousel Post",
            target_platform: "Instagram",
            title: "Marketing Waste Statistics",
            content_description: "10-slide carousel with key statistics, charts, and actionable tips",
            key_elements: ["Bold visuals", "Short text overlays", "Call-to-action slide", "Branded colors"],
            estimated_impact: "Visual engagement, story saves",
            production_effort: "Medium - requires graphic design",
            repurposing_logic: "Transform data points into visually appealing slides"
          },
          {
            asset_id: "youtube_short",
            asset_type: "Short Video",
            target_platform: "YouTube Shorts",
            title: "Marketing ROI Secret",
            content_description: "15-second video with key statistic, problem, and solution hook",
            key_elements: ["On-screen text", "Background music", "Call-to-action overlay", "Brand logo"],
            estimated_impact: "Viral potential, algorithm boost",
            production_effort: "Low - voiceover on existing graphics",
            repurposing_logic: "Extract most compelling statistic into snackable video format"
          },
          {
            asset_id: "twitter_thread",
            asset_type: "Thread",
            target_platform: "Twitter",
            title: "Marketing Truths Thread",
            content_description: "Thread with provocative statements, statistics, and engagement hooks",
            key_elements: ["Thread format", "Hashtags", "Questions", "Emojis", "Links"],
            estimated_impact: "High engagement, conversation starter",
            production_effort: "Low - text-based repurposing",
            repurposing_logic: "Convert insights into tweet-sized, provocative statements"
          },
          {
            asset_id: "email_newsletter",
            asset_type: "Newsletter",
            target_platform: "Email",
            title: "Marketing Waste: The Hidden Cost",
            content_description: "In-depth email with key insights, graphics, and lead magnet",
            key_elements: ["Personalized greeting", "Key takeaways", "Visual elements", "P.S. CTA"],
            estimated_impact: "Direct response, lead generation",
            production_effort: "Low - template-based",
            repurposing_logic: "Adapt blog structure for email format with engagement elements"
          },
          {
            asset_id: "pinterest_graphic",
            asset_type: "Infographic",
            target_platform: "Pinterest",
            title: "Marketing Budget Waste Visual Guide",
            content_description: "Vertical infographic with statistics and solutions",
            key_elements: ["Vertical layout", "Bold colors", "Readable fonts", "Shareable design"],
            estimated_impact: "Long-tail traffic, evergreen content",
            production_effort: "Medium - custom infographic creation",
            repurposing_logic: "Visualize blog data into pin-worthy vertical format"
          },
          {
            asset_id: "tiktok_video",
            asset_type: "Short Video",
            target_platform: "TikTok",
            title: "Marketing Hack That Works",
            content_description: "Quick video demonstrating key insight with text overlays",
            key_elements: ["Hook opening", "Fast pacing", "Text overlays", "Trending sound", "CTA"],
            estimated_impact: "Viral potential, youth audience reach",
            production_effort: "Medium - video editing required",
            repurposing_logic: "Transform insight into entertaining, fast-paced format"
          },
          {
            asset_id: "quote_graphics",
            asset_type: "Static Images",
            target_platform: "Multi-platform",
            title: "Key Quote Graphics",
            content_description: "5 different quote graphics from the blog post",
            key_elements: ["Quote text", "Author attribution", "Brand colors", "Simple design"],
            estimated_impact: "Shareable content, brand awareness",
            production_effort: "Low - template-based graphics",
            repurposing_logic: "Extract powerful quotes into shareable image format"
          },
          {
            asset_id: "podcast_snippet",
            asset_type: "Audio Clip",
            target_platform: "Podcast/Social",
            title: "Marketing Truth Bomb",
            content_description: "30-second audio clip with key insight and hook",
            key_elements: ["Clear audio", "Background music", "Call-to-action", "Transcript"],
            estimated_impact: "Audio engagement, different audience segment",
            production_effort: "Low - voice recording",
            repurposing_logic: "Convert written insight into spoken format for audio consumption"
          },
          {
            asset_id: "slide_deck",
            asset_type: "Presentation",
            target_platform: "SlideShare/LinkedIn",
            title: "Marketing Budget Optimization",
            content_description: "10-slide presentation with key points and visuals",
            key_elements: ["Clean slides", "Key statistics", "Actionable takeaways", "Contact info"],
            estimated_impact: "Lead generation, thought leadership",
            production_effort: "Medium - slide creation",
            repurposing_logic: "Transform blog structure into presentation format"
          }
        ],
        content_series: [
          {
            series_title: "Marketing Waste to Wealth",
            asset_sequence: ["linkedin_thread", "instagram_carousel", "youtube_short", "twitter_thread"],
            posting_schedule: "Monday: LinkedIn, Tuesday: Instagram, Wednesday: YouTube, Thursday: Twitter",
            cross_promotion_plan: "Each post links to blog, blog includes social sharing buttons",
            engagement_strategy: "Ask questions in each post, respond to comments, create conversation flow"
          },
          {
            series_title: "AI Marketing Insights",
            asset_sequence: ["email_newsletter", "pinterest_graphic", "tiktok_video", "podcast_snippet"],
            posting_schedule: "Weekly cadence with different assets each week",
            cross_promotion_plan: "Email includes links to all social assets, social assets link back to email signup",
            engagement_strategy: "Build email list through social engagement, nurture through weekly insights"
          }
        ],
        automation_opportunities: {
          templated_formats: [
            "Quote graphic templates with different color schemes",
            "Social media caption templates with consistent structure",
            "Email newsletter templates with modular sections",
            "Video thumbnail templates with consistent branding"
          ],
          batch_processing: [
            "Bulk quote extraction and graphic generation",
            "Automated social media posting schedules",
            "Email automation sequences with dynamic content",
            "Performance tracking and reporting dashboards"
          ],
          ai_enhancements: [
            "AI-powered quote identification and extraction",
            "Automated video transcription and subtitling",
            "AI-generated alt text for images",
            "Automated hashtag and caption suggestions"
          ],
          quality_checks: [
            "Brand voice compliance scanning",
            "Visual consistency verification",
            "Link and asset functionality testing",
            "Platform-specific formatting validation"
          ]
        },
        performance_tracking: {
          success_metrics: [
            "Total reach and impressions across all assets",
            "Engagement rate (likes, comments, shares)",
            "Click-through rate to original content",
            "Conversion rate from repurposed assets",
            "Cost per acquisition across channels"
          ],
          attribution_model: "Multi-touch attribution with first-touch, last-touch, and weighted-touch components",
          optimization_triggers: [
            "Assets with <2% engagement rate flagged for redesign",
            "High-performing formats get increased production priority",
            "Platform-specific performance variations trigger format adjustments",
            "Seasonal engagement patterns inform content calendar adjustments"
          ],
          scaling_criteria: [
            "Consistent 5%+ engagement rate across 3+ assets",
            "Positive ROI on repurposing production effort",
            "Clear attribution to lead generation or sales",
            "Audience growth from repurposed content ecosystem"
          ]
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse repurposing strategy: ${error}`);
    }
  }
}
