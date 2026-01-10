import { Play } from '@/types/campaign';

// Pre-built Plays
export const preBuiltPlays: Play[] = [
  {
    id: 'play-welcome-series',
    name: 'New User Welcome Series',
    description: 'Comprehensive onboarding sequence for new users with educational content and engagement prompts',
    category: 'onboarding',
    moves: [
      'move-welcome-email',
      'move-getting-started-guide',
      'move-product-tour-email',
      'move-best-practices-email',
      'move-check-in-email'
    ],
    config: {
      steps: [
        {
          id: 'step-1',
          name: 'Immediate Welcome',
          moves: ['move-welcome-email'],
          delay: 0,
          parallel: false
        },
        {
          id: 'step-2',
          name: 'Getting Started',
          moves: ['move-getting-started-guide', 'move-product-tour-email'],
          delay: 24,
          parallel: true
        },
        {
          id: 'step-3',
          name: 'Best Practices',
          moves: ['move-best-practices-email'],
          delay: 72,
          parallel: false
        },
        {
          id: 'step-4',
          name: 'Check In',
          moves: ['move-check-in-email'],
          delay: 168,
          parallel: false,
          conditions: [
            {
              type: 'metric',
              operator: 'less_than',
              value: 1,
              metric: 'login_count'
            }
          ]
        }
      ],
      triggers: [
        {
          event: 'user_signup',
          delay: 0
        }
      ],
      conditions: []
    },
    isActive: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    createdBy: 'system',
    tags: ['onboarding', 'email', 'education'],
    usageCount: 2500,
    rating: 4.9
  },
  {
    id: 'play-lead-nurturing',
    name: 'B2B Lead Nurturing Sequence',
    description: 'Multi-touch nurturing sequence to convert leads into qualified opportunities',
    category: 'nurturing',
    moves: [
      'move-lead-confirmation',
      'move-industry-insights',
      'move-case-study-email',
      'move-demo-invitation',
      'move-follow-up-sequence'
    ],
    config: {
      steps: [
        {
          id: 'step-1',
          name: 'Lead Confirmation',
          moves: ['move-lead-confirmation'],
          delay: 0,
          parallel: false
        },
        {
          id: 'step-2',
          name: 'Value Addition',
          moves: ['move-industry-insights'],
          delay: 48,
          parallel: false
        },
        {
          id: 'step-3',
          name: 'Social Proof',
          moves: ['move-case-study-email'],
          delay: 120,
          parallel: false,
          conditions: [
            {
              type: 'move_status',
              operator: 'equals',
              value: 'completed',
              moveId: 'move-industry-insights'
            }
          ]
        },
        {
          id: 'step-4',
          name: 'Demo Invitation',
          moves: ['move-demo-invitation'],
          delay: 168,
          parallel: false
        },
        {
          id: 'step-5',
          name: 'Follow Up',
          moves: ['move-follow-up-sequence'],
          delay: 240,
          parallel: false,
          conditions: [
            {
              type: 'metric',
              operator: 'equals',
              value: 0,
              metric: 'demo_booked'
            }
          ]
        }
      ],
      triggers: [
        {
          event: 'lead_created',
          delay: 0
        }
      ],
      conditions: []
    },
    isActive: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    createdBy: 'system',
    tags: ['b2b', 'nurturing', 'demo'],
    usageCount: 1800,
    rating: 4.8
  },
  {
    id: 'play-cart-abandonment',
    name: 'E-commerce Cart Recovery',
    description: 'Multi-email sequence to recover abandoned carts with increasing urgency',
    category: 'conversion',
    moves: [
      'move-cart-reminder',
      'move-social-proof-email',
      'move-urgency-offer',
      'move-final-reminder'
    ],
    config: {
      steps: [
        {
          id: 'step-1',
          name: 'Cart Reminder',
          moves: ['move-cart-reminder'],
          delay: 1,
          parallel: false
        },
        {
          id: 'step-2',
          name: 'Social Proof',
          moves: ['move-social-proof-email'],
          delay: 24,
          parallel: false
        },
        {
          id: 'step-3',
          name: 'Urgency Offer',
          moves: ['move-urgency-offer'],
          delay: 72,
          parallel: false,
          conditions: [
            {
              type: 'metric',
              operator: 'greater_than',
              value: 50,
              metric: 'cart_value'
            }
          ]
        },
        {
          id: 'step-4',
          name: 'Final Reminder',
          moves: ['move-final-reminder'],
          delay: 120,
          parallel: false
        }
      ],
      triggers: [
        {
          event: 'cart_abandoned',
          delay: 0
        }
      ],
      conditions: []
    },
    isActive: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    createdBy: 'system',
    tags: ['ecommerce', 'conversion', 'urgency'],
    usageCount: 3200,
    rating: 4.7
  },
  {
    id: 'play-product-launch',
    name: 'Product Launch Sequence',
    description: 'Comprehensive launch sequence with teaser, announcement, and follow-up phases',
    category: 'launch',
    moves: [
      'move-teaser-campaign',
      'move-announcement-blast',
      'move-demo-videos',
      'move-early-bird-offer',
      'move-launch-follow-up'
    ],
    config: {
      steps: [
        {
          id: 'step-1',
          name: 'Teaser Phase',
          moves: ['move-teaser-campaign'],
          delay: -168, // 7 days before launch
          parallel: false
        },
        {
          id: 'step-2',
          name: 'Launch Day',
          moves: ['move-announcement-blast', 'move-demo-videos'],
          delay: 0,
          parallel: true
        },
        {
          id: 'step-3',
          name: 'Early Bird',
          moves: ['move-early-bird-offer'],
          delay: 24,
          parallel: false
        },
        {
          id: 'step-4',
          name: 'Follow Up',
          moves: ['move-launch-follow-up'],
          delay: 72,
          parallel: false
        }
      ],
      triggers: [
        {
          event: 'launch_date',
          delay: 0
        }
      ],
      conditions: []
    },
    isActive: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    createdBy: 'system',
    tags: ['launch', 'product', 'announcement'],
    usageCount: 950,
    rating: 4.8
  },
  {
    id: 'play-customer-retention',
    name: 'Customer Retention Play',
    description: 'Keep customers engaged with value-packed content and check-ins',
    category: 'retention',
    moves: [
      'move-onboarding-complete',
      'move-value-tips',
      'move-success-story',
      'move-upgrade-opportunity',
      'move-renewal-reminder'
    ],
    config: {
      steps: [
        {
          id: 'step-1',
          name: 'Onboarding Complete',
          moves: ['move-onboarding-complete'],
          delay: 0,
          parallel: false
        },
        {
          id: 'step-2',
          name: 'Value Tips',
          moves: ['move-value-tips'],
          delay: 168,
          parallel: false
        },
        {
          id: 'step-3',
          name: 'Success Story',
          moves: ['move-success-story'],
          delay: 504,
          parallel: false
        },
        {
          id: 'step-4',
          name: 'Upgrade Opportunity',
          moves: ['move-upgrade-opportunity'],
          delay: 1008,
          parallel: false,
          conditions: [
            {
              type: 'metric',
              operator: 'greater_than',
              value: 80,
              metric: 'feature_adoption'
            }
          ]
        },
        {
          id: 'step-5',
          name: 'Renewal Reminder',
          moves: ['move-renewal-reminder'],
          delay: 2016,
          parallel: false
        }
      ],
      triggers: [
        {
          event: 'onboarding_complete',
          delay: 0
        }
      ],
      conditions: []
    },
    isActive: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    createdBy: 'system',
    tags: ['retention', 'engagement', 'renewal'],
    usageCount: 1400,
    rating: 4.6
  },
  {
    id: 'play-webinar-sequence',
    name: 'Webinar Promotion & Follow-up',
    description: 'Complete webinar sequence from promotion to post-event follow-up',
    category: 'event',
    moves: [
      'move-webinar-announcement',
      'move-speaker-spotlight',
      'move-last-chance',
      'move-webinar-reminder',
      'move-webinar-followup',
      'move-recording-share'
    ],
    config: {
      steps: [
        {
          id: 'step-1',
          name: 'Initial Announcement',
          moves: ['move-webinar-announcement'],
          delay: -672, // 4 weeks before
          parallel: false
        },
        {
          id: 'step-2',
          name: 'Speaker Spotlight',
          moves: ['move-speaker-spotlight'],
          delay: -504, // 3 weeks before
          parallel: false
        },
        {
          id: 'step-3',
          name: 'Last Chance',
          moves: ['move-last-chance'],
          delay: -48, // 2 days before
          parallel: false
        },
        {
          id: 'step-4',
          name: 'Event Reminder',
          moves: ['move-webinar-reminder'],
          delay: -2, // 2 hours before
          parallel: false
        },
        {
          id: 'step-5',
          name: 'Post-Event Follow-up',
          moves: ['move-webinar-followup'],
          delay: 24,
          parallel: false,
          conditions: [
            {
              type: 'event',
              operator: 'equals',
              value: 'attended'
            }
          ]
        },
        {
          id: 'step-6',
          name: 'Recording Share',
          moves: ['move-recording-share'],
          delay: 72,
          parallel: false
        }
      ],
      triggers: [
        {
          event: 'webinar_scheduled',
          delay: 0
        }
      ],
      conditions: []
    },
    isActive: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    createdBy: 'system',
    tags: ['webinar', 'event', 'promotion'],
    usageCount: 750,
    rating: 4.5
  },
  {
    id: 'play-content-distribution',
    name: 'Content Distribution Amplifier',
    description: 'Amplify content reach across multiple channels systematically',
    category: 'content',
    moves: [
      'move-blog-announcement',
      'move-social-snippets',
      'move-email-newsletter',
      'move-social-boost',
      'move-content-repurpose'
    ],
    config: {
      steps: [
        {
          id: 'step-1',
          name: 'Blog Announcement',
          moves: ['move-blog-announcement'],
          delay: 0,
          parallel: false
        },
        {
          id: 'step-2',
          name: 'Social Snippets',
          moves: ['move-social-snippets'],
          delay: 2,
          parallel: false
        },
        {
          id: 'step-3',
          name: 'Newsletter',
          moves: ['move-email-newsletter'],
          delay: 24,
          parallel: false
        },
        {
          id: 'step-4',
          name: 'Social Boost',
          moves: ['move-social-boost'],
          delay: 48,
          parallel: false,
          conditions: [
            {
              type: 'metric',
              operator: 'greater_than',
              value: 100,
              metric: 'engagement_score'
            }
          ]
        },
        {
          id: 'step-5',
          name: 'Content Repurpose',
          moves: ['move-content-repurpose'],
          delay: 168,
          parallel: false
        }
      ],
      triggers: [
        {
          event: 'content_published',
          delay: 0
        }
      ],
      conditions: []
    },
    isActive: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    createdBy: 'system',
    tags: ['content', 'distribution', 'amplification'],
    usageCount: 1100,
    rating: 4.4
  },
  {
    id: 'play-re-engagement',
    name: 'Dormant User Re-engagement',
    description: 'Win back inactive users with targeted incentives and value',
    category: 'reactivation',
    moves: [
      'move-we-miss-you',
      'move-value-reminder',
      'move-incentive-offer',
      'move-final-attempt'
    ],
    config: {
      steps: [
        {
          id: 'step-1',
          name: 'We Miss You',
          moves: ['move-we-miss-you'],
          delay: 0,
          parallel: false
        },
        {
          id: 'step-2',
          name: 'Value Reminder',
          moves: ['move-value-reminder'],
          delay: 72,
          parallel: false
        },
        {
          id: 'step-3',
          name: 'Incentive Offer',
          moves: ['move-incentive-offer'],
          delay: 168,
          parallel: false,
          conditions: [
            {
              type: 'metric',
              operator: 'equals',
              value: 0,
              metric: 'login_count'
            }
          ]
        },
        {
          id: 'step-4',
          name: 'Final Attempt',
          moves: ['move-final-attempt'],
          delay: 336,
          parallel: false
        }
      ],
      triggers: [
        {
          event: 'user_dormant',
          delay: 0
        }
      ],
      conditions: []
    },
    isActive: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    createdBy: 'system',
    tags: ['reactivation', 'retention', 'winback'],
    usageCount: 890,
    rating: 4.3
  },
  {
    id: 'play-upsell-sequence',
    name: 'Strategic Upsell Sequence',
    description: 'Identify and execute upsell opportunities at optimal moments',
    category: 'sales',
    moves: [
      'move-usage-tracking',
      'move-upsell-identify',
      'move-upsell-offer',
      'move-upsell-followup'
    ],
    config: {
      steps: [
        {
          id: 'step-1',
          name: 'Usage Tracking',
          moves: ['move-usage-tracking'],
          delay: 0,
          parallel: false
        },
        {
          id: 'step-2',
          name: 'Identify Opportunity',
          moves: ['move-upsell-identify'],
          delay: 24,
          parallel: false,
          conditions: [
            {
              type: 'metric',
              operator: 'greater_than',
              value: 80,
              metric: 'feature_usage'
            }
          ]
        },
        {
          id: 'step-3',
          name: 'Upsell Offer',
          moves: ['move-upsell-offer'],
          delay: 48,
          parallel: false
        },
        {
          id: 'step-4',
          name: 'Follow Up',
          moves: ['move-upsell-followup'],
          delay: 120,
          parallel: false,
          conditions: [
            {
              type: 'metric',
              operator: 'equals',
              value: 0,
              metric: 'upgrade_clicked'
            }
          ]
        }
      ],
      triggers: [
        {
          event: 'milestone_reached',
          delay: 0
        }
      ],
      conditions: []
    },
    isActive: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    createdBy: 'system',
    tags: ['upsell', 'revenue', 'optimization'],
    usageCount: 670,
    rating: 4.5
  },
  {
    id: 'play-feedback-collection',
    name: 'Customer Feedback Loop',
    description: 'Systematically collect and act on customer feedback',
    category: 'feedback',
    moves: [
      'move-nps-survey',
      'move-feedback-request',
      'move-thank-you',
      'move-feedback-action'
    ],
    config: {
      steps: [
        {
          id: 'step-1',
          name: 'NPS Survey',
          moves: ['move-nps-survey'],
          delay: 0,
          parallel: false
        },
        {
          id: 'step-2',
          name: 'Detailed Feedback',
          moves: ['move-feedback-request'],
          delay: 24,
          parallel: false,
          conditions: [
            {
              type: 'metric',
              operator: 'less_than',
              value: 9,
              metric: 'nps_score'
            }
          ]
        },
        {
          id: 'step-3',
          name: 'Thank You',
          moves: ['move-thank-you'],
          delay: 48,
          parallel: false
        },
        {
          id: 'step-4',
          name: 'Action on Feedback',
          moves: ['move-feedback-action'],
          delay: 168,
          parallel: false
        }
      ],
      triggers: [
        {
          event: 'customer_milestone',
          delay: 0
        }
      ],
      conditions: []
    },
    isActive: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    createdBy: 'system',
    tags: ['feedback', 'nps', 'improvement'],
    usageCount: 540,
    rating: 4.2
  }
];

