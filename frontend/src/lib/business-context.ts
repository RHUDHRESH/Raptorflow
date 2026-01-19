/**
 * 📋 BUSINESS CONTEXT GENERATOR
 * 
 * Compiles onboarding data into a comprehensive business context JSON.
 * This JSON is used as context for all AI operations in RaptorFlow.
 */

import { StepState } from '@/lib/onboarding-tokens';

export interface BusinessContext {
    version: string;
    generatedAt: string;
    workspaceId: string;
    userId: string;

    // Step 1: Business Basics
    company: {
        name: string;
        website: string;
        industry: string;
        description: string;
    };

    // Step 2: Evidence & Assets
    evidence: {
        uploadedFiles: string[];
        extractedFacts: Record<string, unknown>[];
        classifications: Record<string, unknown>[];
    };

    // Step 3-5: Brand Identity
    brand: {
        values: string[];
        personality: string[];
        tone: string[];
        positioning: string;
    };

    // Step 6-8: Target Market
    market: {
        tamSamSom: {
            tam: number;
            sam: number;
            som: number;
        };
        primaryVerticals: string[];
        geoFocus: string[];
    };

    // Step 9-11: Competitors
    competitors: {
        direct: CompetitorInfo[];
        indirect: CompetitorInfo[];
        positioning: Record<string, unknown>;
    };

    // Step 12-14: ICPs (Ideal Customer Profiles)
    icps: ICP[];

    // Step 15-17: Messaging
    messaging: {
        valueProposition: string;
        taglines: string[];
        keyMessages: string[];
        soundbites: string[];
    };

    // Step 18-20: Channels
    channels: {
        primary: string[];
        secondary: string[];
        strategy: Record<string, unknown>;
    };

    // Step 21-23: Goals & Metrics
    goals: {
        shortTerm: Goal[];
        longTerm: Goal[];
        kpis: string[];
    };

    // Raw step data for AI context
    rawStepData: Record<number, Record<string, unknown>>;
}

interface CompetitorInfo {
    name: string;
    website?: string;
    strengths?: string[];
    weaknesses?: string[];
    positioning?: string;
}

interface ICP {
    name: string;
    title?: string;
    company?: string;
    painPoints?: string[];
    goals?: string[];
    objections?: string[];
}

interface Goal {
    description: string;
    metric?: string;
    target?: string;
    timeline?: string;
}

/**
 * Generate a complete business context from onboarding steps
 */
export function generateBusinessContext(
    steps: StepState[],
    workspaceId: string,
    userId: string
): BusinessContext {
    const rawStepData: Record<number, Record<string, unknown>> = {};

    // Extract data from each step
    steps.forEach(step => {
        if (step.data && Object.keys(step.data).length > 0) {
            rawStepData[step.id] = step.data;
        }
    });

    // Helper to safely get step data
    const getStep = (id: number) => rawStepData[id] || {};

    return {
        version: '1.0.0',
        generatedAt: new Date().toISOString(),
        workspaceId,
        userId,

        // Step 1: Business Basics
        company: {
            name: (getStep(1).companyName as string) || '',
            website: (getStep(1).website as string) || '',
            industry: (getStep(1).industry as string) || '',
            description: (getStep(1).description as string) || '',
        },

        // Step 2: Evidence & Assets
        evidence: {
            uploadedFiles: (getStep(2).files as string[]) || [],
            extractedFacts: (getStep(2).facts as Record<string, unknown>[]) || [],
            classifications: (getStep(2).classifications as Record<string, unknown>[]) || [],
        },

        // Steps 3-5: Brand Identity
        brand: {
            values: (getStep(3).values as string[]) || [],
            personality: (getStep(4).personality as string[]) || [],
            tone: (getStep(5).tone as string[]) || [],
            positioning: (getStep(5).positioning as string) || '',
        },

        // Steps 6-8: Target Market
        market: {
            tamSamSom: {
                tam: (getStep(6).tam as number) || 0,
                sam: (getStep(6).sam as number) || 0,
                som: (getStep(6).som as number) || 0,
            },
            primaryVerticals: (getStep(7).verticals as string[]) || [],
            geoFocus: (getStep(8).geoFocus as string[]) || [],
        },

        // Steps 9-11: Competitors
        competitors: {
            direct: (getStep(9).directCompetitors as CompetitorInfo[]) || [],
            indirect: (getStep(10).indirectCompetitors as CompetitorInfo[]) || [],
            positioning: (getStep(11).positioning as Record<string, unknown>) || {},
        },

        // Steps 12-14: ICPs
        icps: (getStep(12).icps as ICP[]) || (getStep(15).icps as ICP[]) || [],

        // Steps 15-17: Messaging
        messaging: {
            valueProposition: (getStep(13).valueProposition as string) || '',
            taglines: (getStep(16).taglines as string[]) || [],
            keyMessages: (getStep(17).keyMessages as string[]) || [],
            soundbites: (getStep(18).soundbites as string[]) || [],
        },

        // Steps 18-20: Channels
        channels: {
            primary: (getStep(19).primaryChannels as string[]) || [],
            secondary: (getStep(20).secondaryChannels as string[]) || [],
            strategy: (getStep(20).strategy as Record<string, unknown>) || {},
        },

        // Steps 21-23: Goals & Metrics
        goals: {
            shortTerm: (getStep(21).shortTermGoals as Goal[]) || [],
            longTerm: (getStep(22).longTermGoals as Goal[]) || [],
            kpis: (getStep(23).kpis as string[]) || [],
        },

        // Keep raw data for AI reference
        rawStepData,
    };
}

