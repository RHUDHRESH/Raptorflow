import { FoundationData } from './foundation';
import { Icp, IcpFirmographics, IcpPainMap, IcpPsycholinguistics, IcpDisqualifiers } from '@/types/icp-types';
import { ICP_TEMPLATES, IcpTemplate } from './icp-templates';

/**
 * ICP Generator Engine
 * Auto-generates 2-3 ICPs from Foundation data
 */

interface GeneratedIcp {
    icp: Partial<Icp>;
    confidence: number;
    reasoning: string;
}

/**
 * Main generation function - creates ICPs from Foundation data
 * NOW: Triggers the agentic synthesis pipeline via the backend
 */
export async function triggerAgenticSynthesis(data: FoundationData) {
    try {
        const response = await fetch('/api/onboarding/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Synthesis failed');
        }

        return await response.json();
    } catch (error) {
        console.error('Agentic Synthesis Error:', error);
        throw error;
    }
}

/**
 * Legacy generation function - creates ICPs from Foundation data
 */
export function generateICPsFromFoundation(data: FoundationData): GeneratedIcp[] {
    const icps: GeneratedIcp[] = [];

    const customerType = normalizeCustomerType(data.cohorts?.customerType);
    const stage = data.business?.stage || 'early';
    const buyerRole = data.cohorts?.buyerRole || '';

    // Determine which templates to use based on customer type
    const templates = selectTemplates(customerType, stage, buyerRole);

    // Generate ICPs from templates + Foundation data
    templates.forEach((template, index) => {
        const generatedIcp = generateFromTemplate(template, data, index === 0);
        icps.push(generatedIcp);
    });

    return icps;
}

/**
 * Normalize customer type to array
 */
function normalizeCustomerType(value: string | string[] | undefined): string[] {
    if (!value) return [];
    if (Array.isArray(value)) return value;
    return [value];
}

/**
 * Select appropriate templates based on business context
 */
function selectTemplates(customerTypes: string[], stage: string, buyerRole: string): IcpTemplate[] {
    const selected: IcpTemplate[] = [];

    // B2B customers
    if (customerTypes.includes('b2b')) {
        if (buyerRole.toLowerCase().includes('founder') ||
            buyerRole.toLowerCase().includes('ceo') ||
            buyerRole.toLowerCase().includes('owner')) {
            selected.push(ICP_TEMPLATES.techFounder);
        } else if (buyerRole.toLowerCase().includes('marketing') ||
            buyerRole.toLowerCase().includes('cmo')) {
            selected.push(ICP_TEMPLATES.marketingLead);
        } else {
            selected.push(ICP_TEMPLATES.corporateDecider);
        }

        // Add SMB as secondary for growth stage
        if (stage === 'growth' || stage === 'scaling') {
            selected.push(ICP_TEMPLATES.smbOperator);
        }
    }

    // B2C customers
    if (customerTypes.includes('b2c')) {
        if (stage === 'idea' || stage === 'early') {
            selected.push(ICP_TEMPLATES.earlyAdopter);
        } else {
            selected.push(ICP_TEMPLATES.massMarket);
        }
    }

    // Default fallback
    if (selected.length === 0) {
        selected.push(ICP_TEMPLATES.techFounder);
    }

    // Limit to 3 ICPs max
    return selected.slice(0, 3);
}

/**
 * Generate a full ICP from template + Foundation data
 */
function generateFromTemplate(
    template: IcpTemplate,
    data: FoundationData,
    isPrimary: boolean
): GeneratedIcp {
    // Map Foundation data to firmographics
    const firmographics: IcpFirmographics = {
        companyType: template.baseCompanyType,
        geography: ['Global'], // Default
        salesMotion: template.baseSalesMotion,
        budgetComfort: template.baseBudgetComfort,
        decisionMaker: data.cohorts?.buyerRole
            ? [data.cohorts.buyerRole]
            : template.baseDecisionMaker
    };

    // Map confession/positioning to pain points
    const painMap: IcpPainMap = {
        primaryPains: extractPains(data),
        secondaryPains: template.defaultSecondaryPains,
        triggerEvents: extractTriggers(data),
        urgencyLevel: mapUrgency(data.cohorts?.riskTolerance)
    };

    // Map cohort psychology to language preferences
    const psycholinguistics: IcpPsycholinguistics = {
        mindsetTraits: mapMindsetTraits(data),
        emotionalTriggers: extractEmotionalTriggers(data),
        tonePreference: template.baseTone,
        wordsToUse: [...template.baseWordsToUse, ...extractKeywords(data)],
        wordsToAvoid: template.baseWordsToAvoid,
        proofPreference: mapProofPreference(data.cohorts?.decisionStyle),
        ctaStyle: mapCtaStyle(data.cohorts?.decisionStyle)
    };

    // Generate disqualifiers
    const disqualifiers: IcpDisqualifiers = {
        excludedCompanyTypes: template.excludedTypes,
        excludedGeographies: [],
        excludedBehaviors: template.excludedBehaviors
    };

    // Calculate confidence based on data completeness
    const confidence = calculateConfidence(data);

    // Create the ICP name from positioning or default
    const name = generateIcpName(data, template);

    const icp: Partial<Icp> = {
        name,
        priority: isPrimary ? 'primary' : 'secondary',
        status: 'active',
        confidenceScore: confidence,
        firmographics,
        painMap,
        psycholinguistics,
        disqualifiers
    };

    return {
        icp,
        confidence,
        reasoning: template.reasoning
    };
}

