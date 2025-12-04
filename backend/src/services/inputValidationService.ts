/**
 * Input Validation Service
 * Uses AI to validate user inputs and confront them when answers are vague/bullshit
 * Ensures quality data for the GTM engine
 */

import { getLangChainModelForTask } from '../lib/llm';
import { z } from 'zod';
import { StructuredOutputParser } from '@langchain/core/output_parsers';
import { PromptTemplate } from '@langchain/core/prompts';

// Validation result schema
const validationResultSchema = z.object({
  isValid: z.boolean().describe("Whether the input is acceptable"),
  qualityScore: z.number().min(0).max(100).describe("Quality score 0-100"),
  issues: z.array(z.object({
    type: z.enum(['vague', 'generic', 'too_short', 'missing_specifics', 'contradictory', 'unrealistic', 'buzzword_heavy']),
    description: z.string(),
    severity: z.enum(['error', 'warning', 'suggestion'])
  })).describe("Issues found in the input"),
  confrontation: z.string().nullable().describe("Direct, friendly confrontation message if input is bad"),
  suggestions: z.array(z.string()).describe("Specific suggestions for improvement"),
  improvedVersion: z.string().nullable().describe("AI-improved version of their answer (if salvageable)")
});

export type ValidationResult = z.infer<typeof validationResultSchema>;

// Validation prompts for different fields
const VALIDATION_PROMPTS = {
  positioning_kennedy: `You are a brutally honest positioning coach. A founder has answered the Dan Kennedy question: "Why should I choose you over every other option – including doing nothing?"

Their answer: "{input}"

Evaluate this answer. Common problems include:
- Generic statements like "we help businesses grow" (WORTHLESS)
- Listing features instead of outcomes
- No differentiation from alternatives
- No specific target customer
- No quantified outcomes
- Buzzword soup with no substance

If the answer is weak, CONFRONT them directly but constructively. Example:
"Look, 'we help businesses grow' describes every business on Earth. What do you ACTUALLY do differently? If a customer has $10K and is choosing between you, Competitor X, and doing nothing – what's your killer argument?"

Be direct but not mean. Help them get specific.`,

  positioning_dunford: `You are a positioning expert evaluating an April Dunford-style answer: "Who is your product obviously better for – and in what situations?"

Their answer: "{input}"

Evaluate this answer. Good answers include:
- A specific customer segment (not "businesses" or "teams")
- A clear situation or trigger that makes them ideal
- Differentiation from alternatives
- Why "obviously" better (not just "also good")

If weak, confront them. Example:
"You said 'better for growing companies' – that's everyone! Who specifically wakes up thinking 'I need exactly what you offer'? What's the SITUATION where choosing you is a no-brainer?"`,

  value_proposition: `You are evaluating a value proposition statement.

Their statement: "{input}"

A good value proposition:
- Clearly states the target customer
- Identifies the problem solved
- Articulates the primary benefit
- Differentiates from alternatives

If vague, push back hard on specifics.`,

  pain_points: `You are evaluating described customer pain points.

Their answer: "{input}"

Good pain point descriptions:
- Are specific and observable
- Include emotional/business impact
- Are things customers actually say (not what you assume)
- Connect to your solution naturally

If generic ("they need to be more efficient"), push for the REAL pain.`,

  target_audience: `You are evaluating a target audience description.

Their answer: "{input}"

A good target audience:
- Is specific enough to find (job title, company size, industry)
- Has an identifiable trigger/situation
- You can explain WHY they're ideal
- Is not "anyone who needs X"

If too broad, narrow it down aggressively.`
};

