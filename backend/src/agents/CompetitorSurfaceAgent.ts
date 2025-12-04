import { z } from "zod";
import { createAgent } from "langchain";
import { getLangChainModel } from "../lib/llm";
import { webScraperTool, googleSearchTool, g2ScraperTool } from "../tools/competitorTools";

// Input Schema
export interface CompetitorSurfaceInput {
  company_name: string;
  company_positioning: {
    value_proposition: string;
    primary_target: string;
  };
  competitors: string[];
  user_price_position: number;
  user_complexity_position: number;
  industry: string;
}

// Output Schema
const competitorSurfaceOutputSchema = z.object({
  competitor_profiles: z.array(z.object({
    name: z.string(),
    website: z.string(),
    tagline: z.string(),
    value_prop: z.string(),
    target_audience: z.string(),
    pricing_tier: z.enum(["budget", "mid-market", "premium", "enterprise"]),
    key_features: z.array(z.string()),
    positioning_angle: z.string(),
    weaknesses: z.array(z.string()),
    map_coordinates: z.object({
      x: z.number(),
      y: z.number()
    })
  })),
  positioning_gaps: z.array(z.object({
    gap: z.string(),
    opportunity: z.string()
  })),
  differentiation_wedges: z.array(z.object({
    wedge: z.string(),
    competitors_weak_on: z.array(z.string()),
    your_strength: z.string()
  })),
  category_maturity: z.enum(["emerging", "growing", "mature", "declining"]),
  recommended_positioning_angle: z.string()
});

export type CompetitorSurfaceOutput = z.infer<typeof competitorSurfaceOutputSchema>;

export class CompetitorSurfaceAgent {
  private model;
  private tools;
  private agent: any = null;

  constructor() {
    this.model = getLangChainModel("gemini-pro");
    this.tools = [webScraperTool, googleSearchTool, g2ScraperTool];
  }

  async init() {
    this.agent = createAgent({
      model: this.model,
      tools: this.tools,
      responseFormat: competitorSurfaceOutputSchema,
    });
  }

  async analyze(input: CompetitorSurfaceInput): Promise<CompetitorSurfaceOutput> {
    if (!this.agent) {
      await this.init();
    }

    const systemPrompt = `You are a competitive intelligence analyst. For each competitor:

1. Fetch their website and extract key messaging
2. Identify their positioning, tagline, and value prop
3. Determine their approximate pricing tier
4. Map their feature set
5. Identify positioning gaps and potential differentiation angles

Build a competitive landscape map showing where each player sits on:
- X-axis: Price (Budget to Premium)
- Y-axis: Complexity (Simple to Power-user)

Use the available tools (web_scraper, google_search) to gather information.`;

    const userMessage = `Company: ${input.company_name}
Our Positioning: ${JSON.stringify(input.company_positioning)}
Competitors to Analyze: ${JSON.stringify(input.competitors)}
Our Self-Assessment: Price Position ${input.user_price_position}, Complexity Position ${input.user_complexity_position}
Industry: ${input.industry}

Analyze these competitors and return the structured profile and map.`;

    const result = await this.agent.invoke({
      messages: [
        { role: "system", content: systemPrompt },
        { role: "human", content: userMessage }
      ]
    });

    if (result.structuredResponse) {
      return result.structuredResponse as CompetitorSurfaceOutput;
    }
    
    throw new Error("Agent did not return a structured response");
  }
}
