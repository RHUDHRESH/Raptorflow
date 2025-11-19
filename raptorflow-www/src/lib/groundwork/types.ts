/**
 * Groundwork type definitions
 */

export type SectionId = 
  | 'business-identity'
  | 'audience-icp'
  | 'goals-constraints'
  | 'assets-visuals'
  | 'brand-energy';

export interface BusinessIdentityData {
  productDescription: string;
  whoPays: string;
  whoUses: string;
  location?: {
    address: string;
    lat: number;
    lng: number;
    formattedAddress: string;
  };
  legalName?: string;
  gstNumber?: string;
  businessUrl?: string;
}

export interface ICPData {
  id: string;
  name: string;
  role?: string;
  industry?: string;
  painPoints: string[];
  buyingBehavior?: 'fast' | 'slow' | 'comparison' | 'impulse';
}

export interface AudienceICPData {
  icps: ICPData[];
}

export interface GoalsConstraintsData {
  primaryGoal: 'reach' | 'trust' | 'sales' | 'awareness' | 'custom';
  customGoal?: string;
  successMetric: string;
  targetValue: number;
  timeframe: 7 | 14 | 30 | 60 | 90;
  showUpFrequency: 'daily' | '3x-week' | 'weekly';
  marketingPainPoints: string[];
  teamSize: 'solo' | 'small-team' | 'agency';
}

export interface UploadedFile {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  preview?: string;
  ocrStatus?: 'pending' | 'processing' | 'completed' | 'failed';
  extractedData?: Record<string, unknown>;
}

export interface AssetsVisualsData {
  files: UploadedFile[];
}

export interface BrandEnergyData {
  toneSliders: {
    chillBold: number; // 0-100, 0 = chill, 100 = bold
    nerdyMassy: number; // 0-100, 0 = nerdy, 100 = massy
    eliteApproachable: number; // 0-100, 0 = elite, 100 = approachable
  };
  voiceSample?: string;
  admiredBrands: string[];
}

export type SectionData = 
  | BusinessIdentityData
  | AudienceICPData
  | GoalsConstraintsData
  | AssetsVisualsData
  | BrandEnergyData;

export interface AgentQuestion {
  id: string;
  section: SectionId;
  question: string;
  context: string;
  priority: 'high' | 'medium' | 'low';
  suggestedAnswer?: string;
}

export interface SectionState {
  completed: boolean;
  data: SectionData | null;
  agentQuestions: AgentQuestion[];
}

export interface GroundworkState {
  currentSection: SectionId;
  sections: {
    [key in SectionId]: SectionState;
  };
  phase: 'structured' | 'dynamic';
  isSubmitting: boolean;
}

export interface SectionConfig {
  id: SectionId;
  title: string;
  question: string;
  description?: string;
}

