import { IcpCompanyType, IcpSalesMotion } from '@/types/icp-types';

/**
 * ICP Templates Library
 * Pre-built archetypes that get customized with Foundation data
 */

export interface IcpTemplate {
  id: string;
  defaultName: string;
  reasoning: string;

  // Base firmographics
  baseCompanyType: IcpCompanyType[];
  baseSalesMotion: IcpSalesMotion[];
  baseBudgetComfort: string[];
  baseDecisionMaker: string[];

  // Base pains
  defaultSecondaryPains: string[];

  // Base psycholinguistics
  baseTone: string[];
  baseWordsToUse: string[];
  baseWordsToAvoid: string[];

  // Disqualifiers
  excludedTypes: string[];
  excludedBehaviors: string[];
}

export const ICP_TEMPLATES: Record<string, IcpTemplate> = {
  techFounder: {
    id: 'tech-founder',
    defaultName: 'The Tech-Savvy Founder',
    reasoning:
      'Based on your B2B focus and founder-level buyer role, this ICP targets ambitious tech founders who need efficient solutions.',

    baseCompanyType: ['saas'],
    baseSalesMotion: ['self-serve', 'demo-led'],
    baseBudgetComfort: ['medium', 'high'],
    baseDecisionMaker: ['founder', 'ceo'],

    defaultSecondaryPains: [
      'Too many tools, not enough integration',
      'Time wasted on manual work',
    ],

    baseTone: ['direct', 'confident', 'no-nonsense'],
    baseWordsToUse: ['scale', 'automate', 'leverage', 'ROI', 'efficiency'],
    baseWordsToAvoid: ['maybe', 'possibly', 'traditional', 'manual'],

    excludedTypes: ['enterprise', 'government'],
    excludedBehaviors: [
      'Needs long procurement cycles',
      'Risk-averse committees',
    ],
  },

  corporateDecider: {
    id: 'corporate-decider',
    defaultName: 'The Corporate Decision Maker',
    reasoning:
      'Based on your enterprise-level targeting, this ICP captures senior executives who prioritize proven solutions.',

    baseCompanyType: ['saas', 'service'],
    baseSalesMotion: ['sales-assisted', 'demo-led'],
    baseBudgetComfort: ['high', 'enterprise'],
    baseDecisionMaker: ['vp', 'director', 'cmo'],

    defaultSecondaryPains: [
      'Need to justify decisions to board',
      'Risk of picking wrong vendor',
    ],

    baseTone: ['professional', 'consultative', 'authoritative'],
    baseWordsToUse: [
      'enterprise-grade',
      'proven',
      'trusted',
      'secure',
      'compliant',
    ],
    baseWordsToAvoid: ['disrupt', 'hack', 'scrappy', 'beta'],

    excludedTypes: ['startup'],
    excludedBehaviors: ['Price shoppers', 'DIY culture'],
  },

  smbOperator: {
    id: 'smb-operator',
    defaultName: 'The SMB Operator',
    reasoning:
      'Targets hands-on business operators who need practical, affordable solutions.',

    baseCompanyType: ['service', 'd2c'],
    baseSalesMotion: ['self-serve'],
    baseBudgetComfort: ['low', 'medium'],
    baseDecisionMaker: ['owner', 'manager'],

    defaultSecondaryPains: [
      'Limited budget constraints',
      'Wearing too many hats',
    ],

    baseTone: ['friendly', 'practical', 'empathetic'],
    baseWordsToUse: ['simple', 'affordable', 'save time', 'easy', 'all-in-one'],
    baseWordsToAvoid: ['enterprise', 'complex', 'comprehensive'],

    excludedTypes: ['enterprise'],
    excludedBehaviors: ['Needs white-glove service'],
  },

  marketingLead: {
    id: 'marketing-lead',
    defaultName: 'The Marketing Lead',
    reasoning:
      'Targets marketing professionals who need to prove their impact and move fast.',

    baseCompanyType: ['saas', 'agency'],
    baseSalesMotion: ['demo-led', 'self-serve'],
    baseBudgetComfort: ['medium'],
    baseDecisionMaker: ['marketing_manager', 'head_of_marketing'],

    defaultSecondaryPains: [
      'Pressure to show results',
      'Limited resources vs. expectations',
    ],

    baseTone: ['strategic', 'creative', 'data-backed'],
    baseWordsToUse: ['ROI', 'conversion', 'attribution', 'campaigns', 'growth'],
    baseWordsToAvoid: ['vanity metrics', 'spray and pray'],

    excludedTypes: [],
    excludedBehaviors: ['Pure brand focus', 'No metrics culture'],
  },

  earlyAdopter: {
    id: 'early-adopter',
    defaultName: 'The Early Adopter',
    reasoning:
      'Based on your early stage and B2C focus, this ICP targets trend-conscious consumers who love being first.',

    baseCompanyType: ['d2c'],
    baseSalesMotion: ['self-serve'],
    baseBudgetComfort: ['low', 'medium'],
    baseDecisionMaker: ['consumer'],

    defaultSecondaryPains: [
      'FOMO on new solutions',
      'Tired of outdated alternatives',
    ],

    baseTone: ['exciting', 'exclusive', 'innovative'],
    baseWordsToUse: [
      'first',
      'new',
      'exclusive',
      'innovative',
      'before everyone',
    ],
    baseWordsToAvoid: ['proven', 'traditional', 'established'],

    excludedTypes: [],
    excludedBehaviors: ['Waits for reviews', 'Late majority'],
  },

  massMarket: {
    id: 'mass-market',
    defaultName: 'The Pragmatic Consumer',
    reasoning:
      'Targets mainstream consumers who want proven, trusted solutions.',

    baseCompanyType: ['d2c'],
    baseSalesMotion: ['self-serve'],
    baseBudgetComfort: ['low', 'medium'],
    baseDecisionMaker: ['consumer'],

    defaultSecondaryPains: [
      'Information overload',
      'Fear of making wrong choice',
    ],

    baseTone: ['reassuring', 'friendly', 'clear'],
    baseWordsToUse: ['trusted', 'popular', 'loved by', 'simple', 'guaranteed'],
    baseWordsToAvoid: ['experimental', 'beta', 'cutting-edge'],

    excludedTypes: [],
    excludedBehaviors: ['Needs customization'],
  },
};

/**
 * Get template by ID
 */
export function getTemplate(id: string): IcpTemplate | undefined {
  return Object.values(ICP_TEMPLATES).find((t) => t.id === id);
}

/**
 * Get all templates
 */
export function getAllTemplates(): IcpTemplate[] {
  return Object.values(ICP_TEMPLATES);
}
