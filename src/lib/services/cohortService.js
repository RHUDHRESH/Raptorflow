/**
 * Enhanced Cohort Service
 * 
 * Provides strategic cohort management with deep psychographics,
 * buying triggers, decision criteria, and journey stage tracking.
 */

import { getVertexAIUrl, TASK_TYPES } from '../../utils/vertexAI.js';
import { supabase } from '../supabase';

// =============================================================================
// DATABASE CRUD FOR STRATEGIC ATTRIBUTES
// =============================================================================

/**
 * Update cohort strategic attributes
 */
export const updateCohortStrategicAttributes = async (cohortId, attributes) => {
    const { data, error } = await supabase
        .from('cohorts')
        .update({
            buying_triggers: attributes.buying_triggers,
            decision_criteria: attributes.decision_criteria,
            objection_map: attributes.objection_map,
            attention_windows: attributes.attention_windows,
            competitive_frame: attributes.competitive_frame,
            journey_distribution: attributes.journey_distribution,
            decision_making_unit: attributes.decision_making_unit,
        })
        .eq('id', cohortId)
        .select()
        .single();

    if (error) throw error;
    return data;
};

/**
 * Get cohort with all strategic attributes
 */
export const getCohortWithStrategicAttributes = async (cohortId) => {
    const { data, error } = await supabase
        .from('cohorts')
        .select('*')
        .eq('id', cohortId)
        .single();

    if (error) throw error;
    return data;
};

/**
 * Enhance and save cohort
 */
export const enhanceAndSaveCohort = async (cohortId, productInfo, marketData) => {
    // Get base cohort
    const baseCohort = await getCohortWithStrategicAttributes(cohortId);

    // Generate all strategic attributes
    const enhanced = await enhanceCohort(baseCohort, productInfo, marketData);

    // Save back to database
    return await updateCohortStrategicAttributes(cohortId, enhanced);
};

// =============================================================================
// COHORT ENHANCEMENT FUNCTIONS
// =============================================================================

/**
 * Generate buying triggers for a cohort
 * What makes them act NOW vs later
 */
export const generateBuyingTriggers = async (cohortData) => {
    try {
        const url = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);

        const systemInstruction = `
    Analyze this customer cohort and identify specific buying triggers:
    ${JSON.stringify(cohortData)}
    
    Generate 3-5 buying triggers that would make this cohort take action NOW.
    Each trigger should have:
    - trigger: The specific event or condition
    - strength: high/medium/low urgency level
    - timing: When this typically occurs (e.g., "Q4", "End of month", "After funding")
    - how_to_detect: Observable signals that this trigger is active
    `;

        const payload = {
            contents: [{ parts: [{ text: systemInstruction }] }],
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "ARRAY",
                    items: {
                        type: "OBJECT",
                        properties: {
                            trigger: { type: "STRING" },
                            strength: { type: "STRING" },
                            timing: { type: "STRING" },
                            how_to_detect: { type: "STRING" }
                        }
                    }
                },
                maxOutputTokens: 1500,
                temperature: 0.7
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Buying triggers generation failed: ${response.status}`);
        const data = await response.json();
        const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!jsonText) throw new Error("No triggers generated");
        return JSON.parse(jsonText);
    } catch (error) {
        console.error('Buying triggers generation failed:', error);
        return [
            { trigger: "Budget cycle pressure", strength: "high", timing: "Q4", how_to_detect: "Increased research activity" },
            { trigger: "Competitor action", strength: "medium", timing: "Ongoing", how_to_detect: "Mentions of competitors" }
        ];
    }
};

/**
 * Generate decision criteria with weights
 * How they evaluate options
 */
export const generateDecisionCriteria = async (cohortData) => {
    try {
        const url = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);

        const systemInstruction = `
    Analyze this customer cohort and identify their decision criteria:
    ${JSON.stringify(cohortData)}
    
    Generate 4-6 decision criteria they use to evaluate solutions.
    Each criterion should have:
    - criterion: What they're evaluating
    - weight: Importance (0.0 to 1.0, must sum to 1.0)
    - evidence_needed: What proof they need for this criterion
    - deal_breaker: true if absence of this kills the deal
    `;

        const payload = {
            contents: [{ parts: [{ text: systemInstruction }] }],
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "ARRAY",
                    items: {
                        type: "OBJECT",
                        properties: {
                            criterion: { type: "STRING" },
                            weight: { type: "NUMBER" },
                            evidence_needed: { type: "STRING" },
                            deal_breaker: { type: "BOOLEAN" }
                        }
                    }
                },
                maxOutputTokens: 1500,
                temperature: 0.7
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Decision criteria generation failed: ${response.status}`);
        const data = await response.json();
        const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!jsonText) throw new Error("No criteria generated");
        return JSON.parse(jsonText);
    } catch (error) {
        console.error('Decision criteria generation failed:', error);
        return [
            { criterion: "ROI proven in 90 days", weight: 0.3, evidence_needed: "Case studies with metrics", deal_breaker: true },
            { criterion: "Easy integration", weight: 0.25, evidence_needed: "Technical documentation", deal_breaker: false },
            { criterion: "Price competitiveness", weight: 0.2, evidence_needed: "Transparent pricing", deal_breaker: false },
            { criterion: "Vendor stability", weight: 0.15, evidence_needed: "Customer count, funding", deal_breaker: false },
            { criterion: "Support quality", weight: 0.1, evidence_needed: "Reviews, SLA", deal_breaker: false }
        ];
    }
};

