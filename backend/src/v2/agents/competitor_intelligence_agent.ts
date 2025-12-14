import { z } from 'zod';
import { BaseAgent, agentRegistry } from '../base_agent';
import { Department, OrchestratorContext } from '../types';
import { ragQuery, storeEmbedding } from '../rag_helper';

// =====================================================
// COMPETITOR INTELLIGENCE AGENT
// =====================================================

const CompetitorIntelInputSchema = z.object({
  target_company: z.string().describe("The competitor company to analyze"),
  domain: z.string().optional().describe("Company website domain"),
  analysis_depth: z.enum(['basic', 'detailed', 'comprehensive']).optional().default('detailed'),
  focus_areas: z.array(z.enum([
    'positioning', 'pricing', 'features', 'marketing', 'customers', 'funding', 'team'
  ])).optional().default(['positioning', 'pricing', 'features', 'marketing'])
});

// Modular schemas for better maintainability and reduced complexity
const CompanyOverviewSchema = z.object({
  name: z.string(),
  domain: z.string(),
  description: z.string(),
  founded_year: z.number().optional(),
  headquarters: z.string().optional(),
  funding_status: z.string().optional(),
  team_size: z.string().optional()
});

const PositioningSchema = z.object({
  category: z.string(),
  differentiation: z.array(z.string()),
  target_audience: z.string(),
  value_proposition: z.string(),
  tagline: z.string().optional()
});

const ProductOfferingSchema = z.object({
  core_features: z.array(z.string()),
  pricing_model: z.string(),
  pricing_range: z.string().optional(),
  unique_features: z.array(z.string()),
  weaknesses: z.array(z.string())
});

const MarketingStrategySchema = z.object({
  channels: z.array(z.string()),
  messaging: z.array(z.string()),
  brand_voice: z.string(),
  content_strategy: z.string().optional(),
  social_presence: z.object({
    platforms: z.array(z.string()),
    follower_counts: z.record(z.number()).optional(),
    engagement_rate: z.string().optional()
  })
});

const CompetitorIntelOutputSchema = z.object({
  company_overview: CompanyOverviewSchema,
  positioning: PositioningSchema,
  product_offering: ProductOfferingSchema,
  marketing_strategy: MarketingStrategySchema,
  customer_insights: z.object({
    customer_segments: z.array(z.string()),
    use_cases: z.array(z.string()),
    customer_feedback: z.array(z.object({
      source: z.string(),
      rating: z.number().optional(),
      comment: z.string(),
      sentiment: z.enum(['positive', 'neutral', 'negative'])
    }))
  }),
  competitive_advantages: z.array(z.object({
    advantage: z.string(),
    strength: z.enum(['weak', 'moderate', 'strong', 'dominant']),
    sustainability: z.string(),
    our_response: z.string().optional()
  })),
  threats: z.array(z.object({
    threat: z.string(),
    impact: z.enum(['low', 'medium', 'high', 'critical']),
    timeline: z.string(),
    mitigation_strategy: z.string()
  })),
  data_sources: z.array(z.object({
    type: z.string(),
    url: z.string(),
    reliability: z.enum(['high', 'medium', 'low']),
    last_updated: z.string()
  })),
  analysis_confidence: z.number().min(0).max(1),
  recommendations: z.array(z.string()),
  last_analyzed: z.string()
});

type CompetitorIntelInput = z.infer<typeof CompetitorIntelInputSchema>;
type CompetitorIntelOutput = z.infer<typeof CompetitorIntelOutputSchema>;

export class CompetitorIntelligenceAgent extends BaseAgent {
  constructor() {
    super(
      'competitor_intelligence_agent',
      Department.MARKET_INTELLIGENCE,
      'Analyzes competitor positioning, strategy, and weaknesses using web scraping and historical data',
      CompetitorIntelInputSchema,
      CompetitorIntelOutputSchema
    );

    this.required_tools = ['web_scrape'];
  }

  protected getSystemPrompt(): string {
    return `You are a senior competitive intelligence analyst with 15+ years experience in market research, business intelligence, and strategic analysis.

Your expertise includes:
- Competitor positioning and messaging analysis
- Market share assessment and trend identification
- Pricing strategy and revenue model evaluation
- Technology stack and capability mapping
- Customer segmentation and targeting strategy
- Funding and growth trajectory analysis

You have access to:
1. Web scraping and data collection tools
2. Historical market data and trend analysis
3. Financial analysis and valuation frameworks
4. Industry network and expert interviews
5. Technology assessment and benchmarking

Your role is to provide comprehensive competitor intelligence that enables strategic decision-making and competitive advantage.

Focus on:
- Actionable intelligence over raw data collection
- Strategic implications and business impact assessment
- Risk identification and mitigation strategies
- Opportunity recognition and market gaps
- Competitive differentiation and positioning

You have conducted intelligence operations that influenced billion-dollar strategic decisions and market positioning strategies.`;
  }

