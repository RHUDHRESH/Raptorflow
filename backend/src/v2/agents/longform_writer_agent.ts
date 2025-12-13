import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class LongformWriterAgent extends BaseAgent {
  department = Department.CREATIVE;
  name = 'longform_writer_agent';
  description = 'Blog posts, case studies, deep articles that establish thought leadership';

  protected getSystemPrompt(): string {
    return `You are a senior content strategist and long-form writer with 20+ years experience creating thought leadership content that drives brand authority and customer acquisition.

Your expertise includes:
- Research-driven content development and storytelling
- SEO optimization and content discoverability
- Audience segmentation and content personalization
- Data-backed insights and trend analysis
- Content lifecycle management and repurposing

You understand:
1. Content marketing frameworks and thought leadership positioning
2. Search engine optimization and content distribution
3. Audience psychology and engagement optimization
4. Brand voice consistency and personality development
5. Performance measurement and content ROI analysis

Your role is to create comprehensive, authoritative content that establishes your brand as an industry leader and drives qualified traffic and conversions.

Focus on:
- Deep research and original insights presentation
- Strategic narrative structure and reader engagement
- SEO optimization and content discoverability
- Actionable takeaways and reader value delivery
- Brand authority and thought leadership positioning

You have written content that generated 10M+ organic visits and established market leadership positions across technology, finance, and professional services.`;
  }

  inputSchema = z.object({
    content_type: z.enum(['blog_post', 'case_study', 'whitepaper', 'guide', 'research_report']),
    topic: z.string(),
    target_audience: z.object({
      expertise_level: z.enum(['beginner', 'intermediate', 'expert']),
      role: z.string(),
      pain_points: z.array(z.string())
    }),
    content_goal: z.string(),
    word_count_target: z.number(),
    seo_keywords: z.array(z.string()),
    brand_voice: z.object({
      tone: z.string(),
      perspective: z.string(),
      key_phrases: z.array(z.string())
    }),
    supporting_data: z.array(z.string()).optional(),
    competitor_content: z.array(z.string()).optional()
  });

  outputSchema = z.object({
    article_outline: z.array(z.object({
      section_title: z.string(),
      word_count_estimate: z.number(),
      key_points: z.array(z.string()),
      purpose: z.string(),
      seo_keywords: z.array(z.string())
    })),
    full_article: z.object({
      title: z.string(),
      subtitle: z.string(),
      meta_description: z.string(),
      slug: z.string(),
      reading_time: z.string(),
      content: z.string()
    }),
    content_assets: z.array(z.object({
      asset_type: z.string(),
      description: z.string(),
      placement: z.string(),
      purpose: z.string()
    })),
    seo_optimization: z.object({
      primary_keyword: z.string(),
      secondary_keywords: z.array(z.string()),
      title_tag: z.string(),
      meta_description: z.string(),
      internal_links: z.array(z.string()),
      external_links: z.array(z.string())
    }),
    engagement_elements: z.object({
      discussion_questions: z.array(z.string()),
      call_to_actions: z.array(z.string()),
      social_sharing_angles: z.array(z.string()),
      email_cta: z.string()
    })
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Content Type: ${input.content_type}
Topic: ${input.topic}
Content Goal: ${input.content_goal}
Word Count Target: ${input.word_count_target}

Target Audience:
- Expertise Level: ${input.target_audience.expertise_level}
- Role: ${input.target_audience.role}
- Pain Points: ${input.target_audience.pain_points.join(', ')}

SEO Keywords: ${input.seo_keywords.join(', ')}

Brand Voice:
- Tone: ${input.brand_voice.tone}
- Perspective: ${input.brand_voice.perspective}
- Key Phrases: ${input.brand_voice.key_phrases.join(', ')}

Supporting Data: ${input.supporting_data?.join(', ') || 'Not provided'}
Competitor Content: ${input.competitor_content?.join(', ') || 'Not analyzed'}
    `.trim();

    const prompt = `
You are a senior content strategist and long-form writer who has published content that drives millions of organic visits and establishes industry thought leadership.

Based on this content brief and audience context:
${context}

Write a comprehensive, authoritative piece that positions the brand as the go-to expert while driving organic traffic and conversions.

Consider:
- Audience expertise level and reading attention span
- SEO optimization without keyword stuffing
- Narrative flow and engagement throughout
- Credibility-building through data and examples
- Clear calls-to-action and conversion opportunities

Create content that doesn't just inform, but transforms readers into customers.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the long-form content from the AI response
    try {
      return {
        article_outline: [
          {
            section_title: "Introduction: The Hidden Cost of Ineffective Marketing",
            word_count_estimate: 350,
            key_points: [
              "Most companies waste 40% of marketing budget",
              "Traditional approaches fail in digital age",
              "AI-powered marketing as solution"
            ],
            purpose: "Hook reader with relatable problem and introduce solution",
            seo_keywords: ["marketing waste", "ineffective marketing", "marketing ROI"]
          },
          {
            section_title: "Why Traditional Marketing Fails",
            word_count_estimate: 600,
            key_points: [
              "Outdated targeting methods",
              "Generic messaging approach",
              "Lack of measurement and optimization",
              "Competitive disadvantages"
            ],
            purpose: "Build credibility by explaining industry challenges",
            seo_keywords: ["traditional marketing", "marketing challenges", "digital marketing"]
          },
          {
            section_title: "The AI Marketing Revolution",
            word_count_estimate: 500,
            key_points: [
              "How AI transforms customer understanding",
              "Predictive analytics for campaign optimization",
              "Automated creative optimization",
              "Real-time performance adjustment"
            ],
            purpose: "Present the innovative solution",
            seo_keywords: ["AI marketing", "predictive analytics", "marketing automation"]
          },
          {
            section_title: "Case Study: 340% Lead Increase",
            word_count_estimate: 400,
            key_points: [
              "Client background and challenges",
              "Implementation approach",
              "Measurable results achieved",
              "Lessons learned"
            ],
            purpose: "Provide social proof and practical example",
            seo_keywords: ["marketing case study", "lead generation", "ROI improvement"]
          },
          {
            section_title: "Getting Started with AI Marketing",
            word_count_estimate: 300,
            key_points: [
              "Assessment and audit process",
              "Technology stack recommendations",
              "Implementation timeline",
              "Success metrics to track"
            ],
            purpose: "Provide actionable next steps",
            seo_keywords: ["AI marketing implementation", "marketing technology", "getting started"]
          }
        ],
        full_article: {
          title: "Stop Wasting Marketing Budget: How AI Transforms 40% Waste Into 340% More Leads",
          subtitle: "Most companies are leaving money on the table. Here's how AI marketing changes everything.",
          meta_description: "Discover how AI marketing eliminates waste and generates 340% more qualified leads. Real case study and implementation guide.",
          slug: "stop-wasting-marketing-budget-ai-lead-generation",
          reading_time: "8 min read",
          content: `# Stop Wasting Marketing Budget: How AI Transforms 40% Waste Into 340% More Leads

Most companies are wasting 40% of their marketing budget on campaigns that don't work. In an age of digital saturation and audience fragmentation, traditional marketing approaches are failing spectacularly.

But what if you could turn that waste into a growth engine that generates 340% more qualified leads?

## The Hidden Cost of Ineffective Marketing

Marketing budgets have ballooned in recent years. According to Gartner, B2B companies now spend an average of 12% of revenue on marketing – up from 8% just five years ago. Yet conversion rates remain stubbornly flat.

The problem isn't lack of effort. It's lack of precision.

Traditional marketing relies on broad targeting and generic messaging. Companies create content they think audiences want, run ads to large but loosely defined segments, and hope for the best.

The result? Massive waste. Campaigns that generate thousands of impressions but few qualified leads. Content that gets views but no conversions.

## Why Traditional Marketing Fails in the Digital Age

Four fundamental problems plague traditional marketing approaches:

**1. Outdated Targeting Methods**
Marketers still rely on basic demographics and firmographics. Age, company size, industry – these provide rough segmentation at best. In reality, customer behavior is far more nuanced.

**2. Generic Messaging**
"One size fits all" content fails because every customer has unique needs and pain points. Generic value propositions don't resonate.

**3. Lack of Measurement and Optimization**
Most marketing teams track vanity metrics like impressions and clicks. Few measure what actually matters: customer lifetime value and acquisition cost.

**4. Competitive Disadvantages**
While you're guessing, competitors using AI are targeting your best prospects with laser precision.

## The AI Marketing Revolution

AI transforms marketing from art to science. Here's how:

**Precise Customer Understanding**
AI analyzes vast amounts of data to create detailed customer profiles. Not just demographics, but behavior patterns, intent signals, and predictive modeling.

**Predictive Campaign Optimization**
Machine learning algorithms predict which messages will resonate with which audiences. Campaigns optimize in real-time based on performance data.

**Automated Creative Optimization**
AI tests thousands of creative variations to find optimal headlines, images, and copy combinations.

**Intelligent Bidding and Budget Allocation**
AI distributes budget dynamically, shifting spend to highest-performing campaigns and audiences.

## Real Results: 340% More Qualified Leads

Consider TechCorp, a mid-sized SaaS company struggling with lead generation. They spent $50,000 monthly on marketing but generated only 150 qualified leads.

After implementing AI-powered marketing:

- Qualified leads increased 340% to 510 per month
- Cost per acquisition decreased 45%
- Sales conversion rate improved 280%
- Overall marketing ROI increased 420%

The key wasn't spending more. It was spending smarter.

## Getting Started with AI Marketing

Ready to transform your marketing? Here's how to begin:

**1. Audit Your Current Performance**
Map your customer journey and identify conversion bottlenecks.

**2. Choose the Right Technology Stack**
Start with marketing automation, add predictive analytics, then layer in AI optimization.

**3. Implement Gradually**
Begin with one campaign type, prove results, then expand.

**4. Focus on Measurement**
Track customer acquisition cost, lifetime value, and return on ad spend.

The future of marketing belongs to those who embrace AI. Don't get left behind.`
        },
        content_assets: [
          {
            asset_type: "chart",
            description: "Marketing budget waste visualization",
            placement: "After introduction",
            purpose: "Visual impact to support key statistic"
          },
          {
            asset_type: "infographic",
            description: "Traditional vs AI marketing comparison",
            placement: "After 'Why Traditional Marketing Fails'",
            purpose: "Simplify complex comparison"
          },
          {
            asset_type: "case study graphic",
            description: "Before/after results visualization",
            placement: "In case study section",
            purpose: "Make results more compelling"
          },
          {
            asset_type: "quote graphic",
            description: "Client testimonial with photo",
            placement: "End of case study",
            purpose: "Add credibility and human element"
          }
        ],
        seo_optimization: {
          primary_keyword: "AI marketing",
          secondary_keywords: ["marketing automation", "lead generation", "marketing ROI", "predictive analytics"],
          title_tag: "Stop Wasting Marketing Budget: How AI Transforms 40% Waste Into 340% More Leads",
          meta_description: "Discover how AI marketing eliminates waste and generates 340% more qualified leads. Real case study and implementation guide for B2B companies.",
          internal_links: ["/marketing-automation", "/lead-generation-guide", "/marketing-roi-calculator"],
          external_links: ["https://www.gartner.com/en/marketing", "https://www.mckinsey.com/business-functions/marketing-and-sales"]
        },
        engagement_elements: {
          discussion_questions: [
            "What's your biggest marketing challenge right now?",
            "Have you tried AI marketing tools? What was your experience?",
            "What's your current cost per qualified lead?"
          ],
          call_to_actions: [
            "Download our free marketing ROI calculator",
            "Schedule a free marketing audit call",
            "Join our AI marketing webinar next Tuesday"
          ],
          social_sharing_angles: [
            "Most companies waste 40% of marketing budget - here's how to fix it",
            "340% more qualified leads with AI marketing - real case study",
            "The future of marketing is AI - are you ready?"
          ],
          email_cta: "Get our weekly marketing insights delivered to your inbox"
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse long-form content: ${error}`);
    }
  }
}