// Play categories
export const playCategories = [
  { id: 'onboarding', name: 'Onboarding', count: 1 },
  { id: 'nurturing', name: 'Lead Nurturing', count: 1 },
  { id: 'conversion', name: 'Conversion', count: 1 },
  { id: 'launch', name: 'Product Launch', count: 1 },
  { id: 'retention', name: 'Customer Retention', count: 1 },
  { id: 'event', name: 'Events', count: 1 },
  { id: 'content', name: 'Content Marketing', count: 1 },
  { id: 'reactivation', name: 'Reactivation', count: 1 },
  { id: 'sales', name: 'Sales', count: 1 },
  { id: 'feedback', name: 'Feedback', count: 1 }
];

// Helper functions
export const getPlayById = (id: string): Play | undefined => {
  return preBuiltPlays.find(play => play.id === id);
};

export const getPlaysByCategory = (category: string): Play[] => {
  return preBuiltPlays.filter(play => play.category === category);
};

export const getPlaysByTag = (tag: string): Play[] => {
  return preBuiltPlays.filter(play => play.tags.includes(tag));
};

export const getPopularPlays = (limit: number = 5): Play[] => {
  return preBuiltPlays
    .sort((a, b) => b.usageCount - a.usageCount)
    .slice(0, limit);
};

