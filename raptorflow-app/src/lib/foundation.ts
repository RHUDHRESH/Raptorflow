import { z } from 'zod';

// ==========================================
// Enums / Unions
// ==========================================

// Legacy types (kept for backward compatibility)
export type BusinessStage = 'idea' | 'pre-launch' | 'beta' | 'live' | 'scaling' | 'early' | 'growth'; // Updated + legacy
export type RevenueModel = 'saas' | 'services' | 'product' | 'marketplace' | 'other';
export type TeamSize = 'solo' | '2-5' | '6-20' | '20+';

export type CustomerType = 'b2b' | 'b2c' | 'b2g' | 'mixed';
export type SCARFDriver = 'status' | 'certainty' | 'autonomy' | 'relatedness' | 'fairness';
export type DecisionStyle = 'satisficer' | 'maximizer';
export type RiskTolerance = 'regret-minimizer' | 'opportunity-seeker';

// ==========================================
// New Types for Know You Flow
// ==========================================

export type BusinessType = 'saas' | 'agency' | 'd2c' | 'local-service' | 'creator' | 'marketplace' | 'other';
export type PriceBand = 'free' | 'under-5k' | '5k-25k' | '25k-1l' | '1l-plus';
export type SalesMotion = 'self-serve' | 'demo-led' | 'hybrid';
export type BuyerRoleChip = 'founder' | 'marketing' | 'sales' | 'hr' | 'ops' | 'finance' | 'other';
export type RegionCode = 'india' | 'us' | 'eu' | 'global' | 'other';
export type LanguageCode = 'english' | 'hinglish' | 'tamil' | 'hindi' | 'other';
export type PrimaryGoal = 'leads' | 'close-deals' | 'increase-conversion' | 'content-engine' | 'launch' | 'retention';
export type Constraint = 'low-budget' | 'no-time' | 'no-design' | 'compliance' | 'no-audience';
export type Channel = 'linkedin' | 'instagram' | 'whatsapp' | 'email' | 'youtube' | 'seo' | 'ads' | 'offline';
export type ToolOption = 'none' | 'sheets' | 'notion' | 'hubspot' | 'zoho' | 'pipedrive' | 'mailchimp' | 'klaviyo' | 'other';
export type ProofType = 'testimonials' | 'case-study' | 'metrics' | 'logos' | 'none';
export type VoicePreference = 'calm-premium' | 'direct-punchy' | 'friendly-warm' | 'technical-precise' | 'bold-contrarian';

// NEW: Trigger event types
export type TriggerEvent =
  | 'hiring-surge' | 'funding-round' | 'missed-target' | 'compliance-change'
  | 'competitor-threat' | 'tech-migration' | 'team-expansion' | 'churn-spike'
  | 'reorg' | 'new-leadership' | 'budget-approval' | 'seasonal-peak';

// NEW: Alternative/competitor types
export type AlternativeType =
  | 'spreadsheets' | 'notion' | 'hubspot' | 'marketo' | 'agencies'
  | 'freelancers' | 'zapier-glue' | 'internal-team' | 'nothing';

// ==========================================
// Section Data Interfaces
// ==========================================

export interface BusinessBasics {
  name: string;
  industry: string;
  stage: BusinessStage | '';
  businessType?: BusinessType | '';        // NEW: Type of business
  revenueModel: RevenueModel[] | RevenueModel | '';
  teamSize: TeamSize | '';
  contextFiles?: string[];
  websiteUrl?: string;                     // NEW: The one link
  offerStatement?: string;                 // NEW: One-line offer
  priceBand?: PriceBand | '';              // NEW
  salesMotion?: SalesMotion | '';          // NEW
}

export interface ConfessionData {
  expensiveProblem: string;
  embarrassingTruth: string;
  stupidIdea: string;
  signaling: string;
  friction: string;
}

export interface CohortData {
  customerType: CustomerType[] | CustomerType | '';
  buyerRole: string;
  buyerRoleChips?: BuyerRoleChip[];        // NEW: Chip-based buyer role
  primaryRegions?: RegionCode[];            // NEW: Regions where they sell
  languages?: LanguageCode[];               // NEW: Languages they use
  primaryDrivers: SCARFDriver[];
  decisionStyle: DecisionStyle | '';
  riskTolerance: RiskTolerance | '';
  // B2B conditional fields
  companySize?: string;
  salesCycle?: string;
  // D2C conditional field
  averageOrderValue?: string;
}

export interface PositioningData {
  category: string;
  targetAudience: string;
  psychologicalOutcome: string;
  ownedPosition: string;
  reframedWeakness: string;
}

