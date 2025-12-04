import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModel } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

// Input Schema
export interface PositioningInput {
  dan_kennedy_answer: string;
  dunford_answer: string;
  company_name?: string;
  industry?: string;
}

// Output Schema using Zod
const positioningOutputSchema = z.object({
  primary_target: z.string().describe("The specific audience segment (be precise)"),
  primary_problem: z.string().describe("The core pain point they solve"),
  primary_outcome: z.string().describe("The main result/transformation delivered"),
  main_alternatives: z.array(z.string()).describe("List of 3-5 alternatives (competitors, DIY, status quo)"),
  positioning_type: z.enum(["head-to-head", "niche-subcategory", "create-new-category"]).describe("The type of positioning strategy"),
  value_proposition: z.string().describe("One-sentence value prop in format: 'For [WHO] who [PROBLEM], [PRODUCT] [OUTCOME] unlike [ALTERNATIVES]'"),
  clarity_score: z.number().min(0).max(100).describe("0-100 score of how clear/specific the positioning is"),
  suggestions_to_improve: z.array(z.string()).describe("List of suggestions to improve the positioning"),
  confidence: z.number().min(0).max(1).describe("Confidence score of the analysis (0-1)")
});

export type PositioningOutput = z.infer<typeof positioningOutputSchema>;

export class PositioningParseAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    // Initialize the model
    this.model = getLangChainModel("gemini-pro");
    
    // Initialize parser
    this.parser = StructuredOutputParser.fromZodSchema(positioningOutputSchema);

    // Initialize prompt
    this.prompt = new PromptTemplate({
      template: `You are a strategic positioning analyst trained in frameworks from Dan Kennedy, 
April Dunford, and positioning experts. Your job is to analyze raw positioning 
statements and extract structured insights.

Given the user's answers to:
1. Dan Kennedy Question: "Why should I choose you over every other option?"
2. April Dunford Question: "Who is your product obviously better for?"

User Input:
Company Name: {company_name}
Industry: {industry}
Dan Kennedy Answer: {dan_kennedy_answer}
April Dunford Answer: {dunford_answer}

Analyze the input and extract the following:
- primary_target: The specific audience segment (be precise)
- primary_problem: The core pain point they solve
- primary_outcome: The main result/transformation delivered
- main_alternatives: List of 3-5 alternatives (competitors, DIY, status quo)
- positioning_type: One of ["head-to-head", "niche-subcategory", "create-new-category"]
- value_proposition: One-sentence value prop in format: "For [WHO] who [PROBLEM], [PRODUCT] [OUTCOME] unlike [ALTERNATIVES]"
- clarity_score: 0-100 score of how clear/specific the positioning is

Be critical. Vague answers like "we help businesses grow" should score low (20-40).
Specific answers like "we help Series A SaaS CFOs close their books 5x faster" should score high (80-95).

{format_instructions}`,
      inputVariables: ["dan_kennedy_answer", "dunford_answer", "company_name", "industry"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  async analyze(input: PositioningInput): Promise<PositioningOutput> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    
    const result = await chain.invoke({
      dan_kennedy_answer: input.dan_kennedy_answer,
      dunford_answer: input.dunford_answer,
      company_name: input.company_name || "Unknown",
      industry: input.industry || "Unknown",
    });

    return result;
  }
}
