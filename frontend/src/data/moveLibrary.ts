import { Move, MoveType, MoveConfig } from '@/types/campaign';

// Email Sequence Moves
export const emailSequenceMoves = [
  {
    id: 'email-welcome-series',
    name: 'Welcome Email Series',
    type: MoveType.EMAIL,
    description: 'Multi-email welcome sequence for new subscribers',
    category: 'onboarding',
    config: {
      sequence: [
        {
          day: 0,
          subject: 'Welcome to [Company Name]!',
          template: 'welcome',
          content: 'Introduction and value proposition'
        },
        {
          day: 1,
          subject: 'Getting Started Guide',
          template: 'getting-started',
          content: 'Quick start tips and resources'
        },
        {
          day: 3,
          subject: 'Best Practices',
          template: 'best-practices',
          content: 'How to get maximum value'
        },
        {
          day: 7,
          subject: 'Advanced Features',
          template: 'advanced',
          content: 'Deep dive into powerful features'
        }
      ],
      automation: true,
      personalization: ['firstName', 'company'],
      tracking: true
    } as MoveConfig,
    icon: '📧',
    difficulty: 'beginner',
    estimatedTime: '30 minutes setup'
  },
  {
    id: 'email-nurture-sequence',
    name: 'Lead Nurture Sequence',
    type: MoveType.EMAIL,
    description: 'Nurture leads through the funnel with targeted content',
    category: 'lead-generation',
    config: {
      sequence: [
        {
          day: 0,
          subject: 'Thanks for your interest!',
          template: 'initial-response',
          content: 'Acknowledge and provide immediate value'
        },
        {
          day: 2,
          subject: 'Case Study: [Similar Company]',
          template: 'case-study',
          content: 'Social proof and results'
        },
        {
          day: 5,
          subject: 'Common Challenges',
          template: 'problem-solution',
          content: 'Address pain points'
        },
        {
          day: 10,
          subject: 'Ready to talk?',
          template: 'demo-invite',
          content: 'Call to action for demo'
        }
      ],
      triggers: [{
        type: 'event',
        conditions: [{ field: 'source', operator: 'equals', value: 'lead-capture' }]
      }],
      scoring: true,
      segmentation: 'behavior-based'
    } as MoveConfig,
    icon: '🌱',
    difficulty: 'intermediate',
    estimatedTime: '1 hour setup'
  },
  {
    id: 'email-abandoned-cart',
    name: 'Abandoned Cart Recovery',
    type: MoveType.EMAIL,
    description: 'Recover lost sales with targeted cart abandonment emails',
    category: 'conversion',
    config: {
      sequence: [
        {
          delay: '1 hour',
          subject: 'Did you forget something?',
          template: 'cart-reminder',
          content: 'Gentle reminder with product images'
        },
        {
          delay: '24 hours',
          subject: 'Still thinking about it?',
          template: 'cart-benefits',
          content: 'Highlight benefits and social proof'
        },
        {
          delay: '72 hours',
          subject: 'Complete your order',
          template: 'cart-urgency',
          content: 'Limited time offer or bonus'
        }
      ],
      trigger: 'cart-abandonment',
      dynamicContent: true,
      urgency: true
    } as MoveConfig,
    icon: '🛒',
    difficulty: 'intermediate',
    estimatedTime: '45 minutes setup'
  }
];