export interface MessagingData {
  primaryHeuristic: string;
  beliefPillar: string;
  promisePillar: string;
  proofPillar: string;
  voicePreference?: VoicePreference | '';   // NEW: Voice preference
}

// NEW: Goals section for Know You flow
export interface GoalsData {
  primaryGoal?: PrimaryGoal | '';
  constraints?: Constraint[];
}

// NEW: Current reality section
export interface CurrentRealityData {
  currentChannels?: Channel[];
  currentTools?: ToolOption[];
}

// NEW: Proof inventory section
export interface ProofData {
  proofTypes?: ProofType[];
}

// NEW: Customer insights section (best customers, triggers, alternatives, pains)
export interface CustomerInsightsData {
  bestCustomers?: string[];           // 3 best customer descriptions
  triggerEvents?: TriggerEvent[];     // What makes them buy now
  alternatives?: AlternativeType[];   // What they used before
  painRanking?: string[];             // Ranked list of pains
}

// ==========================================
// Derived Data Interfaces (from Backend)
// ==========================================

// ICP Reveal Response
export interface DerivedICP {
  id: string;
  name: string;
  priority: 'primary' | 'secondary' | 'expansion';
  confidence: number;
  description: string;

  firmographics: {
    companySize: string;
    industry: string[];
    geography: string[];
    budget: string;
  };

  painMap: {
    primary: string;
    secondary: string[];
    triggers: string[];
    urgency: 'now' | 'soon' | 'someday';
  };

  social: {
    platforms: Array<{ name: string; timing: string; vibe: string }>;
    authorities: string[];
  };

  buying: {
    committee: Array<{ role: string; focus: string }>;
    timeline: string;
    proofNeeded: string[];
    blockers: string[];
  };

  behavioral: {
    biases: Array<{ name: string; implication: string }>;
    deRisking: string[];
  };
}

// Positioning Reveal Response
export interface DerivedPositioning {
  matrix: {
    xAxis: { label: string; lowEnd: string; highEnd: string };
    yAxis: { label: string; lowEnd: string; highEnd: string };
    positions: Array<{ name: string; x: number; y: number; isYou: boolean }>;
  };

  ladder: Array<{
    rung: number;
    name: string;
    description: string;
    score: number;
    isYou: boolean;
  }>;

  statement: {
    forWhom: string;
    company: string;
    category: string;
    differentiator: string;
    unlikeCompetitor: string;
    because: string;
  };

  oneThing: string;
  defensibility: 'low' | 'medium' | 'high';
}

// Competitive Reveal Response
export interface DerivedCompetitive {
  statusQuo: {
    name: string;
    description: string;
    manualPatches: string[];
    toleratedPain: string;
    yourWedge: string;
  };

  indirect: Array<{
    name: string;
    mechanism: string;
    priceRange: string;
    weakness: string;
    yourEdge: string;
  }>;

  direct: Array<{
    name: string;
    positioning: string;
    weakness: string;
    yourEdge: string;
    featureOverlap: 'low' | 'medium' | 'high';
  }>;
}

// Soundbites Reveal Response
export interface DerivedSoundbites {
  oneLiner: string;

  soundbites: Array<{
    type: 'problem' | 'agitation' | 'mechanism' | 'objection' | 'transformation' | 'proof' | 'urgency';
    awarenessLevel: 'unaware' | 'problem' | 'solution' | 'product' | 'most';
    text: string;
    useCase: string;
  }>;
}

// Market Reveal Response
export interface DerivedMarket {
  tam: { value: number; confidence: 'low' | 'med' | 'high'; method: string };
  sam: { value: number; confidence: 'low' | 'med' | 'high'; method: string };
  som: { value: number; confidence: 'low' | 'med' | 'high'; timeline: string };

  assumptions: Array<{
    factor: string;
    value: string;
    confidence: 'low' | 'med' | 'high';
  }>;

  pathToSom: {
    customersNeeded: number;
    leadsPerMonth: number;
    winRate: number;
    channelMix: Array<{ channel: string; percentage: number }>;
  };

  sliderDefaults: {
    targetAccounts: number;
    reachablePercent: number;
    qualifiedPercent: number;
    adoptionPercent: number;
    arpa: number;
  };
}

// Combined Derived Data
export interface DerivedData {
  derivedAt?: string;
  icps?: DerivedICP[];
  positioning?: DerivedPositioning;
  competitive?: DerivedCompetitive;
  soundbites?: DerivedSoundbites;
  market?: DerivedMarket;
}

