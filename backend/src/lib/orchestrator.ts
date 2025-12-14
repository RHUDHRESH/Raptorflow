import { db } from './supabase';
import { PositioningParseAgent } from '../agents/PositioningParseAgent';
import { 
  websiteScraperTool, 
  companyAnalyzerTool, 
  competitorResearchTool, 
  techStackDetectorTool,
  icpGeneratorTool,
  warPlanGeneratorTool 
} from '../tools/nativeTools';

/**
 * Agent Orchestrator
 * Manages the execution of agents based on onboarding step
 * Uses NATIVE tools only - no external API keys required
 */
export class AgentOrchestrator {
  private positioningAgent: PositioningParseAgent;

  constructor() {
    this.positioningAgent = new PositioningParseAgent();
  }

  /**
   * Process a specific step and run the appropriate agent(s)
   */
  async processStep(intakeId: string, step: number, data: any): Promise<any> {
    console.log(`Processing step ${step} for intake ${intakeId}`);

    try {
      switch (step) {
        case 1:
          return await this.processPositioning(intakeId, data);
        case 2:
          return await this.processCompany(intakeId, data);
        case 3:
          return await this.processProduct(intakeId, data);
        case 4:
          return await this.processMarket(intakeId, data);
        case 5:
          return await this.processStrategy(intakeId, data);
        case 6:
          return await this.generateICPs(intakeId, data);
        case 7:
          return await this.generateWarPlan(intakeId, data);
        default:
          throw new Error(`Unknown step: ${step}`);
      }
    } catch (error: any) {
      console.error(`Error processing step ${step}:`, error);
      // Return graceful fallback
      return { success: false, error: error.message };
    }
  }

  /**
   * Step 1: Process positioning data using PositioningParseAgent
   */
  private async processPositioning(intakeId: string, data: any) {
    const { positioning } = data;
    
    const { data: execution } = await db.logAgentExecution(intakeId, 'PositioningParseAgent', positioning);
    
    try {
      const result = await this.positioningAgent.analyze({
        dan_kennedy_answer: positioning.danKennedy || positioning.dan_kennedy,
        dunford_answer: positioning.dunford || positioning.april_dunford,
        company_name: data.company?.name,
        industry: data.company?.industry
      });

      await db.updateIntake(intakeId, {
        positioning,
        positioning_derived: result
      });

      if (execution) {
        await db.updateAgentExecution(execution.id, result, 'completed');
      }

      return { success: true, derived: result };
    } catch (error: any) {
      console.error('Positioning agent error:', error);
      
      // Fallback: Generate basic derived data
      const mockDerived = {
        primary_target: this.extractTarget(positioning.danKennedy || positioning.dunford || ''),
        primary_problem: 'Marketing clarity and execution',
        primary_outcome: 'Focused growth strategy',
        main_alternatives: ['Marketing consultants', 'DIY approaches', 'Status quo'],
        positioning_type: 'niche-subcategory' as const,
        value_proposition: `For companies seeking growth, we deliver clarity and execution.`,
        clarity_score: 50,
        suggestions_to_improve: ['Be more specific about target audience', 'Quantify outcomes'],
        confidence: 0.5
      };

      await db.updateIntake(intakeId, {
        positioning,
        positioning_derived: mockDerived
      });

      if (execution) {
        await db.updateAgentExecution(execution.id, mockDerived, 'completed', 'Used fallback');
      }

      return { success: true, derived: mockDerived, fallback: true };
    }
  }