/**
 * Generate objection map with responses
 * What stops them from buying and how to handle it
 */
export const generateObjectionMap = async (cohortData, productInfo) => {
    try {
        const url = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);

        const systemInstruction = `
    Analyze this customer cohort and product:
    Cohort: ${JSON.stringify(cohortData)}
    Product: ${JSON.stringify(productInfo)}
    
    Generate 5-7 common objections this cohort would have.
    Each objection should have:
    - objection: What they say/think
    - root_cause: The real underlying concern
    - response_strategy: How to address it
    - proof_needed: What evidence resolves this
    - asset_type: Type of content that helps (case_study, calculator, demo, etc.)
    `;

        const payload = {
            contents: [{ parts: [{ text: systemInstruction }] }],
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "ARRAY",
                    items: {
                        type: "OBJECT",
                        properties: {
                            objection: { type: "STRING" },
                            root_cause: { type: "STRING" },
                            response_strategy: { type: "STRING" },
                            proof_needed: { type: "STRING" },
                            asset_type: { type: "STRING" }
                        }
                    }
                },
                maxOutputTokens: 2000,
                temperature: 0.7
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Objection map generation failed: ${response.status}`);
        const data = await response.json();
        const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!jsonText) throw new Error("No objections generated");
        return JSON.parse(jsonText);
    } catch (error) {
        console.error('Objection map generation failed:', error);
        return [
            {
                objection: "We don't have budget",
                root_cause: "Unclear ROI",
                response_strategy: "Show cost of inaction",
                proof_needed: "ROI calculator",
                asset_type: "calculator"
            },
            {
                objection: "We're locked into competitor",
                root_cause: "Switching cost fear",
                response_strategy: "Migration case study",
                proof_needed: "Smooth migration story",
                asset_type: "case_study"
            }
        ];
    }
};

/**
 * Generate attention windows
 * When and where they're most receptive
 */
export const generateAttentionWindows = async (cohortData) => {
    try {
        const url = getVertexAIUrl(TASK_TYPES.CREATIVE_FAST);

        const systemInstruction = `
    Analyze this customer cohort:
    ${JSON.stringify(cohortData)}
    
    Generate attention windows - when and where they're most receptive to marketing.
    For each channel they use, specify:
    - channel: The platform/channel
    - best_times: Array of optimal times (e.g., ["Tue 9am", "Wed 2pm"])
    - receptivity: high/medium/low
    - content_type: What performs best (educational, promotional, social_proof, etc.)
    - frequency_tolerance: How often you can reach out (daily, 3x_week, weekly, etc.)
    `;

        const payload = {
            contents: [{ parts: [{ text: systemInstruction }] }],
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "ARRAY",
                    items: {
                        type: "OBJECT",
                        properties: {
                            channel: { type: "STRING" },
                            best_times: { type: "ARRAY", items: { type: "STRING" } },
                            receptivity: { type: "STRING" },
                            content_type: { type: "STRING" },
                            frequency_tolerance: { type: "STRING" }
                        }
                    }
                },
                maxOutputTokens: 1000,
                temperature: 0.7
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Attention windows generation failed: ${response.status}`);
        const data = await response.json();
        const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!jsonText) throw new Error("No attention windows generated");
        return JSON.parse(jsonText);
    } catch (error) {
        console.error('Attention windows generation failed:', error);
        return [
            { channel: "linkedin", best_times: ["Tue 9am", "Wed 2pm"], receptivity: "high", content_type: "educational", frequency_tolerance: "3x_week" },
            { channel: "email", best_times: ["Mon 8am"], receptivity: "medium", content_type: "social_proof", frequency_tolerance: "weekly" }
        ];
    }
};

