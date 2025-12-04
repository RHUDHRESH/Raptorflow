import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModel } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";
import type { 
  ICP, 
  CreateICPInput, 
  ICPFirmographics, 
  ICPTechnographics, 
  ICPPsychographics,
  ICPBehavioralTrigger,
  ICPBuyingCommitteeMember,
  ICPCategoryContext,
  BarrierType 
} from "../types";

// =====================================================
// ICP ARCHETYPES - Template Library
// =====================================================

export const ICP_ARCHETYPES = {
  desperate_scaler: {
    label: "Desperate Scaler",
    description: "Fast-growing companies overwhelmed by rapid expansion, need solutions urgently",
    typical_barriers: ['OBSCURITY', 'RISK'] as BarrierType[],
    firmographics_template: {
      employee_range: "50-200",
      stages: ["series-a", "series-b"],
      business_model: "high-growth"
    },
    psychographics_template: {
      risk_tolerance: "high" as const,
      pain_points: ["Scaling chaos", "Process breakdown", "Team overwhelm"],
      motivations: ["Growth", "Efficiency", "Competitive advantage"],
      internal_triggers: ["New funding round", "Hiring surge", "Revenue milestone"],
      buying_constraints: ["Speed > Price", "Need quick implementation"]
    }
  },
  frustrated_optimizer: {
    label: "Frustrated Optimizer",
    description: "Companies that tried other solutions and found them lacking",
    typical_barriers: ['RISK', 'INERTIA'] as BarrierType[],
    firmographics_template: {
      employee_range: "100-500",
      stages: ["series-b", "established"],
      business_model: "mature"
    },
    psychographics_template: {
      risk_tolerance: "medium" as const,
      pain_points: ["Tool fatigue", "Poor ROI from current tools", "Fragmented workflows"],
      motivations: ["Simplicity", "Results", "Consolidation"],
      internal_triggers: ["Contract renewal", "Quarterly review", "Leadership change"],
      buying_constraints: ["Must prove ROI", "Needs stakeholder buy-in"]
    }
  },
  risk_mitigator: {
    label: "Risk Mitigator",
    description: "Conservative organizations that need proven solutions and security assurances",
    typical_barriers: ['RISK'] as BarrierType[],
    firmographics_template: {
      employee_range: "500+",
      stages: ["enterprise", "established"],
      business_model: "enterprise"
    },
    psychographics_template: {
      risk_tolerance: "low" as const,
      pain_points: ["Compliance requirements", "Security concerns", "Change management"],
      motivations: ["Security", "Reliability", "Compliance"],
      internal_triggers: ["Audit findings", "Regulatory change", "Security incident"],
      buying_constraints: ["Long procurement", "Security review required", "Multiple approvals"]
    }
  },
  efficiency_seeker: {
    label: "Efficiency Seeker",
    description: "Cost-conscious companies looking to do more with less",
    typical_barriers: ['INERTIA', 'FRICTION'] as BarrierType[],
    firmographics_template: {
      employee_range: "20-100",
      stages: ["bootstrap", "seed", "series-a"],
      business_model: "lean"
    },
    psychographics_template: {
      risk_tolerance: "medium" as const,
      pain_points: ["Limited budget", "Resource constraints", "Manual processes"],
      motivations: ["Cost savings", "Time savings", "Automation"],
      internal_triggers: ["Budget cut", "Team reduction", "Efficiency mandate"],
      buying_constraints: ["Price sensitive", "Needs clear ROI", "Self-serve preferred"]
    }
  },
  market_leader: {
    label: "Market Leader",
    description: "Established companies looking to maintain or extend their advantage",
    typical_barriers: ['CAPACITY', 'ATROPHY'] as BarrierType[],
    firmographics_template: {
      employee_range: "1000+",
      stages: ["enterprise"],
      business_model: "enterprise"
    },
    psychographics_template: {
      risk_tolerance: "low" as const,
      pain_points: ["Maintaining advantage", "Innovation pressure", "Market disruption"],
      motivations: ["Market leadership", "Innovation", "Customer retention"],
      internal_triggers: ["Competitive threat", "Market shift", "Board pressure"],
      buying_constraints: ["Strategic fit required", "Executive sponsorship needed"]
    }
  }
};

