import { db } from './supabase';
import { PositioningParseAgent } from '../agents/PositioningParseAgent';
import { ICPBuildAgent } from '../agents/ICPBuildAgent';
// Import other agents as needed

/**
 * Agent Orchestrator
 * Manages the execution of agents based on onboarding step
 */
export class AgentOrchestrator {
  private positioningAgent: PositioningParseAgent;
  private icpBuildAgent: ICPBuildAgent;

  constructor() {
    this.positioningAgent = new PositioningParseAgent();
    this.icpBuildAgent = new ICPBuildAgent();
  }

  /**
   * Process a specific step and run the appropriate agent(s)
   */
  async processStep(intakeId: string, step: number, data: any): Promise<any> {
    console.log(`Processing step ${step} for intake ${intakeId}`);

    switch (step) {
      case 1:
        return this.processPositioning(intakeId, data);
      case 2:
        return this.processCompany(intakeId, data);
      case 3:
        return this.processProduct(intakeId, data);
      case 4:
        return this.processMarket(intakeId, data);
      case 5:
        return this.processStrategy(intakeId, data);
      case 6:
        return this.generateICPs(intakeId, data);
      case 7:
        return this.generateWarPlan(intakeId, data);
      default:
        throw new Error(`Unknown step: ${step}`);
    }
  }

  /**
   * Step 1: Process positioning data
   */
  private async processPositioning(intakeId: string, data: any) {
    const { positioning } = data;
    
    // Log execution
    const { data: execution } = await db.logAgentExecution(intakeId, 'PositioningParseAgent', positioning);
    
    try {
      // Run the agent
      const result = await this.positioningAgent.analyze({
        dan_kennedy_answer: positioning.danKennedy,
        dunford_answer: positioning.dunford,
        company_name: data.company?.name,
        industry: data.company?.industry
      });

      // Update intake with derived data
      await db.updateIntake(intakeId, {
        positioning,
        positioning_derived: result
      });

      // Log success
      if (execution) {
        await db.updateAgentExecution(execution.id, result, 'completed');
      }

      return { success: true, derived: result };
    } catch (error: any) {
      // Log failure
      if (execution) {
        await db.updateAgentExecution(execution.id, null, 'failed', error.message);
      }
      
      // Return mock data if agent fails (for demo/development)
      const mockDerived = {
        primary_target: 'Early-stage startup founders',
        primary_problem: 'Lack of clear marketing strategy',
        primary_outcome: 'Clarity and focused execution',
        main_alternatives: ['Marketing consultants', 'DIY frameworks', 'Doing nothing'],
        positioning_type: 'niche-subcategory' as const,
        value_proposition: 'For startup founders who struggle with marketing clarity, RaptorFlow delivers a 90-day execution plan unlike expensive consultants.',
        clarity_score: 65,
        suggestions_to_improve: ['Be more specific about target audience', 'Quantify the outcome'],
        confidence: 0.7
      };

      await db.updateIntake(intakeId, {
        positioning,
        positioning_derived: mockDerived
      });

      return { success: true, derived: mockDerived, mock: true };
    }
  }

  /**
   * Step 2: Process company data
   */
  private async processCompany(intakeId: string, data: any) {
    const { company } = data;
    
    // For now, just store the data (enrichment agents would run here)
    await db.updateIntake(intakeId, {
      company,
      company_enriched: {
        techStack: ['Google Analytics', 'React', 'AWS'], // Mock enriched data
        linkedInUrl: company.website ? `https://linkedin.com/company/${company.website.split('.')[0]}` : null
      }
    });

    return { success: true };
  }

  /**
   * Step 3: Process product data
   */
  private async processProduct(intakeId: string, data: any) {
    const { product } = data;
    
    // JTBD Mapper and Monetization agents would run here
    const mockDerived = {
      jtbd: [
        { type: 'functional', situation: 'When planning marketing', motivation: 'get clear direction', outcome: 'execute confidently' }
      ],
      outcomeType: 'time',
      likelyACV: product.priceRange ? parseInt(product.priceRange.split('-')[0]) * 12 : 5000,
      ticketSize: 'mid',
      saleType: 'sales-assisted'
    };

    await db.updateIntake(intakeId, {
      product,
      product_derived: mockDerived
    });

    return { success: true, derived: mockDerived };
  }

