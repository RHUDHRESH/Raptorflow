export interface Demographics {
    ageRange: string;
    income: string;
    location: string;
    role: string;
    stage: string;
}

export type MarketSophisticationStage = 1 | 2 | 3 | 4 | 5;

export interface Psychographics {
    beliefs: string;
    identity: string;
    becoming: string;
    fears: string;
    values: string[];
    hangouts: string[];
    contentConsumed: string[];
    whoTheyFollow: string[];
    language: string[];
    timing: string[];
    triggers: string[];
}

export interface RICP {
    id: string;
    name: string;
    personaName?: string;
    avatar?: string;
    demographics: Demographics;
    psychographics: Psychographics;
    marketSophistication: MarketSophisticationStage;
    confidence?: number;
    painPoints: string[];
    goals: string[];
    objections: string[];
    createdAt?: number;
    updatedAt?: number;
}

export interface ValueProp {
    title: string;
    description: string;
    proof?: string;
}

export interface CoreMessaging {
    id?: string;
    oneLiner: string;
    positioningStatement: {
        target: string;
        situation: string;
        product: string;
        category: string;
        keyBenefit: string;
        alternatives: string;
        differentiator: string;
    };
    valueProps: ValueProp[];
    brandVoice: {
        tone: string[];
        doList: string[];
        dontList: string[];
    };
    storyBrand: {
        character: string;
        problemExternal: string;
        problemInternal: string;
        problemPhilosophical: string;
        guide: string;
        plan: string[];
        callToAction: string;
        transitionalCTA: string;
        avoidFailure: string[];
        success: string[];
    };
    confidence: number;
    updatedAt?: number;
}

export interface Channel {
    id: string;
    name: string;
    priority: 'primary' | 'secondary' | 'experimental';
    status: 'active' | 'planned' | 'paused';
}

export interface FoundationState {
    ricps: RICP[];
    messaging: CoreMessaging | null;
    channels: Channel[];
    positioningConfidence: number;
}

export const MARKET_SOPHISTICATION_LABELS: Record<number, { name: string; description: string }> = {
    1: { name: "First to Market", description: "Make the claim." },
    2: { name: "Competition Arrives", description: "Expand the claim." },
    3: { name: "Feature Wars", description: "Specific mechanism." },
    4: { name: "Market Saturation", description: "Exhausted claims." },
    5: { name: "Identity/Belief", description: "Identification." },
};
