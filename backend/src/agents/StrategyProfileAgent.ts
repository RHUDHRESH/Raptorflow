import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModel } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

// Input Schema
export interface StrategyProfileInput {
  goal_primary: "velocity" | "efficiency" | "penetration";
  goal_secondary: "velocity" | "efficiency" | "penetration" | null;
  demand_source: "capture" | "creation" | "expansion";
  persuasion_axis: "money" | "time" | "risk-image";
  company_stage: string;
  ticket_size: "low" | "mid" | "high";
  sale_type: "self-serve" | "sales-assisted" | "enterprise";
}

// Output Schema
const strategyProfileOutputSchema = z.object({
  strategy_profile: z.object({
    name: z.string(),
    description: z.string()
  }),
  implied_tradeoffs: z.array(z.string()),
  recommended_protocols: z.object({
    primary: z.array(z.string()),
    secondary: z.array(z.string()),
    disabled: z.array(z.string())
  }),
  budget_allocation: z.object({
    content_creation: z.string(),
    paid_acquisition: z.string(),
    outbound: z.string(),
    events_partnerships: z.string(),
    retention_expansion: z.string()
  }),
  channel_priority: z.array(z.object({
    channel: z.string(),
    priority: z.enum(["high", "medium", "low"]),
    reason: z.string()
  })),
  campaign_recommendations: z.array(z.object({
    campaign_type: z.string(),
    protocol: z.string(),
    timing: z.enum(["phase 1", "phase 2", "phase 3"]),
    expected_impact: z.string()
  }))
});

export type StrategyProfileOutput = z.infer<typeof strategyProfileOutputSchema>;

export class StrategyProfileAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    this.model = getLangChainModel("gemini-pro");
    this.parser = StructuredOutputParser.fromZodSchema(strategyProfileOutputSchema);
    this.prompt = new PromptTemplate({
      template: `You are a B2B marketing strategist. Based on the user's strategic choices:

Goal (Velocity/Efficiency/Penetration) + 
Demand Source (Capture/Creation/Expansion) + 
Persuasion Axis (Money/Time/Risk)

Derive:
1. Implied trade-offs (what they're accepting)
2. Recommended execution protocols (A-F)
3. Budget allocation recommendations
4. Channel prioritization
5. Campaign type recommendations

Protocol mapping:
- A: Authority Blitz (content, thought leadership)
- B: Trust Anchor (social proof, validation)
- C: Cost of Inaction (urgency, competitive displacement)
- D: Facilitator Nudge (onboarding, activation)
- E: Champions Armory (internal advocacy, expansion)
- F: Churn Intercept (retention, save plays)

Input:
Goal Primary: {goal_primary}
Goal Secondary: {goal_secondary}
Demand Source: {demand_source}
Persuasion Axis: {persuasion_axis}
Company Stage: {company_stage}
Ticket Size: {ticket_size}
Sale Type: {sale_type}

{format_instructions}`,
      inputVariables: ["goal_primary", "goal_secondary", "demand_source", "persuasion_axis", "company_stage", "ticket_size", "sale_type"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  async analyze(input: StrategyProfileInput): Promise<StrategyProfileOutput> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    return await chain.invoke({
      goal_primary: input.goal_primary,
      goal_secondary: input.goal_secondary || "None",
      demand_source: input.demand_source,
      persuasion_axis: input.persuasion_axis,
      company_stage: input.company_stage,
      ticket_size: input.ticket_size,
      sale_type: input.sale_type
    });
  }
}