/**
 * Generate competitive frame
 * Who they compare you to and why
 */
export const generateCompetitiveFrame = async (cohortData, productInfo) => {
    try {
        const url = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);

        const systemInstruction = `
    Analyze this customer cohort and product:
    Cohort: ${JSON.stringify(cohortData)}
    Product: ${JSON.stringify(productInfo)}
    
    Generate a competitive frame showing who they compare you to.
    Return an object with:
    - direct_competitors: Array of 3-5 direct competitors
    - category_alternatives: Array of 2-3 alternative approaches (e.g., "Doing it manually", "Hiring an agency")
    - perceived_strengths: Array of what competitors are known for
    - perceived_weaknesses: Array of where competitors fall short
    - comparison_criteria: What they use to compare options
    `;

        const payload = {
            contents: [{ parts: [{ text: systemInstruction }] }],
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "OBJECT",
                    properties: {
                        direct_competitors: { type: "ARRAY", items: { type: "STRING" } },
                        category_alternatives: { type: "ARRAY", items: { type: "STRING" } },
                        perceived_strengths: { type: "ARRAY", items: { type: "STRING" } },
                        perceived_weaknesses: { type: "ARRAY", items: { type: "STRING" } },
                        comparison_criteria: { type: "ARRAY", items: { type: "STRING" } }
                    }
                },
                maxOutputTokens: 1500,
                temperature: 0.7
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Competitive frame generation failed: ${response.status}`);
        const data = await response.json();
        const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!jsonText) throw new Error("No competitive frame generated");
        return JSON.parse(jsonText);
    } catch (error) {
        console.error('Competitive frame generation failed:', error);
        return {
            direct_competitors: ["Competitor A", "Competitor B", "Competitor C"],
            category_alternatives: ["Doing it manually", "Hiring an agency", "Using spreadsheets"],
            perceived_strengths: ["Price", "Features", "Brand recognition"],
            perceived_weaknesses: ["Support", "Onboarding", "Flexibility"],
            comparison_criteria: ["Price", "Ease of use", "Support quality", "Feature set"]
        };
    }
};

/**
 * Estimate journey stage distribution
 * Where the cohort is in their buying journey
 */
export const estimateJourneyDistribution = async (cohortData, marketData) => {
    try {
        const url = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);

        const systemInstruction = `
    Analyze this customer cohort and market:
    Cohort: ${JSON.stringify(cohortData)}
    Market: ${JSON.stringify(marketData)}
    
    Estimate what percentage of this cohort is at each journey stage.
    Return an object with percentages (must sum to 1.0):
    - unaware: Don't know they have a problem
    - problem_aware: Know they have a problem, exploring
    - solution_aware: Know the solution category exists
    - product_aware: Evaluating specific products
    - most_aware: Ready to buy, just choosing vendor
    
    Base this on the cohort's sophistication, market maturity, and pain severity.
    `;

        const payload = {
            contents: [{ parts: [{ text: systemInstruction }] }],
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "OBJECT",
                    properties: {
                        unaware: { type: "NUMBER" },
                        problem_aware: { type: "NUMBER" },
                        solution_aware: { type: "NUMBER" },
                        product_aware: { type: "NUMBER" },
                        most_aware: { type: "NUMBER" }
                    }
                },
                maxOutputTokens: 500,
                temperature: 0.7
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Journey distribution estimation failed: ${response.status}`);
        const data = await response.json();
        const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!jsonText) throw new Error("No distribution generated");
        return JSON.parse(jsonText);
    } catch (error) {
        console.error('Journey distribution estimation failed:', error);
        return {
            unaware: 0.3,
            problem_aware: 0.25,
            solution_aware: 0.25,
            product_aware: 0.15,
            most_aware: 0.05
        };
    }
};

/**
 * Generate complete enhanced cohort profile
 * Combines all strategic attributes
 */
