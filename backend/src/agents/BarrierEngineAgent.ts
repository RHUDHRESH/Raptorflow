import { z } from "zod";
import { PromptTemplate } from "@langchain/core/prompts";
import { getLangChainModelForAgent, logModelSelection, getModelForAgent } from "../lib/llm";
import { StructuredOutputParser } from "@langchain/core/output_parsers";
import type { BarrierType, ProtocolType, Barrier, BarrierSignal } from "../types";

// =====================================================
// BARRIER DEFINITIONS & RULES
// =====================================================

export const BARRIER_DEFINITIONS: Record<BarrierType, {
  name: string;
  description: string;
  symptoms: string[];
  typical_metrics: string[];
  recommended_protocol: ProtocolType;
}> = {
  OBSCURITY: {
    name: "Obscurity",
    description: "Prospects don't know you exist. Low brand awareness, minimal inbound.",
    symptoms: [
      "Low website traffic",
      "Minimal brand search volume",
      "High bounce rate",
      "No organic mentions",
      "Low social following"
    ],
    typical_metrics: [
      "brand_search_volume",
      "direct_traffic",
      "organic_traffic",
      "social_mentions",
      "share_of_voice"
    ],
    recommended_protocol: "A_AUTHORITY_BLITZ"
  },
  RISK: {
    name: "Risk / Trust Gap",
    description: "Prospects know you but don't trust you enough to buy. High interest, low conversion.",
    symptoms: [
      "High traffic but low demo conversion",
      "Pricing page visits with no action",
      "Frequent competitor comparisons",
      "Objections about proof/case studies",
      "Long time on evaluation pages"
    ],
    typical_metrics: [
      "demo_conversion_rate",
      "pricing_page_bounce",
      "trial_to_paid_rate",
      "time_on_pricing_page",
      "competitor_comparison_searches"
    ],
    recommended_protocol: "B_TRUST_ANCHOR"
  },
  INERTIA: {
    name: "Inertia / Urgency Gap",
    description: "Prospects trust you but don't feel urgency to act. Stalled deals, 'not right now'.",
    symptoms: [
      "Long sales cycles",
      "Deals stuck in pipeline",
      "'Not the right time' objections",
      "No-decision losses",
      "Ghost after demo"
    ],
    typical_metrics: [
      "avg_sales_cycle_days",
      "stalled_deal_percentage",
      "no_decision_loss_rate",
      "demo_to_close_rate",
      "follow_up_response_rate"
    ],
    recommended_protocol: "C_COST_OF_INACTION"
  },
  FRICTION: {
    name: "Friction / Activation Gap",
    description: "Users signed up but haven't reached value. Onboarding drop-off, low activation.",
    symptoms: [
      "Low activation rate",
      "Onboarding abandonment",
      "Users don't complete setup",
      "Low feature adoption",
      "Quick time to churn"
    ],
    typical_metrics: [
      "activation_rate",
      "onboarding_completion_rate",
      "time_to_first_value",
      "feature_adoption_rate",
      "day_7_retention"
    ],
    recommended_protocol: "D_HABIT_HARDCODE"
  },
  CAPACITY: {
    name: "Capacity / Expansion Gap",
    description: "Active users not expanding. Power users hitting limits, no upgrade path taken.",
    symptoms: [
      "Users at plan limits",
      "Multiple users from same account",
      "Power user behavior without upgrade",
      "High usage, no expansion",
      "Champions not spreading internally"
    ],
    typical_metrics: [
      "usage_at_limit_rate",
      "seats_per_account",
      "expansion_rate",
      "nrr",
      "multi_user_accounts"
    ],
    recommended_protocol: "E_ENTERPRISE_WEDGE"
  },
  ATROPHY: {
    name: "Atrophy / Churn Risk",
    description: "Active users showing churn signals. Declining engagement, cancellation intent.",
    symptoms: [
      "Declining logins",
      "Support ticket increase",
      "Cancellation page visits",
      "Data export activity",
      "Billing complaints"
    ],
    typical_metrics: [
      "login_frequency_decline",
      "health_score",
      "cancellation_page_visits",
      "support_ticket_rate",
      "nps_score"
    ],
    recommended_protocol: "F_CHURN_INTERCEPT"
  }
};

