import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModel } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";
import type { 
  ICP, 
  ProtocolType, 
  BarrierType, 
  MoveTemplate, 
  Move, 
  MoveTask,
  CreateMoveInput 
} from "../types";
import { v4 as uuidv4 } from 'uuid';

// =====================================================
// INPUT/OUTPUT SCHEMAS
// =====================================================

export interface MoveAssemblyInput {
  campaign: {
    id: string;
    name: string;
    goal: string;
    demand_source: string;
    persuasion_axis: string;
  };
  icp: ICP;
  barrier: BarrierType;
  protocol: ProtocolType;
  template?: MoveTemplate;
  budget?: number;
  timeframe?: {
    start: string;
    end: string;
  };
}

const moveOutputSchema = z.object({
  move: z.object({
    name: z.string(),
    description: z.string(),
    customized_for_icp: z.string(),
    channels: z.array(z.string()),
    tasks: z.array(z.object({
      task: z.string(),
      category: z.string(),
      estimated_hours: z.number(),
      priority: z.enum(["high", "medium", "low"]),
      dependencies: z.array(z.string()).optional()
    })),
    kpis: z.array(z.object({
      metric: z.string(),
      target: z.number(),
      unit: z.string(),
      rationale: z.string()
    })),
    assets_needed: z.array(z.object({
      type: z.string(),
      description: z.string(),
      priority: z.enum(["must_have", "nice_to_have"])
    })),
    messaging_hooks: z.array(z.string()),
    estimated_impact: z.number().min(0).max(100),
    estimated_effort: z.number().min(0).max(100),
    risk_factors: z.array(z.string()),
    success_criteria: z.string()
  }),
  execution_timeline: z.object({
    setup_days: z.number(),
    run_days: z.number(),
    review_days: z.number()
  }),
  budget_allocation: z.object({
    content: z.number(),
    paid_media: z.number(),
    tools: z.number(),
    other: z.number()
  }).optional()
});

export type MoveAssemblyOutput = z.infer<typeof moveOutputSchema>;

// =====================================================
// MOVE ASSEMBLY AGENT
// =====================================================