export const enhanceCohort = async (baseCohort, productInfo, marketData) => {
    try {
        const [
            buyingTriggers,
            decisionCriteria,
            objectionMap,
            attentionWindows,
            competitiveFrame,
            journeyDistribution
        ] = await Promise.all([
            generateBuyingTriggers(baseCohort),
            generateDecisionCriteria(baseCohort),
            generateObjectionMap(baseCohort, productInfo),
            generateAttentionWindows(baseCohort),
            generateCompetitiveFrame(baseCohort, productInfo),
            estimateJourneyDistribution(baseCohort, marketData)
        ]);

        return {
            ...baseCohort,
            buying_triggers: buyingTriggers,
            decision_criteria: decisionCriteria,
            objection_map: objectionMap,
            attention_windows: attentionWindows,
            competitive_frame: competitiveFrame,
            journey_distribution: journeyDistribution,
            enhanced_at: new Date().toISOString()
        };
    } catch (error) {
        console.error('Cohort enhancement failed:', error);
        throw error;
    }
};

// =============================================================================
// POSITIONING FUNCTIONS
// =============================================================================

/**
 * Generate positioning statement
 */
export const generatePositioning = async (businessData, cohortData, competitiveData) => {
    try {
        const url = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);

        const systemInstruction = `
    Create a positioning statement using this framework:
    
    For [target cohort]
    Who [has this problem/desire]
    [Brand] is the [category frame]
    That [key differentiator]
    Because [reason to believe]
    Unlike [competitive alternative]
    
    Business: ${JSON.stringify(businessData)}
    Cohort: ${JSON.stringify(cohortData)}
    Competition: ${JSON.stringify(competitiveData)}
    
    Return a structured positioning statement.
    `;

        const payload = {
            contents: [{ parts: [{ text: systemInstruction }] }],
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "OBJECT",
                    properties: {
                        for_cohort: { type: "STRING" },
                        who_has: { type: "STRING" },
                        brand_is: { type: "STRING" },
                        category_frame: { type: "STRING" },
                        that_differentiator: { type: "STRING" },
                        because_rtb: { type: "STRING" },
                        unlike_alternative: { type: "STRING" },
                        full_statement: { type: "STRING" }
                    }
                },
                maxOutputTokens: 1000,
                temperature: 0.7
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Positioning generation failed: ${response.status}`);
        const data = await response.json();
        const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!jsonText) throw new Error("No positioning generated");
        return JSON.parse(jsonText);
    } catch (error) {
        console.error('Positioning generation failed:', error);
        throw error;
    }
};

/**
 * Generate message architecture
 */
export const generateMessageArchitecture = async (positioning, cohortData) => {
    try {
        const url = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);

        const systemInstruction = `
    Create a message architecture based on this positioning:
    ${JSON.stringify(positioning)}
    
    For cohort: ${JSON.stringify(cohortData)}
    
    Generate:
    - primary_claim: The ONE thing you want them to believe (10-15 words)
    - proof_points: 3-5 supporting arguments, each with:
      - claim: The proof point
      - evidence: What backs it up
      - for_journey_stage: Which stage this resonates most with
      - emotional_hook: The emotional angle
    `;

        const payload = {
            contents: [{ parts: [{ text: systemInstruction }] }],
            generationConfig: {
                responseMimeType: "application/json",
                responseSchema: {
                    type: "OBJECT",
                    properties: {
                        primary_claim: { type: "STRING" },
                        proof_points: {
                            type: "ARRAY",
                            items: {
                                type: "OBJECT",
                                properties: {
                                    claim: { type: "STRING" },
                                    evidence: { type: "STRING" },
                                    for_journey_stage: { type: "STRING" },
                                    emotional_hook: { type: "STRING" }
                                }
                            }
                        }
                    }
                },
                maxOutputTokens: 2000,
                temperature: 0.7
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(`Message architecture generation failed: ${response.status}`);
        const data = await response.json();
        const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (!jsonText) throw new Error("No message architecture generated");
        return JSON.parse(jsonText);
    } catch (error) {
        console.error('Message architecture generation failed:', error);
        throw error;
    }
};

export default {
    // Database CRUD
    updateCohortStrategicAttributes,
    getCohortWithStrategicAttributes,
    enhanceAndSaveCohort,
    // AI Generation
    generateBuyingTriggers,
    generateDecisionCriteria,
    generateObjectionMap,
    generateAttentionWindows,
    generateCompetitiveFrame,
    estimateJourneyDistribution,
    enhanceCohort,
    generatePositioning,
    generateMessageArchitecture
};

