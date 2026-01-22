import { CampaignTemplate, CampaignObjective, MoveType } from '@/types/campaign';

// Product Launch Templates
export const productLaunchTemplates: CampaignTemplate[] = [
  {
    id: 'pl-saas-launch',
    name: 'SaaS Product Launch',
    description: 'Complete launch sequence for SaaS products with pre-launch buzz, launch day coordination, and post-launch optimization',
    category: 'Product Launch',
    objective: CampaignObjective.LAUNCH,
    structure: {
      phases: [
        {
          name: 'Pre-Launch (2 weeks)',
          description: 'Build anticipation and capture early interest',
          startDate: new Date(),
          endDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Launch Week',
          description: 'Maximum visibility and conversion push',
          startDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Post-Launch (2 weeks)',
          description: 'Maintain momentum and gather feedback',
          startDate: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 35 * 24 * 60 * 60 * 1000)
        }
      ],
      recommendedMoves: [
        {
          type: MoveType.EMAIL,
          name: 'Waitlist Announcement',
          description: 'Notify waitlist about upcoming launch',
          config: {
            subject: 'Something big is coming...',
            template: 'teaser'
          },
          optional: false
        },
        {
          type: MoveType.SOCIAL_MEDIA,
          name: 'Teaser Campaign',
          description: 'Build mystery with daily teasers',
          config: {
            platform: 'linkedin',
            postContent: 'Countdown posts',
            frequency: 'daily'
          },
          optional: false
        },
        {
          type: MoveType.CONTENT,
          name: 'Launch Blog Post',
          description: 'Comprehensive product announcement',
          config: {
            contentType: 'blog',
            title: 'Introducing [Product Name]',
            cta: 'Get early access'
          },
          optional: false
        },
        {
          type: MoveType.EMAIL,
          name: 'Launch Day Email',
          description: 'Big launch announcement to all lists',
          config: {
            subject: '≡ƒÄë It\'s live! [Product Name] is here',
            template: 'announcement'
          },
          optional: false
        },
        {
          type: MoveType.ADS,
          name: 'Launch Ads',
          description: 'Paid promotion for launch visibility',
          config: {
            adPlatform: 'google',
            budget: 5000,
            duration: 7
          },
          optional: true
        }
      ],
      defaultSettings: {
        autoOptimization: true,
        abTesting: true,
        notifications: {
          email: true,
          push: true,
          slack: false,
          frequency: 'daily',
          events: ['launch', 'milestone', 'error']
        }
      }
    },
    isPublic: true,
    usageCount: 1250,
    rating: 4.8
  },
  {
    id: 'pl-physical-product',
    name: 'Physical Product Launch',
    description: 'E-commerce product launch with influencer outreach and social proof building',
    category: 'Product Launch',
    objective: CampaignObjective.LAUNCH,
    structure: {
      phases: [
        {
          name: 'Pre-Order Phase',
          description: 'Generate pre-orders and buzz',
          startDate: new Date(),
          endDate: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Launch Day',
          description: 'Coordinate across all channels',
          startDate: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 22 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Launch Week',
          description: 'Scale successful initiatives',
          startDate: new Date(Date.now() + 22 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 29 * 24 * 60 * 60 * 1000)
        }
      ],
      recommendedMoves: [
        {
          type: MoveType.OUTREACH,
          name: 'Influencer Seeding',
          description: 'Send products to influencers',
          config: {
            targetCount: 50,
            tier: 'micro'
          },
          optional: false
        },
        {
          type: MoveType.SOCIAL_MEDIA,
          name: 'Unboxing Campaign',
          description: 'Encourage unboxing content',
          config: {
            hashtag: '#[Product]Unboxing',
            platform: 'instagram'
          },
          optional: false
        },
        {
          type: MoveType.LANDING_PAGE,
          name: 'Product Landing Page',
          description: 'High-conversion product page',
          config: {
            template: 'product-launch',
            elements: ['video', 'reviews', 'countdown']
          },
          optional: false
        },
        {
          type: MoveType.EMAIL,
          name: 'Pre-Order Campaign',
          description: 'Drive pre-order conversions',
          config: {
            sequence: 3,
            discount: '10%',
            urgency: 'limited'
          },
          optional: false
        }
      ],
      defaultSettings: {
        autoOptimization: true,
        abTesting: true,
        notifications: {
          email: true,
          push: false,
          slack: true,
          frequency: 'daily',
          events: ['inventory', 'conversion']
        }
      }
    },
    isPublic: true,
    usageCount: 890,
    rating: 4.7
  }
];