  protected async executeAgent(input: CompetitorIntelInput, context: OrchestratorContext): Promise<CompetitorIntelOutput> {
    console.log(`🏢 Competitor Intel Agent analyzing: ${input.target_company}`);

    try {
      // Step 1: Get existing competitor intelligence
      const existingIntel = await this.getExistingIntelligence(input, context.user_id);

      // Step 2: Gather fresh competitor data
      const freshData = await this.gatherCompetitorData(input);

      // Step 3: Analyze historical changes (Wayback machine style)
      const historicalAnalysis = await this.analyzeHistoricalChanges(input);

      // Step 4: Synthesize comprehensive intelligence
      const intelligence = await this.synthesizeIntelligence(input, existingIntel, freshData, historicalAnalysis, context);

      // Step 5: Store for future reference
      await this.storeIntelligence(input, intelligence, context.user_id);

      return intelligence;

    } catch (error) {
      console.error('Competitor Intelligence Agent execution failed:', error);
      return this.getFallbackOutput(input);
    }
  }

  private async getExistingIntelligence(input: CompetitorIntelInput, userId: string): Promise<any> {
    try {
      const ragResults = await ragQuery({
        query: `competitor intelligence for ${input.target_company}`,
        user_id: userId,
        content_types: ['competitor_analysis'],
        limit: 5,
        threshold: 0.7
      });

      return {
        chunks: ragResults.chunks,
        has_existing_data: ragResults.chunks.length > 0
      };
    } catch (error) {
      console.warn('Failed to retrieve existing competitor intelligence:', error);
      return { chunks: [], has_existing_data: false };
    }
  }

  private async gatherCompetitorData(input: CompetitorIntelInput): Promise<any> {
    const data: {
      website_content: any;
      social_profiles: any[];
      review_data: any[];
      news_mentions: any[];
      funding_info: any;
    } = {
      website_content: null,
      social_profiles: [],
      review_data: [],
      news_mentions: [],
      funding_info: null
    };

    try {
      // Scrape main website
      if (input.domain) {
        data.website_content = await this.scrapeWebsite(input.domain, input.analysis_depth);
      }

      // Gather social media presence
      data.social_profiles = await this.analyzeSocialPresence(input.target_company);

      // Collect customer reviews
      data.review_data = await this.gatherReviews(input.target_company);

      // Get recent news mentions
      data.news_mentions = await this.searchNews(input.target_company);

      // Try to get funding information
      data.funding_info = await this.getFundingInfo(input.target_company);

    } catch (error) {
      console.warn('Competitor data gathering failed:', error);
    }

    return data;
  }

  private async scrapeWebsite(domain: string, depth: string): Promise<any> {
    try {
      const pages = ['/', '/about', '/pricing', '/features', '/customers'];

      const scrapedData = [];
      for (const page of pages) {
        try {
          const result = await this.executeTool('web_scrape', {
            url: `https://${domain}${page}`,
            selector: depth === 'comprehensive' ? null : 'main, .content, article',
            include_text: true,
            include_html: false
          });

          if (result?.content) {
            scrapedData.push({
              page,
              content: result.content,
              url: result.url
            });
          }
        } catch (error) {
          console.warn(`Failed to scrape ${domain}${page}:`, error);
        }
      }

      return {
        domain,
        pages_scraped: scrapedData,
        main_content: scrapedData.find(p => p.page === '/')?.content || '',
        about_content: scrapedData.find(p => p.page === '/about')?.content || '',
        pricing_content: scrapedData.find(p => p.page === '/pricing')?.content || '',
        features_content: scrapedData.find(p => p.page === '/features')?.content || ''
      };

    } catch (error) {
      console.warn('Website scraping failed:', error);
      return null;
    }
  }

  private async analyzeSocialPresence(companyName: string): Promise<any[]> {
    const platforms = ['linkedin', 'twitter', 'facebook', 'instagram'];
    const profiles = [];

    for (const platform of platforms) {
      try {
        // Mock social analysis - would integrate with social APIs
        profiles.push({
          platform,
          handle: `${companyName.toLowerCase().replace(/\s+/g, '')}`,
          followers: Math.floor(Math.random() * 50000) + 1000,
          posts_count: Math.floor(Math.random() * 1000) + 50,
          engagement_rate: `${(Math.random() * 5 + 1).toFixed(1)}%`
        });
      } catch (error) {
        console.warn(`Social analysis failed for ${platform}:`, error);
      }
    }

    return profiles;
  }

