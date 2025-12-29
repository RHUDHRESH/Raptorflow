import { DerivedData } from './foundation';

export const mockDerivedData: DerivedData = {
  derivedAt: new Date().toISOString(),

  // 1. ICP REVEAL
  icps: [
    {
      id: 'icp-1',
      name: 'The "Exhausted Founder"',
      priority: 'primary',
      confidence: 94,
      description:
        'Early-stage SaaS founders who are tired of guessing and want a system.',
      firmographics: {
        companySize: '1-10 employees',
        industry: ['SaaS', 'B2B Tech'],
        geography: ['North America', 'India', 'Europe'],
        budget: '$500 - $2,000 / month',
      },
      painMap: {
        primary: 'Marketing feels like a "black box" they can\'t control.',
        secondary: ['Wasting money on ads', 'Inconsistent lead flow'],
        triggers: ['Missed quarterly target', 'Competitor raised funding'],
        urgency: 'now',
      },
      social: {
        platforms: [
          {
            name: 'LinkedIn',
            timing: 'Daily, morning scroll',
            vibe: 'Professional but personal',
          },
          {
            name: 'Twitter / X',
            timing: 'Evening',
            vibe: 'Vent, learn, connect',
          },
        ],
        authorities: ['Jason Lemkin', 'Lenny Rachitsky'],
      },
      buying: {
        committee: [{ role: 'Founder', focus: 'Speed & ROI' }],
        timeline: '2-7 days',
        proofNeeded: ['Case studies of similar founders', 'ROI calculator'],
        blockers: ['Budget constraints', 'Fear of implementation time'],
      },
      behavioral: {
        biases: [
          {
            name: 'Authority Bias',
            implication: 'Trusts other founders more than sales reps',
          },
        ],
        deRisking: ['Free trial', 'Cancel anytime'],
      },
    },
    {
      id: 'icp-2',
      name: 'The "Stretched Marketing Lead"',
      priority: 'secondary',
      confidence: 88,
      description:
        'Solo marketers or small team leads at Series A companies needing structure.',
      firmographics: {
        companySize: '10-50 employees',
        industry: ['B2B SaaS'],
        geography: ['Global'],
        budget: '$2k - $5k / month',
      },
      painMap: {
        primary: 'Overwhelmed by execution, no time for strategy.',
        secondary: ['Reporting to demanding CEO', 'Content treadmill'],
        triggers: ['New hiring freeze', 'Aggressive new targets'],
        urgency: 'soon',
      },
      social: {
        platforms: [
          { name: 'LinkedIn', timing: 'Work hours', vibe: 'Networking' },
        ],
        authorities: ['Dave Gerhardt', 'Exit Five'],
      },
      buying: {
        committee: [
          { role: 'Marketing Lead', focus: 'Efficiency' },
          { role: 'CEO', focus: 'Cost' },
        ],
        timeline: '2-4 weeks',
        proofNeeded: ['Team collaboration features', 'Reporting capabilities'],
        blockers: ['Integration with existing stack'],
      },
      behavioral: {
        biases: [
          {
            name: 'Sunk Cost',
            implication: 'Reluctant to switch from HubSpot completely',
          },
        ],
        deRisking: ['Migration support'],
      },
    },
  ],

  // 2. POSITIONING REVEAL
  positioning: {
    matrix: {
      xAxis: {
        label: 'Complexity',
        lowEnd: 'Simple / Plug-n-Play',
        highEnd: 'Enterprise / Custom',
      },
      yAxis: {
        label: 'Focus',
        lowEnd: 'Generalist Tool',
        highEnd: 'Specialized OS',
      },
      positions: [
        { name: 'HubSpot', x: 80, y: 20, isYou: false },
        { name: 'Notion Templates', x: 20, y: 40, isYou: false },
        { name: 'Agencies', x: 90, y: 60, isYou: false },
        { name: 'RaptorFlow', x: 30, y: 90, isYou: true },
      ],
    },
    ladder: [
      {
        rung: 1,
        name: 'Feature',
        description: 'AI Marketing Tool',
        score: 20,
        isYou: false,
      },
      {
        rung: 2,
        name: 'Benefit',
        description: 'Faster Content Creation',
        score: 45,
        isYou: false,
      },
      {
        rung: 3,
        name: 'Outcome',
        description: 'Automated Lead Gen',
        score: 70,
        isYou: false,
      },
      {
        rung: 4,
        name: 'Identity',
        description: 'Founder Marketing OS',
        score: 95,
        isYou: true,
      },
    ],
    statement: {
      forWhom: 'For early-stage B2B founders',
      company: 'RaptorFlow is the',
      category: 'Marketing Operating System',
      differentiator: 'that bridges the gap between strategy and execution',
      unlikeCompetitor:
        'unlike general project management tools or disconnected AI writers',
      because: 'because it forces you to build a foundation before you ship.',
    },
    oneThing: 'The only system that stops you from guessing.',
    defensibility: 'high',
  },

  // 3. COMPETITIVE REVEAL
  competitive: {
    statusQuo: {
      name: 'Chaos & Spreadsheets',
      description:
        'The default state of most startups: random acts of marketing.',
      manualPatches: [
        'Google Sheets content cal',
        'Notion docs for strategy',
        'Slack for coordination',
      ],
      toleratedPain: 'Low visibility, high anxiety, inconsistent output.',
      yourWedge: 'Structure. We turn the chaos into a checklist.',
    },
    indirect: [
      {
        name: 'Marketing Agencies',
        mechanism: 'Outsourced Execution',
        priceRange: '$5k - $15k / mo',
        weakness:
          "Slow, expensive, and they don't understand your product like you do.",
        yourEdge: 'Founder-led speed at 1/10th the cost.',
      },
    ],
    direct: [
      {
        name: 'HubSpot',
        positioning: 'All-in-one CRM',
        weakness: 'Complex, expensive, overkill for early stage.',
        yourEdge:
          'Purpose-built for lean execution, not just database management.',
        featureOverlap: 'medium',
      },
    ],
  },

  // 4. SOUNDBITES REVEAL
  soundbites: {
    oneLiner:
      'Stop guessing. Start executing. The operating system for founder-led growth.',
    soundbites: [
      {
        type: 'problem',
        awarenessLevel: 'problem',
        text: 'You don\'t have a traffic problem. You have a "what do I say?" problem.',
        useCase: 'LinkedIn Hook',
      },
      {
        type: 'agitation',
        awarenessLevel: 'problem',
        text: 'Every day you wait to build a marketing system is another day your competitor steals your best leads.',
        useCase: 'Email Subject',
      },
      {
        type: 'transformation',
        awarenessLevel: 'solution',
        text: 'Turn your random marketing ideas into a repeatable revenue engine.',
        useCase: 'Website Hero',
      },
      {
        type: 'objection',
        awarenessLevel: 'product',
        text: "You don't need more time. You need a better system.",
        useCase: 'Sales Call Handling',
      },
      {
        type: 'mechanism',
        awarenessLevel: 'solution',
        text: 'The Tri-Vector Positioning Engine',
        useCase: 'Feature Highlight',
      },
    ],
  },

  // 5. MARKET REVEAL
  market: {
    tam: { value: 12000000000, confidence: 'med', method: 'Top-down' },
    sam: { value: 450000000, confidence: 'high', method: 'Bottom-up' },
    som: { value: 15000000, confidence: 'high', timeline: '18 months' },

    assumptions: [
      {
        factor: 'Total SaaS Founders',
        value: '150,000 active',
        confidence: 'high',
      },
      {
        factor: 'Willingness to Pay',
        value: 'Expected to rise',
        confidence: 'med',
      },
      { factor: 'Churn Rate', value: 'Est 2.5% monthly', confidence: 'low' },
    ],

    pathToSom: {
      customersNeeded: 1500,
      leadsPerMonth: 450,
      winRate: 0.15,
      channelMix: [
        { channel: 'LinkedIn Organic', percentage: 40 },
        { channel: 'Cold Outbound', percentage: 30 },
        { channel: 'Referral / WOM', percentage: 20 },
        { channel: 'Content / SEO', percentage: 10 },
      ],
    },

    sliderDefaults: {
      targetAccounts: 5000,
      reachablePercent: 40,
      qualifiedPercent: 25,
      adoptionPercent: 10,
      arpa: 2000,
    },
  },
};
