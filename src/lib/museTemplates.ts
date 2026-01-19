export interface Template {
  id: string;
  title: string;
  description: string;
  category: 'saas' | 'ecommerce' | 'consulting' | 'b2b' | 'b2c' | 'startup' | 'enterprise';
  type: 'email' | 'blog' | 'social' | 'script' | 'campaign';
  sections: TemplateSection[];
  placeholders?: Record<string, string>;
  tags: string[];
  estimatedReadTime?: number;
  conversionTips?: string[];
}

export interface TemplateSection {
  id: string;
  title: string;
  prompt: string;
  placeholder?: string;
  required?: boolean;
}

export const SAAS_TEMPLATES: Template[] = [
  {
    id: 'saas-product-launch',
    title: 'Product Launch Announcement',
    description: 'Announce your new SaaS product to the world with compelling messaging',
    category: 'saas',
    type: 'email',
    sections: [
      {
        id: 'hook',
        title: 'Hook',
        prompt: 'Start with a compelling hook that grabs attention and states the problem',
        placeholder: 'Tired of [problem]? What if you could [solution]?',
        required: true
      },
      {
        id: 'solution',
        title: 'Solution',
        prompt: 'Introduce your product as the solution to the problem',
        placeholder: 'Introducing [Product Name] - the [adjective] solution that [benefit]',
        required: true
      },
      {
        id: 'features',
        title: 'Key Features',
        prompt: 'List 3-5 key features with benefits',
        placeholder: '• [Feature 1]: [Benefit]\n• [Feature 2]: [Benefit]\n• [Feature 3]: [Benefit]',
        required: true
      },
      {
        id: 'social-proof',
        title: 'Social Proof',
        prompt: 'Add testimonials, user numbers, or success metrics',
        placeholder: 'Join [number] users who have already [achieved result]',
        required: false
      },
      {
        id: 'cta',
        title: 'Call to Action',
        prompt: 'Clear call to action with urgency',
        placeholder: 'Start your [trial period] trial today - no credit card required',
        required: true
      }
    ],
    placeholders: {
      productName: 'Your product name',
      companyName: 'Your company name',
      targetAudience: 'Your target audience',
      keyBenefit: 'Main benefit',
      trialPeriod: '14-day',
      launchDate: 'Launch date'
    },
    tags: ['Launch', 'Product', 'Announcement'],
    estimatedReadTime: 2,
    conversionTips: [
      'Use numbers and specific metrics',
      'Include a clear P.S. with bonus',
      'Add scarcity with limited-time offer'
    ]
  },
  {
    id: 'saas-customer-story',
    title: 'Customer Success Story',
    description: 'Showcase how customers succeed with your product',
    category: 'saas',
    type: 'blog',
    sections: [
      {
        id: 'customer-intro',
        title: 'Customer Introduction',
        prompt: 'Introduce the customer and their background',
        placeholder: '[Customer Name] is a [industry] company that [does what]',
        required: true
      },
      {
        id: 'challenge',
        title: 'The Challenge',
        prompt: 'Describe the problem they faced before your product',
        placeholder: 'Before using [Product], they struggled with [specific challenges]',
        required: true
      },
      {
        id: 'solution',
        title: 'The Solution',
        prompt: 'Explain how your product solved their problem',
        placeholder: 'With [Product], they were able to [achieve specific results]',
        required: true
      },
      {
        id: 'results',
        title: 'Results',
        prompt: 'Quantify the results with specific metrics',
        placeholder: '• [Metric 1]: [specific result]\n• [Metric 2]: [specific result]\n• [Metric 3]: [specific result]',
        required: true
      },
      {
        id: 'quote',
        title: 'Customer Quote',
        prompt: 'Include a powerful quote from the customer',
        placeholder: '"[Product] has completely transformed how we [process]"',
        required: true
      }
    ],
    placeholders: {
      customerName: 'Customer name',
      industry: 'Industry',
      productName: 'Your product name',
      metric1: 'Key metric',
      metric2: 'Second metric',
      metric3: 'Third metric'
    },
    tags: ['Case Study', 'Social Proof', 'Success'],
    estimatedReadTime: 3,
    conversionTips: [
      'Use real customer names with permission',
      'Include before/after comparisons',
      'Add specific ROI calculations'
    ]
  },
  {
    id: 'saas-onboarding-email',
    title: 'User Onboarding Sequence',
    description: 'Welcome new users and guide them to success',
    category: 'saas',
    type: 'email',
    sections: [
      {
        id: 'welcome',
        title: 'Welcome',
        prompt: 'Warm welcome and confirmation',
        placeholder: 'Welcome to [Product Name]! We\'re excited to have you aboard',
        required: true
      },
      {
        id: 'first-step',
        title: 'First Step',
        prompt: 'Guide them to the first critical action',
        placeholder: 'Your first step: [complete this action] to [achieve this benefit]',
        required: true
      },
      {
        id: 'resources',
        title: 'Helpful Resources',
        prompt: 'Point to documentation, tutorials, or support',
        placeholder: 'Check out our [resource type] to learn more',
        required: false
      },
      {
        id: 'support',
        title: 'Support',
        prompt: 'Let them know how to get help',
        placeholder: 'Questions? Reply to this email or visit our help center',
        required: true
      }
    ],
    placeholders: {
      productName: 'Your product name',
      firstAction: 'First action to take',
      resourceType: 'Type of resource',
      supportEmail: 'Support email'
    },
    tags: ['Onboarding', 'Welcome', 'Tutorial'],
    estimatedReadTime: 1,
    conversionTips: [
      'Keep it short and actionable',
      'Use progress tracking',
      'Include video tutorials'
    ]
  }
];