// Social Media Moves
export const socialMediaMoves = [
  {
    id: 'social-content-calendar',
    name: 'Content Calendar Automation',
    type: MoveType.SOCIAL_MEDIA,
    description: 'Automated posting schedule across multiple platforms',
    category: 'content',
    config: {
      platforms: ['linkedin', 'twitter', 'facebook', 'instagram'],
      schedule: {
        scheduleType: 'recurring',
        frequency: 'daily',
        times: ['09:00', '14:00', '18:00'],
        timezone: 'user-timezone'
      } as any,
      contentTypes: ['blog-links', 'tips', 'questions', 'behind-scenes'],
      hashtags: ['auto-generate', 'custom'],
      engagement: {
        respondToComments: true,
        monitorMentions: true,
        engageWithFollowers: true
      }
    } as MoveConfig,
    icon: '📅',
    difficulty: 'intermediate',
    estimatedTime: '2 hours setup'
  },
  {
    id: 'social-launch-campaign',
    name: 'Product Launch Campaign',
    type: MoveType.SOCIAL_MEDIA,
    description: 'Coordinated social media campaign for product launches',
    category: 'launch',
    config: {
      phases: [
        {
          name: 'Teaser',
          duration: '7 days',
          content: 'Mystery posts, countdowns',
          frequency: 'daily'
        },
        {
          name: 'Announcement',
          duration: '3 days',
          content: 'Big reveal, features',
          frequency: 'multiple-daily'
        },
        {
          name: 'Launch',
          duration: '14 days',
          content: 'Demo, testimonials, offers',
          frequency: 'daily'
        }
      ],
      platforms: ['all'],
      paidAmplification: true,
      influencerOutreach: true
    } as MoveConfig,
    icon: '🚀',
    difficulty: 'advanced',
    estimatedTime: '4 hours setup'
  },
  {
    id: 'social-engagement-boost',
    name: 'Engagement Boost',
    type: MoveType.SOCIAL_MEDIA,
    description: 'Increase engagement with interactive content',
    category: 'engagement',
    config: {
      contentTypes: ['polls', 'quizzes', 'questions', 'contests'],
      schedule: {
        scheduleType: 'recurring',
        frequency: 'weekly',
        optimalTimes: true
      } as any,
      automation: {
        autoRespond: true,
        likeComments: true,
        followBack: true
      },
      analytics: {
        trackEngagement: true,
        optimizeTiming: true,
        'a/bTest': true
      }
    } as MoveConfig,
    icon: '💬',
    difficulty: 'beginner',
    estimatedTime: '1 hour setup'
  }
];

// Content Creation Moves
export const contentCreationMoves = [
  {
    id: 'content-blog-series',
    name: 'Blog Post Series',
    type: MoveType.CONTENT,
    description: 'Create and publish a series of related blog posts',
    category: 'content-marketing',
    config: {
      series: {
        topic: 'industry-trends',
        posts: 8,
        frequency: 'weekly',
        length: '1500-2000 words'
      },
      seo: {
        keywordResearch: true,
        metaOptimization: true,
        internalLinking: true
      },
      distribution: {
        emailNewsletter: true,
        socialMedia: true,
        syndication: ['medium', 'linkedin']
      },
      repurposing: {
        socialSnippets: true,
        videoSummary: true,
        infographic: true,
        podcast: true
      }
    } as MoveConfig,
    icon: '📝',
    difficulty: 'intermediate',
    estimatedTime: '8 hours total'
  },
  {
    id: 'content-video-series',
    name: 'YouTube Video Series',
    type: MoveType.CONTENT,
    description: 'Produce and publish a video series on YouTube',
    category: 'video',
    config: {
      series: {
        format: 'educational',
        episodes: 12,
        duration: '10-15 minutes',
        frequency: 'bi-weekly'
      },
      production: {
        quality: '1080p',
        branding: true,
        thumbnails: 'custom',
        captions: true
      },
      optimization: {
        seo: true,
        endScreen: true,
        cards: true,
        playlist: true
      },
      promotion: {
        socialClips: true,
        emailAnnounce: true,
        crossPromotion: true
      }
    } as MoveConfig,
    icon: '🎥',
    difficulty: 'advanced',
    estimatedTime: '20 hours total'
  },
  {
    id: 'content-lead-magnet',
    name: 'Lead Magnet Creation',
    type: MoveType.CONTENT,
    description: 'Create a comprehensive lead magnet and promotion strategy',
    category: 'lead-generation',
    config: {
      magnet: {
        type: 'ebook',
        topic: 'industry-guide',
        length: '30 pages',
        design: 'professional'
      },
      landingPage: {
        template: 'high-conversion',
        elements: ['video', 'testimonials', 'countdown'],
        optimization: 'a/b-test'
      },
      promotion: {
        socialPosts: true,
        emailSequence: true,
        paidAds: true,
        partnerships: true
      },
      followUp: {
        nurtureSequence: true,
        segmentation: true,
        scoring: true
      }
    } as MoveConfig,
    icon: '🎁',
    difficulty: 'intermediate',
    estimatedTime: '12 hours total'
  }
];