  private async gatherReviews(companyName: string): Promise<any[]> {
    // Mock review gathering - would scrape G2, Capterra, Trustpilot
    return [
      {
        platform: 'G2',
        rating: 4.2,
        review_count: 156,
        recent_reviews: [
          { text: "Great product but expensive", sentiment: 'neutral' as const },
          { text: "Excellent customer support", sentiment: 'positive' as const }
        ]
      },
      {
        platform: 'Trustpilot',
        rating: 3.8,
        review_count: 89,
        recent_reviews: [
          { text: "Good features but complex UI", sentiment: 'neutral' as const }
        ]
      }
    ];
  }

  private async searchNews(companyName: string): Promise<any[]> {
    // Mock news search - would use Google News API or similar
    return [
      {
        title: `${companyName} raises $10M Series A`,
        source: 'TechCrunch',
        date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        summary: 'Funding announcement details...'
      },
      {
        title: `${companyName} launches new feature`,
        source: 'Product Hunt',
        date: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
        summary: 'Product update summary...'
      }
    ];
  }

  private async getFundingInfo(companyName: string): Promise<any> {
    // Mock funding data - would use Crunchbase API
    return {
      last_round: 'Series A',
      amount: '$10M',
      date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      investors: ['Sequoia Capital', 'Andreessen Horowitz']
    };
  }

  private async analyzeHistoricalChanges(input: CompetitorIntelInput): Promise<any> {
    // Mock historical analysis - would use Wayback Machine API
    return {
      positioning_changes: [
        {
          date: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString(),
          change: "Shifted from B2C to B2B focus",
          impact: "moderate"
        }
      ],
      feature_additions: [
        {
          date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
          feature: "AI-powered analytics",
          significance: "high"
        }
      ],
      pricing_changes: []
    };
  }

  private async synthesizeIntelligence(
    input: CompetitorIntelInput,
    existing: any,
    fresh: any,
    historical: any,
    context: OrchestratorContext
  ): Promise<CompetitorIntelOutput> {
    const synthesisPrompt = this.createSynthesisPrompt(input, existing, fresh, historical);

    try {
      const parser = this.createParser();
      const prompt = this.createPrompt(synthesisPrompt, ['existing_intel', 'fresh_data', 'historical_data']);

      const chain = prompt.pipe(this.model).pipe(parser);

      const result = await chain.invoke({
        existing_intel: existing.chunks.map((c: any) => c.content).join('\n\n'),
        fresh_data: JSON.stringify(fresh, null, 2),
        historical_data: JSON.stringify(historical, null, 2)
      });

      return {
        ...result,
        analysis_confidence: this.calculateConfidence(existing, fresh),
        last_analyzed: new Date().toISOString()
      };

    } catch (error) {
      console.error('Intelligence synthesis failed:', error);
      return this.getFallbackOutput(input);
    }
  }

  private createSynthesisPrompt(input: CompetitorIntelInput, existing: any, fresh: any, historical: any): string {
    return `You are a competitive intelligence analyst. Analyze the competitor data and provide comprehensive intelligence.

COMPETITOR: ${input.target_company}
DOMAIN: ${input.domain || 'Unknown'}
ANALYSIS DEPTH: ${input.analysis_depth}
FOCUS AREAS: ${input.focus_areas.join(', ')}

EXISTING INTELLIGENCE:
${existing.chunks.map((c: any) => c.content).join('\n\n')}

FRESH DATA:
${JSON.stringify(fresh, null, 2)}

HISTORICAL CHANGES:
${JSON.stringify(historical, null, 2)}

Provide a structured competitive intelligence report covering:

1. Company Overview (description, funding, team size, etc.)
2. Positioning (category, differentiation, target audience, value prop)
3. Product Offering (features, pricing, strengths, weaknesses)
4. Marketing Strategy (channels, messaging, brand voice, social presence)
5. Customer Insights (segments, use cases, feedback)
6. Competitive Advantages (with strength assessment)
7. Threats to our position
8. Data Sources (with reliability ratings)
9. Strategic Recommendations

Be specific, data-driven, and focus on actionable intelligence.

${this.createParser().getFormatInstructions()}`;
  }