  /**
   * Step 2: Process company data using native web scraping
   */
  private async processCompany(intakeId: string, data: any) {
    const { company } = data;
    
    const { data: execution } = await db.logAgentExecution(intakeId, 'CompanyEnrichAgent', company);
    
    let enriched: any = {};
    
    try {
      // Scrape website if provided
      if (company.website) {
        console.log('Scraping website:', company.website);
        const scrapeResult = await websiteScraperTool.invoke({ url: company.website });
        const scraped = JSON.parse(scrapeResult);
        
        if (scraped.success) {
          // Analyze the scraped content
          const analysisResult = await companyAnalyzerTool.invoke({
            websiteContent: `Title: ${scraped.title}\nDescription: ${scraped.metaDescription}\nContent: ${scraped.contentPreview}`,
            companyName: company.name
          });
          const analysis = JSON.parse(analysisResult);
          
          if (analysis.success) {
            enriched.websiteAnalysis = analysis.analysis;
          }
          
          // Detect tech stack
          const techResult = await techStackDetectorTool.invoke({ url: company.website });
          const tech = JSON.parse(techResult);
          
          if (tech.success) {
            enriched.techStack = tech.detectedTechnologies;
            enriched.techStackCategorized = tech.categorized;
          }
        }
      }
      
      enriched.enrichedAt = new Date().toISOString();
      
      await db.updateIntake(intakeId, {
        company,
        company_enriched: enriched
      });

      if (execution) {
        await db.updateAgentExecution(execution.id, enriched, 'completed');
      }

      return { success: true, enriched };
    } catch (error: any) {
      console.error('Company enrichment error:', error);
      
      // Fallback
      enriched = {
        techStack: ['Unknown'],
        enrichedAt: new Date().toISOString(),
        error: error.message
      };
      
      await db.updateIntake(intakeId, {
        company,
        company_enriched: enriched
      });

      if (execution) {
        await db.updateAgentExecution(execution.id, enriched, 'completed', error.message);
      }

      return { success: true, enriched, fallback: true };
    }
  }

  /**
   * Step 3: Process product data
   */
  private async processProduct(intakeId: string, data: any) {
    const { product } = data;
    
    // Derive JTBD and monetization insights
    const derived = {
      jtbd: this.deriveJTBD(product),
      outcomeType: this.deriveOutcomeType(product),
      likelyACV: this.estimateACV(product),
      ticketSize: this.determineTicketSize(product),
      saleType: this.determineSaleType(product),
      derivedAt: new Date().toISOString()
    };

    await db.updateIntake(intakeId, {
      product,
      product_derived: derived
    });

    return { success: true, derived };
  }

  /**
   * Step 4: Process market data using native competitor research
   */
  private async processMarket(intakeId: string, data: any) {
    const { market } = data;
    
    const { data: execution } = await db.logAgentExecution(intakeId, 'CompetitorSurfaceAgent', market);
    
    let systemView: any = {};
    
    try {
      // Get intake data for context
      const { data: intake } = await db.getIntake((await db.getIntake('')).data?.user_id || '');
      
      // Research competitors using AI
      const researchResult = await competitorResearchTool.invoke({
        companyDescription: intake?.positioning?.danKennedy || market.differentiator || 'B2B company',
        industry: intake?.company?.industry || 'Technology',
        knownCompetitors: market.namedCompetitors || []
      });
      
      const research = JSON.parse(researchResult);
      
      if (research.success) {
        systemView = {
          competitors: research.research.competitors || [],
          marketLandscape: research.research.market_landscape || {},
          userPerception: {
            pricePosition: market.pricePosition,
            complexityPosition: market.complexityPosition,
            mainEnemy: market.alternativeAction,
            differentiator: market.differentiator
          },
          analyzedAt: new Date().toISOString()
        };
      }
      
      await db.updateIntake(intakeId, {
        market,
        market_system_view: systemView
      });

      if (execution) {
        await db.updateAgentExecution(execution.id, systemView, 'completed');
      }

      return { success: true, systemView };
    } catch (error: any) {
      console.error('Market analysis error:', error);
      
      // Fallback
      systemView = {
        competitors: market.namedCompetitors?.map((name: string) => ({
          name,
          analyzed: false
        })) || [],
        userPerception: {
          pricePosition: market.pricePosition,
          complexityPosition: market.complexityPosition,
          mainEnemy: market.alternativeAction
        },
        error: error.message
      };
      
      await db.updateIntake(intakeId, {
        market,
        market_system_view: systemView
      });

      if (execution) {
        await db.updateAgentExecution(execution.id, systemView, 'completed', error.message);
      }

      return { success: true, systemView, fallback: true };
    }
  }

  /**
   * Step 5: Process strategy data
   */
  private async processStrategy(intakeId: string, data: any) {
    const { strategy } = data;
    
    const derived = {
      strategyProfile: {
        name: `${strategy.goalPrimary || 'Balanced'} ${strategy.demandSource || 'Growth'}`,
        goal: strategy.goalPrimary,
        demandSource: strategy.demandSource,
        persuasion: strategy.persuasionAxis
      },
      impliedTradeoffs: this.deriveTradeoffs(strategy),
      recommendedProtocols: this.deriveProtocols(strategy),
      derivedAt: new Date().toISOString()
    };

    await db.updateIntake(intakeId, {
      strategy,
      strategy_derived: derived
    });

    return { success: true, derived };
  }

