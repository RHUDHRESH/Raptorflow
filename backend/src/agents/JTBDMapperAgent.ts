import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

// Input Schema
export interface JTBDMapperInput {
  product_name: string;
  product_type: "saas" | "service" | "hybrid" | "marketplace" | "other";
  main_job: string;
  used_by: string[];
  positioning: {
    primary_target: string;
    primary_problem: string;
    primary_outcome: string;
  };
}

// Output Schema
const jtbdMapperOutputSchema = z.object({
  jobs: z.array(z.object({
    type: z.enum(["functional", "emotional", "social"]),
    situation: z.string(),
    motivation: z.string(),
    outcome: z.string(),
    full_statement: z.string(),
    priority: z.enum(["primary", "secondary", "tertiary"])
  })),
  primary_outcome_type: z.enum(["money", "time", "risk", "status"]),
  outcome_metrics: z.array(z.object({
    metric: z.string(),
    estimated_value: z.string()
  })),
  hook_candidates: z.array(z.string())
});

export type JTBDMapperOutput = z.infer<typeof jtbdMapperOutputSchema>;

export class JTBDMapperAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    const agentName = 'JTBDMapperAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'general', getModelForAgent(agentName));
    this.parser = StructuredOutputParser.fromZodSchema(jtbdMapperOutputSchema);
    this.prompt = new PromptTemplate({
      template: `You are a Jobs-to-be-Done (JTBD) analyst following the frameworks of Clayton 
Christensen and Alan Klement. Analyze the product description to extract:

1. Functional jobs (what task gets done)
2. Emotional jobs (how they want to feel)
3. Social jobs (how they want to be perceived)
4. The primary outcome type (Money, Time, Risk, Status)

For each job, identify the "when" (situation trigger) and "so that" (desired outcome).

Format jobs as: "When [SITUATION], I want to [MOTIVATION], so that I can [OUTCOME]"

Input:
Product Name: {product_name}
Type: {product_type}
Main Job: {main_job}
Used By: {used_by}
Positioning: {positioning}

{format_instructions}`,
      inputVariables: ["product_name", "product_type", "main_job", "used_by", "positioning"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  async analyze(input: JTBDMapperInput): Promise<JTBDMapperOutput> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    return await chain.invoke({
      product_name: input.product_name,
      product_type: input.product_type,
      main_job: input.main_job,
      used_by: JSON.stringify(input.used_by),
      positioning: JSON.stringify(input.positioning)
    });
  }
}