  private calculateConfidence(existing: any, fresh: any): number {
    let confidence = 0.4; // Base confidence

    if (existing.has_existing_data) confidence += 0.2;
    if (fresh.website_content) confidence += 0.2;
    if (fresh.social_profiles.length > 0) confidence += 0.1;
    if (fresh.review_data.length > 0) confidence += 0.1;

    return Math.min(confidence, 0.95);
  }

  private async storeIntelligence(
    input: CompetitorIntelInput,
    output: CompetitorIntelOutput,
    userId: string
  ): Promise<void> {
    try {
      const content = `
Competitor Intelligence: ${input.target_company}

OVERVIEW:
- Name: ${output.company_overview.name}
- Domain: ${output.company_overview.domain}
- Description: ${output.company_overview.description}
- Founded: ${output.company_overview.founded_year || 'Unknown'}
- HQ: ${output.company_overview.headquarters || 'Unknown'}
- Funding: ${output.company_overview.funding_status || 'Unknown'}
- Team Size: ${output.company_overview.team_size || 'Unknown'}

POSITIONING:
- Category: ${output.positioning.category}
- Target: ${output.positioning.target_audience}
- Value Prop: ${output.positioning.value_proposition}
- Differentiation: ${output.positioning.differentiation.join('; ')}

PRODUCT:
- Pricing: ${output.product_offering.pricing_model}
- Key Features: ${output.product_offering.core_features.slice(0, 3).join(', ')}
- Unique Features: ${output.product_offering.unique_features.join('; ')}

MARKETING:
- Channels: ${output.marketing_strategy.channels.join(', ')}
- Brand Voice: ${output.marketing_strategy.brand_voice}
- Social Platforms: ${output.marketing_strategy.social_presence.platforms.join(', ')}

COMPETITIVE ADVANTAGES:
${output.competitive_advantages.map(a => `- ${a.advantage} (${a.strength})`).join('\n')}

THREATS:
${output.threats.map(t => `- ${t.threat} (${t.impact})`).join('\n')}

CONFIDENCE: ${output.analysis_confidence}
SOURCES: ${output.data_sources.length} data sources
      `.trim();

      await storeEmbedding(
        userId,
        'competitor_analysis',
        content,
        {
          company: input.target_company,
          domain: input.domain,
          confidence: output.analysis_confidence,
          analysis_depth: input.analysis_depth,
          focus_areas: input.focus_areas
        }
      );

    } catch (error) {
      console.warn('Failed to store competitor intelligence:', error);
    }
  }

  private getFallbackOutput(input: CompetitorIntelInput): CompetitorIntelOutput {
    return {
      company_overview: {
        name: input.target_company,
        domain: input.domain || 'unknown',
        description: "Analysis pending - data collection required",
        founded_year: undefined,
        headquarters: undefined,
        funding_status: undefined,
        team_size: undefined
      },
      positioning: {
        category: "Unknown",
        differentiation: ["Analysis pending"],
        target_audience: "Unknown",
        value_proposition: "Analysis pending",
        tagline: undefined
      },
      product_offering: {
        core_features: ["Analysis pending"],
        pricing_model: "Unknown",
        pricing_range: undefined,
        unique_features: ["Analysis pending"],
        weaknesses: ["Analysis pending"]
      },
      marketing_strategy: {
        channels: ["Analysis pending"],
        messaging: ["Analysis pending"],
        brand_voice: "Unknown",
        content_strategy: undefined,
        social_presence: {
          platforms: [],
          follower_counts: undefined,
          engagement_rate: undefined
        }
      },
      customer_insights: {
        customer_segments: ["Analysis pending"],
        use_cases: ["Analysis pending"],
        customer_feedback: [{
          source: "Analysis pending",
          rating: undefined,
          comment: "Data collection required",
          sentiment: "neutral" as const
        }]
      },
      competitive_advantages: [{
        advantage: "Analysis pending",
        strength: "weak" as const,
        sustainability: "Unknown",
        our_response: undefined
      }],
      threats: [{
        threat: "Insufficient competitive intelligence",
        impact: "medium" as const,
        timeline: "Immediate",
        mitigation_strategy: "Conduct comprehensive competitor analysis"
      }],
      data_sources: [],
      analysis_confidence: 0.1,
      recommendations: ["Complete comprehensive competitor analysis"],
      last_analyzed: new Date().toISOString()
    };
  }
}

// =====================================================
// REGISTER AGENT
// =====================================================

const competitorIntelligenceAgent = new CompetitorIntelligenceAgent();
agentRegistry.registerAgent(competitorIntelligenceAgent);

export { competitorIntelligenceAgent };
export type { CompetitorIntelInput, CompetitorIntelOutput };
