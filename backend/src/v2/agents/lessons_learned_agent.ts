import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class LessonsLearnedAgent extends BaseAgent {
  department = Department.ANALYTICS;
  name = 'lessons_learned_agent';
  description = 'Writes actionable retrospectives per Move with patterns and improvements';

  protected getSystemPrompt(): string {
    return `You are a senior organizational learning specialist and retrospective facilitator with 15+ years experience in continuous improvement and knowledge management.

Your expertise includes:
- Retrospective facilitation and lessons learned capture
- Pattern recognition across initiatives and campaigns
- Root cause analysis and systemic issue identification
- Knowledge management and organizational learning
- Change management and process improvement

You understand:
1. Organizational psychology and team dynamics
2. Systems thinking and interconnected process analysis
3. Statistical analysis and trend identification
4. Communication and stakeholder management
5. Implementation planning and change adoption

Your role is to analyze campaign performance, identify patterns, and create actionable recommendations that improve future marketing effectiveness.

Focus on:
- Systemic pattern identification and root cause analysis
- Actionable recommendations with clear ownership
- Cross-initiative learning and knowledge transfer
- Process improvement and efficiency gains
- Organizational capability building

You have facilitated learning processes that improved organizational performance by 40%+ and prevented million-dollar mistakes through proactive pattern recognition.`;
  }

  inputSchema = z.object({
    move_data: z.object({
      move_id: z.string(),
      objective: z.string(),
      duration: z.number(),
      budget: z.number(),
      results: z.record(z.any()),
      challenges: z.array(z.string()),
      successes: z.array(z.string())
    }),
    stakeholder_feedback: z.array(z.string()),
    performance_data: z.record(z.any()),
    comparative_analysis: z.record(z.any())
  });

  outputSchema = z.object({
    retrospective_report: z.object({
      executive_summary: z.string(),
      objective_assessment: z.object({
        goal_achievement: z.string(),
        kpi_performance: z.record(z.string()),
        stakeholder_satisfaction: z.string()
      }),
      key_learnings: z.array(z.object({
        learning_type: z.enum(['success', 'failure', 'insight', 'warning']),
        description: z.string(),
        evidence: z.string(),
        impact_assessment: z.string()
      })),
      process_improvements: z.array(z.object({
        improvement_area: z.string(),
        current_state: z.string(),
        proposed_change: z.string(),
        expected_benefit: z.string(),
        implementation_priority: z.enum(['high', 'medium', 'low'])
      }))
    }),
    pattern_identification: z.object({
      success_patterns: z.array(z.string()),
      failure_patterns: z.array(z.string()),
      contextual_factors: z.array(z.string()),
      predictive_indicators: z.array(z.string())
    }),
    future_application: z.object({
      similar_scenarios: z.array(z.string()),
      modified_approaches: z.array(z.string()),
      preventive_measures: z.array(z.string()),
      scaling_opportunities: z.array(z.string())
    }),
    knowledge_base_updates: z.array(z.object({
      update_type: z.enum(['best_practice', 'cautionary_tale', 'methodology_update', 'tool_recommendation']),
      title: z.string(),
      content: z.string(),
      applicability: z.array(z.string())
    }))
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const prompt = `Create comprehensive lessons learned retrospective from marketing campaign execution.`;
    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);
    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    return {
      retrospective_report: {
        executive_summary: '',
        objective_assessment: {
          goal_achievement: '',
          kpi_performance: {},
          stakeholder_satisfaction: ''
        },
        key_learnings: [],
        process_improvements: []
      },
      pattern_identification: {
        success_patterns: [],
        failure_patterns: [],
        contextual_factors: [],
        predictive_indicators: []
      },
      future_application: {
        similar_scenarios: [],
        modified_approaches: [],
        preventive_measures: [],
        scaling_opportunities: []
      },
      knowledge_base_updates: []
    };
  }
}
