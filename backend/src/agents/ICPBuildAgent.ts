import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModel } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

// Input Schema
export interface ICPBuildInput {
  company: any;
  product: any;
  positioning: any;
  market: any;
  strategy: any;
  jtbd: any;
}

// Output Schema
const icpBuildOutputSchema = z.object({
  icps: z.array(z.object({
    id: z.string(),
    label: z.string(),
    summary: z.string(),
    firmographics: z.object({
      employee_range: z.string(),
      revenue_range: z.string().nullable(),
      industries: z.array(z.string()),
      stages: z.array(z.string()),
      regions: z.array(z.string()),
      exclude: z.array(z.string())
    }),
    technographics: z.object({
      must_have: z.array(z.string()),
      nice_to_have: z.array(z.string()),
      red_flags: z.array(z.string())
    }),
    psychographics: z.object({
      pain_points: z.array(z.string()),
      motivations: z.array(z.string()),
      internal_triggers: z.array(z.string()),
      buying_constraints: z.array(z.string())
    }),
    behavioral_triggers: z.array(z.object({
      signal: z.string(),
      source: z.string(),
      urgency_boost: z.number().min(0).max(100)
    })),
    buying_committee: z.array(z.object({
      role: z.enum(["Decision Maker", "Champion", "Economic Buyer", "Technical Eval", "End User"]),
      typical_title: z.string(),
      concerns: z.array(z.string()),
      success_criteria: z.array(z.string())
    })),
    category_context: z.object({
      market_position: z.enum(["leader", "challenger", "newcomer"]),
      current_solution: z.string(),
      switching_triggers: z.array(z.string())
    }),
    fit_score: z.number().min(0).max(100),
    fit_reasoning: z.string(),
    messaging_angle: z.string(),
    qualification_questions: z.array(z.string())
  })),
  icp_comparison: z.object({
    highest_urgency: z.string(),
    largest_market: z.string(),
    easiest_to_reach: z.string()
  })
});

export type ICPBuildOutput = z.infer<typeof icpBuildOutputSchema>;

export class ICPBuildAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    this.model = getLangChainModel("gemini-pro");
    this.parser = StructuredOutputParser.fromZodSchema(icpBuildOutputSchema);
    this.prompt = new PromptTemplate({
      template: `You are an ICP (Ideal Customer Profile) architect. Using the 6D ICP Framework:

1. Firmographics - Company characteristics
2. Technographics - Technology stack
3. Psychographics - Motivations, pain points, triggers
4. Behavioral Triggers - Signals they're in-market
5. Buying Committee - Key personas and roles
6. Category Context - Market position and competitive landscape

Generate 3 distinct ICPs:
- ICP 1: "Desperate Scaler" - High urgency, immediate need
- ICP 2: "Frustrated Optimizer" - Tried alternatives, ready to switch
- ICP 3: "Risk Mitigator" - Conservative, needs assurance

Each ICP should be specific enough to inform:
- Targeting criteria for ads
- Messaging angles for content
- Qualification questions for sales
- Trigger-based outreach campaigns

Score each ICP on fit (0-100) based on:
- Alignment with positioning
- Alignment with strategy
- Market size potential
- Likelihood to convert

Input Data:
Company: {company}
Product: {product}
Positioning: {positioning}
Market: {market}
Strategy: {strategy}
JTBD: {jtbd}

{format_instructions}`,
      inputVariables: ["company", "product", "positioning", "market", "strategy", "jtbd"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  async analyze(input: ICPBuildInput): Promise<ICPBuildOutput> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    return await chain.invoke({
      company: JSON.stringify(input.company),
      product: JSON.stringify(input.product),
      positioning: JSON.stringify(input.positioning),
      market: JSON.stringify(input.market),
      strategy: JSON.stringify(input.strategy),
      jtbd: JSON.stringify(input.jtbd)
    });
  }
}