// Outreach Moves
export const outreachMoves = [
  {
    id: 'outreach-cold-email',
    name: 'Cold Email Campaign',
    type: MoveType.OUTREACH,
    description: 'Systematic cold email outreach with personalization',
    category: 'sales',
    config: {
      sequence: [
        {
          day: 0,
          type: 'introduction',
          personalization: 'research-based',
          cta: 'reply'
        },
        {
          day: 3,
          type: 'value-proposition',
          socialProof: true,
          cta: '15-min-call'
        },
        {
          day: 7,
          type: 'follow-up',
          caseStudy: true,
          cta: 'demo'
        },
        {
          day: 14,
          type: 'breakup',
          helpful: true,
          doorOpen: true
        }
      ],
      targeting: {
        listSize: 500,
        criteria: 'ideal-customer',
        enrichment: true
      },
      personalization: {
        companyResearch: true,
        triggerEvents: true,
        customFields: true
      },
      tracking: {
        opens: true,
        clicks: true,
        replies: true,
        bookings: true
      }
    } as MoveConfig,
    icon: '📨',
    difficulty: 'advanced',
    estimatedTime: '6 hours setup'
  },
  {
    id: 'outreach-linkedin',
    name: 'LinkedIn Outreach',
    type: MoveType.OUTREACH,
    description: 'Multi-touch LinkedIn outreach strategy',
    category: 'social-selling',
    config: {
      sequence: [
        {
          day: 0,
          action: 'connect-request',
          message: 'personalized'
        },
        {
          day: 2,
          action: 'follow-up-message',
          value: 'helpful-content'
        },
        {
          day: 5,
          action: 'engage-with-content',
          type: 'meaningful-comment'
        },
        {
          day: 10,
          action: 'inmail',
          cta: 'value-first'
        }
      ],
      targeting: {
        filters: ['title', 'company', 'industry'],
        listSize: 200,
        warmIntro: true
      },
      automation: {
        connectionRequests: true,
        messageSequences: true,
        engagement: true
      },
      compliance: {
        dailyLimits: true,
        spacing: true,
        personalization: true
      }
    } as MoveConfig,
    icon: '💼',
    difficulty: 'intermediate',
    estimatedTime: '4 hours setup'
  },
  {
    id: 'outreach-partnership',
    name: 'Partnership Outreach',
    type: MoveType.OUTREACH,
    description: 'Strategic partnership development program',
    category: 'business-development',
    config: {
      targets: {
        types: ['complementary', 'industry', 'influencer'],
        criteria: 'alignment-score',
        research: 'deep-dive'
      },
      approach: {
        valueProposition: true,
        mutualBenefit: true,
        customization: 'high'
      },
      followUp: {
        sequence: 5,
        valueAdd: true,
        persistence: 'respectful'
      },
      tracking: {
        crmIntegration: true,
        pipelineStage: true,
        roi: true
      }
    } as MoveConfig,
    icon: '🤝',
    difficulty: 'advanced',
    estimatedTime: '8 hours setup'
  }
];