// Lead Generation Templates
export const leadGenTemplates: CampaignTemplate[] = [
  {
    id: 'lg-b2b-high-ticket',
    name: 'B2B High-Ticket Lead Gen',
    description: 'Generate qualified leads for high-value B2B solutions',
    category: 'Lead Generation',
    objective: CampaignObjective.LEAD_GENERATION,
    structure: {
      phases: [
        {
          name: 'Awareness (Week 1-2)',
          description: 'Build problem awareness',
          startDate: new Date(),
          endDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Consideration (Week 3-4)',
          description: 'Demonstrate solution value',
          startDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 28 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Conversion (Week 5-6)',
          description: 'Drive demo requests',
          startDate: new Date(Date.now() + 28 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 42 * 24 * 60 * 60 * 1000)
        }
      ],
      recommendedMoves: [
        {
          type: MoveType.CONTENT,
          name: 'Problem-Solution Whitepaper',
          description: 'Deep dive into problem and solution',
          config: {
            contentType: 'whitepaper',
            gate: 'form',
            fields: ['email', 'company', 'role']
          },
          optional: false
        },
        {
          type: MoveType.WEBINAR,
          name: 'Solution Webinar',
          description: 'Live demonstration and Q&A',
          config: {
            duration: 45,
            format: 'demo',
            followUp: 'automated'
          },
          optional: false
        },
        {
          type: MoveType.LANDING_PAGE,
          name: 'Demo Request Page',
          description: 'Optimized demo request form',
          config: {
            template: 'demo-request',
            socialProof: true,
            urgency: 'limited slots'
          },
          optional: false
        },
        {
          type: MoveType.EMAIL,
          name: 'Lead Nurturing Sequence',
          description: '6-week nurture campaign',
          config: {
            sequence: 8,
            frequency: 'weekly',
            personalization: 'industry'
          },
          optional: false
        },
        {
          type: MoveType.ADS,
          name: 'LinkedIn Lead Gen Ads',
          description: 'Targeted professional ads',
          config: {
            adPlatform: 'linkedin',
            objective: 'leads',
            budget: 3000
          },
          optional: true
        }
      ],
      defaultSettings: {
        autoOptimization: true,
        abTesting: true,
        notifications: {
          email: true,
          push: true,
          slack: true,
          frequency: 'daily',
          events: ['lead', 'demo', 'conversion']
        }
      }
    },
    isPublic: true,
    usageCount: 2100,
    rating: 4.9
  },
  {
    id: 'lg-lead-magnet',
    name: 'Lead Magnet Funnel',
    description: 'Convert visitors with valuable lead magnets',
    category: 'Lead Generation',
    objective: CampaignObjective.LEAD_GENERATION,
    structure: {
      phases: [
        {
          name: 'Magnet Promotion',
          description: 'Drive traffic to lead magnet',
          startDate: new Date(),
          endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Nurture Sequence',
          description: 'Convert leads to customers',
          startDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000)
        }
      ],
      recommendedMoves: [
        {
          type: MoveType.CONTENT,
          name: 'Lead Magnet Creation',
          description: 'Create valuable resource',
          config: {
            contentType: 'ebook',
            topic: 'industry-guide',
            length: 30
          },
          optional: false
        },
        {
          type: MoveType.LANDING_PAGE,
          name: 'Lead Magnet Landing Page',
          description: 'High-conversion squeeze page',
          config: {
            template: 'lead-magnet',
            cta: 'Download Free',
            urgency: 'limited time'
          },
          optional: false
        },
        {
          type: MoveType.EMAIL,
          name: 'Welcome Sequence',
          description: 'Deliver value and build trust',
          config: {
            sequence: 5,
            frequency: 'daily',
            valueFirst: true
          },
          optional: false
        },
        {
          type: MoveType.SOCIAL_MEDIA,
          name: 'Social Promotion',
          description: 'Promote across channels',
          config: {
            platforms: ['twitter', 'linkedin', 'facebook'],
            frequency: 'daily',
            content: 'value-snippets'
          },
          optional: false
        }
      ],
      defaultSettings: {
        autoOptimization: false,
        abTesting: true,
        notifications: {
          email: true,
          push: false,
          slack: false,
          frequency: 'weekly',
          events: ['download', 'conversion']
        }
      }
    },
    isPublic: true,
    usageCount: 3400,
    rating: 4.6
  }
];

