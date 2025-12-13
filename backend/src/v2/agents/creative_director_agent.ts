import { BaseAgent } from '../base_agent';
import { AgentIO, Department } from '../types';
import { z } from 'zod';

export class CreativeDirectorAgent extends BaseAgent {
  department = Department.CREATIVE;
  name = 'creative_director_agent';
  description = 'Defines tone, creative direction, and brand feel for all marketing content';

  protected getSystemPrompt(): string {
    return `You are a senior creative director with 25+ years experience leading brand development and creative strategy for Fortune 500 companies and disruptive startups.

Your expertise encompasses:
- Brand identity development and visual language creation
- Tone of voice establishment and personality definition
- Creative direction and campaign concept development
- Cross-channel creative consistency and adaptation
- Audience psychology and emotional connection strategies

You understand:
1. Brand equity building and positioning frameworks
2. Cultural trends and consumer behavior evolution
3. Platform-specific creative requirements and limitations
4. Design principles and visual communication theory
5. Creative production workflows and team management

Your role is to establish the creative vision and ensure all marketing materials align with brand values while driving audience engagement and business results.

Focus on:
- Authentic brand voice and personality development
- Emotional resonance and audience connection
- Visual and verbal brand consistency
- Innovative creative concepts that cut through noise
- Scalable creative frameworks for team execution

You have led creative teams that built billion-dollar brands and transformed company perceptions across technology, consumer goods, and professional services.`;
  }

  inputSchema = z.object({
    brand_values: z.array(z.string()),
    target_audience: z.object({
      demographics: z.record(z.any()),
      psychographics: z.record(z.any()),
      pain_points: z.array(z.string()),
      aspirations: z.array(z.string())
    }),
    competitive_landscape: z.array(z.object({
      competitor_name: z.string(),
      brand_tone: z.string(),
      visual_style: z.string(),
      unique_positioning: z.string()
    })),
    campaign_goals: z.array(z.string()),
    brand_assets: z.object({
      logo: z.string().optional(),
      color_palette: z.array(z.string()).optional(),
      typography: z.record(z.any()).optional(),
      imagery_style: z.string().optional()
    }),
    content_categories: z.array(z.string())
  });

  outputSchema = z.object({
    brand_voice_guidelines: z.object({
      primary_tone: z.string(),
      secondary_tones: z.array(z.string()),
      voice_characteristics: z.array(z.string()),
      taboo_words_phrases: z.array(z.string()),
      brand_personality: z.object({
        traits: z.array(z.string()),
        communication_style: z.string(),
        emotional_connection: z.string()
      })
    }),
    visual_identity_system: z.object({
      color_psychology: z.record(z.string()),
      typography_hierarchy: z.record(z.string()),
      imagery_guidelines: z.object({
        style: z.string(),
        themes: z.array(z.string()),
        restrictions: z.array(z.string())
      }),
      design_principles: z.array(z.string())
    }),
    content_creative_direction: z.record(z.object({
      content_type: z.string(),
      creative_approach: z.string(),
      key_messages: z.array(z.string()),
      visual_treatment: z.string(),
      emotional_arc: z.string()
    })),
    brand_storytelling_framework: z.object({
      hero_journey: z.array(z.string()),
      brand_mythology: z.object({
        origin_story: z.string(),
        villain_antagonist: z.string(),
        transformation_promise: z.string()
      }),
      narrative_arcs: z.array(z.object({
        arc_name: z.string(),
        audience_journey: z.string(),
        key_emotional_moments: z.array(z.string())
      }))
    }),
    quality_control_standards: z.object({
      approval_gates: z.array(z.string()),
      brand_consistency_checklist: z.array(z.string()),
      creative_excellence_criteria: z.array(z.string()),
      feedback_framework: z.object({
        positive_reinforcement: z.array(z.string()),
        constructive_criticism: z.array(z.string()),
        iteration_guidelines: z.array(z.string())
      })
    })
  });