// ================================
// Mapping Helpers
// ================================

function extractPains(data: FoundationData): string[] {
    const pains: string[] = [];

    // From confession
    if (data.confession?.expensiveProblem) {
        pains.push(data.confession.expensiveProblem.slice(0, 100));
    }

    // From positioning (psychological outcome = pain inverse)
    if (data.positioning?.psychologicalOutcome) {
        pains.push(`Lack of ${data.positioning.psychologicalOutcome.toLowerCase()}`);
    }

    // From SCARF drivers
    const drivers = data.cohorts?.primaryDrivers || [];
    const driverPains: Record<string, string> = {
        'status': 'Being overlooked or undervalued',
        'certainty': 'Uncertainty and unpredictable outcomes',
        'autonomy': 'Loss of control over decisions',
        'relatedness': 'Feeling disconnected from peers',
        'fairness': 'Unfair treatment or hidden agendas'
    };

    drivers.forEach(d => {
        if (driverPains[d]) pains.push(driverPains[d]);
    });

    return pains.slice(0, 2); // Max 2 primary pains
}

function extractTriggers(data: FoundationData): string[] {
    const triggers: string[] = [];

    if (data.confession?.embarrassingTruth) {
        triggers.push('Realized current approach isn\'t working');
    }

    if (data.business?.stage === 'growth') {
        triggers.push('Hitting growth plateau');
    } else if (data.business?.stage === 'early') {
        triggers.push('Need to get first customers');
    }

    return triggers;
}

function mapUrgency(riskTolerance?: string): 'now' | 'soon' | 'someday' {
    if (riskTolerance === 'opportunity-seeker') return 'now';
    if (riskTolerance === 'regret-minimizer') return 'soon';
    return 'soon';
}

function mapMindsetTraits(data: FoundationData): string[] {
    const traits: string[] = [];

    const decisionStyle = data.cohorts?.decisionStyle;
    if (decisionStyle === 'maximizer') {
        traits.push('analytical', 'thorough', 'comparison-driven');
    } else if (decisionStyle === 'satisficer') {
        traits.push('decisive', 'practical', 'action-oriented');
    }

    const riskTolerance = data.cohorts?.riskTolerance;
    if (riskTolerance === 'opportunity-seeker') {
        traits.push('ambitious', 'risk-tolerant');
    } else if (riskTolerance === 'regret-minimizer') {
        traits.push('cautious', 'research-driven');
    }

    return traits;
}

function extractEmotionalTriggers(data: FoundationData): string[] {
    const drivers = data.cohorts?.primaryDrivers || [];
    const emotionalMap: Record<string, string> = {
        'status': 'Recognition and respect',
        'certainty': 'Security and predictability',
        'autonomy': 'Freedom and control',
        'relatedness': 'Belonging and connection',
        'fairness': 'Trust and transparency'
    };

    return drivers.map(d => emotionalMap[d]).filter(Boolean);
}

function extractKeywords(data: FoundationData): string[] {
    const words: string[] = [];

    if (data.positioning?.category) {
        words.push(data.positioning.category);
    }
    if (data.positioning?.ownedPosition) {
        words.push(data.positioning.ownedPosition);
    }

    return words;
}

function mapProofPreference(decisionStyle?: string): string[] {
    if (decisionStyle === 'maximizer') {
        return ['data', 'case-study', 'comparisons'];
    }
    return ['case-study', 'testimonials'];
}

function mapCtaStyle(decisionStyle?: string): string[] {
    if (decisionStyle === 'satisficer') {
        return ['direct', 'action-oriented'];
    }
    return ['soft', 'exploratory'];
}

function calculateConfidence(data: FoundationData): number {
    let score = 0.3; // Base score

    // Add points for completeness
    if (data.cohorts?.customerType) score += 0.1;
    if (data.cohorts?.buyerRole) score += 0.1;
    if (data.cohorts?.primaryDrivers?.length) score += 0.1;
    if (data.confession?.expensiveProblem) score += 0.1;
    if (data.positioning?.targetAudience) score += 0.1;
    if (data.positioning?.psychologicalOutcome) score += 0.1;
    if (data.messaging?.beliefPillar) score += 0.1;

    return Math.min(score, 1.0);
}

function generateIcpName(data: FoundationData, template: IcpTemplate): string {
    const audience = data.positioning?.targetAudience;

    if (audience && audience.length < 50) {
        return `The ${audience}`;
    }

    return template.defaultName;
}
