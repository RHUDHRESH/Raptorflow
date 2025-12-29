import { Skill } from './skill-selector';

export const SYSTEM_SKILLS: Skill[] = [
  {
    id: 'cold_email_founder_soft',
    name: 'Soft Founder Outreach',
    owner: 'system',
    intent: 'cold_outreach',
    compatiblePains: [
      'Founder doing marketing themselves',
      'No positioning clarity',
    ],
    compatibleUrgency: ['now', 'soon'],
    compatibleTone: ['Calm', 'Empathetic'],
    compatibleCta: ['soft'],
    incompatibleTraits: ['Enterpise'],
    minIcpConfidence: 0.6,
    baseQualityScore: 0.8,
  },
  {
    id: 'cold_email_direct_sales',
    name: 'Direct Sales Pitch',
    owner: 'system',
    intent: 'cold_outreach',
    compatiblePains: ['Leads are inconsistent', 'Pipeline unpredictable'],
    compatibleUrgency: ['now'],
    compatibleTone: ['Direct', 'Bold'],
    compatibleCta: ['direct'],
    incompatibleTraits: ['Hates marketing jargon', 'Skeptical of agencies'],
    minIcpConfidence: 0.7,
    baseQualityScore: 0.75,
  },
  {
    id: 'generic_cold_outreach',
    name: 'Generic Cold Outreach (Safe)',
    owner: 'system',
    intent: 'cold_outreach',
    compatiblePains: [],
    compatibleUrgency: [],
    compatibleTone: [], // Neutral
    compatibleCta: ['soft'],
    incompatibleTraits: [],
    minIcpConfidence: 0.0,
    baseQualityScore: 0.5,
  },
];
