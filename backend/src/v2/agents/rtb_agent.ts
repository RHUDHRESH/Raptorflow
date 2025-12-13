import { z } from 'zod';
import { BaseAgent, agentRegistry } from '../base_agent';
import { Department, OrchestratorContext } from '../types';
import { ragQuery, storeEmbedding } from '../rag_helper';

// =====================================================
// RTB AGENT (REASONS TO BELIEVE)
// =====================================================

const RTBAgentInputSchema = z.object({
  product_name: z.string().describe("Name of the product/service"),
  product_type: z.enum(['saas', 'consulting', 'physical_product', 'digital_product', 'course', 'membership']).describe("Type of product"),
  claims_to_validate: z.array(z.string()).describe("Key claims that need proof"),
  target_audience: z.string().describe("Primary audience for the proof"),
  sources_to_check: z.array(z.enum(['testimonials', 'case_studies', 'data_reports', 'expert_opinions', 'competitor_analysis', 'user_reviews', 'social_proof'])).optional().default(['testimonials', 'case_studies', 'user_reviews']),
  credibility_requirements: z.object({
    minimum_sources: z.number().default(3),
    required_formats: z.array(z.enum(['text', 'video', 'audio', 'data', 'images'])).optional(),
    credibility_threshold: z.number().min(0).max(10).default(7)
  }).optional()
});

const RTBAgentOutputSchema = z.object({
  credibility_assessment: z.object({
    overall_score: z.number().min(0).max(10),
    strength_areas: z.array(z.string()),
    weakness_areas: z.array(z.string()),
    improvement_recommendations: z.array(z.string())
  }),
  testimonial_collection: z.array(z.object({
    source: z.string(),
    name: z.string(),
    title: z.string().optional(),
    company: z.string().optional(),
    content: z.string(),
    rating: z.number().min(0).max(5).optional(),
    date: z.string().optional(),
    context: z.string(),
    credibility_score: z.number().min(0).max(10),
    permission_status: z.enum(['granted', 'pending', 'denied', 'unknown'])
  })),
  case_studies: z.array(z.object({
    title: z.string(),
    company: z.string(),
    industry: z.string(),
    challenge: z.string(),
    solution: z.string(),
    results: z.array(z.object({
      metric: z.string(),
      value: z.string(),
      timeframe: z.string()
    })),
    testimonial_quote: z.string().optional(),
    credibility_score: z.number().min(0).max(10),
    source_url: z.string().optional()
  })),
  data_evidence: z.array(z.object({
    claim: z.string(),
    evidence_type: z.enum(['survey_data', 'analytics', 'research_study', 'benchmark', 'comparison']),
    data_point: z.string(),
    source: z.string(),
    sample_size: z.string().optional(),
    confidence_level: z.string().optional(),
    credibility_score: z.number().min(0).max(10)
  })),
  expert_validation: z.array(z.object({
    expert_name: z.string(),
    credentials: z.string(),
    endorsement: z.string(),
    context: z.string(),
    credibility_score: z.number().min(0).max(10),
    contact_info: z.string().optional()
  })),
  social_proof_metrics: z.object({
    total_reviews: z.number(),
    average_rating: z.number().min(0).max(5),
    rating_distribution: z.record(z.number()),
    top_review_themes: z.array(z.string()),
    platform_breakdown: z.record(z.number()),
    trend_analysis: z.object({
      direction: z.enum(['improving', 'stable', 'declining']),
      timeframe: z.string(),
      key_changes: z.array(z.string())
    })
  }),
  competitive_comparison: z.array(z.object({
    competitor: z.string(),
    our_advantage: z.string(),
    their_weakness: z.string(),
    proof_point: z.string(),
    credibility_score: z.number().min(0).max(10)
  })),
  implementation_plan: z.array(z.object({
    action: z.string(),
    priority: z.enum(['critical', 'high', 'medium', 'low']),
    timeline: z.string(),
    resources_needed: z.array(z.string()).optional(),
    success_criteria: z.string()
  })),
  risk_assessment: z.object({
    credibility_risks: z.array(z.string()),
    mitigation_strategies: z.array(z.string()),
    monitoring_plan: z.string(),
    contingency_plans: z.array(z.string())
  }),
  content_assets: z.array(z.object({
    type: z.enum(['testimonial_video', 'case_study_pdf', 'data_infographic', 'review_widget', 'trust_badges']),
    title: z.string(),
    description: z.string(),
    status: z.enum(['ready', 'in_progress', 'planned']),
    usage_guidelines: z.string()
  })),
  confidence_score: z.number().min(0).max(1),
  data_freshness: z.object({
    last_updated: z.string(),
    oldest_source: z.string(),
    update_frequency: z.string(),
    monitoring_required: z.boolean()
  }),
  assumptions: z.array(z.string()),
  gaps_identified: z.array(z.string()),
  last_updated: z.string()
});