// =====================================================
// INPUT/OUTPUT SCHEMAS
// =====================================================

export interface BarrierAnalysisInput {
  icp_id?: string;
  cohort_id?: string;
  metrics: Record<string, number>;
  context?: {
    industry?: string;
    stage?: string;
    product_type?: string;
    funnel_stage?: string;
  };
}

const barrierOutputSchema = z.object({
  primary_barrier: z.enum(["OBSCURITY", "RISK", "INERTIA", "FRICTION", "CAPACITY", "ATROPHY"]),
  confidence: z.number().min(0).max(1),
  secondary_barriers: z.array(z.object({
    barrier: z.enum(["OBSCURITY", "RISK", "INERTIA", "FRICTION", "CAPACITY", "ATROPHY"]),
    confidence: z.number().min(0).max(1)
  })),
  supporting_signals: z.array(z.object({
    signal_name: z.string(),
    value: z.number(),
    threshold: z.number(),
    assessment: z.string(),
    contributes_to: z.enum(["OBSCURITY", "RISK", "INERTIA", "FRICTION", "CAPACITY", "ATROPHY"])
  })),
  recommended_protocols: z.array(z.enum([
    "A_AUTHORITY_BLITZ",
    "B_TRUST_ANCHOR", 
    "C_COST_OF_INACTION",
    "D_HABIT_HARDCODE",
    "E_ENTERPRISE_WEDGE",
    "F_CHURN_INTERCEPT"
  ])),
  analysis_summary: z.string(),
  next_diagnostic_questions: z.array(z.string())
});

export type BarrierAnalysisOutput = z.infer<typeof barrierOutputSchema>;

// =====================================================
// BARRIER ENGINE AGENT
// =====================================================

export class BarrierEngineAgent {
  private model;
  private parser;
  private prompt;

  constructor() {
    const agentName = 'BarrierEngineAgent';
    this.model = getLangChainModelForAgent(agentName);
    logModelSelection(agentName, 'heavy', getModelForAgent(agentName));
    this.parser = StructuredOutputParser.fromZodSchema(barrierOutputSchema);
    this.prompt = new PromptTemplate({
      template: `You are a GTM diagnostic engine. Your job is to analyze metrics and classify the primary BARRIER blocking growth.

## The 6 Barriers

1. **OBSCURITY** - They don't know you exist
   - Symptoms: Low traffic, minimal brand search, no organic mentions
   - Key metrics: brand_search_volume < 100, direct_traffic < 500/mo
   
2. **RISK** - They know you but don't trust you
   - Symptoms: High traffic but low conversion, pricing page bounces
   - Key metrics: demo_conversion < 15%, trial_to_paid < 20%

3. **INERTIA** - They trust you but it's not urgent
   - Symptoms: Long sales cycles, stalled deals, "not right now"
   - Key metrics: avg_sales_cycle > 60 days, stalled_deals > 30%

4. **FRICTION** - They signed up but haven't activated
   - Symptoms: Low activation, onboarding drop-off
   - Key metrics: activation_rate < 40%, day_7_retention < 50%

5. **CAPACITY** - They're active but not expanding
   - Symptoms: Users at limits, no upgrades, flat NRR
   - Key metrics: usage_at_limit > 50%, expansion_rate < 10%

6. **ATROPHY** - They're showing churn signals
   - Symptoms: Declining logins, cancel page visits, support spikes
   - Key metrics: health_score < 40, login_decline > 30%

## Input Metrics
{metrics}

## Context
{context}

## Your Task
1. Analyze each metric against typical thresholds
2. Classify the PRIMARY barrier (highest confidence)
3. Identify secondary barriers if applicable
4. Recommend protocols to address the barrier
5. Suggest what additional data would improve the diagnosis

{format_instructions}`,
      inputVariables: ["metrics", "context"],
      partialVariables: { format_instructions: this.parser.getFormatInstructions() },
    });
  }

