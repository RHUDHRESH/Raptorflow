/* ══════════════════════════════════════════════════════════════════════════════
   FOUNDATION TYPES — RICP & Messaging Frameworks
   Rich Ideal Customer Profiles and StoryBrand Messaging
   ══════════════════════════════════════════════════════════════════════════════ */

// Market Sophistication Stages (Eugene Schwartz)
export type MarketSophisticationStage = 1 | 2 | 3 | 4 | 5;

export const MARKET_SOPHISTICATION_LABELS: Record<MarketSophisticationStage, { name: string; description: string }> = {
    1: { name: "Unaware", description: "Doesn't know they have a problem" },
    2: { name: "Problem Aware", description: "Knows the problem, seeking solutions" },
    3: { name: "Solution Aware", description: "Knows solutions exist, evaluating options" },
    4: { name: "Product Aware", description: "Knows your product, comparing to others" },
    5: { name: "Most Aware", description: "Ready to buy, needs final push" },
};

// ══════════════════════════════════════════════════════════════════════════════
// RICP (Rich Ideal Customer Profile)
// ══════════════════════════════════════════════════════════════════════════════

export interface RICPDemographics {
    ageRange: string;           // "32-45 years old"
    income: string;             // "$150,000 - $400,000"
    location: string;           // "Urban tech hubs (SF, NYC, Austin)"
    role: string;               // "Founder/CEO of B2B SaaS"
    stage: string;              // "Seed to Series A"
}

export interface RICPPsychographics {
    // Mindset
    beliefs: string;            // "Marketing should be measurable and strategic"
    identity: string;           // "A builder who is technical but knows marketing is the bottleneck"
    becoming: string;           // "A CEO who understands GTM as well as product"
    fears: string;              // "Wasting money on agencies that don't understand their business"
    values: string[];           // ["Speed", "Clarity", "Data-driven decisions"]

    // Behaviors
    hangouts: string[];         // ["Twitter/X", "YC forums", "Indie Hacker communities"]
    contentConsumed: string[];  // ["Lenny's Podcast", "My First Million", "SaaS newsletters"]
    whoTheyFollow: string[];    // ["Successful founders", "Marketing operators"]

    // Triggers & Timing
    language: string[];         // ["CAC", "LTV", "PMF", "growth loops", "positioning"]
    timing: string[];           // ["Sunday evenings", "Wednesday mornings"]
    triggers: string[];         // ["Plateaued growth", "Raising funding", "Hiring first marketer"]
}

export interface RICP {
    id: string;
    name: string;               // "Ambitious SaaS Founder" (cohort name)
    personaName?: string;       // "Sarah" (optional persona name)
    avatar?: string;            // Emoji or image URL

    demographics: RICPDemographics;
    psychographics: RICPPsychographics;
    marketSophistication: MarketSophisticationStage;

    // Metadata
    createdAt: number;
    updatedAt: number;
    confidence?: number;        // 0-100
}

// ══════════════════════════════════════════════════════════════════════════════
// CORE MESSAGING
// ══════════════════════════════════════════════════════════════════════════════

export interface PositioningStatement {
    target: string;             // "B2B SaaS founders"
    situation: string;          // "who struggle with inconsistent marketing"
    product: string;            // "RaptorFlow"
    category: string;           // "Marketing Operating System"
    keyBenefit: string;         // "converts chaos into clarity"
    alternatives: string;       // "random posting and agency guesswork"
    differentiator: string;     // "it's built by founders, for founders"
}

export interface ValueProp {
    title: string;              // "Clarity"
    description: string;        // "Know exactly what to say and who to say it to"
    proof?: string;             // "92% positioning confidence score"
}

export interface BrandVoice {
    tone: string[];             // ["Calm", "Precise", "Confident", "Surgical"]
    doList: string[];           // ["Short sentences", "Strong verbs", "Data-backed claims"]
    dontList: string[];         // ["Emojis in product UI", "Hype words", "Unproven claims"]
}

export interface StoryBrand {
    character: string;          // "Sarah, the ambitious SaaS founder"
    problemExternal: string;    // "Plateaued growth"
    problemInternal: string;    // "Feeling overwhelmed and out of control"
    problemPhilosophical: string; // "Marketing shouldn't be this hard"
    guide: string;              // "RaptorFlow - the calm, surgical system"
    plan: string[];             // ["Define Foundation", "Create Moves", "Execute & Track"]
    callToAction: string;       // "Start your first Move"
    transitionalCTA?: string;   // "See how it works"
    avoidFailure: string[];     // ["Continued random posting", "Wasted ad spend", "Founder burnout"]
    success: string[];          // ["Marketing under control", "Predictable growth", "Focus on product"]
}

export interface CoreMessaging {
    id: string;
    oneLiner: string;           // "RaptorFlow is the marketing operating system for founders who want control, not chaos."
    positioningStatement: PositioningStatement;
    valueProps: ValueProp[];    // Max 3
    brandVoice: BrandVoice;
    storyBrand: StoryBrand;

    // Metadata
    updatedAt: number;
    confidence?: number;
}

// ══════════════════════════════════════════════════════════════════════════════
// CHANNEL STRATEGY
// ══════════════════════════════════════════════════════════════════════════════

export interface Channel {
    id: string;
    name: string;               // "LinkedIn"
    priority: "primary" | "secondary" | "experimental";
    status: "active" | "planned" | "paused";
    notes?: string;
}

// ══════════════════════════════════════════════════════════════════════════════
// FOUNDATION STATE
// ══════════════════════════════════════════════════════════════════════════════

export interface FoundationState {
    ricps: RICP[];
    messaging: CoreMessaging | null;
    channels: Channel[];
    positioningConfidence: number;
}