// =====================================================
// INPUT/OUTPUT SCHEMAS
// =====================================================

export interface ICPBuildInput {
  company: any;
  product: any;
  positioning: any;
  market: any;
  strategy: any;
  jtbd?: any;
}

const icpOutputSchema = z.object({
  icps: z.array(z.object({
    id: z.string(),
    label: z.string(),
    archetype: z.string(),
    summary: z.string(),
    firmographics: z.object({
      employee_range: z.string(),
      revenue_range: z.string().optional(),
      industries: z.array(z.string()),
      stages: z.array(z.string()),
      regions: z.array(z.string()),
      exclude: z.array(z.string()).optional(),
      business_model: z.string().optional()
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
      buying_constraints: z.array(z.string()),
      risk_tolerance: z.enum(["low", "medium", "high"])
    }),
    behavioral_triggers: z.array(z.object({
      signal: z.string(),
      source: z.string(),
      urgency_boost: z.number().min(0).max(100),
      description: z.string().optional()
    })),
    buying_committee: z.array(z.object({
      role: z.string(),
      typical_title: z.string(),
      concerns: z.array(z.string()),
      success_criteria: z.array(z.string()),
      influence_level: z.enum(["low", "medium", "high"]).optional()
    })),
    category_context: z.object({
      market_position: z.enum(["leader", "challenger", "newcomer"]),
      current_solution: z.string(),
      switching_triggers: z.array(z.string()),
      awareness_level: z.enum(["unaware", "problem_aware", "solution_aware", "product_aware"]).optional()
    }),
    fit_score: z.number().min(0).max(100),
    fit_reasoning: z.string(),
    messaging_angle: z.string(),
    primary_value_proposition: z.string(),
    qualification_questions: z.array(z.string()),
    primary_barriers: z.array(z.enum(["OBSCURITY", "RISK", "INERTIA", "FRICTION", "CAPACITY", "ATROPHY"]))
  })),
  selection_rationale: z.string(),
  icp_comparison: z.object({
    highest_urgency: z.string(),
    largest_market: z.string(),
    easiest_to_reach: z.string(),
    highest_ltv: z.string()
  })
});

export type ICPBuildOutput = z.infer<typeof icpOutputSchema>;

// =====================================================
// ICP BUILD AGENT
// =====================================================