  /**
   * Step 4: Process market data
   */
  private async processMarket(intakeId: string, data: any) {
    const { market } = data;
    
    // Competitor Surface agent would run here
    const mockSystemView = {
      competitorProfiles: market.namedCompetitors?.map((name: string, i: number) => ({
        name,
        tagline: `${name} - Competitor solution`,
        mapCoordinates: { x: 30 + i * 20, y: 40 + i * 15 }
      })) || [],
      positioningGaps: ['Underserved early-stage segment'],
      wedges: ['Speed of implementation']
    };

    await db.updateIntake(intakeId, {
      market,
      market_system_view: mockSystemView
    });

    return { success: true, systemView: mockSystemView };
  }

  /**
   * Step 5: Process strategy data
   */
  private async processStrategy(intakeId: string, data: any) {
    const { strategy } = data;
    
    // Strategy Profile agent would run here
    const mockDerived = {
      strategyProfile: {
        name: `${strategy.goalPrimary} ${strategy.demandSource}`,
        description: 'Balanced growth approach'
      },
      impliedTradeoffs: [
        strategy.goalPrimary === 'velocity' ? 'Accept higher CAC' : 'Focus on efficiency'
      ],
      recommendedProtocols: strategy.demandSource === 'creation' ? ['A', 'B'] : ['B', 'C']
    };

    await db.updateIntake(intakeId, {
      strategy,
      strategy_derived: mockDerived
    });

    return { success: true, derived: mockDerived };
  }

  /**
   * Step 6: Generate ICPs
   */
  async generateICPs(intakeId: string, allData: any) {
    const { data: execution } = await db.logAgentExecution(intakeId, 'ICPBuildAgent', allData);
    
    try {
      const result = await this.icpBuildAgent.analyze({
        company: allData.company,
        product: allData.product,
        positioning: allData.positioning_derived || allData.positioning,
        market: allData.market,
        strategy: allData.strategy,
        jtbd: allData.product_derived
      });

      await db.updateIntake(intakeId, { icps: result.icps });
      
      if (execution) {
        await db.updateAgentExecution(execution.id, result, 'completed');
      }

      return { success: true, icps: result.icps };
    } catch (error: any) {
      // Return mock ICPs if agent fails
      const mockICPs = [
        {
          id: 'desperate-scaler',
          label: 'Desperate Scaler',
          summary: 'High-growth companies overwhelmed by rapid expansion',
          fitScore: 92,
          selected: true,
          firmographics: { employee_range: '50-200', industries: ['SaaS', 'Tech'], stages: ['series-a', 'series-b+'], regions: ['North America'], exclude: [] },
          technographics: { must_have: ['CRM'], nice_to_have: ['Marketing automation'], red_flags: [] },
          psychographics: { pain_points: ['Scaling chaos'], motivations: ['Growth'], internal_triggers: ['New funding'], buying_constraints: [] },
          behavioral_triggers: [{ signal: 'Hiring spike', source: 'LinkedIn', urgency_boost: 80 }],
          buying_committee: [{ role: 'Decision Maker', typical_title: 'VP Growth', concerns: ['ROI'], success_criteria: ['Speed'] }],
          category_context: { market_position: 'challenger', current_solution: 'Manual', switching_triggers: ['Growth'] },
          fit_reasoning: 'High urgency matches product',
          messaging_angle: 'Scale without chaos',
          qualification_questions: ['What is your growth rate?']
        },
        {
          id: 'frustrated-optimizer',
          label: 'Frustrated Optimizer',
          summary: 'Companies that tried other solutions and found them lacking',
          fitScore: 78,
          selected: true,
          firmographics: { employee_range: '200-1000', industries: ['Enterprise'], stages: ['established-sme'], regions: ['Global'], exclude: [] },
          technographics: { must_have: ['Enterprise CRM'], nice_to_have: [], red_flags: ['Competitor X'] },
          psychographics: { pain_points: ['Tool fatigue'], motivations: ['Simplicity'], internal_triggers: ['Contract renewal'], buying_constraints: ['Budget'] },
          behavioral_triggers: [{ signal: 'Competitor churn', source: 'G2', urgency_boost: 60 }],
          buying_committee: [{ role: 'Champion', typical_title: 'Director Ops', concerns: ['Adoption'], success_criteria: ['Ease of use'] }],
          category_context: { market_position: 'leader', current_solution: 'Competitor', switching_triggers: ['Frustration'] },
          fit_reasoning: 'Ready to switch',
          messaging_angle: 'Finally, something that works',
          qualification_questions: ['What have you tried before?']
        },
        {
          id: 'risk-mitigator',
          label: 'Risk Mitigator',
          summary: 'Conservative organizations needing proven solutions',
          fitScore: 65,
          selected: false,
          firmographics: { employee_range: '500+', industries: ['Finance', 'Healthcare'], stages: ['enterprise'], regions: ['North America', 'EU'], exclude: [] },
          technographics: { must_have: ['Compliance tools'], nice_to_have: ['SOC2'], red_flags: [] },
          psychographics: { pain_points: ['Risk'], motivations: ['Compliance'], internal_triggers: ['Audit'], buying_constraints: ['Security'] },
          behavioral_triggers: [{ signal: 'Regulation change', source: 'News', urgency_boost: 70 }],
          buying_committee: [{ role: 'Economic Buyer', typical_title: 'CFO', concerns: ['Risk'], success_criteria: ['Compliance'] }],
          category_context: { market_position: 'newcomer', current_solution: 'Legacy', switching_triggers: ['Compliance'] },
          fit_reasoning: 'Longer sales cycle but high LTV',
          messaging_angle: 'Enterprise-grade security',
          qualification_questions: ['What compliance requirements do you have?']
        }
      ];

      await db.updateIntake(intakeId, { icps: mockICPs });
      
      if (execution) {
        await db.updateAgentExecution(execution.id, { icps: mockICPs }, 'completed', 'Used mock data');
      }

      return { success: true, icps: mockICPs, mock: true };
    }
  }