  /**
   * Step 6: Generate ICPs using native AI tool
   */
  async generateICPs(intakeId: string, allData?: any) {
    // Get all intake data if not provided
    if (!allData) {
      const result = await db.getIntake(intakeId);
      allData = result.data;
    }
    
    const { data: execution } = await db.logAgentExecution(intakeId, 'ICPBuildAgent', { generating: true });
    
    try {
      const icpResult = await icpGeneratorTool.invoke({
        companyData: allData.company || {},
        positioningData: allData.positioning_derived || allData.positioning || {},
        productData: allData.product_derived || allData.product || {},
        strategyData: allData.strategy_derived || allData.strategy || {}
      });
      
      const result = JSON.parse(icpResult);
      
      if (result.success && result.icps) {
        // Add selection state
        const icpsWithSelection = result.icps.map((icp: any, i: number) => ({
          ...icp,
          selected: i < 2 // Select first 2 by default
        }));
        
        await db.updateIntake(intakeId, { icps: icpsWithSelection });
        
        if (execution) {
          await db.updateAgentExecution(execution.id, { icps: icpsWithSelection }, 'completed');
        }
        
        return { success: true, icps: icpsWithSelection };
      }
      
      throw new Error(result.error || 'Failed to generate ICPs');
    } catch (error: any) {
      console.error('ICP generation error:', error);
      
      // Fallback ICPs
      const fallbackICPs = this.getFallbackICPs(allData);
      
      await db.updateIntake(intakeId, { icps: fallbackICPs });
      
      if (execution) {
        await db.updateAgentExecution(execution.id, { icps: fallbackICPs }, 'completed', 'Used fallback');
      }
      
      return { success: true, icps: fallbackICPs, fallback: true };
    }
  }

  /**
   * Step 7: Generate War Plan using native AI tool
   */
  async generateWarPlan(intakeId: string, allData?: any) {
    if (!allData) {
      const result = await db.getIntake(intakeId);
      allData = result.data;
    }
    
    const { data: execution } = await db.logAgentExecution(intakeId, 'MoveAssemblyAgent', { generating: true });
    
    try {
      const warPlanResult = await warPlanGeneratorTool.invoke({
        icps: allData.icps || [],
        strategyData: allData.strategy_derived || allData.strategy || {},
        companyData: allData.company || {}
      });
      
      const result = JSON.parse(warPlanResult);
      
      if (result.success && result.warPlan) {
        await db.updateIntake(intakeId, { war_plan: result.warPlan });
        
        if (execution) {
          await db.updateAgentExecution(execution.id, result.warPlan, 'completed');
        }
        
        return { success: true, warPlan: result.warPlan };
      }
      
      throw new Error(result.error || 'Failed to generate war plan');
    } catch (error: any) {
      console.error('War plan generation error:', error);
      
      // Fallback war plan
      const fallbackWarPlan = this.getFallbackWarPlan(allData);
      
      await db.updateIntake(intakeId, { war_plan: fallbackWarPlan });
      
      if (execution) {
        await db.updateAgentExecution(execution.id, fallbackWarPlan, 'completed', 'Used fallback');
      }
      
      return { success: true, warPlan: fallbackWarPlan, fallback: true };
    }
  }

  // ============ HELPER METHODS ============

