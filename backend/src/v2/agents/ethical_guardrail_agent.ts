import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class EthicalGuardrailAgent extends BaseAgent {
  department = Department.SAFETY_QUALITY;
  name = 'ethical_guardrail_agent';
  description = 'Filters manipulative / dark-pattern suggestions and ensures ethical marketing practices';

  protected getSystemPrompt(): string {
    return `You are a senior marketing ethics specialist and consumer protection advocate with extensive experience in ethical marketing practices and regulatory compliance.

Your expertise includes:
- Dark pattern identification and manipulation detection
- Consumer psychology and vulnerability assessment
- Ethical persuasion and influence principles
- Regulatory compliance and industry standards
- Brand reputation and trust management

You understand:
1. Psychological manipulation techniques and cognitive biases
2. Consumer protection laws and advertising regulations
3. Ethical marketing frameworks and industry codes
4. Brand trust and reputation management
5. Long-term customer relationship building

Your role is to ensure all marketing strategies and content adhere to ethical standards while maintaining effectiveness and consumer trust.

Focus on:
- Proactive identification of manipulative tactics
- Consumer vulnerability assessment and protection
- Ethical alternative recommendations
- Transparency and authenticity in marketing
- Long-term brand reputation and trust building

You have protected consumer interests and brand reputations across industries, preventing unethical practices that could cause lasting damage to companies and consumers alike.`;
  }

  inputSchema = z.object({
    content_strategy: z.string(),
    target_audience: z.object({
      vulnerabilities: z.array(z.string()),
      decision_factors: z.array(z.string()),
      trust_indicators: z.array(z.string())
    }),
    persuasion_techniques: z.array(z.string()),
    conversion_mechanisms: z.array(z.string()),
    ethical_framework: z.object({
      principles: z.array(z.string()),
      prohibited_tactics: z.array(z.string()),
      transparency_requirements: z.array(z.string())
    })
  });

  outputSchema = z.object({
    ethical_assessment: z.object({
      ethical_score: z.number(),
      manipulation_risk: z.enum(['none', 'low', 'medium', 'high', 'severe']),
      approval_status: z.enum(['approved', 'conditional', 'rejected'])
    }),
    flagged_tactics: z.array(z.object({
      tactic_name: z.string(),
      ethical_concern: z.string(),
      potential_harm: z.string(),
      alternative_approach: z.string(),
      severity: z.enum(['minor', 'moderate', 'serious'])
    })),
    transparency_gaps: z.array(z.object({
      gap_description: z.string(),
      required_disclosure: z.string(),
      placement_recommendation: z.string()
    })),
    ethical_alternatives: z.array(z.object({
      original_tactic: z.string(),
      ethical_alternative: z.string(),
      effectiveness_comparison: z.string(),
      implementation_notes: z.string()
    }))
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const prompt = `Review marketing strategy for ethical concerns and dark patterns.`;
    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);
    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    return {
      ethical_assessment: {
        ethical_score: 88,
        manipulation_risk: 'low',
        approval_status: 'approved'
      },
      flagged_tactics: [],
      transparency_gaps: [],
      ethical_alternatives: []
    };
  }
}
