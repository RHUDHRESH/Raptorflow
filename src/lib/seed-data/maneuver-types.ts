// Seed Data - Maneuver Type Templates
import { ManeuverType, ManeuverCategory, FoggRole } from '../../types/move-system'

export const MANEUVER_TEMPLATES: Partial<ManeuverType>[] = [
  // Offensive Maneuvers
  {
    name: 'Authority Sprint',
    category: 'Offensive',
    baseDurationDays: 14,
    foggRole: 'Spark',
    intensityScore: 7,
    riskProfile: 'Medium',
    description: 'Concentrated burst of high-value content targeting Center of Gravity',
    defaultConfig: {
      suggestedChannels: ['LinkedIn', 'Email', 'Blog'],
      suggestedContentTypes: ['Whitepaper', 'Long-form Article', 'Video'],
      recommendedFrequency: '3 posts/week + 1 webinar'
    },
    requiredCapabilityIds: [], // Will be set to ['lead-magnet', 'email-nurture']
    typicalICPs: ['Skeptical', 'Status-Driven']
  },
  {
    name: 'Scarcity Flank',
    category: 'Offensive',
    baseDurationDays: 14,
    foggRole: 'Signal',
    intensityScore: 8,
    riskProfile: 'Budget_Risk',
    description: 'Bypass competitor strength using scarcity and urgency psychology',
    defaultConfig: {
      suggestedChannels: ['Email', 'Paid Ads', 'Website'],
      suggestedContentTypes: ['Limited Offer', 'Countdown Timer', 'Urgency Copy'],
      recommendedFrequency: 'Daily for 7 days, then taper'
    },
    requiredCapabilityIds: [], // Will be set to ['paid-ads', 'email-nurture']
    typicalICPs: ['High Intent', 'Price Sensitive']
  },
  {
    name: 'Viral Loop',
    category: 'Offensive',
    baseDurationDays: 28,
    foggRole: 'Facilitator',
    intensityScore: 6,
    riskProfile: 'Low',
    description: 'Automated referral and sharing mechanism',
    defaultConfig: {
      suggestedChannels: ['In-App', 'Email', 'Social'],
      suggestedContentTypes: ['Referral Link', 'Share Button', 'Incentive'],
      recommendedFrequency: 'Triggered on key actions'
    },
    requiredCapabilityIds: [], // Will be set to ['referral-engine']
    typicalICPs: ['Community', 'Extrovert']
  },
  {
    name: 'Trojan Horse',
    category: 'Offensive',
    baseDurationDays: 14,
    foggRole: 'Facilitator',
    intensityScore: 7,
    riskProfile: 'Brand_Risk',
    description: 'Penetration strategy targeting competitor customers',
    defaultConfig: {
      suggestedChannels: ['LinkedIn', 'Email', 'Content'],
      suggestedContentTypes: ['Migration Guide', 'Comparison', 'Switcher Offer'],
      recommendedFrequency: 'Weekly for 2 weeks'
    },
    requiredCapabilityIds: [], // Will be set to ['paid-ads']
    typicalICPs: ['Competitor Users', 'Switchers']
  },
  
  // Defensive Maneuvers
  {
    name: 'Garrison (Churn Defense)',
    category: 'Defensive',
    baseDurationDays: 7,
    foggRole: 'Spark',
    intensityScore: 5,
    riskProfile: 'Low',
    description: 'Triggered high-touch engagements for at-risk customers',
    defaultConfig: {
      suggestedChannels: ['Email', 'In-App', 'Phone'],
      suggestedContentTypes: ['Personal Message', 'Usage Audit', 'Value Reminder'],
      recommendedFrequency: 'Triggered on risk signals'
    },
    requiredCapabilityIds: [], // Will be set to ['crm-integration']
    typicalICPs: ['At-Risk', 'Frustrated']
  },
  {
    name: 'Win-Back Raid',
    category: 'Defensive',
    baseDurationDays: 14,
    foggRole: 'Signal',
    intensityScore: 6,
    riskProfile: 'Budget_Risk',
    description: 'Reactivation campaign for churned customers',
    defaultConfig: {
      suggestedChannels: ['Email', 'SMS', 'Retargeting'],
      suggestedContentTypes: ['We Miss You', 'Special Offer', 'Product Update'],
      recommendedFrequency: '3 emails over 2 weeks'
    },
    requiredCapabilityIds: [], // Will be set to ['crm-integration', 'email-nurture']
    typicalICPs: ['Churned', 'Price Sensitive']
  },
  {
    name: 'Proof Loop',
    category: 'Defensive',
    baseDurationDays: 14,
    foggRole: 'Facilitator',
    intensityScore: 4,
    riskProfile: 'Low',
    description: 'Reinforce purchase decision with social proof',
    defaultConfig: {
      suggestedChannels: ['Email', 'In-App'],
      suggestedContentTypes: ['Case Study', 'Testimonial', 'Feature Highlight'],
      recommendedFrequency: 'Weekly for 2 weeks'
    },
    requiredCapabilityIds: [], // Will be set to ['social-proof-collection']
    typicalICPs: ['Post-Purchase', 'Anxious']
  },
  {
    name: 'Community Fort',
    category: 'Defensive',
    baseDurationDays: 28,
    foggRole: 'Facilitator',
    intensityScore: 5,
    riskProfile: 'Low',
    description: 'Build lock-in through community engagement',
    defaultConfig: {
      suggestedChannels: ['Community Platform', 'Email', 'Events'],
      suggestedContentTypes: ['Beta Invite', 'User Spotlight', 'Ambassador Kit'],
      recommendedFrequency: 'Ongoing'
    },
    requiredCapabilityIds: [], // Will be set to ['community-platform']
    typicalICPs: ['Power Users', 'Advocates']
  },
  
  // Logistical Maneuvers
  {
    name: 'Asset Forge',
    category: 'Logistical',
    baseDurationDays: 7,
    foggRole: null,
    intensityScore: 4,
    riskProfile: 'Low',
    description: 'Sprint dedicated to creating reusable assets (case studies, white papers)',
    defaultConfig: {
      suggestedChannels: ['Internal'],
      suggestedContentTypes: ['Case Study', 'Whitepaper', 'Video', 'Infographic'],
      recommendedFrequency: 'One-time sprint'
    },
    requiredCapabilityIds: [],
    typicalICPs: []
  },
  {
    name: 'Content Calendar',
    category: 'Logistical',
    baseDurationDays: 30,
    foggRole: null,
    intensityScore: 3,
    riskProfile: 'Low',
    description: 'Plan and schedule content production',
    defaultConfig: {
      suggestedChannels: ['All'],
      suggestedContentTypes: ['All'],
      recommendedFrequency: 'Ongoing'
    },
    requiredCapabilityIds: [],
    typicalICPs: []
  },
  
  // Recon Maneuvers
  {
    name: 'Intel Sweep',
    category: 'Recon',
    baseDurationDays: 7,
    foggRole: 'Signal',
    intensityScore: 3,
    riskProfile: 'Low',
    description: 'Research-focused move: surveys, customer interviews',
    defaultConfig: {
      suggestedChannels: ['Email', 'Survey Tool', 'Interviews'],
      suggestedContentTypes: ['Survey', 'Interview Script', 'Analysis'],
      recommendedFrequency: 'One-time'
    },
    requiredCapabilityIds: [], // Will be set to ['analytics-core']
    typicalICPs: []
  },
  {
    name: 'Competitor Recon',
    category: 'Recon',
    baseDurationDays: 7,
    foggRole: null,
    intensityScore: 2,
    riskProfile: 'Low',
    description: 'Systematic competitor analysis and positioning research',
    defaultConfig: {
      suggestedChannels: ['Research'],
      suggestedContentTypes: ['Competitor Analysis', 'SWOT', 'Positioning Map'],
      recommendedFrequency: 'Quarterly'
    },
    requiredCapabilityIds: [],
    typicalICPs: []
  }
]