// Analytics Moves
export const analyticsMoves = [
  {
    id: 'analytics-dashboard',
    name: 'Performance Dashboard',
    type: MoveType.ANALYTICS,
    description: 'Comprehensive analytics dashboard setup',
    category: 'measurement',
    config: {
      metrics: {
        primary: ['conversions', 'revenue', 'roi'],
        secondary: ['engagement', 'reach', 'cost'],
        custom: ['business-specific-kpis']
      },
      sources: [
        'google-analytics',
        'crm-data',
        'email-platform',
        'social-media',
        'ad-platforms'
      ],
      visualization: {
        charts: ['funnel', 'trend', 'comparison'],
        realTime: true,
        drillDown: true
      },
      reporting: {
        automated: true,
        frequency: 'weekly',
        stakeholders: ['team', 'management'],
        format: ['web', 'pdf', 'email']
      }
    } as MoveConfig,
    icon: '📊',
    difficulty: 'intermediate',
    estimatedTime: '4 hours setup'
  },
  {
    id: 'analytics-ab-testing',
    name: 'A/B Testing Framework',
    type: MoveType.ANALYTICS,
    description: 'Continuous optimization through A/B testing',
    category: 'optimization',
    config: {
      testTypes: [
        'email-subjects',
        'landing-pages',
        'ad-copy',
        'call-to-action',
        'pricing'
      ],
      methodology: {
        significance: '95%',
        sampleSize: 'auto-calculate',
        duration: 'auto-determine'
      },
      implementation: {
        tool: 'platform-native',
        segmentation: true,
        multivariate: true
      },
      learning: {
        automatedInsights: true,
        winnerDeployment: true,
        resultLibrary: true
      }
    } as MoveConfig,
    icon: '🧪',
    difficulty: 'advanced',
    estimatedTime: '6 hours setup'
  },
  {
    id: 'analytics-attribution',
    name: 'Multi-Touch Attribution',
    type: MoveType.ANALYTICS,
    description: 'Track customer journey across all touchpoints',
    category: 'attribution',
    config: {
      model: {
        type: 'data-driven',
        algorithms: ['markov-chain', 'shapley-value'],
        customWeights: true
      },
      tracking: {
        touchpoints: 'all-channels',
        customerJourney: true,
        timeDecay: true
      },
      integration: {
        crm: true,
        analytics: true,
        advertising: true,
        email: true
      },
      insights: {
        pathAnalysis: true,
        channelContribution: true,
        optimization: true
      }
    } as MoveConfig,
    icon: '🎯',
    difficulty: 'expert',
    estimatedTime: '10 hours setup'
  }
];

// All moves combined
export const allMoves = [
  ...emailSequenceMoves,
  ...socialMediaMoves,
  ...contentCreationMoves,
  ...outreachMoves,
  ...analyticsMoves
];

// Move categories
export const moveCategories = [
  { id: 'email', name: 'Email Marketing', count: emailSequenceMoves.length },
  { id: 'social', name: 'Social Media', count: socialMediaMoves.length },
  { id: 'content', name: 'Content Creation', count: contentCreationMoves.length },
  { id: 'outreach', name: 'Outreach', count: outreachMoves.length },
  { id: 'analytics', name: 'Analytics', count: analyticsMoves.length }
];

// Helper functions
export const getMoveById = (id: string) => {
  return allMoves.find(move => move.id === id);
};

export const getMovesByType = (type: MoveType) => {
  return allMoves.filter(move => move.type === type);
};

export const getMovesByCategory = (category: string) => {
  return allMoves.filter(move => move.category === category);
};

export const getMovesByDifficulty = (difficulty: string) => {
  return allMoves.filter(move => move.difficulty === difficulty);
};

export const getPopularMoves = (limit: number = 5) => {
  // In real implementation, this would be based on usage data
  return [
    allMoves[0], // Welcome Email Series
    allMoves[3], // Content Calendar Automation
    allMoves[6], // Blog Post Series
    allMoves[9], // Lead Magnet Creation
    allMoves[12] // Performance Dashboard
  ].slice(0, limit);
};

export const getRecommendedMoves = (objective: string, budget: number, teamSize: number) => {
  let recommended: any[] = [];

  if (objective === 'lead-generation') {
    recommended = [
      allMoves[1], // Lead Nurture Sequence
      allMoves[8], // Lead Magnet Creation
      allMoves[9]  // Cold Email Campaign
    ];
  } else if (objective === 'awareness') {
    recommended = [
      allMoves[3], // Content Calendar Automation
      allMoves[4], // Launch Campaign
      allMoves[6]  // Blog Post Series
    ];
  } else if (objective === 'conversion') {
    recommended = [
      allMoves[2], // Abandoned Cart
      allMoves[10], // Partnership Outreach
      allMoves[14] // A/B Testing
    ];
  }

  // Filter by team size and budget
  if (teamSize === 1) {
    recommended = recommended.filter(m => m.difficulty !== 'expert');
  }

  return recommended;
};