export const getTopRatedPlays = (limit: number = 5): Play[] => {
  return preBuiltPlays
    .sort((a, b) => b.rating - a.rating)
    .slice(0, limit);
};

export const getRecommendedPlays = (objective: string, industry: string, companySize: string): Play[] => {
  let recommended = [...preBuiltPlays];

  // Filter by objective
  if (objective === 'acquisition') {
    recommended = recommended.filter(p =>
      ['nurturing', 'conversion', 'launch'].includes(p.category)
    );
  } else if (objective === 'retention') {
    recommended = recommended.filter(p =>
      ['onboarding', 'retention', 'reactivation'].includes(p.category)
    );
  } else if (objective === 'growth') {
    recommended = recommended.filter(p =>
      ['sales', 'content', 'event'].includes(p.category)
    );
  }

  // Filter by company size
  if (companySize === 'small') {
    recommended = recommended.filter(p =>
      !p.tags.includes('enterprise')
    );
  }

  return recommended.slice(0, 5);
};

// Play statistics
export const playStats = {
  totalPlays: preBuiltPlays.length,
  totalUsage: preBuiltPlays.reduce((sum, play) => sum + play.usageCount, 0),
  averageRating: preBuiltPlays.reduce((sum, play) => sum + play.rating, 0) / preBuiltPlays.length,
  mostUsedCategory: 'conversion',
  highestRated: preBuiltPlays.reduce((max, play) => play.rating > max.rating ? play : max)
};