export class MoveAssemblyAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    this.model = getLangChainModel("gemini-pro");
    this.parser = StructuredOutputParser.fromZodSchema(moveOutputSchema);
    this.prompt = new PromptTemplate({
      template: `You are a GTM Move architect. Create a customized tactical move for this specific campaign and ICP.

## Campaign Context
- Name: {campaign_name}
- Goal: {goal} ({goal_description})
- Demand Source: {demand_source}
- Persuasion Axis: {persuasion_axis}

## Target ICP: {icp_label}
{icp_details}

## Barrier Being Addressed: {barrier}
{barrier_description}

## Protocol: {protocol}
{protocol_description}

## Move Template (if provided)
{template_info}

## Timeframe
{timeframe}

## Your Task
Create a customized move that:
1. Addresses the specific barrier for this ICP
2. Aligns with the campaign goal and persuasion axis
3. Includes specific, actionable tasks
4. Defines measurable KPIs with realistic targets
5. Lists required assets with priorities
6. Provides messaging hooks specific to this ICP's pain points
7. Estimates impact and effort realistically

The move should be immediately actionable - someone should be able to execute it without additional clarification.

{format_instructions}`,
      inputVariables: [
        "campaign_name", "goal", "goal_description", "demand_source", "persuasion_axis",
        "icp_label", "icp_details", "barrier", "barrier_description",
        "protocol", "protocol_description", "template_info", "timeframe"
      ],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  /**
   * Assemble a customized move from inputs
   */
  async assemble(input: MoveAssemblyInput): Promise<MoveAssemblyOutput> {
    const goalDescriptions: Record<string, string> = {
      velocity: "Maximize growth speed, accept higher CAC",
      efficiency: "Optimize unit economics, slower but profitable growth",
      penetration: "Maximize market share, heavy brand investment"
    };

    const barrierDescriptions: Record<BarrierType, string> = {
      OBSCURITY: "Prospects don't know you exist - need awareness and discovery",
      RISK: "Prospects know you but don't trust you - need proof and validation",
      INERTIA: "Prospects trust you but aren't urgent - need to create urgency",
      FRICTION: "Users signed up but not activated - need onboarding help",
      CAPACITY: "Users active but not expanding - need expansion triggers",
      ATROPHY: "Users showing churn signals - need retention intervention"
    };

    const protocolDescriptions: Record<ProtocolType, string> = {
      A_AUTHORITY_BLITZ: "Build thought leadership through content-first demand creation",
      B_TRUST_ANCHOR: "Build credibility through social proof and validation",
      C_COST_OF_INACTION: "Create urgency through consequences of delay",
      D_HABIT_HARDCODE: "Drive activation through progressive onboarding",
      E_ENTERPRISE_WEDGE: "Expand within accounts through champion enablement",
      F_CHURN_INTERCEPT: "Prevent churn through early intervention"
    };

    try {
      const chain = this.prompt.pipe(this.model).pipe(this.parser);
      const result = await chain.invoke({
        campaign_name: input.campaign.name,
        goal: input.campaign.goal,
        goal_description: goalDescriptions[input.campaign.goal] || "",
        demand_source: input.campaign.demand_source,
        persuasion_axis: input.campaign.persuasion_axis,
        icp_label: input.icp.label,
        icp_details: this.formatICPDetails(input.icp),
        barrier: input.barrier,
        barrier_description: barrierDescriptions[input.barrier],
        protocol: input.protocol,
        protocol_description: protocolDescriptions[input.protocol],
        template_info: input.template ? this.formatTemplateInfo(input.template) : "No template provided - create from scratch",
        timeframe: input.timeframe 
          ? `Start: ${input.timeframe.start}, End: ${input.timeframe.end}`
          : "Flexible - optimize for 30-day execution"
      });
      
      return result as MoveAssemblyOutput;
    } catch (error: any) {
      console.error('MoveAssemblyAgent error:', error);
      return this.getFallbackMove(input);
    }
  }

  /**
   * Convert output to database-ready format
   */
  toCreateInput(output: MoveAssemblyOutput, input: MoveAssemblyInput): CreateMoveInput & { tasks: MoveTask[], kpis: Record<string, any> } {
    const tasks: MoveTask[] = output.move.tasks.map((t, i) => ({
      id: uuidv4(),
      task: t.task,
      status: 'pending' as const,
      due_date: undefined,
      completed_at: undefined
    }));

    const kpis = output.move.kpis.reduce((acc, kpi) => {
      acc[kpi.metric] = { target: kpi.target, unit: kpi.unit };
      return acc;
    }, {} as Record<string, any>);

    // Calculate EV score
    const ev_score = (output.move.estimated_impact * 0.5) / Math.max(output.move.estimated_effort, 1);

    return {
      name: output.move.name,
      description: output.move.description,
      campaign_id: input.campaign.id,
      icp_id: input.icp.id,
      template_id: input.template?.id,
      protocol: input.protocol,
      channels: output.move.channels,
      tasks,
      kpis,
      impact_score: output.move.estimated_impact,
      effort_score: output.move.estimated_effort,
      ev_score,
      planned_start: input.timeframe?.start,
      planned_end: input.timeframe?.end
    } as any;
  }

  /**
   * Generate multiple moves for a campaign
   */
  async assembleBatch(
    campaign: MoveAssemblyInput['campaign'],
    icps: ICP[],
    barriers: BarrierType[],
    protocols: ProtocolType[],
    templates?: MoveTemplate[]
  ): Promise<MoveAssemblyOutput[]> {
    const moves: MoveAssemblyOutput[] = [];
    
    // Generate a move for each ICP + protocol combination
    for (const icp of icps) {
      // Find primary barrier for this ICP
      const icpBarrier = icp.primary_barriers?.[0] || barriers[0];
      
      // Get protocol for this barrier
      const protocolForBarrier = protocols.find(p => {
        const barrierProtocolMap: Record<BarrierType, ProtocolType> = {
          OBSCURITY: 'A_AUTHORITY_BLITZ',
          RISK: 'B_TRUST_ANCHOR',
          INERTIA: 'C_COST_OF_INACTION',
          FRICTION: 'D_HABIT_HARDCODE',
          CAPACITY: 'E_ENTERPRISE_WEDGE',
          ATROPHY: 'F_CHURN_INTERCEPT'
        };
        return p === barrierProtocolMap[icpBarrier];
      }) || protocols[0];
      
      // Find matching template
      const template = templates?.find(t => t.protocol_type === protocolForBarrier);
      
      try {
        const move = await this.assemble({
          campaign,
          icp,
          barrier: icpBarrier,
          protocol: protocolForBarrier,
          template
        });
        moves.push(move);
      } catch (error) {
        console.error(`Failed to generate move for ICP ${icp.label}:`, error);
      }
    }
    
    return moves;
  }

  /**
   * Format ICP details for prompt
   */
  private formatICPDetails(icp: ICP): string {
    return `
Summary: ${icp.summary}
Firmographics: ${JSON.stringify(icp.firmographics)}
Pain Points: ${icp.psychographics?.pain_points?.join(', ') || 'Unknown'}
Motivations: ${icp.psychographics?.motivations?.join(', ') || 'Unknown'}
Internal Triggers: ${icp.psychographics?.internal_triggers?.join(', ') || 'Unknown'}
Buying Constraints: ${icp.psychographics?.buying_constraints?.join(', ') || 'Unknown'}
Risk Tolerance: ${icp.psychographics?.risk_tolerance || 'medium'}
Messaging Angle: ${icp.messaging_angle || 'Not specified'}
    `.trim();
  }

  /**
   * Format template info for prompt
   */
  private formatTemplateInfo(template: MoveTemplate): string {
    return `
Template: ${template.name}
Description: ${template.description}
Channels: ${template.channels.join(', ')}
Standard Tasks: ${template.task_template.map(t => t.task).join('; ')}
Success Metrics: ${template.success_metrics.map(m => `${m.metric}: ${m.target} ${m.unit}`).join(', ')}
    `.trim();
  }

  /**
   * Fallback move when LLM fails
   */
  private getFallbackMove(input: MoveAssemblyInput): MoveAssemblyOutput {
    const fallbackMoves: Record<ProtocolType, MoveAssemblyOutput['move']> = {
      A_AUTHORITY_BLITZ: {
        name: `Authority Blitz for ${input.icp.label}`,
        description: `Build thought leadership and awareness among ${input.icp.label} segment through content-first approach.`,
        customized_for_icp: input.icp.label,
        channels: ['linkedin_organic', 'youtube', 'newsletter'],
        tasks: [
          { task: 'Research and outline pillar content topic', category: 'planning', estimated_hours: 4, priority: 'high' },
          { task: 'Create pillar content piece (webinar/guide)', category: 'creation', estimated_hours: 12, priority: 'high' },
          { task: 'Extract 20 micro-content pieces', category: 'creation', estimated_hours: 6, priority: 'medium' },
          { task: 'Schedule content distribution', category: 'distribution', estimated_hours: 2, priority: 'medium' }
        ],
        kpis: [
          { metric: 'impressions', target: 50000, unit: 'total', rationale: 'Build awareness' },
          { metric: 'engagement_rate', target: 3, unit: 'percentage', rationale: 'Measure resonance' }
        ],
        assets_needed: [
          { type: 'pillar_content', description: 'Main webinar or guide', priority: 'must_have' },
          { type: 'social_posts', description: '20 micro-content pieces', priority: 'must_have' }
        ],
        messaging_hooks: [
          `For ${input.icp.label}s struggling with ${input.icp.psychographics?.pain_points?.[0] || 'growth'}`,
          'The hidden cost of the status quo',
          'What top performers do differently'
        ],
        estimated_impact: 70,
        estimated_effort: 60,
        risk_factors: ['Content may not resonate', 'Algorithm changes'],
        success_criteria: '50K+ impressions with 3%+ engagement rate'
      },
      B_TRUST_ANCHOR: {
        name: `Trust Anchor for ${input.icp.label}`,
        description: `Build credibility and trust through social proof and validation for ${input.icp.label} segment.`,
        customized_for_icp: input.icp.label,
        channels: ['website', 'retargeting', 'email'],
        tasks: [
          { task: 'Create comparison page vs competitors', category: 'content', estimated_hours: 8, priority: 'high' },
          { task: 'Build ROI calculator', category: 'tools', estimated_hours: 16, priority: 'high' },
          { task: 'Collect and deploy testimonials', category: 'social_proof', estimated_hours: 6, priority: 'high' },
          { task: 'Set up retargeting campaign', category: 'paid', estimated_hours: 4, priority: 'medium' }
        ],
        kpis: [
          { metric: 'demo_conversion_rate', target: 20, unit: 'percentage', rationale: 'Measure trust building' },
          { metric: 'pricing_page_conversion', target: 5, unit: 'percentage', rationale: 'Track high-intent conversion' }
        ],
        assets_needed: [
          { type: 'comparison_page', description: 'Us vs competitors breakdown', priority: 'must_have' },
          { type: 'roi_calculator', description: 'Interactive value calculator', priority: 'must_have' },
          { type: 'testimonials', description: 'Customer quotes and logos', priority: 'must_have' }
        ],
        messaging_hooks: [
          `Why ${input.icp.label}s choose us over the alternative`,
          'See the ROI in 2 minutes',
          'Trusted by companies like yours'
        ],
        estimated_impact: 75,
        estimated_effort: 70,
        risk_factors: ['May need more testimonials', 'Calculator assumptions'],
        success_criteria: '20%+ demo conversion from retargeting'
      },
      C_COST_OF_INACTION: {
        name: `Urgency Campaign for ${input.icp.label}`,
        description: `Create urgency and overcome inertia for ${input.icp.label} segment through consequence-based messaging.`,
        customized_for_icp: input.icp.label,
        channels: ['email', 'linkedin_dm', 'abm'],
        tasks: [
          { task: 'Create wake-up report on industry trends', category: 'content', estimated_hours: 10, priority: 'high' },
          { task: 'Build cost-of-delay calculator', category: 'tools', estimated_hours: 8, priority: 'high' },
          { task: 'Design time-sensitive offer', category: 'campaign', estimated_hours: 4, priority: 'medium' },
          { task: 'Execute targeted outreach', category: 'outreach', estimated_hours: 8, priority: 'high' }
        ],
        kpis: [
          { metric: 'reactivation_rate', target: 15, unit: 'percentage', rationale: 'Measure urgency creation' },
          { metric: 'deal_velocity', target: 20, unit: 'percentage_improvement', rationale: 'Track cycle compression' }
        ],
        assets_needed: [
          { type: 'wake_up_report', description: 'Industry trends and consequences', priority: 'must_have' },
          { type: 'cost_calculator', description: 'Cost of delay calculator', priority: 'must_have' }
        ],
        messaging_hooks: [
          `What ${input.icp.label}s lose every month they wait`,
          'Your competitors aren\'t waiting',
          'The market is moving - are you?'
        ],
        estimated_impact: 65,
        estimated_effort: 55,
        risk_factors: ['May feel too pushy', 'Timing dependent'],
        success_criteria: '15%+ stalled deal reactivation'
      },
      D_HABIT_HARDCODE: {
        name: `Activation Push for ${input.icp.label}`,
        description: `Drive activation and habit formation for ${input.icp.label} segment users.`,
        customized_for_icp: input.icp.label,
        channels: ['in_app', 'email', 'push'],
        tasks: [
          { task: 'Define activation event for this ICP', category: 'analytics', estimated_hours: 4, priority: 'high' },
          { task: 'Create onboarding email sequence', category: 'lifecycle', estimated_hours: 8, priority: 'high' },
          { task: 'Build in-app progress tracker', category: 'product', estimated_hours: 12, priority: 'medium' },
          { task: 'Set up milestone celebrations', category: 'product', estimated_hours: 4, priority: 'low' }
        ],
        kpis: [
          { metric: 'activation_rate', target: 60, unit: 'percentage', rationale: 'Core success metric' },
          { metric: 'time_to_value', target: 3, unit: 'days', rationale: 'Speed to value' }
        ],
        assets_needed: [
          { type: 'email_sequence', description: '7-day onboarding emails', priority: 'must_have' },
          { type: 'in_app_guides', description: 'Interactive walkthroughs', priority: 'must_have' }
        ],
        messaging_hooks: [
          'Your first win is 3 steps away',
          'Most successful users do this first',
          'You\'re ahead of 80% of new users'
        ],
        estimated_impact: 70,
        estimated_effort: 65,
        risk_factors: ['Requires product integration', 'May need A/B testing'],
        success_criteria: '60%+ activation rate within 7 days'
      },
      E_ENTERPRISE_WEDGE: {
        name: `Expansion Play for ${input.icp.label}`,
        description: `Drive expansion and upsells within ${input.icp.label} segment accounts.`,
        customized_for_icp: input.icp.label,
        channels: ['customer_success', 'email', 'in_app'],
        tasks: [
          { task: 'Identify expansion-ready accounts', category: 'analytics', estimated_hours: 4, priority: 'high' },
          { task: 'Create business case PDF generator', category: 'tools', estimated_hours: 16, priority: 'high' },
          { task: 'Build QBR deck template', category: 'sales_enablement', estimated_hours: 8, priority: 'high' },
          { task: 'Launch expansion outreach', category: 'customer_success', estimated_hours: 8, priority: 'medium' }
        ],
        kpis: [
          { metric: 'expansion_rate', target: 25, unit: 'percentage', rationale: 'Core expansion metric' },
          { metric: 'nrr', target: 115, unit: 'percentage', rationale: 'Overall retention health' }
        ],
        assets_needed: [
          { type: 'business_case_pdf', description: 'Boss-forwardable document', priority: 'must_have' },
          { type: 'qbr_deck', description: 'Quarterly review template', priority: 'must_have' }
        ],
        messaging_hooks: [
          'Your team is outgrowing your current plan',
          'Unlock these features your power users want',
          'Your success makes the case'
        ],
        estimated_impact: 80,
        estimated_effort: 70,
        risk_factors: ['Requires CS coordination', 'Champion may not exist'],
        success_criteria: '25%+ expansion rate from targeted accounts'
      },
      F_CHURN_INTERCEPT: {
        name: `Churn Prevention for ${input.icp.label}`,
        description: `Intercept and prevent churn for at-risk ${input.icp.label} segment accounts.`,
        customized_for_icp: input.icp.label,
        channels: ['email', 'in_app', 'phone'],
        tasks: [
          { task: 'Set up churn prediction alerts', category: 'analytics', estimated_hours: 8, priority: 'high' },
          { task: 'Create loss aversion email sequence', category: 'lifecycle', estimated_hours: 6, priority: 'high' },
          { task: 'Build pause plan option', category: 'product', estimated_hours: 8, priority: 'high' },
          { task: 'Train CS team on save playbook', category: 'enablement', estimated_hours: 4, priority: 'medium' }
        ],
        kpis: [
          { metric: 'save_rate', target: 30, unit: 'percentage', rationale: 'Core retention metric' },
          { metric: 'churn_rate', target: 5, unit: 'percentage_max', rationale: 'Overall churn health' }
        ],
        assets_needed: [
          { type: 'email_sequence', description: '5-touch save sequence', priority: 'must_have' },
          { type: 'pause_page', description: 'Alternative to cancel', priority: 'must_have' }
        ],
        messaging_hooks: [
          'We noticed you haven\'t been around lately',
          'Here\'s what you\'ll lose if you leave',
          'Take a break, don\'t break up'
        ],
        estimated_impact: 75,
        estimated_effort: 55,
        risk_factors: ['May be too late for some', 'Requires early detection'],
        success_criteria: '30%+ save rate from triggered accounts'
      }
    };

    const move = fallbackMoves[input.protocol] || fallbackMoves.A_AUTHORITY_BLITZ;

    return {
      move,
      execution_timeline: {
        setup_days: 7,
        run_days: 21,
        review_days: 3
      },
      budget_allocation: {
        content: 40,
        paid_media: 30,
        tools: 20,
        other: 10
      }
    };
  }
}