export const ECOMMERCE_TEMPLATES: Template[] = [
  {
    id: 'ecommerce-product-launch',
    title: 'New Product Launch',
    description: 'Launch a new product with excitement and urgency',
    category: 'ecommerce',
    type: 'email',
    sections: [
      {
        id: 'announcement',
        title: 'Big News',
        prompt: 'Announce the new product with excitement',
        placeholder: 'It\'s finally here! Introducing [Product Name]',
        required: true
      },
      {
        id: 'product-details',
        title: 'Product Details',
        prompt: 'Describe the product and its unique features',
        placeholder: '[Product Name] is [description] that [solves problem]',
        required: true
      },
      {
        id: 'benefits',
        title: 'Benefits',
        prompt: 'List the key benefits for the customer',
        placeholder: '• [Benefit 1]\n• [Benefit 2]\n• [Benefit 3]',
        required: true
      },
      {
        id: 'offer',
        title: 'Special Offer',
        prompt: 'Create urgency with a limited-time offer',
        placeholder: 'Launch special: [discount] off for [time period] only',
        required: true
      },
      {
        id: 'cta',
        title: 'Shop Now',
        prompt: 'Clear call to action to shop',
        placeholder: 'Shop now before it\'s gone!',
        required: true
      }
    ],
    placeholders: {
      productName: 'Product name',
      discount: 'Discount percentage',
      timePeriod: 'Time period',
      uniqueFeature: 'Unique feature'
    },
    tags: ['Launch', 'Product', 'Sale'],
    estimatedReadTime: 2,
    conversionTips: [
      'Use high-quality product images',
      'Include customer reviews',
      'Add countdown timer for urgency'
    ]
  },
  {
    id: 'ecommerce-abandoned-cart',
    title: 'Abandoned Cart Recovery',
    description: 'Recover lost sales with targeted cart recovery emails',
    category: 'ecommerce',
    type: 'email',
    sections: [
      {
        id: 'reminder',
        title: 'Gentle Reminder',
        prompt: 'Remind them about their abandoned cart',
        placeholder: 'Did you forget something? Your cart is waiting',
        required: true
      },
      {
        id: 'items',
        title: 'Items in Cart',
        prompt: 'List the items they left behind',
        placeholder: 'You left behind:\n• [Item 1]\n• [Item 2]',
        required: true
      },
      {
        id: 'incentive',
        title: 'Special Incentive',
        prompt: 'Offer a small discount to complete purchase',
        placeholder: 'Complete your order now and get [discount] off',
        required: false
      },
      {
        id: 'urgency',
        title: 'Urgency',
        prompt: 'Create urgency around stock or offer',
        placeholder: 'Items in your cart are selling fast',
        required: true
      },
      {
        id: 'cta',
        title: 'Return to Cart',
        prompt: 'Clear link back to their cart',
        placeholder: 'Return to your cart',
        required: true
      }
    ],
    placeholders: {
      discount: 'Discount percentage',
      item1: 'First item',
      item2: 'Second item',
      timeLimit: 'Time limit'
    },
    tags: ['Recovery', 'Sales', 'Urgency'],
    estimatedReadTime: 1,
    conversionTips: [
      'Show product images in email',
      'Include customer reviews for items',
      'Use exit-intent popups'
    ]
  }
];

