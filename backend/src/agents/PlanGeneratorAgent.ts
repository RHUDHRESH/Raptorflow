/**
 * PlanGeneratorAgent - Generates detailed week-by-week execution plans
 * 
 * Creates maniacally detailed GTM plans with exact activities, deliverables,
 * and expected outcomes for each day of execution
 */

import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";

export interface PlanGeneratorInput {
  company_name: string;
  positioning: any;
  cohorts: any[];
  protocols: string[];
  campaigns: any[];
  goals: {
    primary: string;
    metrics: string[];
    timeline: string;
  };
  budget?: {
    monthly: number;
    allocation?: Record<string, number>;
  };
  team_size?: number;
}

const dailyActivitySchema = z.object({
  day: z.number(),
  day_name: z.string(), // "Monday", "Tuesday", etc.
  focus_area: z.string(),
  activities: z.array(z.object({
    time_slot: z.string(), // "9:00 AM", "2:00 PM", etc.
    duration: z.string(), // "30 min", "2 hours"
    activity: z.string(),
    details: z.string(),
    owner: z.string(), // "Founder", "Marketing", "Sales"
    tools_needed: z.array(z.string()),
    deliverable: z.string(),
    success_metric: z.string()
  })),
  end_of_day_checklist: z.array(z.string()),
  blockers_to_avoid: z.array(z.string())
});

const weeklyPlanSchema = z.object({
  week_number: z.number(),
  week_theme: z.string(),
  week_goal: z.string(),
  
  days: z.array(dailyActivitySchema),
  
  week_deliverables: z.array(z.object({
    deliverable: z.string(),
    format: z.string(),
    quality_criteria: z.array(z.string())
  })),
  
  metrics_to_track: z.array(z.object({
    metric: z.string(),
    target: z.string(),
    tracking_method: z.string()
  })),
  
  budget_allocation: z.object({
    total: z.number(),
    breakdown: z.array(z.object({
      category: z.string(),
      amount: z.number(),
      justification: z.string()
    }))
  }),
  
  risk_mitigation: z.array(z.object({
    risk: z.string(),
    mitigation: z.string(),
    trigger_to_act: z.string()
  })),
  
  week_end_review: z.object({
    questions_to_answer: z.array(z.string()),
    decisions_to_make: z.array(z.string()),
    adjustments_if_needed: z.array(z.string())
  })
});

const fullPlanSchema = z.object({
  plan_name: z.string(),
  plan_duration: z.string(),
  
  executive_summary: z.object({
    situation: z.string(),
    strategy: z.string(),
    expected_outcome: z.string(),
    investment_required: z.string(),
    roi_projection: z.string()
  }),
  
  weeks: z.array(weeklyPlanSchema),
  
  overall_milestones: z.array(z.object({
    milestone: z.string(),
    target_date: z.string(),
    success_criteria: z.array(z.string()),
    dependencies: z.array(z.string())
  })),
  
  resource_requirements: z.object({
    team: z.array(z.object({
      role: z.string(),
      hours_per_week: z.number(),
      skills_needed: z.array(z.string())
    })),
    tools: z.array(z.object({
      tool: z.string(),
      purpose: z.string(),
      cost: z.string()
    })),
    budget_total: z.number()
  }),
  
  success_metrics: z.object({
    leading_indicators: z.array(z.object({
      indicator: z.string(),
      target: z.string(),
      measurement_frequency: z.string()
    })),
    lagging_indicators: z.array(z.object({
      indicator: z.string(),
      target: z.string(),
      expected_by: z.string()
    }))
  }),
  
  contingency_plans: z.array(z.object({
    scenario: z.string(),
    trigger: z.string(),
    response: z.string()
  }))
});

export type FullPlan = z.infer<typeof fullPlanSchema>;

export class PlanGeneratorAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    const agentName = 'PlanGeneratorAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'reasoning', getModelForAgent(agentName));
    
    this.parser = StructuredOutputParser.fromZodSchema(fullPlanSchema);
    
    this.prompt = new PromptTemplate({
      template: `You are a GTM execution architect. Create a MANIACALLY DETAILED week-by-week execution plan.

## COMPANY CONTEXT
Company: {company_name}
Positioning: {positioning}

## TARGET COHORTS
{cohorts}

## PROTOCOLS TO EXECUTE
{protocols}

## CAMPAIGNS
{campaigns}

## GOALS
Primary Goal: {primary_goal}
Key Metrics: {metrics}
Timeline: {timeline}

## BUDGET
Monthly Budget: {budget}

## TEAM SIZE
{team_size} people available for execution

## YOUR TASK

Generate a DETAILED 4-week execution plan where:

### EVERY DAY MUST SPECIFY:
- Exact activities with time slots
- Duration for each activity
- WHO does it (by role)
- WHAT tools they need
- WHAT the deliverable is
- HOW to measure success

### EVERY WEEK MUST INCLUDE:
- Clear theme and goal
- All 5 working days detailed
- End-of-week deliverables
- Metrics to track
- Budget allocation
- Risks and mitigation
- Review questions

### THE PLAN MUST:
1. Start from DAY 1 - assume nothing is set up
2. Build momentum - early wins matter
3. Be REALISTIC - account for learning curves
4. Include BUFFER time - things take longer than expected
5. Have clear DECISION POINTS - when to adjust
6. Show ROI PROJECTIONS - tie activities to outcomes

### ACTIVITY EXAMPLES (this level of detail):
- "9:00 AM - Set up Google Analytics tracking (45 min): Install GA4 tag via GTM, configure conversion events for demo requests and signups. Deliverable: Working analytics with 3 conversion events. Success: Events firing correctly in real-time view."

- "2:00 PM - Create first LinkedIn post (30 min): Write authority-building post about [specific topic from positioning]. Include hook, 3 insights, CTA to website. Deliverable: Drafted post in content calendar. Success: Post scheduled for optimal time tomorrow."

Be SPECIFIC. Be PRACTICAL. Be HONEST about time requirements.

{format_instructions}`,
      inputVariables: [
        "company_name", "positioning", "cohorts", "protocols", 
        "campaigns", "primary_goal", "metrics", "timeline", 
        "budget", "team_size"
      ],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() }
    });
  }

  async generatePlan(input: PlanGeneratorInput): Promise<FullPlan> {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
    
    return await chain.invoke({
      company_name: input.company_name,
      positioning: JSON.stringify(input.positioning),
      cohorts: JSON.stringify(input.cohorts),
      protocols: input.protocols.join(', '),
      campaigns: JSON.stringify(input.campaigns),
      primary_goal: input.goals.primary,
      metrics: input.goals.metrics.join(', '),
      timeline: input.goals.timeline,
      budget: input.budget?.monthly ? `₹${input.budget.monthly.toLocaleString()}` : 'Not specified',
      team_size: input.team_size || 1
    });
  }
}