  private extractTarget(text: string): string {
    // Simple extraction of target audience from text
    const patterns = [
      /for\s+([^,\.]+)/i,
      /help\s+([^,\.]+)/i,
      /serve\s+([^,\.]+)/i
    ];
    
    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) return match[1].trim();
    }
    
    return 'B2B companies';
  }

  private deriveJTBD(product: any): any[] {
    return [{
      type: 'functional',
      situation: `When ${product.mainJob || 'doing their work'}`,
      motivation: 'achieve better results',
      outcome: product.mainJob || 'improved efficiency'
    }];
  }

  private deriveOutcomeType(product: any): string {
    const job = (product.mainJob || '').toLowerCase();
    if (job.includes('save') || job.includes('time') || job.includes('faster')) return 'time';
    if (job.includes('money') || job.includes('revenue') || job.includes('cost')) return 'money';
    if (job.includes('risk') || job.includes('secure') || job.includes('complian')) return 'risk';
    return 'efficiency';
  }

  private estimateACV(product: any): number {
    const price = product.priceRange || '';
    const match = price.match(/\d+/);
    if (match) {
      const monthlyPrice = parseInt(match[0]);
      return monthlyPrice * 12;
    }
    return 5000;
  }

  private determineTicketSize(product: any): string {
    const acv = this.estimateACV(product);
    if (acv < 5000) return 'low';
    if (acv < 25000) return 'mid';
    return 'high';
  }

  private determineSaleType(product: any): string {
    const ticketSize = this.determineTicketSize(product);
    return ticketSize === 'low' ? 'self-serve' : 'sales-assisted';
  }

  private deriveTradeoffs(strategy: any): string[] {
    const tradeoffs: string[] = [];
    
    if (strategy.goalPrimary === 'velocity') {
      tradeoffs.push('Accept higher CAC for faster growth');
    } else if (strategy.goalPrimary === 'efficiency') {
      tradeoffs.push('Slower growth for better unit economics');
    } else if (strategy.goalPrimary === 'penetration') {
      tradeoffs.push('Heavy brand investment for market share');
    }
    
    if (strategy.demandSource === 'creation') {
      tradeoffs.push('Invest in education and content');
    } else if (strategy.demandSource === 'capture') {
      tradeoffs.push('Focus on in-market buyers');
    }
    
    return tradeoffs;
  }

  private deriveProtocols(strategy: any): string[] {
    const protocols: string[] = [];
    
    if (strategy.demandSource === 'creation') {
      protocols.push('A', 'B'); // Authority Blitz, Trust Anchor
    } else {
      protocols.push('B', 'C'); // Trust Anchor, Cost of Inaction
    }
    
    if (strategy.goalPrimary === 'velocity') {
      protocols.push('D'); // Facilitator Nudge
    }
    
    return [...new Set(protocols)];
  }

  private getFallbackICPs(data: any): any[] {
    const industry = data.company?.industry || 'Technology';
    
    return [
      {
        id: 'desperate-scaler',
        label: 'Desperate Scaler',
        summary: `Fast-growing ${industry} companies overwhelmed by rapid expansion and need solutions now.`,
        fitScore: 92,
        selected: true,
        firmographics: { employee_range: '50-200', industries: [industry], stages: ['series-a', 'series-b'], regions: ['Global'], exclude: [] },
        technographics: { must_have: ['CRM'], nice_to_have: ['Marketing automation'], red_flags: [] },
        psychographics: { pain_points: ['Scaling chaos', 'No clear process'], motivations: ['Growth', 'Efficiency'], internal_triggers: ['New funding'], buying_constraints: ['Speed > Price'] },
        behavioral_triggers: [{ signal: 'Hiring spike', source: 'LinkedIn', urgency_boost: 80 }],
        buying_committee: [{ role: 'Decision Maker', typical_title: 'VP Growth', concerns: ['ROI', 'Speed'], success_criteria: ['Pipeline growth'] }],
        category_context: { market_position: 'challenger', current_solution: 'Manual processes', switching_triggers: ['Growth wall'] },
        fit_reasoning: 'High urgency and immediate need matches our value prop',
        messaging_angle: 'Scale without the chaos',
        qualification_questions: ['What is your growth rate?', 'What have you tried?']
      },
      {
        id: 'frustrated-optimizer',
        label: 'Frustrated Optimizer',
        summary: `${industry} companies that have tried other solutions and found them lacking.`,
        fitScore: 78,
        selected: true,
        firmographics: { employee_range: '100-500', industries: [industry], stages: ['series-b', 'established'], regions: ['Global'], exclude: [] },
        technographics: { must_have: ['Existing tools'], nice_to_have: [], red_flags: [] },
        psychographics: { pain_points: ['Tool fatigue', 'Poor ROI'], motivations: ['Simplicity', 'Results'], internal_triggers: ['Contract renewal'], buying_constraints: ['Prove ROI'] },
        behavioral_triggers: [{ signal: 'Competitor churn', source: 'G2/Reviews', urgency_boost: 60 }],
        buying_committee: [{ role: 'Champion', typical_title: 'Director Ops', concerns: ['Adoption'], success_criteria: ['Ease of use'] }],
        category_context: { market_position: 'challenger', current_solution: 'Competitor', switching_triggers: ['Frustration'] },
        fit_reasoning: 'Ready to switch and knows what they want',
        messaging_angle: 'Finally, something that actually works',
        qualification_questions: ['What solutions have you tried?', 'Why are you switching?']
      },
      {
        id: 'risk-mitigator',
        label: 'Risk Mitigator',
        summary: 'Conservative organizations that need proven solutions and security assurances.',
        fitScore: 65,
        selected: false,
        firmographics: { employee_range: '500+', industries: ['Enterprise', 'Finance'], stages: ['enterprise'], regions: ['North America', 'EU'], exclude: [] },
        technographics: { must_have: ['Enterprise systems'], nice_to_have: ['SOC2'], red_flags: [] },
        psychographics: { pain_points: ['Risk', 'Compliance'], motivations: ['Security', 'Reliability'], internal_triggers: ['Audit'], buying_constraints: ['Security review'] },
        behavioral_triggers: [{ signal: 'Compliance requirement', source: 'News', urgency_boost: 70 }],
        buying_committee: [{ role: 'Economic Buyer', typical_title: 'CFO', concerns: ['Risk', 'TCO'], success_criteria: ['Compliance'] }],
        category_context: { market_position: 'newcomer', current_solution: 'Legacy', switching_triggers: ['Compliance mandate'] },
        fit_reasoning: 'Longer sales cycle but high LTV potential',
        messaging_angle: 'Enterprise-grade security and reliability',
        qualification_questions: ['What compliance requirements do you have?']
      }
    ];
  }

  private getFallbackWarPlan(data: any): any {
    return {
      generated: true,
      summary: 'A focused 90-day plan to establish market presence and generate pipeline.',
      phases: [
        {
          id: 1,
          name: 'Discovery & Authority',
          days: '1-30',
          objectives: ['Build thought leadership', 'Establish content foundation', 'Set up tracking'],
          campaigns: ['Authority Blitz', 'Content Waterfall'],
          kpis: [
            { name: 'Content published', target: '8-12 pieces' },
            { name: 'Website traffic', target: '+30%' }
          ],
          key_tasks: ['Create pillar content', 'Set up analytics', 'Launch LinkedIn presence']
        },
        {
          id: 2,
          name: 'Launch & Validation',
          days: '31-60',
          objectives: ['Launch demand gen', 'Build social proof', 'Start outbound'],
          campaigns: ['Trust Anchor', 'Spear Attack'],
          kpis: [
            { name: 'Demo conversion', target: '15%+' },
            { name: 'Pipeline', target: '$100k+' }
          ],
          key_tasks: ['Launch paid campaigns', 'Start outbound', 'Collect testimonials']
        },
        {
          id: 3,
          name: 'Optimization & Scale',
          days: '61-90',
          objectives: ['Double down on winners', 'Kill underperformers', 'Plan Q2'],
          campaigns: ['Expansion Plays', 'Optimization'],
          kpis: [
            { name: 'CAC payback', target: '<12 months' },
            { name: 'Win rate', target: '25%+' }
          ],
          key_tasks: ['Analyze performance', 'Optimize campaigns', 'Plan expansion']
        }
      ],
      protocols: {
        A: { name: 'Authority Blitz', active: true, description: 'Build thought leadership through content' },
        B: { name: 'Trust Anchor', active: true, description: 'Social proof and validation' },
        C: { name: 'Cost of Inaction', active: false, description: 'Fear-based urgency messaging' },
        D: { name: 'Facilitator Nudge', active: true, description: 'Help buyers navigate buying process' },
        E: { name: 'Champions Armory', active: false, description: 'Enable internal champions' },
        F: { name: 'Churn Intercept', active: false, description: 'Retention and expansion plays' }
      },
      recommended_budget_split: {
        content: '30%',
        paid_media: '40%',
        tools: '15%',
        events: '15%'
      }
    };
  }
}

export const orchestrator = new AgentOrchestrator();