// ==========================================
// Main Foundation Data
// ==========================================

export const brandKitSchema = z.object({
  brandVoice: z.string().min(1, 'Brand voice is required'),
  positioning: z.string().min(1, 'Positioning statement is required'),
  messagingPillars: z.array(z.string().min(1))
    .min(1, 'At least one messaging pillar is required')
    .max(5, 'Maximum of 5 messaging pillars allowed'),
});

export type BrandKit = z.infer<typeof brandKitSchema>;

export const defaultBrandKit: BrandKit = {
  brandVoice: '',
  positioning: '',
  messagingPillars: [''],
};

export interface FoundationData {
  currentStep: number;
  completedAt?: string;

  // Core sections
  business: BusinessBasics;
  confession: ConfessionData;
  cohorts: CohortData;
  positioning: PositioningData;
  messaging: MessagingData;

  // Know You sections
  goals?: GoalsData;
  reality?: CurrentRealityData;
  proof?: ProofData;
  customerInsights?: CustomerInsightsData;  // NEW

  // Derived data (from backend)
  derived?: DerivedData;  // NEW

  // Legacy support
  brandVoice?: string;
}

// ==========================================
// Initial State
// ==========================================

export const emptyFoundation: FoundationData = {
  currentStep: 0,
  business: {
    name: '',
    industry: '',
    stage: '',
    businessType: '',
    revenueModel: '',
    teamSize: '',
    websiteUrl: '',
    offerStatement: '',
    priceBand: '',
    salesMotion: '',
  },
  confession: {
    expensiveProblem: '',
    embarrassingTruth: '',
    stupidIdea: '',
    signaling: '',
    friction: ''
  },
  cohorts: {
    customerType: '',
    buyerRole: '',
    buyerRoleChips: [],
    primaryRegions: [],
    languages: [],
    primaryDrivers: [],
    decisionStyle: '',
    riskTolerance: '',
    companySize: '',
    salesCycle: '',
    averageOrderValue: '',
  },
  positioning: {
    category: '',
    targetAudience: '',
    psychologicalOutcome: '',
    ownedPosition: '',
    reframedWeakness: ''
  },
  messaging: {
    primaryHeuristic: '',
    beliefPillar: '',
    promisePillar: '',
    proofPillar: '',
    voicePreference: '',
  },
  goals: {
    primaryGoal: '',
    constraints: [],
  },
  reality: {
    currentChannels: [],
    currentTools: [],
  },
  proof: {
    proofTypes: [],
  },
  brandVoice: ''
};

// ==========================================
// Storage & Helpers
// ==========================================

const STORAGE_KEY = 'rf_brand_kit';
const FOUNDATION_STORAGE_KEY = 'rf_foundation';

export const saveBrandKit = (kit: BrandKit) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(kit));
  }
};

export const getBrandKit = (): BrandKit | null => {
  if (typeof window !== 'undefined') {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  }
  return null;
};

export const saveFoundation = (data: FoundationData) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(FOUNDATION_STORAGE_KEY, JSON.stringify(data));

    // Sync minimal data to legacy brand kit
    const legacyKit: BrandKit = {
      brandVoice: data.brandVoice || '',
      positioning: `We are the ${data.positioning.category} for ${data.positioning.targetAudience} who want ${data.positioning.psychologicalOutcome}.`,
      messagingPillars: [data.messaging.beliefPillar, data.messaging.promisePillar, data.messaging.proofPillar].filter(Boolean)
    };
    if (legacyKit.messagingPillars.length === 0) legacyKit.messagingPillars = [''];
    saveBrandKit(legacyKit);
  }
};

export const loadFoundation = (): FoundationData => {
  if (typeof window !== 'undefined') {
    const data = localStorage.getItem(FOUNDATION_STORAGE_KEY);
    if (data) return JSON.parse(data);

    // Fallback to legacy brand kit if foundation missing
    const kit = getBrandKit();
    if (kit) {
      return {
        ...emptyFoundation,
        brandVoice: kit.brandVoice,
      };
    }
  }
  return emptyFoundation;
};

export const ONBOARDING_STEPS = [
  { id: 'business', name: 'Business Basics', description: 'Your core identity' },
  { id: 'confession', name: 'Confession', description: 'Current reality check' },
  { id: 'cohorts', name: 'Cohorts', description: 'Who you serve' },
  { id: 'positioning', name: 'Positioning', description: 'How you win' },
  { id: 'messaging', name: 'Messaging', description: 'What you say' },
  { id: 'review', name: 'Review', description: 'Verify & Launch' },
];
