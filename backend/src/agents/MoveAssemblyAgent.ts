import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModel } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

// Input Schema
export interface MoveAssemblyInput {
  strategy_profile: any;
  selected_icps: any[];
  company: any;
  product: any;
  budget_range?: string;
}

// Output Schema
const moveAssemblyOutputSchema = z.object({
  war_plan: z.object({
    summary: z.string(),
    phases: z.array(z.object({
      id: z.number(),
      name: z.string(),
      days: z.string(),
      objective: z.string(),
      protocols_active: z.array(z.string()),
      campaigns: z.array(z.object({
        name: z.string(),
        protocol: z.string(),
        description: z.string(),
        target_icps: z.array(z.string()),
        channels: z.array(z.string()),
        estimated_effort: z.enum(["low", "medium", "high"])
      })),
      moves: z.array(z.object({
        name: z.string(),
        type: z.enum(["content", "ad", "email", "event", "outbound"]),
        description: z.string(),
        deliverables: z.array(z.string()),
        owner: z.string(),
        timeline: z.string()
      })),
      kpis: z.array(z.object({
        name: z.string(),
        target: z.string(),
        rag_thresholds: z.object({
          green: z.string(),
          amber: z.string(),
          red: z.string()
        })
      }))
    })),
    "90_day_north_star": z.object({
      metric: z.string(),
      target: z.string()
    }),
    first_week_checklist: z.array(z.string()),
    critical_dependencies: z.array(z.string())
  })
});

export type MoveAssemblyOutput = z.infer<typeof moveAssemblyOutputSchema>;

export class MoveAssemblyAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    this.model = getLangChainModel("gemini-pro");
    this.parser = StructuredOutputParser.fromZodSchema(moveAssemblyOutputSchema);
    this.prompt = new PromptTemplate({
      template: `You are a B2B marketing strategist building a 90-day execution plan.

Using the strategy profile and selected ICPs, create a phased war plan:

Phase 1 (Days 1-30): Discovery & Foundation
- Objective: Establish presence, build content foundation
- Protocols: A (Authority Blitz)
- Key activities: Pillar content, positioning validation

Phase 2 (Days 31-60): Launch & Validation
- Objective: Generate demand, validate messaging
- Protocols: B (Trust Anchor), C (Cost of Inaction)
- Key activities: Case studies, demand campaigns, outbound

Phase 3 (Days 61-90): Optimization & Scale
- Objective: Double down on winners, prepare for next quarter
- Protocols: D, E, F (as needed)
- Key activities: Optimization, expansion plays

For each phase, define:
- Specific campaigns (with protocol mapping)
- Tactical moves (content pieces, ad campaigns, etc.)
- KPIs with targets
- RAG thresholds (Red/Amber/Green)

Input Data:
Strategy Profile: {strategy_profile}
Selected ICPs: {selected_icps}
Company: {company}
Product: {product}
Budget Range: {budget_range}

{format_instructions}`,
      inputVariables: ["strategy_profile", "selected_icps", "company", "product", "budget_range"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  async analyze(input: MoveAssemblyInput): Promise<MoveAssemblyOutput> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    return await chain.invoke({
      strategy_profile: JSON.stringify(input.strategy_profile),
      selected_icps: JSON.stringify(input.selected_icps),
      company: JSON.stringify(input.company),
      product: JSON.stringify(input.product),
      budget_range: input.budget_range || "Unknown"
    });
  }
}