export class ICPBuildAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    this.model = getLangChainModel("gemini-pro");
    this.parser = StructuredOutputParser.fromZodSchema(icpOutputSchema);
    this.prompt = new PromptTemplate({
      template: `You are an expert ICP (Ideal Customer Profile) architect using the 6D Intelligence Framework.

## Your Task
Generate 3-5 distinct, actionable ICPs for this company based on their positioning, product, and strategy.

## 6D Framework Dimensions
1. **Firmographics** - Company characteristics (size, stage, industry, region)
2. **Technographics** - Technology stack and tools they use
3. **Psychographics** - Motivations, pain points, buying style, risk tolerance
4. **Behavioral Triggers** - Signals that indicate they're in-market NOW
5. **Buying Committee** - Key personas, their concerns, and success criteria
6. **Category Context** - Market position, current solutions, switching triggers

## ICP Archetypes to Consider
Select 3-5 that best fit this company's positioning:
- **Desperate Scaler**: High urgency, rapid growth, needs solutions NOW
- **Frustrated Optimizer**: Tried alternatives, ready to switch
- **Risk Mitigator**: Conservative, needs assurance and proof
- **Efficiency Seeker**: Cost-conscious, needs clear ROI
- **Market Leader**: Established, looking to maintain advantage

## Input Data

### Company Context
{company}

### Product Details
{product}

### Positioning (Dan Kennedy / April Dunford)
{positioning}

### Market & Competition
{market}

### Strategic Focus
{strategy}

## Requirements for Each ICP

1. **Be Specific**: Each ICP should be specific enough to:
   - Set ad targeting criteria
   - Write personalized messaging
   - Create qualification questions
   - Build trigger-based campaigns

2. **Score Fit (0-100)** based on:
   - Alignment with positioning statement
   - Match with product capabilities
   - Strategic goal fit (velocity/efficiency/penetration)
- Likelihood to convert

3. **Assign Primary Barriers**: Each ICP faces specific barriers:
   - OBSCURITY: Don't know you exist
   - RISK: Know you but don't trust you
   - INERTIA: Trust you but not urgent
   - FRICTION: Signed up but not activated
   - CAPACITY: Active but not expanding
   - ATROPHY: Churning or at risk

4. **Provide Messaging Angle**: One sentence that captures how to talk to this ICP

5. **List Behavioral Triggers**: Real-world signals with specific sources (LinkedIn, G2, news, job boards, etc.)

{format_instructions}`,
      inputVariables: ["company", "product", "positioning", "market", "strategy"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  async analyze(input: ICPBuildInput): Promise<ICPBuildOutput> {
    try {
    const chain = this.prompt.pipe(this.model).pipe(this.parser);
      const result = await chain.invoke({
        company: JSON.stringify(input.company || {}, null, 2),
        product: JSON.stringify(input.product || {}, null, 2),
        positioning: JSON.stringify(input.positioning || {}, null, 2),
        market: JSON.stringify(input.market || {}, null, 2),
        strategy: JSON.stringify(input.strategy || {}, null, 2)
      });
      
      return result as ICPBuildOutput;
    } catch (error: any) {
      console.error('ICPBuildAgent error:', error);
      // Return fallback ICPs
      return this.getFallbackICPs(input);
    }
  }

  /**
   * Generate ICPs with archetype selection
   */
  async generateWithArchetypes(input: ICPBuildInput, archetypeKeys?: string[]): Promise<ICPBuildOutput> {
    // Select archetypes based on strategy or use defaults
    const selectedArchetypes = archetypeKeys 
      ? archetypeKeys.filter(k => k in ICP_ARCHETYPES)
      : this.selectArchetypesForStrategy(input.strategy);
    
    // Enhance prompt with selected archetypes
    const archetypeContext = selectedArchetypes.map(key => {
      const archetype = ICP_ARCHETYPES[key as keyof typeof ICP_ARCHETYPES];
      return `- ${archetype.label}: ${archetype.description}`;
    }).join('\n');

    const enhancedPrompt = new PromptTemplate({
      template: `You are an expert ICP architect. Generate ICPs based on these pre-selected archetypes:

## Selected Archetypes
${archetypeContext}

## Company Data
{company}

## Product
{product}

## Positioning
{positioning}

## Market
{market}

## Strategy
{strategy}

Create a complete ICP for EACH selected archetype, customized for this specific company.

{format_instructions}`,
      inputVariables: ["company", "product", "positioning", "market", "strategy"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });

    try {
      const chain = enhancedPrompt.pipe(this.model).pipe(this.parser);
      return await chain.invoke({
        company: JSON.stringify(input.company || {}, null, 2),
        product: JSON.stringify(input.product || {}, null, 2),
        positioning: JSON.stringify(input.positioning || {}, null, 2),
        market: JSON.stringify(input.market || {}, null, 2),
        strategy: JSON.stringify(input.strategy || {}, null, 2)
      });
    } catch (error) {
      console.error('ICPBuildAgent archetype generation error:', error);
      return this.getFallbackICPs(input);
    }
  }

  /**
   * Select appropriate archetypes based on strategy
   */
  private selectArchetypesForStrategy(strategy: any): string[] {
    const goal = strategy?.goalPrimary || strategy?.goal;
    const demandSource = strategy?.demandSource || strategy?.demand_source;
    
    // Default selection
    const defaults = ['desperate_scaler', 'frustrated_optimizer', 'risk_mitigator'];
    
    if (goal === 'velocity') {
      return ['desperate_scaler', 'frustrated_optimizer', 'efficiency_seeker'];
    }
    
    if (goal === 'efficiency') {
      return ['frustrated_optimizer', 'efficiency_seeker', 'risk_mitigator'];
    }
    
    if (goal === 'penetration') {
      return ['market_leader', 'frustrated_optimizer', 'risk_mitigator'];
    }
    
    if (demandSource === 'expansion') {
      return ['frustrated_optimizer', 'market_leader', 'desperate_scaler'];
    }
    
    return defaults;
  }

  /**
   * Convert LLM output to database-ready format
   */
  toCreateInput(icpOutput: ICPBuildOutput['icps'][0], intakeId?: string): CreateICPInput {
    return {
      label: icpOutput.label,
      summary: icpOutput.summary,
      intake_id: intakeId,
      firmographics: icpOutput.firmographics as ICPFirmographics,
      technographics: icpOutput.technographics as ICPTechnographics,
      psychographics: {
        ...icpOutput.psychographics,
        risk_tolerance: icpOutput.psychographics.risk_tolerance
      } as ICPPsychographics,
      behavioral_triggers: icpOutput.behavioral_triggers as ICPBehavioralTrigger[],
      buying_committee: icpOutput.buying_committee.map(bc => ({
        ...bc,
        influence_level: bc.influence_level || 'medium'
      })) as ICPBuyingCommitteeMember[],
      category_context: {
        ...icpOutput.category_context,
        awareness_level: icpOutput.category_context.awareness_level || 'problem_aware'
      } as ICPCategoryContext,
      fit_score: icpOutput.fit_score,
      fit_reasoning: icpOutput.fit_reasoning,
      messaging_angle: icpOutput.messaging_angle,
      qualification_questions: icpOutput.qualification_questions,
      primary_barriers: icpOutput.primary_barriers as BarrierType[],
      is_selected: icpOutput.fit_score >= 70 // Auto-select high-fit ICPs
    };
  }

  /**
   * Fallback ICPs when LLM fails
   */
  private getFallbackICPs(input: ICPBuildInput): ICPBuildOutput {
    const industry = input.company?.industry || 'Technology';
    const product = input.product?.name || 'this product';
    
    return {
      icps: [
        {
          id: 'desperate-scaler',
          label: 'Desperate Scaler',
          archetype: 'desperate_scaler',
          summary: `Fast-growing ${industry} companies overwhelmed by rapid expansion and need ${product} urgently.`,
          firmographics: {
            employee_range: '50-200',
            industries: [industry],
            stages: ['series-a', 'series-b'],
            regions: ['Global']
          },
          technographics: {
            must_have: ['CRM'],
            nice_to_have: ['Marketing automation'],
            red_flags: []
          },
          psychographics: {
            pain_points: ['Scaling chaos', 'No clear process'],
            motivations: ['Growth', 'Efficiency'],
            internal_triggers: ['New funding'],
            buying_constraints: ['Speed > Price'],
            risk_tolerance: 'high' as const
          },
          behavioral_triggers: [
            { signal: 'Hiring spike', source: 'LinkedIn', urgency_boost: 80 },
            { signal: 'Funding announcement', source: 'Crunchbase', urgency_boost: 90 }
          ],
          buying_committee: [
            { role: 'Decision Maker', typical_title: 'VP Growth', concerns: ['ROI', 'Speed'], success_criteria: ['Pipeline growth'], influence_level: 'high' as const }
          ],
          category_context: {
            market_position: 'challenger' as const,
            current_solution: 'Manual processes',
            switching_triggers: ['Growth wall']
          },
          fit_score: 92,
          fit_reasoning: 'High urgency and immediate need matches our value prop',
          messaging_angle: 'Scale without the chaos',
          primary_value_proposition: `${product} helps you scale faster without breaking`,
          qualification_questions: ['What is your growth rate?', 'What have you tried before?'],
          primary_barriers: ['OBSCURITY', 'RISK'] as const
        },
        {
          id: 'frustrated-optimizer',
          label: 'Frustrated Optimizer',
          archetype: 'frustrated_optimizer',
          summary: `${industry} companies that have tried other solutions and found them lacking.`,
          firmographics: {
            employee_range: '100-500',
            industries: [industry],
            stages: ['series-b', 'established'],
            regions: ['Global']
          },
          technographics: {
            must_have: ['Existing tools'],
            nice_to_have: [],
            red_flags: []
          },
          psychographics: {
            pain_points: ['Tool fatigue', 'Poor ROI'],
            motivations: ['Simplicity', 'Results'],
            internal_triggers: ['Contract renewal'],
            buying_constraints: ['Prove ROI'],
            risk_tolerance: 'medium' as const
          },
          behavioral_triggers: [
            { signal: 'Competitor churn', source: 'G2 Reviews', urgency_boost: 60 }
          ],
          buying_committee: [
            { role: 'Champion', typical_title: 'Director Ops', concerns: ['Adoption'], success_criteria: ['Ease of use'], influence_level: 'medium' as const }
          ],
          category_context: {
            market_position: 'challenger' as const,
            current_solution: 'Competitor',
            switching_triggers: ['Frustration']
          },
          fit_score: 78,
          fit_reasoning: 'Ready to switch and knows what they want',
          messaging_angle: 'Finally, something that actually works',
          primary_value_proposition: `Unlike other tools, ${product} delivers real results`,
          qualification_questions: ['What solutions have you tried?', 'Why are you switching?'],
          primary_barriers: ['RISK', 'INERTIA'] as const
        },
        {
          id: 'risk-mitigator',
          label: 'Risk Mitigator',
          archetype: 'risk_mitigator',
          summary: 'Conservative organizations that need proven solutions and security assurances.',
          firmographics: {
            employee_range: '500+',
            industries: ['Enterprise', 'Finance'],
            stages: ['enterprise'],
            regions: ['North America', 'EU']
          },
          technographics: {
            must_have: ['Enterprise systems'],
            nice_to_have: ['SOC2 compliance'],
            red_flags: []
          },
          psychographics: {
            pain_points: ['Risk', 'Compliance'],
            motivations: ['Security', 'Reliability'],
            internal_triggers: ['Audit'],
            buying_constraints: ['Security review required'],
            risk_tolerance: 'low' as const
          },
          behavioral_triggers: [
            { signal: 'Compliance requirement', source: 'News', urgency_boost: 70 }
          ],
          buying_committee: [
            { role: 'Economic Buyer', typical_title: 'CFO', concerns: ['Risk', 'TCO'], success_criteria: ['Compliance'], influence_level: 'high' as const }
          ],
          category_context: {
            market_position: 'newcomer' as const,
            current_solution: 'Legacy',
            switching_triggers: ['Compliance mandate']
          },
          fit_score: 65,
          fit_reasoning: 'Longer sales cycle but high LTV potential',
          messaging_angle: 'Enterprise-grade security and reliability',
          primary_value_proposition: `${product} meets the strictest security requirements`,
          qualification_questions: ['What compliance requirements do you have?'],
          primary_barriers: ['RISK'] as const
        }
      ],
      selection_rationale: 'Selected archetypes that match the company positioning and strategy focus.',
      icp_comparison: {
        highest_urgency: 'Desperate Scaler',
        largest_market: 'Frustrated Optimizer',
        easiest_to_reach: 'Frustrated Optimizer',
        highest_ltv: 'Risk Mitigator'
      }
    };
  }
}