export const inputValidationService = {
  /**
   * Validate a single input field with AI
   */
  async validateInput(
    input: string,
    fieldType: keyof typeof VALIDATION_PROMPTS,
    context?: Record<string, any>
  ): Promise<ValidationResult> {
    const model = getLangChainModelForTask('reasoning');
    const parser = StructuredOutputParser.fromZodSchema(validationResultSchema);
    
    const basePrompt = VALIDATION_PROMPTS[fieldType] || VALIDATION_PROMPTS.value_proposition;
    
    const prompt = new PromptTemplate({
      template: `${basePrompt}

${context ? `Additional context: ${JSON.stringify(context)}` : ''}

Evaluate the input and provide structured feedback.

{format_instructions}`,
      inputVariables: ['input'],
      partialVariables: { format_instructions: parser.getFormatInstructions() }
    });

    try {
      const chain = prompt.pipe(model).pipe(parser);
      return await chain.invoke({ input });
    } catch (error) {
      console.error('Validation error:', error);
      return {
        isValid: true,
        qualityScore: 50,
        issues: [],
        confrontation: null,
        suggestions: ['Try to be more specific about your unique value'],
        improvedVersion: null
      };
    }
  },

  /**
   * Validate the entire positioning step
   */
  async validatePositioning(
    danKennedy: string,
    dunford: string
  ): Promise<{
    overall: ValidationResult;
    danKennedy: ValidationResult;
    dunford: ValidationResult;
    canProceed: boolean;
    blockingIssues: string[];
  }> {
    const [kennedyResult, dunfordResult] = await Promise.all([
      this.validateInput(danKennedy, 'positioning_kennedy'),
      this.validateInput(dunford, 'positioning_dunford')
    ]);

    const overallScore = (kennedyResult.qualityScore + dunfordResult.qualityScore) / 2;
    const blockingIssues: string[] = [];

    // Check for blocking issues (errors)
    [...kennedyResult.issues, ...dunfordResult.issues].forEach(issue => {
      if (issue.severity === 'error') {
        blockingIssues.push(issue.description);
      }
    });

    // Require minimum quality to proceed
    const canProceed = overallScore >= 40 && blockingIssues.length === 0;

    return {
      overall: {
        isValid: canProceed,
        qualityScore: overallScore,
        issues: [...kennedyResult.issues, ...dunfordResult.issues],
        confrontation: !canProceed ? this.generateOverallConfrontation(kennedyResult, dunfordResult) : null,
        suggestions: [...new Set([...kennedyResult.suggestions, ...dunfordResult.suggestions])],
        improvedVersion: null
      },
      danKennedy: kennedyResult,
      dunford: dunfordResult,
      canProceed,
      blockingIssues
    };
  },

  /**
   * Generate a direct but helpful confrontation message
   */
  generateOverallConfrontation(kennedy: ValidationResult, dunford: ValidationResult): string {
    const avgScore = (kennedy.qualityScore + dunford.qualityScore) / 2;
    
    if (avgScore < 30) {
      return `🚨 Hold up – I can't let you proceed with this. Your positioning is too vague to build a real GTM strategy on. Let me be direct: "${kennedy.confrontation || dunford.confrontation || "What you've written could describe almost any business."}" 

Take 5 more minutes and get specific. WHO exactly are you serving? What MEASURABLE outcome do they get? Why YOU and not the 100 alternatives?`;
    }
    
    if (avgScore < 50) {
      return `⚠️ We can work with this, but it needs tightening. ${kennedy.confrontation || dunford.confrontation || "Your answers are still quite broad."} 

The more specific you are now, the better your ICPs and campaigns will be. It's worth the extra effort.`;
    }

    return `📝 Good start, but there's room to sharpen this. ${kennedy.suggestions[0] || dunford.suggestions[0] || "Try to add more specifics about your unique differentiation."}`;
  },

  /**
   * Check if an input is "bullshit" (too generic/vague)
   */
  async detectBullshit(input: string): Promise<{
    isBullshit: boolean;
    reason: string;
    callout: string;
  }> {
    // Common bullshit phrases
    const bullshitPhrases = [
      'help businesses grow',
      'increase efficiency',
      'save time and money',
      'best in class',
      'world-class',
      'cutting-edge',
      'revolutionary',
      'disruptive',
      'synergy',
      'leverage',
      'empower',
      'enable',
      'all-in-one',
      'end-to-end',
      'seamless',
      'robust solution',
      'comprehensive platform'
    ];

    const lowercaseInput = input.toLowerCase();
    const foundPhrases = bullshitPhrases.filter(phrase => lowercaseInput.includes(phrase));

    if (foundPhrases.length >= 2) {
      return {
        isBullshit: true,
        reason: `Contains multiple generic phrases: ${foundPhrases.join(', ')}`,
        callout: `🛑 I stopped reading at "${foundPhrases[0]}". That phrase means nothing. Every company says that. What do you ACTUALLY do that's different? Be specific or we can't build a real strategy.`
      };
    }

    // Check for too-short responses
    if (input.length < 100) {
      return {
        isBullshit: true,
        reason: 'Response too short to contain meaningful positioning',
        callout: `📏 That's only ${input.length} characters. A real positioning answer needs detail. Who's your customer? What outcome do they get? What makes you better than alternatives? Give me something to work with.`
      };
    }

    // Check for lack of specifics
    const hasNumbers = /\d/.test(input);
    const hasSpecificPeople = /(CEO|CTO|founder|manager|director|head of|VP|lead|engineer|marketer|sales)/i.test(input);
    const hasCompanySize = /(startup|smb|enterprise|small business|mid-market|\d+ employees)/i.test(input);

    if (!hasNumbers && !hasSpecificPeople && !hasCompanySize) {
      return {
        isBullshit: false, // Not bullshit, just needs improvement
        reason: 'Lacks specific details about target customer',
        callout: `💡 Good start, but who specifically? Add details: What's their job title? Company size? What trigger makes them need you NOW?`
      };
    }

    return {
      isBullshit: false,
      reason: 'Input appears to contain meaningful content',
      callout: ''
    };
  }
};