// Brand Awareness Templates
export const brandAwarenessTemplates: CampaignTemplate[] = [
  {
    id: 'ba-thought-leadership',
    name: 'Thought Leadership Campaign',
    description: 'Establish authority and build brand recognition',
    category: 'Brand Awareness',
    objective: CampaignObjective.AWARENESS,
    structure: {
      phases: [
        {
          name: 'Content Creation',
          description: 'Develop thought leadership content',
          startDate: new Date(),
          endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Distribution',
          description: 'Amplify content reach',
          startDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Engagement',
          description: 'Build community and authority',
          startDate: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
        }
      ],
      recommendedMoves: [
        {
          type: MoveType.CONTENT,
          name: 'Industry Report',
          description: 'Original research and insights',
          config: {
            contentType: 'report',
            dataPoints: 50,
            visualization: 'interactive'
          },
          optional: false
        },
        {
          type: MoveType.WEBINAR,
          name: 'Expert Panel',
          description: 'Host industry experts',
          config: {
            format: 'panel',
            duration: 60,
            promotion: 4
          },
          optional: false
        },
        {
          type: MoveType.SOCIAL_MEDIA,
          name: 'LinkedIn Thought Leadership',
          description: 'Daily insights and engagement',
          config: {
            platform: 'linkedin',
            frequency: 'daily',
            content: 'insights'
          },
          optional: false
        },
        {
          type: MoveType.EMAIL,
          name: 'Newsletter Series',
          description: 'Weekly insights newsletter',
          config: {
            frequency: 'weekly',
            content: 'curated + original',
            personalization: true
          },
          optional: false
        }
      ],
      defaultSettings: {
        autoOptimization: true,
        abTesting: false,
        notifications: {
          email: true,
          push: false,
          slack: true,
          frequency: 'weekly',
          events: ['mention', 'engagement']
        }
      }
    },
    isPublic: true,
    usageCount: 1560,
    rating: 4.7
  }
];