/**
 * Validate business context completeness
 */
export function validateBusinessContext(context: BusinessContext): {
    isValid: boolean;
    missingFields: string[];
    completionPercentage: number;
} {
    const requiredFields = [
        { path: 'company.name', label: 'Company Name' },
        { path: 'company.industry', label: 'Industry' },
        { path: 'brand.positioning', label: 'Brand Positioning' },
        { path: 'icps', label: 'Ideal Customer Profiles' },
        { path: 'messaging.valueProposition', label: 'Value Proposition' },
    ];

    const missingFields: string[] = [];
    let completedCount = 0;

    requiredFields.forEach(field => {
        const value = getNestedValue(context, field.path);
        if (!value || (Array.isArray(value) && value.length === 0)) {
            missingFields.push(field.label);
        } else {
            completedCount++;
        }
    });

    return {
        isValid: missingFields.length === 0,
        missingFields,
        completionPercentage: Math.round((completedCount / requiredFields.length) * 100),
    };
}

function getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
}

/**
 * Convert business context to prompt-friendly format
 */
export function contextToPrompt(context: BusinessContext): string {
    return `
## Business Context

### Company Overview
- Name: ${context.company.name}
- Industry: ${context.company.industry}
- Website: ${context.company.website}
- Description: ${context.company.description}

### Brand Identity
- Values: ${context.brand.values.join(', ')}
- Personality: ${context.brand.personality.join(', ')}
- Tone: ${context.brand.tone.join(', ')}
- Positioning: ${context.brand.positioning}

### Target Market
- TAM: $${(context.market.tamSamSom.tam / 1000000).toFixed(1)}M
- SAM: $${(context.market.tamSamSom.sam / 1000000).toFixed(1)}M
- SOM: $${(context.market.tamSamSom.som / 1000000).toFixed(1)}M
- Primary Verticals: ${context.market.primaryVerticals.join(', ')}
- Geographic Focus: ${context.market.geoFocus.join(', ')}

### Ideal Customer Profiles
${context.icps.map((icp, i) => `${i + 1}. ${icp.name}${icp.title ? ` (${icp.title})` : ''}`).join('\n')}

### Messaging
- Value Proposition: ${context.messaging.valueProposition}
- Key Messages: ${context.messaging.keyMessages.join('; ')}

### Channels
- Primary: ${context.channels.primary.join(', ')}
- Secondary: ${context.channels.secondary.join(', ')}

### Goals
${context.goals.shortTerm.map(g => `- ${g.description}`).join('\n')}
  `.trim();
}