export const CONSULTING_TEMPLATES: Template[] = [
  {
    id: 'consulting-proposal',
    title: 'Consulting Proposal',
    description: 'Professional proposal for consulting services',
    category: 'consulting',
    type: 'email',
    sections: [
      {
        id: 'understanding',
        title: 'Understanding',
        prompt: 'Show you understand their problem',
        placeholder: 'Based on our discussion, I understand you\'re facing [challenge]',
        required: true
      },
      {
        id: 'solution',
        title: 'Proposed Solution',
        prompt: 'Outline your proposed solution',
        placeholder: 'I propose we [solution approach] to achieve [desired outcome]',
        required: true
      },
      {
        id: 'deliverables',
        title: 'Deliverables',
        prompt: 'List specific deliverables',
        placeholder: '• [Deliverable 1]\n• [Deliverable 2]\n• [Deliverable 3]',
        required: true
      },
      {
        id: 'timeline',
        title: 'Timeline',
        prompt: 'Proposed project timeline',
        placeholder: 'Project timeline: [duration] weeks starting [start date]',
        required: true
      },
      {
        id: 'investment',
        title: 'Investment',
        prompt: 'Clear pricing and payment terms',
        placeholder: 'Total investment: $[amount] with [payment terms]',
        required: true
      },
      {
        id: 'next-steps',
        title: 'Next Steps',
        prompt: 'Clear next steps to move forward',
        placeholder: 'To proceed, simply [next action]',
        required: true
      }
    ],
    placeholders: {
      challenge: 'Their challenge',
      solution: 'Your solution',
      duration: 'Project duration',
      amount: 'Total amount',
      startDate: 'Start date'
    },
    tags: ['Proposal', 'Business', 'Sales'],
    estimatedReadTime: 3,
    conversionTips: [
      'Include case studies',
      'Offer multiple pricing tiers',
      'Add satisfaction guarantee'
    ]
  }
];

export const B2B_TEMPLATES: Template[] = [
  {
    id: 'b2b-cold-email',
    title: 'B2B Cold Email',
    description: 'Effective cold email for B2B outreach',
    category: 'b2b',
    type: 'email',
    sections: [
      {
        id: 'research',
        title: 'Personalized Research',
        prompt: 'Show you\'ve done your research',
        placeholder: 'I noticed [specific observation about their company]',
        required: true
      },
      {
        id: 'problem',
        title: 'Problem Identification',
        prompt: 'Identify a problem you can solve',
        placeholder: 'Many [industry] companies struggle with [problem]',
        required: true
      },
      {
        id: 'solution',
        title: 'Solution',
        prompt: 'Brief solution overview',
        placeholder: 'We help [industry] companies [achieve result] through [method]',
        required: true
      },
      {
        id: 'proof',
        title: 'Social Proof',
        prompt: 'Add relevant social proof',
        placeholder: 'We helped [similar company] achieve [specific result]',
        required: true
      },
      {
        id: 'ask',
        title: 'Clear Ask',
        prompt: 'Specific, low-friction ask',
        placeholder: 'Would you be open to a 15-minute call next week?',
        required: true
      }
    ],
    placeholders: {
      industry: 'Their industry',
      problem: 'Their problem',
      result: 'Desired result',
      similarCompany: 'Similar company'
    },
    tags: ['Cold Email', 'Sales', 'Outreach'],
    estimatedReadTime: 1,
    conversionTips: [
      'Keep under 150 words',
      'Use their name in subject',
      'Reference recent company news'
    ]
  }
];

export const B2C_TEMPLATES: Template[] = [
  {
    id: 'b2c-promotional-email',
    title: 'Promotional Email',
    description: 'Drive sales with promotional content',
    category: 'b2c',
    type: 'email',
    sections: [
      {
        id: 'headline',
        title: 'Catchy Headline',
        prompt: 'Grab attention with an exciting headline',
        placeholder: '🎉 BIG NEWS! [Exciting announcement]',
        required: true
      },
      {
        id: 'offer',
        title: 'The Offer',
        prompt: 'Clearly state the promotion',
        placeholder: 'Get [discount] off all [product category]!',
        required: true
      },
      {
        id: 'products',
        title: 'Featured Products',
        prompt: 'Highlight 3-4 featured products',
        placeholder: '• [Product 1] - [price]\n• [Product 2] - [price]',
        required: true
      },
      {
        id: 'urgency',
        title: 'Urgency',
        prompt: 'Create time-sensitive urgency',
        placeholder: 'Sale ends [date] - Don\'t miss out!',
        required: true
      },
      {
        id: 'cta',
        title: 'Shop Now',
        prompt: 'Clear call to action',
        placeholder: 'Shop the Sale →',
        required: true
      }
    ],
    placeholders: {
      discount: 'Discount amount',
      productCategory: 'Product category',
      endDate: 'End date',
      product1: 'First product'
    },
    tags: ['Promotion', 'Sale', 'B2C'],
    estimatedReadTime: 2,
    conversionTips: [
      'Use emojis strategically',
      'Include hero product image',
      'Add free shipping threshold'
    ]
  }
];