  /**
   * Analyze metrics to diagnose barriers
   */
  async analyze(input: BarrierAnalysisInput): Promise<BarrierAnalysisOutput> {
    try {
      // First, do rule-based classification
      const ruleBasedResult = this.ruleBasedClassification(input.metrics);
      
      // If we have high confidence from rules, use that
      if (ruleBasedResult.confidence >= 0.8) {
        return ruleBasedResult;
      }
      
      // Otherwise, use LLM for more nuanced analysis
      const chain = this.prompt.pipe(this.model).pipe(this.parser);
      const llmResult = await chain.invoke({
        metrics: JSON.stringify(input.metrics, null, 2),
        context: JSON.stringify(input.context || {}, null, 2)
      });
      
      // Merge rule-based and LLM results
      return this.mergeResults(ruleBasedResult, llmResult as BarrierAnalysisOutput);
      
    } catch (error: any) {
      console.error('BarrierEngineAgent error:', error);
      // Fall back to rule-based only
      return this.ruleBasedClassification(input.metrics);
    }
  }

  /**
   * Rule-based barrier classification
   */
  private ruleBasedClassification(metrics: Record<string, number>): BarrierAnalysisOutput {
    const signals: BarrierAnalysisOutput['supporting_signals'] = [];
    const barrierScores: Record<BarrierType, number> = {
      OBSCURITY: 0,
      RISK: 0,
      INERTIA: 0,
      FRICTION: 0,
      CAPACITY: 0,
      ATROPHY: 0
    };

    // OBSCURITY signals
    if (metrics.brand_search_volume !== undefined) {
      const threshold = 100;
      if (metrics.brand_search_volume < threshold) {
        barrierScores.OBSCURITY += 30;
        signals.push({
          signal_name: 'brand_search_volume',
          value: metrics.brand_search_volume,
          threshold,
          assessment: 'Below threshold - indicates low brand awareness',
          contributes_to: 'OBSCURITY'
        });
      }
    }
    
    if (metrics.direct_traffic !== undefined) {
      const threshold = 500;
      if (metrics.direct_traffic < threshold) {
        barrierScores.OBSCURITY += 20;
        signals.push({
          signal_name: 'direct_traffic',
          value: metrics.direct_traffic,
          threshold,
          assessment: 'Low direct traffic indicates weak brand recognition',
          contributes_to: 'OBSCURITY'
        });
      }
    }

    // RISK signals
    if (metrics.demo_conversion_rate !== undefined) {
      const threshold = 15;
      if (metrics.demo_conversion_rate < threshold) {
        barrierScores.RISK += 30;
        signals.push({
          signal_name: 'demo_conversion_rate',
          value: metrics.demo_conversion_rate,
          threshold,
          assessment: 'Low demo conversion suggests trust/proof gap',
          contributes_to: 'RISK'
        });
      }
    }

    if (metrics.trial_to_paid_rate !== undefined) {
      const threshold = 20;
      if (metrics.trial_to_paid_rate < threshold) {
        barrierScores.RISK += 25;
        signals.push({
          signal_name: 'trial_to_paid_rate',
          value: metrics.trial_to_paid_rate,
          threshold,
          assessment: 'Low trial conversion indicates lack of confidence in value',
          contributes_to: 'RISK'
        });
      }
    }

    // INERTIA signals
    if (metrics.avg_sales_cycle_days !== undefined) {
      const threshold = 60;
      if (metrics.avg_sales_cycle_days > threshold) {
        barrierScores.INERTIA += 30;
        signals.push({
          signal_name: 'avg_sales_cycle_days',
          value: metrics.avg_sales_cycle_days,
          threshold,
          assessment: 'Long sales cycle suggests lack of urgency',
          contributes_to: 'INERTIA'
        });
      }
    }

    if (metrics.stalled_deal_percentage !== undefined) {
      const threshold = 30;
      if (metrics.stalled_deal_percentage > threshold) {
        barrierScores.INERTIA += 25;
        signals.push({
          signal_name: 'stalled_deal_percentage',
          value: metrics.stalled_deal_percentage,
          threshold,
          assessment: 'High stalled deals indicate decision paralysis',
          contributes_to: 'INERTIA'
        });
      }
    }

    // FRICTION signals
    if (metrics.activation_rate !== undefined) {
      const threshold = 40;
      if (metrics.activation_rate < threshold) {
        barrierScores.FRICTION += 35;
        signals.push({
          signal_name: 'activation_rate',
          value: metrics.activation_rate,
          threshold,
          assessment: 'Low activation rate indicates onboarding friction',
          contributes_to: 'FRICTION'
        });
      }
    }

    if (metrics.day_7_retention !== undefined) {
      const threshold = 50;
      if (metrics.day_7_retention < threshold) {
        barrierScores.FRICTION += 25;
        signals.push({
          signal_name: 'day_7_retention',
          value: metrics.day_7_retention,
          threshold,
          assessment: 'Low early retention indicates users not finding value',
          contributes_to: 'FRICTION'
        });
      }
    }

    // CAPACITY signals
    if (metrics.usage_at_limit_rate !== undefined) {
      const threshold = 50;
      if (metrics.usage_at_limit_rate > threshold) {
        barrierScores.CAPACITY += 30;
        signals.push({
          signal_name: 'usage_at_limit_rate',
          value: metrics.usage_at_limit_rate,
          threshold,
          assessment: 'Users hitting limits but not upgrading',
          contributes_to: 'CAPACITY'
        });
      }
    }

    if (metrics.expansion_rate !== undefined) {
      const threshold = 10;
      if (metrics.expansion_rate < threshold) {
        barrierScores.CAPACITY += 25;
        signals.push({
          signal_name: 'expansion_rate',
          value: metrics.expansion_rate,
          threshold,
          assessment: 'Low expansion rate despite usage',
          contributes_to: 'CAPACITY'
        });
      }
    }

    // ATROPHY signals
    if (metrics.health_score !== undefined) {
      const threshold = 40;
      if (metrics.health_score < threshold) {
        barrierScores.ATROPHY += 35;
        signals.push({
          signal_name: 'health_score',
          value: metrics.health_score,
          threshold,
          assessment: 'Low health score indicates churn risk',
          contributes_to: 'ATROPHY'
        });
      }
    }

    if (metrics.login_frequency_decline !== undefined) {
      const threshold = 30;
      if (metrics.login_frequency_decline > threshold) {
        barrierScores.ATROPHY += 25;
        signals.push({
          signal_name: 'login_frequency_decline',
          value: metrics.login_frequency_decline,
          threshold,
          assessment: 'Declining engagement signals churn intent',
          contributes_to: 'ATROPHY'
        });
      }
    }

    // Find primary barrier
    const sortedBarriers = (Object.entries(barrierScores) as [BarrierType, number][])
      .sort(([, a], [, b]) => b - a);
    
    const [primaryBarrier, primaryScore] = sortedBarriers[0];
    const totalScore = Object.values(barrierScores).reduce((a, b) => a + b, 0);
    const confidence = totalScore > 0 ? Math.min(primaryScore / 50, 1) : 0.3; // Max confidence from rules alone
    
    // Get secondary barriers
    const secondaryBarriers = sortedBarriers
      .slice(1)
      .filter(([, score]) => score > 0)
      .map(([barrier, score]) => ({
        barrier: barrier as BarrierType,
        confidence: Math.min(score / 50, 0.8)
      }));

    // Map barriers to recommended protocols
    const recommendedProtocols: ProtocolType[] = [
      BARRIER_DEFINITIONS[primaryBarrier].recommended_protocol,
      ...secondaryBarriers.slice(0, 1).map(b => BARRIER_DEFINITIONS[b.barrier].recommended_protocol)
    ];

    return {
      primary_barrier: primaryBarrier,
      confidence,
      secondary_barriers: secondaryBarriers,
      supporting_signals: signals,
      recommended_protocols: [...new Set(recommendedProtocols)],
      analysis_summary: this.generateSummary(primaryBarrier, confidence, signals),
      next_diagnostic_questions: this.getDiagnosticQuestions(primaryBarrier, metrics)
    };
  }

