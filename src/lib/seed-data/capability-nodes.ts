// Seed Data - Initial Capability Nodes for Tech Tree
import { CapabilityNode, CapabilityTier } from '../../types/move-system'

export const FOUNDATION_NODES: Partial<CapabilityNode>[] = [
  {
    name: 'Analytics Core',
    tier: 'Foundation',
    description: 'Basic analytics setup and tracking infrastructure',
    parentNodeIds: [],
    completionCriteria: {
      type: 'automatic',
      conditions: { hasAnalytics: true, hasTracking: true }
    },
    unlocksManeuverIds: []
  },
  {
    name: 'ICP Definition',
    tier: 'Foundation',
    description: 'At least one ICP fully defined with psychographic profile',
    parentNodeIds: [],
    completionCriteria: {
      type: 'automatic',
      conditions: { minICPs: 1 }
    },
    unlocksManeuverIds: []
  },
  {
    name: 'Value Proposition',
    tier: 'Foundation',
    description: 'Clear positioning and value prop documented',
    parentNodeIds: [],
    completionCriteria: {
      type: 'manual'
    },
    unlocksManeuverIds: []
  },
  {
    name: 'Basic Website',
    tier: 'Foundation',
    description: 'Functional website with core pages',
    parentNodeIds: [],
    completionCriteria: {
      type: 'manual'
    },
    unlocksManeuverIds: []
  }
]

export const TRACTION_NODES: Partial<CapabilityNode>[] = [
  {
    name: 'Lead Magnet v1',
    tier: 'Traction',
    description: 'First lead generation asset created and deployed',
    parentNodeIds: [], // Will be set to ICP Definition ID
    completionCriteria: {
      type: 'automatic',
      conditions: { hasLeadMagnet: true, minDownloads: 10 }
    },
    unlocksManeuverIds: [] // Will be set to Authority Sprint, etc.
  },
  {
    name: 'Email Nurture',
    tier: 'Traction',
    description: 'Email sequence and automation setup',
    parentNodeIds: [], // Will be set to Lead Magnet ID
    completionCriteria: {
      type: 'automatic',
      conditions: { hasEmailSequence: true, hasAutomation: true }
    },
    unlocksManeuverIds: []
  },
  {
    name: 'Social Proof Collection',
    tier: 'Traction',
    description: 'System for gathering and displaying testimonials',
    parentNodeIds: [], // Will be set to ICP Definition
    completionCriteria: {
      type: 'automatic',
      conditions: { minTestimonials: 3 }
    },
    unlocksManeuverIds: []
  },
  {
    name: 'CRM Integration',
    tier: 'Traction',
    description: 'Customer relationship management system connected',
    parentNodeIds: [], // Will be set to Analytics Core
    completionCriteria: {
      type: 'automatic',
      conditions: { hasCRM: true, isConnected: true }
    },
    unlocksManeuverIds: [] // Will unlock Garrison maneuver
  }
]

export const SCALE_NODES: Partial<CapabilityNode>[] = [
  {
    name: 'Paid Acquisition',
    tier: 'Scale',
    description: 'Paid ads infrastructure and tracking setup',
    parentNodeIds: [], // Will be set to Analytics Core + Lead Magnet
    completionCriteria: {
      type: 'manual'
    },
    unlocksManeuverIds: [] // Will unlock Scarcity Flank, etc.
  },
  {
    name: 'A/B Testing Framework',
    tier: 'Scale',
    description: 'Systematic testing and optimization infrastructure',
    parentNodeIds: [], // Will be set to Analytics Core
    completionCriteria: {
      type: 'automatic',
      conditions: { hasTestingSetup: true, minTestsRun: 5 }
    },
    unlocksManeuverIds: []
  },
  {
    name: 'Referral Loop',
    tier: 'Scale',
    description: 'Automated referral tracking and rewards',
    parentNodeIds: [], // Will be set to Email Nurture
    completionCriteria: {
      type: 'automatic',
      conditions: { hasReferralProgram: true, minReferrals: 10 }
    },
    unlocksManeuverIds: []
  },
  {
    name: 'Marketing Automation',
    tier: 'Scale',
    description: 'Advanced automation workflows',
    parentNodeIds: [], // Will be set to Email Nurture
    completionCriteria: {
      type: 'automatic',
      conditions: { hasAutomation: true, minWorkflows: 3 }
    },
    unlocksManeuverIds: []
  }
]

export const DOMINANCE_NODES: Partial<CapabilityNode>[] = [
  {
    name: 'Referral Engine',
    tier: 'Dominance',
    description: 'Viral loop and referral tracking with high NPS',
    parentNodeIds: [], // Will be set to Email Nurture + A/B Testing
    completionCriteria: {
      type: 'automatic',
      conditions: { hasReferralProgram: true, minNPS: 50, minReferrals: 50 }
    },
    unlocksManeuverIds: []
  },
  {
    name: 'Predictive Analytics',
    tier: 'Dominance',
    description: 'AI-powered forecasting and insights',
    parentNodeIds: [], // Will be set to A/B Testing
    completionCriteria: {
      type: 'automatic',
      conditions: { hasMLModel: true, accuracyThreshold: 0.8 }
    },
    unlocksManeuverIds: []
  },
  {
    name: 'Community Platform',
    tier: 'Dominance',
    description: 'User community and engagement platform',
    parentNodeIds: [], // Will be set to Social Proof
    completionCriteria: {
      type: 'automatic',
      conditions: { hasCommunity: true, minActiveUsers: 100 }
    },
    unlocksManeuverIds: []
  },
  {
    name: 'Category Design',
    tier: 'Dominance',
    description: 'Thought leadership and category creation',
    parentNodeIds: [], // Will be set to Value Proposition
    completionCriteria: {
      type: 'manual'
    },
    unlocksManeuverIds: []
  }
]

// Helper to get all nodes
export const getAllCapabilityNodes = (): Partial<CapabilityNode>[] => {
  return [
    ...FOUNDATION_NODES,
    ...TRACTION_NODES,
    ...SCALE_NODES,
    ...DOMINANCE_NODES
  ]
}


