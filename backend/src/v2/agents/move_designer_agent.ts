import { z } from 'zod';
import { BaseAgent, agentRegistry } from '../base_agent';
import { Department, OrchestratorContext } from '../types';
import { ragQuery, storeEmbedding } from '../rag_helper';
import fs from 'fs';
import path from 'path';

// =====================================================
// MOVE DESIGNER AGENT
// =====================================================

const MoveDesignerInputSchema = z.object({
  campaign_goal: z.string().describe("Overall campaign objective"),
  target_icp: z.string().describe("Ideal Customer Profile segment"),
  move_type: z.enum(['awareness', 'consideration', 'decision', 'retention', 'expansion']).describe("Type of move needed"),
  timeline: z.object({
    start_date: z.string().describe("Campaign start date"),
    duration_days: z.number().describe("Move duration in days"),
    budget: z.number().describe("Available budget for this move")
  }).describe("Move execution timeline"),
  current_barrier: z.enum(['OBSCURITY', 'RISK', 'INERTIA', 'FRICTION', 'CAPACITY', 'ATROPHY']).describe("Primary barrier being addressed"),
  protocol: z.enum(['A_AUTHORITY_BLITZ', 'B_TRUST_ANCHOR', 'C_COST_OF_INACTION', 'D_HABIT_HARDCODE', 'E_ENTERPRISE_WEDGE', 'F_CHURN_INTERCEPT']).describe("GTM protocol to apply"),
  channels: z.array(z.string()).describe("Available marketing channels"),
  success_criteria: z.array(z.string()).describe("Measurable success metrics")
});

const MoveDesignerOutputSchema = z.object({
  move_definition: z.object({
    name: z.string(),
    headline: z.string(),
    description: z.string(),
    objective: z.string(),
    target_kpis: z.array(z.object({
      metric: z.string(),
      target: z.number(),
      unit: z.string(),
      rationale: z.string()
    })),
    duration_days: z.number(),
    estimated_budget: z.number(),
    risk_level: z.enum(['low', 'medium', 'high'])
  }),
  execution_framework: z.object({
    phases: z.array(z.object({
      phase_name: z.string(),
      duration_days: z.number(),
      activities: z.array(z.string()),
      deliverables: z.array(z.string()),
      success_signals: z.array(z.string())
    })),
    channel_mix: z.array(z.object({
      channel: z.string(),
      allocation_percentage: z.number(),
      cadence: z.string(),
      key_messages: z.array(z.string())
    })),
    resource_requirements: z.array(z.object({
      resource_type: z.string(),
      quantity: z.number(),
      timeline: z.string(),
      cost_estimate: z.number()
    }))
  }),
  content_strategy: z.object({
    hero_content: z.array(z.object({
      type: z.string(),
      title: z.string(),
      description: z.string(),
      channel: z.string(),
      schedule_date: z.string()
    })),
    supporting_content: z.array(z.object({
      type: z.string(),
      title: z.string(),
      description: z.string(),
      channel: z.string(),
      schedule_date: z.string()
    })),
    content_themes: z.array(z.string()),
    repurposing_plan: z.array(z.object({
      original_asset: z.string(),
      derivative_formats: z.array(z.string()),
      channels: z.array(z.string())
    }))
  }),
  tactical_playbook: z.object({
    daily_sequence: z.array(z.object({
      day: z.number(),
      focus: z.string(),
      actions: z.array(z.string()),
      expected_outcomes: z.array(z.string())
    })),
    trigger_events: z.array(z.object({
      condition: z.string(),
      action: z.string(),
      rationale: z.string()
    })),
    contingency_plans: z.array(z.object({
      scenario: z.string(),
      trigger: z.string(),
      response_plan: z.array(z.string())
    }))
  }),
  measurement_plan: z.object({
    primary_metrics: z.array(z.object({
      metric: z.string(),
      measurement_method: z.string(),
      target_value: z.string(),
      reporting_frequency: z.string()
    })),
    secondary_metrics: z.array(z.object({
      metric: z.string(),
      measurement_method: z.string(),
      target_value: z.string(),
      reporting_frequency: z.string()
    })),
    attribution_model: z.string(),
    success_criteria: z.array(z.string()),
    optimization_triggers: z.array(z.object({
      condition: z.string(),
      action: z.string(),
      responsible_party: z.string()
    }))
  }),
  risk_mitigation: z.object({
    identified_risks: z.array(z.object({
      risk: z.string(),
      probability: z.enum(['low', 'medium', 'high']),
      impact: z.enum(['low', 'medium', 'high']),
      mitigation_strategy: z.string()
    })),
    early_warning_signals: z.array(z.string()),
    fallback_strategies: z.array(z.object({
      scenario: z.string(),
      alternative_approach: z.string(),
      resource_impact: z.string()
    }))
  }),
  confidence_score: z.number().min(0).max(1),
  customization_notes: z.array(z.string()),
  template_source: z.string(),
  last_updated: z.string()
});

