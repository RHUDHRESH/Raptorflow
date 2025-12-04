import { z } from "zod";
import { createAgent } from "langchain";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { clearbitTool, builtwithTool, linkedinTool } from "../tools/companyTools";

// Input Schema
export interface CompanyEnrichInput {
  domain: string;
  user_provided: {
    company_name: string;
    employee_count: string;
    industry: string;
    stage: string;
  };
}

// Output Schema
const companyEnrichOutputSchema = z.object({
  firmographics: z.object({
    legal_name: z.string(),
    domain: z.string(),
    employee_count: z.number(),
    employee_range: z.string(),
    annual_revenue: z.number().nullable(),
    founded_year: z.number().nullable(),
    industry: z.string(),
    industry_group: z.string(),
    location: z.object({
      city: z.string(),
      country: z.string(),
      country_code: z.string()
    }),
    funding: z.object({
      total_raised: z.number().nullable(),
      last_round: z.string().nullable(),
      last_round_date: z.string().nullable()
    })
  }),
  technographics: z.object({
    website_technologies: z.array(z.string()),
    crm: z.string().nullable(),
    marketing_automation: z.string().nullable(),
    analytics: z.array(z.string()),
    cloud_provider: z.string().nullable(),
    other_notable: z.array(z.string())
  }),
  social: z.object({
    linkedin_url: z.string().nullable(),
    twitter_handle: z.string().nullable(),
    linkedin_employees: z.number().nullable()
  }),
  conflicts: z.array(z.object({
    field: z.string(),
    user_value: z.any(),
    enriched_value: z.any(),
    recommendation: z.string()
  })),
  enrichment_confidence: z.number().min(0).max(1)
});

export type CompanyEnrichOutput = z.infer<typeof companyEnrichOutputSchema>;

export class CompanyEnrichAgent {
  private model;
  private tools;
  private agent: any = null;

  constructor() {
    const agentName = 'CompanyEnrichAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'general', getModelForAgent(agentName));
    this.tools = [clearbitTool, builtwithTool, linkedinTool];
  }

  async init() {
    this.agent = createAgent({
      model: this.model,
      tools: this.tools,
      responseFormat: companyEnrichOutputSchema,
    });
  }

  async enrich(input: CompanyEnrichInput): Promise<CompanyEnrichOutput> {
    if (!this.agent) {
      await this.init();
    }

    const systemPrompt = `You are a company research specialist. Given a company domain, use the available 
tools to gather comprehensive firmographic and technographic data.

Your goal is to:
1. Call the Clearbit API to get company details
2. Call BuiltWith to get technology stack
3. Cross-reference and validate the data
4. Flag any conflicts between user input and enriched data

Always prioritize accuracy. If data is uncertain, mark confidence level.`;

    const userMessage = `Domain: ${input.domain}
User Provided Info: ${JSON.stringify(input.user_provided)}

Enrich this company data.`;

    const result = await this.agent.invoke({
      messages: [
        { role: "system", content: systemPrompt },
        { role: "human", content: userMessage }
      ]
    });

    // ReactAgent with responseFormat returns the structured response in `structuredResponse`
    // or it might be in the last message content if parsed.
    // Based on the d.ts I read: "a `structuredResponse` property containing the structured response (if configured)"
    
    if (result.structuredResponse) {
      return result.structuredResponse as CompanyEnrichOutput;
    }
    
    throw new Error("Agent did not return a structured response");
  }
}
