import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

// Input Schema
export interface TechStackSeedInput {
  technographics: {
    website_technologies: string[];
    crm?: string | null;
    marketing_automation?: string | null;
    analytics: string[];
    cloud_provider?: string | null;
  };
  our_integrations: string[];
}

// Output Schema
const techStackSeedOutputSchema = z.object({
  relevant_integrations: z.array(z.object({
    integration: z.string(),
    priority: z.enum(["high", "medium", "low"]),
    reason: z.string()
  })),
  uses_competitor: z.boolean(),
  competitor_products: z.array(z.string()),
  technical_requirements: z.array(z.string()),
  implementation_complexity: z.enum(["low", "medium", "high"]),
  data_sources_available: z.array(z.string())
});

export type TechStackSeedOutput = z.infer<typeof techStackSeedOutputSchema>;

export class TechStackSeedAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    const agentName = 'TechStackSeedAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'general', getModelForAgent(agentName));
    this.parser = StructuredOutputParser.fromZodSchema(techStackSeedOutputSchema);
    this.prompt = new PromptTemplate({
      template: `You are a technical integration specialist. Analyze the company's technology 
stack and determine:

1. Which of our integrations would be immediately relevant
2. What data sources they likely have
3. Potential technical requirements for implementation
4. Whether they use any competing products

Map technologies to our integration catalog:
- Salesforce → CRM integration, lead scoring
- HubSpot → Marketing automation sync
- Slack → Notifications, workflows
- AWS/GCP → Cloud data connectors
- Snowflake/BigQuery → Data warehouse sync

Input:
Technographics: {technographics}
Our Integrations: {our_integrations}

{format_instructions}`,
      inputVariables: ["technographics", "our_integrations"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  async analyze(input: TechStackSeedInput): Promise<TechStackSeedOutput> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    return await chain.invoke({
      technographics: JSON.stringify(input.technographics),
      our_integrations: JSON.stringify(input.our_integrations)
    });
  }
}