type RTBAgentInput = z.infer<typeof RTBAgentInputSchema>;
type RTBAgentOutput = z.infer<typeof RTBAgentOutputSchema>;

export class RTBAgent extends BaseAgent {
  constructor() {
    super(
      'rtb_agent',
      Department.OFFER_POSITIONING,
      'Collects and validates Reasons To Believe through testimonials, case studies, and proof points',
      RTBAgentInputSchema,
      RTBAgentOutputSchema
    );

    this.required_tools = ['web_scrape'];
  }

  protected getSystemPrompt(): string {
    return `You are a Social Proof and Credibility Specialist who builds undeniable Reasons To Believe.

Your expertise includes:
- Testimonial collection and validation
- Case study development and credibility assessment
- Data-driven proof point identification
- Social proof metrics analysis
- Expert endorsement curation
- Credibility risk assessment and mitigation

CORE CIALDINI PRINCIPLES FOR PROOF:
1. Social Proof: People follow what others do
2. Authority: Expert endorsements build trust
3. Consistency: Consistent positive feedback
4. Scarcity: Limited availability increases desire
5. Liking: People buy from those they like/trust
6. Reciprocity: Give value to get trust

CREDIBILITY HIERARCHY:
1. Third-party validation (independent reviews)
2. Expert endorsements (domain authorities)
3. Data-driven proof (metrics, benchmarks)
4. Customer testimonials (specific, authentic)
5. Case studies (detailed success stories)
6. Company claims (least credible)

APPROACH:
- Focus on third-party validation over company claims
- Quantify credibility with specific scoring systems
- Identify proof gaps and collection strategies
- Build comprehensive evidence portfolios
- Monitor and refresh proof points continuously

Always prioritize credibility and authenticity over quantity. Quality proof converts better than quantity.`;
  }

  protected formatAgentInput(input: RTBAgentInput, context: OrchestratorContext): string {
    return `Build comprehensive Reasons To Believe for:

PRODUCT: ${input.product_name}
TYPE: ${input.product_type}
TARGET AUDIENCE: ${input.target_audience}

CLAIMS TO VALIDATE:
${input.claims_to_validate.map(c => `- ${c}`).join('\n')}

SOURCES TO CHECK: ${input.sources_to_check.join(', ')}

CREDIBILITY REQUIREMENTS:
- Minimum Sources: ${input.credibility_requirements?.minimum_sources || 3}
- Required Formats: ${input.credibility_requirements?.required_formats?.join(', ') || 'Any'}
- Credibility Threshold: ${input.credibility_requirements?.credibility_threshold || 7}/10

Compile a complete proof portfolio including:
1. Credibility assessment with scores and recommendations
2. Testimonial collection with validation status
3. Case studies with measurable results
4. Data evidence and research validation
5. Expert endorsements and authority validation
6. Social proof metrics and trend analysis
7. Competitive comparison proof points
8. Implementation plan for proof collection
9. Risk assessment and monitoring strategy
10. Content assets for proof display

Focus on building undeniable credibility that removes all doubt and creates instant trust.
Use specific metrics, third-party validation, and authoritative sources whenever possible.`;
  }