  /**
   * Merge rule-based and LLM results
   */
  private mergeResults(
    ruleBased: BarrierAnalysisOutput, 
    llmResult: BarrierAnalysisOutput
  ): BarrierAnalysisOutput {
    // If they agree on primary barrier, boost confidence
    if (ruleBased.primary_barrier === llmResult.primary_barrier) {
      return {
        ...llmResult,
        confidence: Math.min((ruleBased.confidence + llmResult.confidence) / 2 + 0.1, 1),
        supporting_signals: [...ruleBased.supporting_signals, ...llmResult.supporting_signals]
      };
    }
    
    // If they disagree, use the one with higher confidence
    if (ruleBased.confidence > llmResult.confidence) {
      return {
        ...ruleBased,
        analysis_summary: llmResult.analysis_summary,
        next_diagnostic_questions: llmResult.next_diagnostic_questions
      };
    }
    
    return llmResult;
  }

  /**
   * Generate analysis summary
   */
  private generateSummary(barrier: BarrierType, confidence: number, signals: any[]): string {
    const def = BARRIER_DEFINITIONS[barrier];
    const signalCount = signals.filter(s => s.contributes_to === barrier).length;
    
    return `Primary barrier identified: **${def.name}** (${(confidence * 100).toFixed(0)}% confidence). ` +
      `${def.description} ` +
      `Based on ${signalCount} supporting signal(s). ` +
      `Recommended protocol: ${def.recommended_protocol.replace(/_/g, ' ')}.`;
  }