// Event Promotion Templates
export const eventPromotionTemplates: CampaignTemplate[] = [
  {
    id: 'ep-virtual-summit',
    name: 'Virtual Summit Promotion',
    description: 'Drive registrations for virtual events',
    category: 'Event Promotion',
    objective: CampaignObjective.PROMOTION,
    structure: {
      phases: [
        {
          name: 'Early Bird (4 weeks)',
          description: 'Maximize early registrations',
          startDate: new Date(),
          endDate: new Date(Date.now() + 28 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Regular Registration (4 weeks)',
          description: 'Steady registration flow',
          startDate: new Date(Date.now() + 28 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 56 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Last Call (1 week)',
          description: 'Urgency-driven registrations',
          startDate: new Date(Date.now() + 56 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 63 * 24 * 60 * 60 * 1000)
        }
      ],
      recommendedMoves: [
        {
          type: MoveType.LANDING_PAGE,
          name: 'Event Registration Page',
          description: 'Compelling event page',
          config: {
            template: 'virtual-summit',
            elements: ['speakers', 'agenda', 'testimonials'],
            countdown: true
          },
          optional: false
        },
        {
          type: MoveType.EMAIL,
          name: 'Speaker Announcement Sequence',
          description: 'Build excitement with speakers',
          config: {
            sequence: 5,
            frequency: 'weekly',
            focus: 'speaker-spotlight'
          },
          optional: false
        },
        {
          type: MoveType.SOCIAL_MEDIA,
          name: 'Speaker Promotion',
          description: 'Leverage speaker networks',
          config: {
            platforms: ['linkedin', 'twitter'],
            content: 'speaker-announcements',
            frequency: 'daily'
          },
          optional: false
        },
        {
          type: MoveType.ADS,
          name: 'Registration Ads',
          description: 'Targeted event ads',
          config: {
            adPlatform: 'facebook',
            objective: 'registrations',
            budget: 2000
          },
          optional: true
        }
      ],
      defaultSettings: {
        autoOptimization: true,
        abTesting: true,
        notifications: {
          email: true,
          push: true,
          slack: true,
          frequency: 'daily',
          events: ['registration', 'milestone']
        }
      }
    },
    isPublic: true,
    usageCount: 780,
    rating: 4.5
  }
];

// Content Marketing Templates
export const contentMarketingTemplates: CampaignTemplate[] = [
  {
    id: 'cm-content-pipeline',
    name: 'Content Pipeline System',
    description: 'Systematic content creation and distribution',
    category: 'Content Marketing',
    objective: CampaignObjective.AWARENESS,
    structure: {
      phases: [
        {
          name: 'Planning',
          description: 'Content calendar and topics',
          startDate: new Date(),
          endDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Creation',
          description: 'Produce content assets',
          startDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 35 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Distribution',
          description: 'Amplify content reach',
          startDate: new Date(Date.now() + 35 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 63 * 24 * 60 * 60 * 1000)
        }
      ],
      recommendedMoves: [
        {
          type: MoveType.CONTENT,
          name: 'Blog Post Series',
          description: 'Weekly blog posts',
          config: {
            contentType: 'blog',
            frequency: 'weekly',
            topics: 8,
            seo: true
          },
          optional: false
        },
        {
          type: MoveType.SOCIAL_MEDIA,
          name: 'Content Distribution',
          description: 'Share across platforms',
          config: {
            platforms: ['all'],
            frequency: 'daily',
            automation: true
          },
          optional: false
        },
        {
          type: MoveType.EMAIL,
          name: 'Content Digest',
          description: 'Weekly content roundup',
          config: {
            frequency: 'weekly',
            template: 'digest',
            personalization: true
          },
          optional: false
        },
        {
          type: MoveType.ANALYTICS,
          name: 'Performance Tracking',
          description: 'Monitor content performance',
          config: {
            metrics: ['views', 'engagement', 'conversions'],
            frequency: 'weekly',
            reporting: 'automated'
          },
          optional: false
        }
      ],
      defaultSettings: {
        autoOptimization: true,
        abTesting: false,
        notifications: {
          email: true,
          push: false,
          slack: true,
          frequency: 'weekly',
          events: ['publish', 'milestone']
        }
      }
    },
    isPublic: true,
    usageCount: 1920,
    rating: 4.6
  },
  {
    id: 'cm-video-series',
    name: 'YouTube Video Series',
    description: 'Build audience with video content',
    category: 'Content Marketing',
    objective: CampaignObjective.AWARENESS,
    structure: {
      phases: [
        {
          name: 'Pre-Launch',
          description: 'Build anticipation',
          startDate: new Date(),
          endDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Launch Phase',
          description: 'Release initial episodes',
          startDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 42 * 24 * 60 * 60 * 1000)
        },
        {
          name: 'Growth Phase',
          description: 'Scale and optimize',
          startDate: new Date(Date.now() + 42 * 24 * 60 * 60 * 1000),
          endDate: new Date(Date.now() + 84 * 24 * 60 * 60 * 1000)
        }
      ],
      recommendedMoves: [
        {
          type: MoveType.CONTENT,
          name: 'Video Production',
          description: 'Create video episodes',
          config: {
            contentType: 'video',
            frequency: 'weekly',
            duration: 10,
            quality: '4k'
          },
          optional: false
        },
        {
          type: MoveType.SOCIAL_MEDIA,
          name: 'YouTube SEO',
          description: 'Optimize for search',
          config: {
            platform: 'youtube',
            optimization: 'seo',
            thumbnails: 'custom',
            scheduling: 'optimal'
          },
          optional: false
        },
        {
          type: MoveType.EMAIL,
          name: 'Video Alerts',
          description: 'Notify subscribers',
          config: {
            trigger: 'new-video',
            template: 'video-alert',
            preview: 'thumbnail'
          },
          optional: false
        }
      ],
      defaultSettings: {
        autoOptimization: true,
        abTesting: true,
        notifications: {
          email: true,
          push: true,
          slack: false,
          frequency: 'weekly',
          events: ['upload', 'milestone']
        }
      }
    },
    isPublic: true,
    usageCount: 650,
    rating: 4.4
  }
];

// All templates combined
export const allCampaignTemplates = [
  ...productLaunchTemplates,
  ...leadGenTemplates,
  ...brandAwarenessTemplates,
  ...eventPromotionTemplates,
  ...contentMarketingTemplates
];

// Template categories
export const templateCategories = [
  { id: 'product-launch', name: 'Product Launch', count: 2 },
  { id: 'lead-generation', name: 'Lead Generation', count: 2 },
  { id: 'brand-awareness', name: 'Brand Awareness', count: 1 },
  { id: 'event-promotion', name: 'Event Promotion', count: 1 },
  { id: 'content-marketing', name: 'Content Marketing', count: 2 }
];

// Helper functions
export const getTemplateById = (id: string): CampaignTemplate | undefined => {
  return allCampaignTemplates.find(template => template.id === id);
};

export const getTemplatesByObjective = (objective: CampaignObjective): CampaignTemplate[] => {
  return allCampaignTemplates.filter(template => template.objective === objective);
};

export const getTemplatesByCategory = (category: string): CampaignTemplate[] => {
  return allCampaignTemplates.filter(template => template.category === category);
};

export const getPopularTemplates = (limit: number = 5): CampaignTemplate[] => {
  return allCampaignTemplates
    .sort((a, b) => b.usageCount - a.usageCount)
    .slice(0, limit);
};

export const getTopRatedTemplates = (limit: number = 5): CampaignTemplate[] => {
  return allCampaignTemplates
    .sort((a, b) => b.rating - a.rating)
    .slice(0, limit);
};
