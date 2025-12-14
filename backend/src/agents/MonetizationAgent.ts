import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

// Input Schema
export interface MonetizationInput {
  pricing_model: "one-time" | "monthly" | "usage-based" | "hybrid";
  price_range: string;
  has_tiers: boolean;
  tiers: Array<{
    name: string;
    for_who: string;
    price: string;
  }>;
  industry: string;
  company_stage: string;
}

// Output Schema
const monetizationOutputSchema = z.object({
  likely_acv: z.object({
    low: z.number(),
    mid: z.number(),
    high: z.number()
  }),
  ticket_size: z.enum(["low", "mid", "high"]),
  sale_type: z.enum(["self-serve", "sales-assisted", "enterprise"]),
  recommended_motion: z.enum(["PLG", "demo-led", "outbound", "hybrid"]),
  unit_economics_notes: z.array(z.string()),
  pricing_recommendations: z.array(z.string())
});

export type MonetizationOutput = z.infer<typeof monetizationOutputSchema>;

export class MonetizationAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    const agentName = 'MonetizationAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'reasoning', getModelForAgent(agentName));
    this.parser = StructuredOutputParser.fromZodSchema(monetizationOutputSchema);
    this.prompt = new PromptTemplate({
      template: `You are a SaaS pricing analyst. Analyze the pricing structure to determine:

1. Likely Annual Contract Value (ACV)
2. Ticket size classification (low: <$1k, mid: $1k-$10k, high: >$10k)
3. Whether this is a self-serve or high-touch sale
4. Unit economics implications

Consider industry benchmarks:
- Low-ticket SaaS: typically self-serve, PLG motion
- Mid-ticket SaaS: sales-assisted, demo-driven
- High-ticket SaaS: enterprise sales, custom pricing

Input:
Pricing Model: {pricing_model}
Price Range: {price_range}
Has Tiers: {has_tiers}
Tiers: {tiers}
Industry: {industry}
Company Stage: {company_stage}

{format_instructions}`,
      inputVariables: ["pricing_model", "price_range", "has_tiers", "tiers", "industry", "company_stage"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  async analyze(input: MonetizationInput): Promise<MonetizationOutput> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    return await chain.invoke({
      pricing_model: input.pricing_model,
      price_range: input.price_range,
      has_tiers: input.has_tiers ? "yes" : "no",
      tiers: JSON.stringify(input.tiers),
      industry: input.industry,
      company_stage: input.company_stage
    });
  }
}