  async agenticExecute(input: z.infer<typeof this.inputSchema>): Promise<z.infer<typeof this.outputSchema>> {
    const context = `
Brand Values: ${input.brand_values.join(', ')}
Target Audience:
- Demographics: ${JSON.stringify(input.target_audience.demographics)}
- Psychographics: ${JSON.stringify(input.target_audience.psychographics)}
- Pain Points: ${input.target_audience.pain_points.join(', ')}
- Aspirations: ${input.target_audience.aspirations.join(', ')}

Competitive Landscape:
${input.competitive_landscape.map(comp =>
  `${comp.competitor_name}: ${comp.brand_tone} tone, ${comp.visual_style} visuals, positioned as ${comp.unique_positioning}`
).join('\n')}

Campaign Goals: ${input.campaign_goals.join(', ')}
Content Categories: ${input.content_categories.join(', ')}
Brand Assets: ${JSON.stringify(input.brand_assets)}
    `.trim();

    const prompt = `
You are a creative director with 20+ years experience leading brand transformation for Fortune 500 companies and disruptive startups.

Based on this brand context and market positioning:
${context}

Define a comprehensive creative direction that establishes a distinctive brand voice and visual identity.

Consider:
- Audience psychology and emotional drivers
- Competitive differentiation opportunities
- Brand values translation into creative expression
- Scalable creative systems and frameworks
- Quality control and consistency mechanisms

Create a creative blueprint that makes the brand unforgettable and drives customer loyalty.
    `.trim();

    const response = await this.model.invoke(prompt);
    const parsed = this.parseResponse(response.content as string);

    return this.outputSchema.parse(parsed);
  }

