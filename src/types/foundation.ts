export interface Demographics {
    role: string;
    stage: string;
}

export type MarketSophisticationLevel = 1 | 2 | 3 | 4 | 5;

export interface RICP {
    id: string;
    name: string;
    personaName?: string;
    avatar?: string;
    demographics: Demographics;
    marketSophistication: MarketSophisticationLevel;
    confidence?: number;
    painPoints: string[];
    goals: string[];
    objections: string[];
}

export interface CoreMessaging {
    oneLiner: string;
    valueProps: string[];
    brandVoice: {
        tone: string[];
        style: string;
    };
    confidence: number;
}

export interface Channel {
    id: string;
    name: string;
    priority: 'primary' | 'secondary' | 'experimental';
    status: 'active' | 'planned' | 'paused';
}

export const MARKET_SOPHISTICATION_LABELS: Record<number, { name: string; desc: string }> = {
    1: { name: "First to Market", desc: "Make the claim." },
    2: { name: "Competition Arrives", desc: "Expand the claim." },
    3: { name: "Feature Wars", desc: "Specific mechanism." },
    4: { name: "Market Saturation", desc: "Exhausted claims." },
    5: { name: "Identity/Belief", desc: "Identification." },
};
