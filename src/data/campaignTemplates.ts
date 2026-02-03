export interface CampaignTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  objective: string;
  usageCount?: number;
  rating?: number;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  estimatedDuration?: string;
  structure?: {
    phases: Array<{
      name: string;
      duration: string;
    }>;
  };
}

export const allCampaignTemplates: CampaignTemplate[] = [
  {
    id: 'product-launch',
    name: 'Product Launch',
    description: 'Launch your new product with a comprehensive campaign',
    category: 'launch',
    objective: 'launch',
    usageCount: 1247,
    rating: 4.8,
    difficulty: 'intermediate',
    estimatedDuration: '4-6 weeks',
    structure: {
      phases: [
        { name: 'Pre-launch', duration: '1 week' },
        { name: 'Launch Day', duration: '1 day' },
        { name: 'Post-launch', duration: '2 weeks' }
      ]
    }
  },
  {
    id: 'lead-generation',
    name: 'Lead Generation',
    description: 'Generate qualified leads for your sales team',
    category: 'leads',
    objective: 'lead_generation',
    usageCount: 3421,
    rating: 4.9,
    difficulty: 'beginner',
    estimatedDuration: '2-4 weeks',
    structure: {
      phases: [
        { name: 'Audience Research', duration: '3 days' },
        { name: 'Campaign Setup', duration: '1 week' },
        { name: 'Execution', duration: '2 weeks' }
      ]
    }
  },
  {
    id: 'brand-awareness',
    name: 'Brand Awareness',
    description: 'Increase visibility and recognition for your brand',
    category: 'awareness',
    objective: 'awareness',
    usageCount: 2156,
    rating: 4.7,
    difficulty: 'beginner',
    estimatedDuration: '6-8 weeks',
    structure: {
      phases: [
        { name: 'Brand Audit', duration: '1 week' },
        { name: 'Content Creation', duration: '3 weeks' },
        { name: 'Distribution', duration: '4 weeks' }
      ]
    }
  },
  {
    id: 'conversion-boost',
    name: 'Conversion Boost',
    description: 'Optimize your funnel for higher conversion rates',
    category: 'conversion',
    objective: 'conversion',
    usageCount: 1893,
    rating: 4.9,
    difficulty: 'advanced',
    estimatedDuration: '3-5 weeks',
    structure: {
      phases: [
        { name: 'Funnel Analysis', duration: '1 week' },
        { name: 'Optimization', duration: '2 weeks' },
        { name: 'Testing', duration: '2 weeks' }
      ]
    }
  },
  {
    id: 'customer-retention',
    name: 'Customer Retention',
    description: 'Keep existing customers engaged and loyal',
    category: 'retention',
    objective: 'retention',
    usageCount: 987,
    rating: 4.6,
    difficulty: 'intermediate',
    estimatedDuration: '4-6 weeks',
    structure: {
      phases: [
        { name: 'Customer Analysis', duration: '1 week' },
        { name: 'Engagement Strategy', duration: '2 weeks' },
        { name: 'Implementation', duration: '3 weeks' }
      ]
    }
  },
  {
    id: 'event-promotion',
    name: 'Event Promotion',
    description: 'Drive attendance and engagement for your event',
    category: 'promotion',
    objective: 'promotion',
    usageCount: 756,
    rating: 4.8,
    difficulty: 'intermediate',
    estimatedDuration: '2-4 weeks',
    structure: {
      phases: [
        { name: 'Pre-event', duration: '2 weeks' },
        { name: 'Event Day', duration: '1 day' },
        { name: 'Follow-up', duration: '1 week' }
      ]
    }
  }
];

export function getTemplateById(id: string): CampaignTemplate | undefined {
  return allCampaignTemplates.find(template => template.id === id);
}
