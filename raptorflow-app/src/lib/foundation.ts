import { z } from 'zod';

// ==========================================
// Enums / Unions
// ==========================================

export type BusinessStage = 'idea' | 'early' | 'growth' | 'scaling';
export type RevenueModel = 'saas' | 'services' | 'product' | 'marketplace' | 'other';
export type TeamSize = 'solo' | '2-5' | '6-20' | '20+';

export type CustomerType = 'b2b' | 'b2c' | 'b2g' | 'mixed';
export type SCARFDriver = 'status' | 'certainty' | 'autonomy' | 'relatedness' | 'fairness';
export type DecisionStyle = 'satisficer' | 'maximizer';
export type RiskTolerance = 'regret-minimizer' | 'opportunity-seeker';

// ==========================================
// Section Data Interfaces
// ==========================================

export interface BusinessBasics {
  name: string;
  industry: string;
  stage: BusinessStage | '';
  revenueModel: RevenueModel[] | RevenueModel | '';
  teamSize: TeamSize | '';
  contextFiles?: string[];
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
  primaryDrivers: SCARFDriver[];
  decisionStyle: DecisionStyle | '';
  riskTolerance: RiskTolerance | '';
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

  // Sections
  business: BusinessBasics;
  confession: ConfessionData;
  cohorts: CohortData;
  positioning: PositioningData;
  messaging: MessagingData;

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
    revenueModel: '',
    teamSize: ''
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
    primaryDrivers: [],
    decisionStyle: '',
    riskTolerance: ''
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
    proofPillar: ''
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