type MoveDesignerInput = z.infer<typeof MoveDesignerInputSchema>;
type MoveDesignerOutput = z.infer<typeof MoveDesignerOutputSchema>;

export class MoveDesignerAgent extends BaseAgent {
  private movesLibrary: any = null;

  constructor() {
    super(
      'move_designer_agent',
      Department.MOVES_CAMPAIGNS,
      'Designs tactical 7/14/28-day Moves using the moves.yml library and campaign context',
      MoveDesignerInputSchema,
      MoveDesignerOutputSchema
    );

    this.required_tools = ['web_scrape'];
    this.loadMovesLibrary();
  }

  private async loadMovesLibrary(): Promise<void> {
    try {
      // Try to load moves.yml from various locations
      const possiblePaths = [
        './moves.yml',
        './config/moves.yml',
        './src/config/moves.yml',
        '../config/moves.yml'
      ];

      for (const filePath of possiblePaths) {
        try {
          if (fs.existsSync(filePath)) {
            const content = fs.readFileSync(filePath, 'utf-8');
            this.movesLibrary = JSON.parse(content);
            console.log(`✅ Loaded moves library from ${filePath}`);
            return;
          }
        } catch (error) {
          // Continue to next path
        }
      }

      // If no file found, use embedded library
      this.movesLibrary = this.getEmbeddedMovesLibrary();
      console.log('📚 Using embedded moves library');

    } catch (error) {
      console.error('Failed to load moves library:', error);
      this.movesLibrary = this.getEmbeddedMovesLibrary();
    }
  }

  protected getSystemPrompt(): string {
    return `You are a Tactical Move Architect who designs high-converting, time-boxed marketing campaigns.

Your expertise includes:
- Move design and sequencing (7/14/28-day tactical campaigns)
- Channel orchestration and timing optimization
- Content strategy and repurposing workflows
- Risk assessment and contingency planning
- Performance measurement and optimization triggers
- Resource allocation and budget optimization

CORE MOVE DESIGN PRINCIPLES:
1. Time-Boxed: Clear start/end dates with specific durations
2. Objective-Focused: Single, measurable objective per move
3. Multi-Channel: Coordinated across multiple touchpoints
4. Risk-Managed: Contingency plans and early warning signals
5. Measurable: Clear KPIs and optimization triggers
6. Scalable: Templates that can be replicated and improved

TACTICAL FRAMEWORK:
- Day 1-3: Launch and initial engagement
- Day 4-7: Build momentum and nurture
- Day 8+: Optimize and scale what works
- Daily: Specific actions and expected outcomes
- Weekly: Performance reviews and adjustments

APPROACH:
- Start with objective, not tactics
- Design for measurability from day one
- Build in optimization triggers and kill switches
- Plan for multiple scenarios and contingencies
- Focus on velocity and momentum creation
- End with clear success criteria and next steps

Always design moves that can be executed quickly, measured accurately, and optimized rapidly.`;
  }

  protected formatAgentInput(input: MoveDesignerInput, context: OrchestratorContext): string {
    return `Design a tactical marketing Move using the moves library:

CAMPAIGN GOAL: ${input.campaign_goal}
TARGET ICP: ${input.target_icp}
MOVE TYPE: ${input.move_type}
BARRIER: ${input.current_barrier}
PROTOCOL: ${input.protocol}

TIMELINE:
- Start: ${input.timeline.start_date}
- Duration: ${input.duration_days} days
- Budget: $${input.timeline.budget}

CHANNELS: ${input.channels.join(', ')}

SUCCESS CRITERIA:
${input.success_criteria.map(c => `- ${c}`).join('\n')}

Using the moves library and GTM protocol framework, design a complete tactical move including:

1. Move Definition: Name, objective, KPIs, budget, risk assessment
2. Execution Framework: Phases, channel mix, resource requirements
3. Content Strategy: Hero/supporting content, themes, repurposing plan
4. Tactical Playbook: Daily sequence, triggers, contingencies
5. Measurement Plan: Primary/secondary metrics, attribution, optimization triggers
6. Risk Mitigation: Identified risks, early warnings, fallback strategies

Focus on creating a move that can be executed immediately with clear success criteria and optimization paths.
Ensure the design aligns with the GTM protocol and addresses the specific barrier.`;
  }