  /**
   * Get diagnostic questions to improve analysis
   */
  private getDiagnosticQuestions(barrier: BarrierType, existingMetrics: Record<string, number>): string[] {
    const def = BARRIER_DEFINITIONS[barrier];
    const missingMetrics = def.typical_metrics.filter(m => !(m in existingMetrics));
    
    const questions: string[] = [];
    
    if (missingMetrics.length > 0) {
      questions.push(`What are your current values for: ${missingMetrics.join(', ')}?`);
    }
    
    switch (barrier) {
      case 'OBSCURITY':
        questions.push('What is your current content/marketing output volume?');
        questions.push('How are prospects currently discovering you?');
        break;
      case 'RISK':
        questions.push('What objections do you hear most in sales calls?');
        questions.push('How many case studies/testimonials do you have live?');
        break;
      case 'INERTIA':
        questions.push('What percentage of deals are "no decision" losses?');
        questions.push('What event typically triggers purchase decisions?');
        break;
      case 'FRICTION':
        questions.push('What is your defined activation event?');
        questions.push('At what step do users most commonly drop off?');
        break;
      case 'CAPACITY':
        questions.push('What percentage of users are multi-seat accounts?');
        questions.push('What triggers typically lead to expansion conversations?');
        break;
      case 'ATROPHY':
        questions.push('What is your current churn rate?');
        questions.push('What are the top 3 reasons customers give for canceling?');
        break;
    }
    
    return questions.slice(0, 3);
  }

  /**
   * Quick classification without LLM (for real-time UI)
   */
  quickClassify(metrics: Record<string, number>): { barrier: BarrierType; confidence: number } {
    const result = this.ruleBasedClassification(metrics);
    return {
      barrier: result.primary_barrier,
      confidence: result.confidence
    };
  }
}