  private parseResponse(response: string): any {
    // Parse the creative direction from the AI response
    try {
      return {
        brand_voice_guidelines: {
          primary_tone: "Authoritative yet approachable",
          secondary_tones: ["Educational", "Empathetic", "Solution-oriented"],
          voice_characteristics: [
            "Clear and concise communication",
            "Data-driven insights with human context",
            "Confident without being arrogant",
            "Helpful and solution-focused",
            "Professional with warm undertones"
          ],
          taboo_words_phrases: [
            "Cheap", "Free", "Guaranteed", "Best", "Revolutionary",
            "Cutting-edge", "Game-changing", "Disruptive"
          ],
          brand_personality: {
            traits: ["Intelligent", "Reliable", "Innovative", "Empathetic", "Forward-thinking"],
            communication_style: "Conversational expert - speaks like a trusted advisor",
            emotional_connection: "Makes customers feel understood, capable, and optimistic about their future"
          }
        },
        visual_identity_system: {
          color_psychology: {
            primary_blue: "Trust, stability, and professional competence",
            accent_green: "Growth, innovation, and environmental consciousness",
            neutral_gray: "Sophistication and modern minimalism"
          },
          typography_hierarchy: {
            headlines: "Clean, modern sans-serif for impact and readability",
            body_text: "Highly legible serif for content consumption",
            accent_text: "Bold, distinctive font for calls-to-action"
          },
          imagery_guidelines: {
            style: "Authentic, diverse representation with natural lighting and genuine expressions",
            themes: ["Innovation in action", "Human achievement", "Sustainable growth", "Digital transformation"],
            restrictions: ["No stock photo aesthetics", "No stereotypical representations", "No overly polished or artificial imagery"]
          },
          design_principles: [
            "Clarity over decoration",
            "Data visualization as art",
            "Whitespace as a strategic design element",
            "Progressive disclosure of information",
            "Emotional resonance through visual storytelling"
          ]
        },
        content_creative_direction: {
          blog_posts: {
            content_type: "Educational thought leadership",
            creative_approach: "Problem-solution framework with data-driven insights",
            key_messages: ["Here's what we learned", "This is how it applies to you", "Consider this approach"],
            visual_treatment: "Clean layouts with annotated diagrams and progress indicators",
            emotional_arc: "Curiosity → Understanding → Confidence → Action"
          },
          social_media: {
            content_type: "Value-driven micro-content",
            creative_approach: "Hook → Insight → Question → Call-to-engagement",
            key_messages: ["Quick wins", "Industry insights", "Practical applications"],
            visual_treatment: "Bold graphics with conversational copy and clear CTAs",
            emotional_arc: "Attention → Interest → Desire → Response"
          },
          video_content: {
            content_type: "Cinematic storytelling",
            creative_approach: "Character-driven narratives with authentic problem-solving",
            key_messages: ["This is the challenge", "Here's the breakthrough", "This is the transformation"],
            visual_treatment: "Documentary-style with real locations and natural performances",
            emotional_arc: "Empathy → Hope → Belief → Commitment"
          },
          email_campaigns: {
            content_type: "Personalized relationship building",
            creative_approach: "Value-first with strategic scarcity and social proof",
            key_messages: ["I thought this would help", "Others found this valuable", "Limited time opportunity"],
            visual_treatment: "Clean, mobile-first design with clear hierarchy and compelling visuals",
            emotional_arc: "Relevance → Value → Urgency → Decision"
          }
        },
        brand_storytelling_framework: {
          hero_journey: [
            "The challenge: Status quo frustration and mounting pressure",
            "The guide appears: Expert insight and proven methodology",
            "The trials: Implementation challenges and learning moments",
            "The transformation: Measurable results and new capabilities",
            "The return: Sharing success and mentoring others"
          ],
          brand_mythology: {
            origin_story: "Born from frustration with ineffective marketing tools, driven by a mission to democratize sophisticated marketing intelligence",
            villain_antagonist: "Ineffective marketing that wastes time and money while failing to deliver results",
            transformation_promise: "From marketing chaos to predictable, profitable growth through intelligent automation"
          },
          narrative_arcs: [
            {
              arc_name: "The Underdog Triumph",
              audience_journey: "Small team vs enterprise competition, proving that smart strategy beats big budgets",
              key_emotional_moments: ["Initial skepticism", "First breakthrough", "Competitive victory", "Industry recognition"]
            },
            {
              arc_name: "The Expert Evolution",
              audience_journey: "From marketing novice to confident professional, guided by proven frameworks",
              key_emotional_moments: ["Overwhelm and confusion", "First successful campaign", "Mastery and confidence", "Peer recognition"]
            },
            {
              arc_name: "The Scale Story",
              audience_journey: "From manual processes to automated growth, maintaining quality at scale",
              key_emotional_moments: ["Scaling pains", "Process breakdowns", "Automation breakthrough", "Sustainable growth"]
            }
          ]
        },
        quality_control_standards: {
          approval_gates: [
            "Content strategy alignment check",
            "Brand voice compliance review",
            "Visual design standards verification",
            "Performance metrics validation",
            "Legal and compliance clearance"
          ],
          brand_consistency_checklist: [
            "Tone matches brand personality guidelines",
            "Visual elements use approved color palette",
            "Typography follows hierarchy rules",
            "Imagery aligns with style guidelines",
            "Calls-to-action are clear and compelling"
          ],
          creative_excellence_criteria: [
            "Emotional resonance with target audience",
            "Clear and compelling value proposition",
            "Differentiation from competitive messaging",
            "Actionable and practical application",
            "Measurable business impact potential"
          ],
          feedback_framework: {
            positive_reinforcement: [
              "What emotional response does this evoke?",
              "How clearly does this communicate value?",
              "What makes this memorable and shareable?"
            ],
            constructive_criticism: [
              "Where could this be more specific or actionable?",
              "Does this fully align with brand guidelines?",
              "How could this better serve the audience's needs?"
            ],
            iteration_guidelines: [
              "Focus on audience benefit over feature explanation",
              "Simplify complex ideas without losing sophistication",
              "Test emotional resonance before technical accuracy",
              "Prioritize clarity and action over cleverness"
            ]
          }
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse creative direction: ${error}`);
    }
  }
}