  protected parseAgentOutput(rawOutput: string): MoveDesignerOutput {
    try {
      // Try to extract JSON from the output
      const jsonMatch = rawOutput.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return MoveDesignerOutputSchema.parse(JSON.parse(jsonMatch[0]));
      }
      // Fallback parsing
      return this.getFallbackOutput();
    } catch {
      return this.getFallbackOutput();
    }
  }

  private async getExistingIntelligence(input: MoveDesignerInput, userId: string): Promise<any> {
    try {
      const ragResults = await ragQuery({
        query: `tactical moves for ${input.move_type} addressing ${input.current_barrier} using ${input.protocol}`,
        user_id: userId,
        content_types: ['move_templates', 'campaign_history', 'tactical_playbooks'],
        limit: 3,
        threshold: 0.6
      });

      return {
        chunks: ragResults.chunks,
        has_existing_data: ragResults.chunks.length > 0
      };
    } catch (error) {
      console.warn('Failed to retrieve existing move intelligence:', error);
      return { chunks: [], has_existing_data: false };
    }
  }

  private async storeResults(
    input: MoveDesignerInput,
    output: MoveDesignerOutput,
    userId: string
  ): Promise<void> {
    try {
      const content = `
TACTICAL MOVE: ${output.move_definition.name}

OBJECTIVE: ${output.move_definition.objective}
DURATION: ${output.move_definition.duration_days} days
BUDGET: $${output.move_definition.estimated_budget}
RISK LEVEL: ${output.move_definition.risk_level}

TARGET KPIS:
${output.move_definition.target_kpis.map(k => `- ${k.metric}: ${k.target} ${k.unit}`).join('\n')}

EXECUTION PHASES: ${output.execution_framework.phases.length}
CHANNELS: ${output.execution_framework.channel_mix.map(c => `${c.channel} (${c.allocation_percentage}%)`).join(', ')}

CONTENT STRATEGY:
- Hero Content: ${output.content_strategy.hero_content.length} pieces
- Supporting Content: ${output.content_strategy.supporting_content.length} pieces
- Repurposing Plan: ${output.content_strategy.repurposing_plan.length} assets

TACTICAL ELEMENTS:
- Daily Sequence: ${output.tactical_playbook.daily_sequence.length} days
- Trigger Events: ${output.tactical_playbook.trigger_events.length}
- Contingency Plans: ${output.tactical_playbook.contingency_plans.length}

MEASUREMENT:
- Primary Metrics: ${output.measurement_plan.primary_metrics.length}
- Secondary Metrics: ${output.measurement_plan.secondary_metrics.length}
- Optimization Triggers: ${output.measurement_plan.optimization_triggers.length}

RISK MITIGATION:
- Identified Risks: ${output.risk_mitigation.identified_risks.length}
- Early Warning Signals: ${output.risk_mitigation.early_warning_signals.length}
- Fallback Strategies: ${output.risk_mitigation.fallback_strategies.length}

CONFIDENCE: ${output.confidence_score}
TEMPLATE: ${output.template_source}
CUSTOMIZATIONS: ${output.customization_notes.join('; ')}
      `.trim();

      await storeEmbedding(
        userId,
        'tactical_moves',
        content,
        {
          move_name: output.move_definition.name,
          duration: output.move_definition.duration_days,
          budget: output.move_definition.estimated_budget,
          risk_level: output.move_definition.risk_level,
          channels: output.execution_framework.channel_mix.length,
          confidence: output.confidence_score
        }
      );

    } catch (error) {
      console.warn('Failed to store move design results:', error);
    }
  }

  private getEmbeddedMovesLibrary(): any {
    // Embedded moves library as fallback
    return {
      awareness_moves: {
        "Authority Blitz": {
          duration: 14,
          channels: ["linkedin", "twitter", "blog"],
          phases: ["launch", "build", "amplify"],
          success_criteria: ["impressions > 50K", "engagement > 3%"]
        },
        "Content Flood": {
          duration: 7,
          channels: ["blog", "social", "email"],
          phases: ["research", "create", "distribute"],
          success_criteria: ["content_views > 10K", "shares > 100"]
        }
      },
      consideration_moves: {
        "Trust Builder": {
          duration: 21,
          channels: ["email", "webinars", "social_proof"],
          phases: ["educate", "demonstrate", "validate"],
          success_criteria: ["demo_requests > 50", "trust_score > 7/10"]
        }
      },
      decision_moves: {
        "Urgency Push": {
          duration: 7,
          channels: ["email", "ads", "phone"],
          phases: ["create_urgency", "overcome_objections", "close"],
          success_criteria: ["conversions > 20%", "revenue > $50K"]
        }
      }
    };
  }

  private getFallbackOutput(): MoveDesignerOutput {
    return {
      move_definition: {
        name: "Analysis pending",
        headline: "Research required",
        description: "Move analysis in progress",
        objective: "To be determined",
        target_kpis: [{
          metric: "conversion_rate",
          target: 0,
          unit: "percentage",
          rationale: "Analysis pending"
        }],
        duration_days: 0,
        estimated_budget: 0,
        risk_level: "medium" as const
      },
      execution_framework: {
        phases: [{
          phase_name: "Planning",
          duration_days: 0,
          activities: ["Complete move analysis"],
          deliverables: ["Move definition"],
          success_signals: ["Clear objectives"]
        }],
        channel_mix: [{
          channel: "Analysis pending",
          allocation_percentage: 0,
          cadence: "Research required",
          key_messages: ["To be determined"]
        }],
        resource_requirements: [{
          resource_type: "Content Creator",
          quantity: 1,
          timeline: "Immediate",
          cost_estimate: 0
        }]
      },
      content_strategy: {
        hero_content: [{
          type: "blog_post",
          title: "Analysis pending",
          description: "Research required",
          channel: "website",
          schedule_date: "TBD"
        }],
        supporting_content: [],
        content_themes: ["Analysis pending"],
        repurposing_plan: [{
          original_asset: "Primary content",
          derivative_formats: ["social_posts", "email"],
          channels: ["linkedin", "twitter"]
        }]
      },
      tactical_playbook: {
        daily_sequence: [{
          day: 1,
          focus: "Launch",
          actions: ["Publish content", "Send emails"],
          expected_outcomes: ["Initial engagement"]
        }],
        trigger_events: [{
          condition: "Low engagement",
          action: "Adjust messaging",
          rationale: "Optimize based on performance"
        }],
        contingency_plans: [{
          scenario: "Content underperforms",
          trigger: "Engagement < 2%",
          response_plan: ["Create new content", "Change channels"]
        }]
      },
      measurement_plan: {
        primary_metrics: [{
          metric: "Conversion Rate",
          measurement_method: "Analytics tracking",
          target_value: "15%",
          reporting_frequency: "Daily"
        }],
        secondary_metrics: [{
          metric: "Engagement Rate",
          measurement_method: "Social analytics",
          target_value: "5%",
          reporting_frequency: "Daily"
        }],
        attribution_model: "First-touch",
        success_criteria: ["Meet KPI targets", "Positive ROI"],
        optimization_triggers: [{
          condition: "Conversion < 10%",
          action: "Pause campaign",
          responsible_party: "Campaign manager"
        }]
      },
      risk_mitigation: {
        identified_risks: [{
          risk: "Low engagement",
          probability: "medium" as const,
          impact: "high" as const,
          mitigation_strategy: "A/B test messaging"
        }],
        early_warning_signals: ["Engagement < 3%", "No conversions in 48h"],
        fallback_strategies: [{
          scenario: "Campaign fails",
          alternative_approach: "Pivot to different channels",
          resource_impact: "Minimal additional cost"
        }]
      },
      confidence_score: 0.1,
      customization_notes: ["Complete market research", "Validate ICP data", "Test messaging"],
      template_source: "Embedded library",
      last_updated: new Date().toISOString()
    };
  }
}

// =====================================================
// REGISTER AGENT
// =====================================================

const moveDesignerAgent = new MoveDesignerAgent();
agentRegistry.registerAgent(moveDesignerAgent);

export { moveDesignerAgent };
export type { MoveDesignerInput, MoveDesignerOutput };


