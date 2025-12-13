import { z } from 'zod';
import { BaseAgent, agentRegistry } from '../base_agent';
import { Department, OrchestratorContext } from '../types';
import { ragQuery, storeEmbedding } from '../rag_helper';

// =====================================================
// MARKET INTEL AGENT
// =====================================================

const MarketIntelInputSchema = z.object({
  query: z.string().describe("The market research query/topic to investigate"),
  industry: z.string().optional().describe("Specific industry to focus on"),
  geography: z.string().optional().describe("Geographic region to analyze"),
  time_range: z.enum(['week', 'month', 'quarter', 'year']).optional().default('month'),
  depth: z.enum(['overview', 'detailed', 'comprehensive']).optional().default('detailed')
});

const MarketIntelOutputSchema = z.object({
  market_overview: z.object({
    size: z.string(),
    growth_rate: z.string(),
    key_players: z.array(z.string()),
    trends: z.array(z.string())
  }),
  competitive_landscape: z.object({
    main_competitors: z.array(z.object({
      name: z.string(),
      market_share: z.string(),
      strengths: z.array(z.string()),
      weaknesses: z.array(z.string())
    })),
    market_gaps: z.array(z.string()),
    entry_barriers: z.array(z.string())
  }),
  customer_insights: z.object({
    pain_points: z.array(z.string()),
    buying_behavior: z.array(z.string()),
    price_sensitivity: z.string(),
    decision_factors: z.array(z.string())
  }),
  opportunities: z.array(z.object({
    opportunity: z.string(),
    potential_impact: z.string(),
    feasibility: z.string(),
    recommended_action: z.string()
  })),
  risks: z.array(z.object({
    risk: z.string(),
    probability: z.string(),
    impact: z.string(),
    mitigation: z.string()
  })),
  sources: z.array(z.string()),
  confidence_score: z.number().min(0).max(1),
  last_updated: z.string()
});

type MarketIntelInput = z.infer<typeof MarketIntelInputSchema>;
type MarketIntelOutput = z.infer<typeof MarketIntelOutputSchema>;

export class MarketIntelAgent extends BaseAgent {
  constructor() {
    super(
      'market_intel_agent',
      Department.MARKET_INTELLIGENCE,
      'Researches market landscape, competitive analysis, and customer insights using web scraping and search tools',
      MarketIntelInputSchema,
      MarketIntelOutputSchema
    );

    this.required_tools = ['web_scrape'];
  }

  protected getSystemPrompt(): string {
    return `You are a senior market intelligence analyst with 10+ years experience.
You have access to web scraping tools and search capabilities.

Your role is to provide comprehensive market analysis including:
- Market size and growth trends
- Key competitors and their positioning
- Customer pain points and buying behavior
- Market opportunities and threats
- Data sources and confidence levels

Always cite sources and provide confidence levels for your analysis.
Be data-driven and specific in your recommendations.

When using tools, be systematic and thorough. Structure your output as valid JSON matching the required schema.`;
  }

  protected formatAgentInput(input: MarketIntelInput, context: OrchestratorContext): string {
    return `Conduct comprehensive market intelligence analysis for: ${input.query}

Parameters:
- Industry: ${input.industry || 'General'}
- Geography: ${input.geography || 'Global'}
- Time Range: ${input.time_range}
- Depth: ${input.depth}

Available Context:
- Goal: ${context.goal}
- Campaign: ${JSON.stringify(context.campaign_context || {})}
- ICP: ${JSON.stringify(context.icp_context || {})}

Use your web scraping tools to gather data, then analyze and synthesize findings.
Provide specific, actionable market intelligence that will inform positioning and strategy.`;
  }