  /**
   * Step 7: Generate War Plan
   */
  async generateWarPlan(intakeId: string, allData: any) {
    // Move Assembly agent would run here
    const mockWarPlan = {
      generated: true,
      phases: [
        {
          id: 1,
          name: 'Discovery & Authority',
          days: '1-30',
          objectives: ['Build thought leadership', 'Establish content foundation', 'Set up tracking'],
          campaigns: ['Authority Blitz', 'Content Waterfall'],
          kpis: [
            { name: 'Content published', target: '8-12' },
            { name: 'Website traffic', target: '+30%' }
          ]
        },
        {
          id: 2,
          name: 'Launch & Validation',
          days: '31-60',
          objectives: ['Launch demand campaigns', 'Build social proof', 'Start outbound'],
          campaigns: ['Trust Anchor', 'Spear Attack'],
          kpis: [
            { name: 'Demo conversion', target: '15%+' },
            { name: 'Pipeline', target: '$100k+' }
          ]
        },
        {
          id: 3,
          name: 'Optimization & Scale',
          days: '61-90',
          objectives: ['Double down on winners', 'Kill underperformers', 'Plan Q2'],
          campaigns: ['Expansion Plays', 'Churn Intercept'],
          kpis: [
            { name: 'CAC payback', target: '<12mo' },
            { name: 'Win rate', target: '25%+' }
          ]
        }
      ],
      protocols: {
        A: { name: 'Authority Blitz', active: true },
        B: { name: 'Trust Anchor', active: true },
        C: { name: 'Cost of Inaction', active: false },
        D: { name: 'Facilitator Nudge', active: true },
        E: { name: 'Champions Armory', active: false },
        F: { name: 'Churn Intercept', active: false }
      }
    };

    await db.updateIntake(intakeId, { war_plan: mockWarPlan });

    return { success: true, warPlan: mockWarPlan };
  }
}

export const orchestrator = new AgentOrchestrator();