export const STARTUP_TEMPLATES: Template[] = [
  {
    id: 'startup-investor-update',
    title: 'Investor Update',
    description: 'Keep investors informed and engaged',
    category: 'startup',
    type: 'email',
    sections: [
      {
        id: 'highlights',
        title: 'Monthly Highlights',
        prompt: '3-5 key achievements this month',
        placeholder: '• [Achievement 1]\n• [Achievement 2]\n• [Achievement 3]',
        required: true
      },
      {
        id: 'metrics',
        title: 'Key Metrics',
        prompt: 'Important business metrics',
        placeholder: 'Revenue: $[amount]\nUsers: [number]\nGrowth: [percentage]%',
        required: true
      },
      {
        id: 'challenges',
        title: 'Challenges',
        prompt: 'Be transparent about challenges',
        placeholder: 'We\'re currently working through [challenge]',
        required: true
      },
      {
        id: 'focus',
        title: 'Next Month Focus',
        prompt: 'What you\'re working on next',
        placeholder: 'Next month, we\'re focusing on [priority]',
        required: true
      },
      {
        id: 'ask',
        title: 'The Ask',
        prompt: 'Specific help needed from investors',
        placeholder: 'We could use your help with [specific request]',
        required: false
      }
    ],
    placeholders: {
      achievement1: 'First achievement',
      revenue: 'Monthly revenue',
      users: 'User count',
      growth: 'Growth percentage',
      challenge: 'Current challenge'
    },
    tags: ['Investors', 'Update', 'Startup'],
    estimatedReadTime: 2,
    conversionTips: [
      'Be honest about setbacks',
      'Include customer testimonials',
      'Forward to strategic introductions'
    ]
  }
];

export const ENTERPRISE_TEMPLATES: Template[] = [
  {
    id: 'enterprise-solution-brief',
    title: 'Enterprise Solution Brief',
    description: 'Comprehensive overview for enterprise clients',
    category: 'enterprise',
    type: 'email',
    sections: [
      {
        id: 'executive-summary',
        title: 'Executive Summary',
        prompt: 'High-level overview for executives',
        placeholder: '[Solution] addresses [critical business need] for [industry]',
        required: true
      },
      {
        id: 'business-impact',
        title: 'Business Impact',
        prompt: 'Quantify business value',
        placeholder: 'Typical ROI: [percentage]% within [timeframe]',
        required: true
      },
      {
        id: 'technical-overview',
        title: 'Technical Overview',
        prompt: 'Brief technical details',
        placeholder: 'Built on [technology] with [security standards]',
        required: true
      },
      {
        id: 'integration',
        title: 'Integration',
        prompt: 'How it integrates with existing systems',
        placeholder: 'Seamlessly integrates with [existing systems]',
        required: true
      },
      {
        id: 'case-study',
        title: 'Relevant Case Study',
        prompt: 'Similar enterprise success story',
        placeholder: '[Similar Company] achieved [specific results]',
        required: true
      },
      {
        id: 'next-steps',
        title: 'Next Steps',
        prompt: 'Clear path forward',
        placeholder: 'Schedule a technical demo with your team',
        required: true
      }
    ],
    placeholders: {
      solution: 'Your solution',
      industry: 'Target industry',
      roi: 'ROI percentage',
      timeframe: 'Timeframe',
      similarCompany: 'Similar company'
    },
    tags: ['Enterprise', 'B2B', 'Solution'],
    estimatedReadTime: 3,
    conversionTips: [
      'Focus on risk mitigation',
      'Include compliance information',
      'Address security concerns upfront'
    ]
  }
];

// Combine all templates
export const ALL_TEMPLATES = [
  ...SAAS_TEMPLATES,
  ...ECOMMERCE_TEMPLATES,
  ...CONSULTING_TEMPLATES,
  ...B2B_TEMPLATES,
  ...B2C_TEMPLATES,
  ...STARTUP_TEMPLATES,
  ...ENTERPRISE_TEMPLATES
];

// Template categories for filtering
export const TEMPLATE_CATEGORIES = [
  { id: 'saas', label: 'SaaS', icon: '☁️' },
  { id: 'ecommerce', label: 'E-commerce', icon: '🛒' },
  { id: 'consulting', label: 'Consulting', icon: '💼' },
  { id: 'b2b', label: 'B2B', icon: '🏢' },
  { id: 'b2c', label: 'B2C', icon: '👥' },
  { id: 'startup', label: 'Startup', icon: '🚀' },
  { id: 'enterprise', label: 'Enterprise', icon: '🏛️' }
];

// Template types for filtering
export const TEMPLATE_TYPES = [
  { id: 'email', label: 'Email', icon: '✉️' },
  { id: 'blog', label: 'Blog Post', icon: '📝' },
  { id: 'social', label: 'Social Media', icon: '💬' },
  { id: 'script', label: 'Script', icon: '📽️' },
  { id: 'campaign', label: 'Campaign', icon: '📢' }
];