  protected parseAgentOutput(rawOutput: string): MarketIntelOutput {
    try {
      // Try to extract JSON from the output
      const jsonMatch = rawOutput.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return MarketIntelOutputSchema.parse(JSON.parse(jsonMatch[0]));
      }
      // Fallback parsing - this would be enhanced with better NLP
      return this.getFallbackOutput({
        query: 'unknown',
        time_range: 'month' as any,
        depth: 'overview' as any,
        industry: undefined,
        geography: undefined
      });
    } catch {
      return this.getFallbackOutput({
        query: 'unknown',
        time_range: 'month' as any,
        depth: 'overview' as any,
        industry: undefined,
        geography: undefined
      });
    }
  }

  private async executeAgent(input: MarketIntelInput, context: OrchestratorContext): Promise<MarketIntelOutput> {
    console.log(`🔍 Market Intel Agent analyzing: ${input.query}`);

    try {
      // Step 1: Gather existing knowledge from RAG
      const existingKnowledge = await this.getExistingKnowledge(input, context.user_id);

      // Step 2: Perform fresh research
      const freshResearch = await this.performMarketResearch(input);

      // Step 3: Synthesize findings
      const synthesizedOutput = await this.synthesizeFindings(input, existingKnowledge, freshResearch, context);

      // Step 4: Store results for future use
      await this.storeResults(input, synthesizedOutput, context.user_id);

      return synthesizedOutput;

    } catch (error) {
      console.error('Market Intel Agent execution failed:', error);
      return this.getFallbackOutput(input);
    }
  }

  private async getExistingKnowledge(input: MarketIntelInput, userId: string): Promise<any> {
    try {
      const ragResults = await ragQuery({
        query: `market intelligence for ${input.query} ${input.industry || ''} ${input.geography || ''}`,
        user_id: userId,
        content_types: ['market_research', 'competitor_analysis'],
        limit: 5,
        threshold: 0.6
      });

      return {
        chunks: ragResults.chunks,
        has_existing_data: ragResults.chunks.length > 0
      };
    } catch (error) {
      console.warn('Failed to retrieve existing knowledge:', error);
      return { chunks: [], has_existing_data: false };
    }
  }

  private async performMarketResearch(input: MarketIntelInput): Promise<any> {
    const research: {
      market_data: any[];
      competitor_data: any[];
      customer_insights: any[];
      sources: any[];
    } = {
      market_data: [],
      competitor_data: [],
      customer_insights: [],
      sources: []
    };

    try {
      // Search for market overview
      const marketQuery = `${input.query} market size growth trends ${input.industry || ''} ${input.geography || ''}`;
      const marketResults = await this.searchAndScrape(marketQuery, 3);
      research.market_data = marketResults;

      // Search for competitors
      const competitorQuery = `${input.query} competitors alternatives ${input.industry || ''}`;
      const competitorResults = await this.searchAndScrape(competitorQuery, 3);
      research.competitor_data = competitorResults;

      // Search for customer insights
      const customerQuery = `${input.query} customer reviews pain points ${input.industry || ''}`;
      const customerResults = await this.searchAndScrape(customerQuery, 3);
      research.customer_insights = customerResults;

      research.sources = [
        ...marketResults.map(r => r.source),
        ...competitorResults.map(r => r.source),
        ...customerResults.map(r => r.source)
      ].filter(Boolean);

    } catch (error) {
      console.warn('Market research failed:', error);
    }

    return research;
  }

  private async searchAndScrape(query: string, maxResults: number = 3): Promise<any[]> {
    const results = [];

    try {
      // Use web scraping tool (placeholder - would integrate with actual scraping service)
      for (let i = 0; i < maxResults; i++) {
        try {
          const scrapeResult = await this.executeTool('web_scrape', {
            url: `https://example.com/search?q=${encodeURIComponent(query)}&page=${i + 1}`,
            include_text: true,
            include_html: false
          });

          if (scrapeResult?.content) {
            results.push({
              query,
              content: scrapeResult.content,
              source: scrapeResult.url || `search_result_${i + 1}`,
              timestamp: new Date().toISOString()
            });
          }
        } catch (error) {
          console.warn(`Scraping attempt ${i + 1} failed:`, error);
        }
      }
    } catch (error) {
      console.warn('Search and scrape failed:', error);
    }

    return results;
  }

  private async synthesizeFindings(
    input: MarketIntelInput,
    existingKnowledge: any,
    freshResearch: any,
    context: OrchestratorContext
  ): Promise<MarketIntelOutput> {
    // Use LLM to synthesize the research findings
    const synthesisPrompt = this.createSynthesisPrompt(input, existingKnowledge, freshResearch);

    try {
      const parser = this.createParser();
      const prompt = this.createPrompt(synthesisPrompt, ['research_data', 'existing_knowledge']);

      const chain = prompt.pipe(this.model).pipe(parser);

      const result = await chain.invoke({
        research_data: JSON.stringify(freshResearch, null, 2),
        existing_knowledge: existingKnowledge.chunks.map((c: any) => c.content).join('\n\n')
      });

      return {
        ...result,
        confidence_score: this.calculateConfidence(existingKnowledge, freshResearch),
        last_updated: new Date().toISOString()
      };

    } catch (error) {
      console.error('Synthesis failed:', error);
      return this.getFallbackOutput(input);
    }
  }

  private createSynthesisPrompt(input: MarketIntelInput, existing: any, fresh: any): string {
    return `You are a market intelligence analyst. Synthesize the following research data into a comprehensive market analysis.

Research Query: ${input.query}
Industry: ${input.industry || 'General'}
Geography: ${input.geography || 'Global'}
Time Range: ${input.time_range}
Depth: ${input.depth}

Existing Knowledge:
${existing.chunks.map((c: any) => c.content).join('\n\n')}

Fresh Research Data:
${JSON.stringify(fresh, null, 2)}

Based on this data, provide a structured market intelligence report with:

1. Market Overview (size, growth, key players, trends)
2. Competitive Landscape (competitors, market gaps, entry barriers)
3. Customer Insights (pain points, buying behavior, decision factors)
4. Opportunities (with impact and feasibility assessments)
5. Risks (with probability and mitigation strategies)

Be specific, data-driven, and actionable. If data is insufficient, note the gaps.

${this.createParser().getFormatInstructions()}`;
  }

  private calculateConfidence(existing: any, fresh: any): number {
    let confidence = 0.5; // Base confidence

    // Increase confidence based on data quality and quantity
    if (existing.has_existing_data) confidence += 0.2;
    if (fresh.market_data.length > 0) confidence += 0.1;
    if (fresh.competitor_data.length > 0) confidence += 0.1;
    if (fresh.customer_insights.length > 0) confidence += 0.1;

    // Cap at 0.9 (never 100% confident)
    return Math.min(confidence, 0.9);
  }

  private async storeResults(
    input: MarketIntelInput,
    output: MarketIntelOutput,
    userId: string
  ): Promise<void> {
    try {
      const content = `
Market Intelligence Report: ${input.query}

Market Size: ${output.market_overview.size}
Growth Rate: ${output.market_overview.growth_rate}
Key Players: ${output.market_overview.key_players.join(', ')}
Trends: ${output.market_overview.trends.join(', ')}

Main Competitors: ${output.competitive_landscape.main_competitors.map(c => c.name).join(', ')}
Market Gaps: ${output.competitive_landscape.market_gaps.join(', ')}
Entry Barriers: ${output.competitive_landscape.entry_barriers.join(', ')}

Key Pain Points: ${output.customer_insights.pain_points.join(', ')}
Buying Behavior: ${output.customer_insights.buying_behavior.join(', ')}

Top Opportunities: ${output.opportunities.map(o => o.opportunity).join('; ')}
Key Risks: ${output.risks.map(r => r.risk).join('; ')}

Confidence: ${output.confidence_score}
Sources: ${output.sources.join(', ')}
      `.trim();

      await storeEmbedding(
        userId,
        'market_research',
        content,
        {
          query: input.query,
          industry: input.industry,
          geography: input.geography,
          confidence: output.confidence_score,
          sources_count: output.sources.length
        }
      );

    } catch (error) {
      console.warn('Failed to store market intel results:', error);
    }
  }

  private getFallbackOutput(input: MarketIntelInput): MarketIntelOutput {
    return {
      market_overview: {
        size: "Unable to determine from available data",
        growth_rate: "Data unavailable",
        key_players: ["Research needed"],
        trends: ["Further investigation required"]
      },
      competitive_landscape: {
        main_competitors: [{
          name: "Research needed",
          market_share: "Unknown",
          strengths: ["To be determined"],
          weaknesses: ["To be determined"]
        }],
        market_gaps: ["Analysis pending"],
        entry_barriers: ["Research required"]
      },
      customer_insights: {
        pain_points: ["Data collection in progress"],
        buying_behavior: ["Analysis pending"],
        price_sensitivity: "Unknown",
        decision_factors: ["Research needed"]
      },
      opportunities: [{
        opportunity: "Market research required",
        potential_impact: "To be determined",
        feasibility: "Unknown",
        recommended_action: "Complete market analysis first"
      }],
      risks: [{
        risk: "Insufficient market intelligence",
        probability: "High",
        impact: "High",
        mitigation: "Conduct comprehensive market research"
      }],
      sources: [],
      confidence_score: 0.1,
      last_updated: new Date().toISOString()
    };
  }
}

// =====================================================
// REGISTER AGENT
// =====================================================

const marketIntelAgent = new MarketIntelAgent();
agentRegistry.registerAgent(marketIntelAgent);

export { marketIntelAgent };
export type { MarketIntelInput, MarketIntelOutput };