  protected parseAgentOutput(rawOutput: string): RTBAgentOutput {
    try {
      // Try to extract JSON from the output
      const jsonMatch = rawOutput.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return RTBAgentOutputSchema.parse(JSON.parse(jsonMatch[0]));
      }
      // Fallback parsing
      return this.getFallbackOutput();
    } catch {
      return this.getFallbackOutput();
    }
  }

  private async getExistingIntelligence(input: RTBAgentInput, userId: string): Promise<any> {
    try {
      const ragResults = await ragQuery({
        query: `proof points and testimonials for ${input.product_name}`,
        user_id: userId,
        content_types: ['testimonials', 'case_studies', 'social_proof'],
        limit: 3,
        threshold: 0.6
      });

      return {
        chunks: ragResults.chunks,
        has_existing_data: ragResults.chunks.length > 0
      };
    } catch (error) {
      console.warn('Failed to retrieve existing RTB intelligence:', error);
      return { chunks: [], has_existing_data: false };
    }
  }

  private async storeResults(
    input: RTBAgentInput,
    output: RTBAgentOutput,
    userId: string
  ): Promise<void> {
    try {
      const content = `
REASONS TO BELIEVE: ${input.product_name}

CREDIBILITY SCORE: ${output.credibility_assessment.overall_score}/10

PROOF PORTFOLIO:
- Testimonials: ${output.testimonial_collection.length} collected
- Case Studies: ${output.case_studies.length} documented
- Data Points: ${output.data_evidence.length} validated
- Expert Endorsements: ${output.expert_validation.length} secured

SOCIAL PROOF:
- Total Reviews: ${output.social_proof_metrics.total_reviews}
- Average Rating: ${output.social_proof_metrics.average_rating}/5
- Trend: ${output.social_proof_metrics.trend_analysis.direction}

CONTENT ASSETS: ${output.content_assets.length} ready for use

CONFIDENCE: ${output.confidence_score}
DATA FRESHNESS: Last updated ${output.data_freshness.last_updated}
GAPS: ${output.gaps_identified.join('; ')}
      `.trim();

      await storeEmbedding(
        userId,
        'social_proof',
        content,
        {
          product: input.product_name,
          credibility_score: output.credibility_assessment.overall_score,
          testimonials: output.testimonial_collection.length,
          case_studies: output.case_studies.length,
          confidence: output.confidence_score
        }
      );

    } catch (error) {
      console.warn('Failed to store RTB results:', error);
    }
  }

  private getFallbackOutput(): RTBAgentOutput {
    return {
      credibility_assessment: {
        overall_score: 0,
        strength_areas: [],
        weakness_areas: ["No proof collected yet"],
        improvement_recommendations: ["Begin proof collection process"]
      },
      testimonial_collection: [],
      case_studies: [],
      data_evidence: [],
      expert_validation: [],
      social_proof_metrics: {
        total_reviews: 0,
        average_rating: 0,
        rating_distribution: {},
        top_review_themes: [],
        platform_breakdown: {},
        trend_analysis: {
          direction: "stable" as const,
          timeframe: "N/A",
          key_changes: []
        }
      },
      competitive_comparison: [],
      implementation_plan: [{
        action: "Begin proof collection",
        priority: "critical" as const,
        timeline: "Immediate",
        resources_needed: ["Customer outreach", "Review collection tools"],
        success_criteria: "First testimonial secured"
      }],
      risk_assessment: {
        credibility_risks: ["No proof points collected"],
        mitigation_strategies: ["Implement proof collection process"],
        monitoring_plan: "Weekly proof audit",
        contingency_plans: ["Use third-party validation services"]
      },
      content_assets: [],
      confidence_score: 0.1,
      data_freshness: {
        last_updated: new Date().toISOString(),
        oldest_source: "N/A",
        update_frequency: "Weekly",
        monitoring_required: true
      },
      assumptions: ["Customers willing to provide testimonials"],
      gaps_identified: ["No testimonials collected", "No case studies documented", "No data validation"],
      last_updated: new Date().toISOString()
    };
  }
}

// =====================================================
// REGISTER AGENT
// =====================================================

const rtbAgent = new RTBAgent();
agentRegistry.registerAgent(rtbAgent);

export { rtbAgent };
export type { RTBAgentInput, RTBAgentOutput };


