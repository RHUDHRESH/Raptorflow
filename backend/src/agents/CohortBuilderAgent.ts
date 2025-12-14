/**
 * CohortBuilderAgent - Generates a complete 6D cohort from a simple description
 * 
 * Takes a natural language description like "19-21 year old male college students in Chennai"
 * and generates a fully populated cohort with all 6 dimensions
 */

import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

// Full cohort schema
const cohortSchema = z.object({
  name: z.string().describe("Short, memorable cohort name"),
  description: z.string().describe("2-3 sentence cohort description"),
  
  firmographics: z.object({
    age_range: z.string().nullable(),
    gender: z.string().nullable(),
    income_level: z.string().nullable(),
    education: z.string().nullable(),
    occupation: z.string().nullable(),
    company_size: z.string().nullable(),
    industries: z.array(z.string()),
    locations: z.array(z.string()),
    exclude: z.array(z.string())
  }),
  
  psychographics: z.object({
    pain_points: z.array(z.string()),
    motivations: z.array(z.string()),
    values: z.array(z.string()),
    lifestyle: z.array(z.string()),
    internal_triggers: z.array(z.string()),
    buying_constraints: z.array(z.string())
  }),
  
  behavioral_triggers: z.array(z.object({
    signal: z.string(),
    source: z.string(),
    urgency_boost: z.number().min(0).max(100)
  })),
  
  buying_committee: z.array(z.object({
    role: z.string(),
    typical_title: z.string(),
    concerns: z.array(z.string()),
    success_criteria: z.array(z.string())
  })).nullable(),
  
  category_context: z.object({
    market_position: z.enum(['leader', 'challenger', 'newcomer', 'niche']),
    current_solutions: z.array(z.string()),
    switching_triggers: z.array(z.string())
  }),
  
  fit_score: z.number().min(0).max(100),
  messaging_angle: z.string(),
  qualification_questions: z.array(z.string())
});

export type CohortData = z.infer<typeof cohortSchema>;

export class CohortBuilderAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    const agentName = 'CohortBuilderAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'heavy', getModelForAgent(agentName));
    
    this.parser = StructuredOutputParser.fromZodSchema(cohortSchema);
    
    this.prompt = new PromptTemplate({
      template: `You are a cohort intelligence architect. Build a complete, detailed cohort profile from a simple description.

## INPUT DESCRIPTION
"{description}"

## YOUR TASK

Generate a comprehensive cohort profile with all 6 dimensions:

### 1. FIRMOGRAPHICS (WHO they are)
- Demographics: age, gender, income, education, occupation
- For B2B: company size, industry, stage
- Location specifics
- Who to EXCLUDE

### 2. PSYCHOGRAPHICS (WHY they buy)
- Pain points (be specific, use their language)
- Motivations (what they want to achieve)
- Values (what matters to them)
- Lifestyle markers
- Internal triggers (events that make them buy)
- Buying constraints (what stops them)

### 3. BEHAVIORAL TRIGGERS (WHEN to reach them)
- Observable signals they're in-market
- Sources where you'd see these signals
- Urgency boost (how much this signal increases priority)

### 4. BUYING COMMITTEE (WHO decides) - if B2B
- Key roles in the decision
- Their typical titles
- What each cares about
- How they define success

### 5. CATEGORY CONTEXT (WHERE they stand)
- Their position in their market
- Current solutions they use
- What would make them switch

### 6. QUALIFICATION
- Fit score (how ideal is this cohort, 0-100)
- Key messaging angle (one powerful hook)
- Qualification questions to ask them

## IMPORTANT RULES
- Be SPECIFIC - avoid generic statements
- Use THEIR language - how they'd describe themselves
- Think about what makes them UNIQUE
- Include LOCAL context if location is specified
- For B2C, buying_committee can be null

{format_instructions}`,
      inputVariables: ["description"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() }
    });
  }

  async buildFromDescription(description: string): Promise<CohortData> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    return await chain.invoke({ description });
  }

  /**
   * Refine an existing cohort based on feedback
   */
  async refineCohort(
    existingCohort: CohortData,
    feedback: string
  ): Promise<CohortData> {
    const refinePrompt = new PromptTemplate({
      template: `You are a cohort intelligence architect. Refine this existing cohort based on feedback.

## EXISTING COHORT
{existing_cohort}

## FEEDBACK
{feedback}

## TASK
Update the cohort based on the feedback while maintaining the overall structure.
Make targeted improvements without changing things that weren't mentioned in feedback.

{format_instructions}`,
      inputVariables: ["existing_cohort", "feedback"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() }
    });

    const chain = refinePrompt.pipe(this.model).pipe(this.parser);
    return await chain.invoke({
      existing_cohort: JSON.stringify(existingCohort, null, 2),
      feedback
    });
  }
}

// Add to LLM agent registry
export const COHORT_BUILDER_AGENT_CONFIG = {
  name: 'CohortBuilderAgent',
  taskType: 'heavy' as const,
  description: 'Generates complete 6D cohort profiles from simple descriptions'
};

