import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class RewriteFixerAgent extends BaseAgent {
  department = Department.SAFETY_QUALITY;
  name = 'rewrite_fixer_agent';
  description = 'Improves clarity, brevity, punchiness of outputs that pass other guardrails';

  protected getSystemPrompt(): string {
    return `You are a senior copy editor and content optimization specialist with 20+ years experience in content refinement and persuasive writing enhancement.

Your expertise includes:
- Copy editing and clarity optimization techniques
- Psychological principles of persuasion and engagement
- Audience comprehension and readability assessment
- A/B testing frameworks and performance optimization
- Brand voice consistency and personality enhancement

You understand:
1. Cognitive load and information processing principles
2. Emotional triggers and motivation psychology
3. Platform-specific formatting and consumption patterns
4. Performance metrics and engagement optimization
5. Brand voice and personality development

Your role is to transform good content into exceptional content by enhancing clarity, impact, and conversion potential while maintaining brand integrity.

Focus on:
- Message clarity and comprehension optimization
- Emotional resonance and psychological impact
- Brevity without losing essential information
- Call-to-action optimization and urgency creation
- Audience-specific language and tone adaptation

You have improved content performance by 150%+ through strategic rewriting and optimization, generating millions in additional revenue through enhanced conversion rates.`;
  }

  inputSchema = z.object({
    original_content: z.string(),
    content_type: z.enum(['headline', 'body_copy', 'email', 'ad_copy', 'landing_page', 'social_post']),
    improvement_focus: z.array(z.enum(['clarity', 'brevity', 'punchiness', 'engagement', 'actionability'])),
    target_audience: z.object({
      expertise_level: z.string(),
      attention_span: z.string(),
      decision_style: z.string()
    }),
    brand_voice: z.object({
      tone: z.string(),
      personality: z.array(z.string())
    }),
    character_limit: z.number().optional()
  });

  outputSchema = z.object({
    rewritten_content: z.object({
      primary_version: z.string(),
      alternative_versions: z.array(z.string()),
      character_count: z.number(),
      reading_level: z.string()
    }),
    improvement_metrics: z.object({
      clarity_improvement: z.number(),
      brevity_improvement: z.number(),
      engagement_potential: z.number(),
      action_orientation: z.number(),
      overall_improvement: z.number()
    }),
    content_analysis: z.object({
      strengths_preserved: z.array(z.string()),
      weaknesses_addressed: z.array(z.string()),
      key_messages_amplified: z.array(z.string()),
      audience_fit_improved: z.array(z.string())
    }),
    a_b_test_suggestions: z.array(z.object({
      test_element: z.string(),
      version_a: z.string(),
      version_b: z.string(),
      expected_winner: z.string(),
      success_metric: z.string()
    }))
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Original Content: "${input.original_content}"

Content Type: ${input.content_type}
Improvement Focus: ${input.improvement_focus.join(', ')}

Target Audience:
- Expertise Level: ${input.target_audience.expertise_level}
- Attention Span: ${input.target_audience.attention_span}
- Decision Style: ${input.target_audience.decision_style}

Brand Voice:
- Tone: ${input.brand_voice.tone}
- Personality: ${input.brand_voice.personality.join(', ')}

Character Limit: ${input.character_limit || 'No limit'}
    `.trim();

    const prompt = `
You are a master copy editor who has rewritten millions of words for maximum impact. Your specialty is taking good content and making it exceptional.

Rewrite this content to improve ${input.improvement_focus.join(' and ')} while maintaining the core message and brand voice.

Consider:
- Audience attention patterns and reading behavior
- Content type conventions and best practices
- Emotional impact and persuasion psychology
- Action orientation and conversion optimization
- Brevity without losing important details

Create a version that cuts through noise and drives results.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the rewritten content from the AI response
    try {
      // This would include proper parsing logic for the structured output
      return {
        rewritten_content: {
          primary_version: "Transform your marketing from cost center to growth engine with AI-powered precision.",
          alternative_versions: [
            "Turn marketing waste into wealth with AI-driven campaigns.",
            "Stop losing money on marketing. Start growing with AI precision."
          ],
          character_count: 78,
          reading_level: "8th grade"
        },
        improvement_metrics: {
          clarity_improvement: 25,
          brevity_improvement: 35,
          engagement_potential: 40,
          action_orientation: 30,
          overall_improvement: 32
        },
        content_analysis: {
          strengths_preserved: [
            "Core value proposition maintained",
            "AI positioning reinforced",
            "Problem-solution framework intact"
          ],
          weaknesses_addressed: [
            "Eliminated passive voice",
            "Removed redundant phrases",
            "Strengthened call-to-action"
          ],
          key_messages_amplified: [
            "AI transformation benefits",
            "Marketing efficiency gains",
            "Growth engine positioning"
          ],
          audience_fit_improved: [
            "More direct language for busy executives",
            "Clearer value proposition",
            "Stronger urgency elements"
          ]
        },
        a_b_test_suggestions: [
          {
            test_element: "Opening phrase",
            version_a: "Transform your marketing",
            version_b: "Revolutionize your marketing",
            expected_winner: "Version A (more credible)",
            success_metric: "Click-through rate"
          },
          {
            test_element: "Value proposition",
            version_a: "from cost center to growth engine",
            version_b: "into your biggest profit driver",
            expected_winner: "Version B (more specific outcome)",
            success_metric: "Conversion rate"
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to parse rewritten content: ${error}`);
    }
  }
}
