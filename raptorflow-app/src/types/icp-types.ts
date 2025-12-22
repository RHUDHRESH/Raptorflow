export type IcpPriority = 'primary' | 'secondary';
export type IcpStatus = 'draft' | 'active' | 'deprecated';
export type UrgencyLevel = 'now' | 'soon' | 'someday';
export type IcpCompanyType = 'saas' | 'd2c' | 'agency' | 'service';
export type IcpSalesMotion = 'self-serve' | 'demo-led' | 'sales-assisted';

export interface Icp {
    id: string;
    workspaceId: string;
    name: string;
    priority: IcpPriority;
    status: IcpStatus;
    confidenceScore: number; // 0.00 to 1.00
    createdAt: string;
    updatedAt: string;

    // Relations
    firmographics: IcpFirmographics;
    painMap: IcpPainMap;
    psycholinguistics: IcpPsycholinguistics;
    disqualifiers: IcpDisqualifiers;
    performance?: IcpPerformance;
}

export interface IcpFirmographics {
    companyType: IcpCompanyType[];
    companySizeMin?: number;
    companySizeMax?: number;
    geography: string[];
    acvMin?: number;
    acvMax?: number;
    salesMotion: IcpSalesMotion[];
    budgetComfort: string[]; // 'low', 'medium', 'high', 'enterprise'
    decisionMaker: string[]; // 'founder', 'marketing_manager', etc.
}

export interface IcpPainMap {
    primaryPains: string[]; // Max 2
    secondaryPains: string[];
    triggerEvents: string[];
    urgencyLevel: UrgencyLevel;
}

export interface IcpPsycholinguistics {
    mindsetTraits: string[]; // 'skeptical', 'data-driven'
    emotionalTriggers: string[];
    tonePreference: string[];
    wordsToUse: string[];
    wordsToAvoid: string[];
    proofPreference: string[]; // 'case-study', 'data', 'logos'
    ctaStyle: string[]; // 'soft', 'direct'
}

export interface IcpDisqualifiers {
    excludedCompanyTypes: string[];
    excludedSizes?: string[];
    excludedGeographies: string[];
    excludedBehaviors: string[];
}

export interface IcpPerformance {
    impressions: number;
    leads: number;
    conversions: number;
    avgConversionRate: number;
    lastEvaluatedAt: string;
    confidenceAdjustment: number;
    notes?: string;
}

// Memory Object (Agent Facing)
export interface IcpMemory {
    id: string;
    priority: IcpPriority;
    confidence: number;
    targeting: {
        who: string[];
        whoNot: string[];
        budget: string[];
        urgency: UrgencyLevel;
    };
    pains: {
        primary: string[];
        triggers: string[];
    };
    language: {
        tone: string[];
        wordsToUse: string[];
        wordsToAvoid: string[];
        proofStyle: string[];
        ctaStyle: string[];
    };
}
