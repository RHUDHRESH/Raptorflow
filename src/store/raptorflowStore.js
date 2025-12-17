import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import useNotificationsStore from './notificationsStore'

/**
 * RaptorFlow App Store
 * 
 * Complete state management for the RaptorFlow marketing OS:
 * - Strategy (versioned, in Settings)
 * - Campaigns (AI/Manual build)
 * - Moves (tactical strikes)
 * - Assets (from Muse)
 * - Radar (scans)
 * - Black Box (duels)
 * - Trail (targets)
 * - Usage & Limits
 */

// Plan limits configuration
const PLAN_LIMITS = {
  starter: {
    name: 'Starter',
    price: 5000,
    radarScansPerDay: 3,
    blackBoxDuelsPerMonth: 8,
    museGenerationsPerMonth: 200,
    icps: 3,
    activeCampaigns: 1,
    movesPerMonth: 20,
    seats: 1
  },
  glide: {
    name: 'Glide',
    price: 7000,
    radarScansPerDay: 6,
    blackBoxDuelsPerMonth: 25,
    museGenerationsPerMonth: 600,
    icps: 5,
    activeCampaigns: 3,
    movesPerMonth: 60,
    seats: 2
  },
  soar: {
    name: 'Soar',
    price: 12000,
    radarScansPerDay: 15,
    blackBoxDuelsPerMonth: 80,
    museGenerationsPerMonth: 1500,
    icps: 15,
    activeCampaigns: 10,
    movesPerMonth: 150,
    seats: 5
  },
  orbit: {
    name: 'Orbit',
    price: 25000,
    radarScansPerDay: 50,
    blackBoxDuelsPerMonth: 250,
    museGenerationsPerMonth: 5000,
    icps: 50,
    activeCampaigns: 999,
    movesPerMonth: 999,
    seats: 10
  }
}

const clamp = (value, min, max) => Math.min(Math.max(value, min), max)

const getDayNumberFromStart = (startDate, durationDays) => {
  if (!startDate) return 1
  const startMs = new Date(startDate).getTime()
  if (Number.isNaN(startMs)) return 1
  const diffDays = Math.floor((Date.now() - startMs) / (24 * 60 * 60 * 1000))
  const day = diffDays + 1
  return clamp(day, 1, Math.max(durationDays || 1, 1))
}

// Channel fit levels
const CHANNEL_FIT = {
  recommended: { label: 'Recommended', color: 'green' },
  risky: { label: 'Risky', color: 'amber' },
  notfit: { label: "Don't waste time", color: 'red' }
}

// Generate unique IDs
const generateId = () => `${Date.now()}_${Math.random().toString(36).substring(2, 9)}`

const emitNotification = (notification, options) => {
  try {
    useNotificationsStore.getState().addNotification(notification, options)
  } catch {
  }
}

const DEFAULT_CAMPAIGN_PHASES = ['Awareness', 'Engagement', 'Conversion', 'Retention']

const toMoveTasksFromChecklist = (checklistItems = []) => {
  return checklistItems.map(item => ({
    id: item.id,
    text: item.text,
    day: item.day || 1,
    status: item.done ? 'done' : 'todo',
    proof: item.proof || null,
    createdAt: item.createdAt || null,
  }))
}

const toChecklistFromMoveTasks = (tasks = []) => {
  return tasks.map(task => ({
    id: task.id,
    text: task.text,
    done: task.status === 'done',
    day: task.day,
    proof: task.proof || null,
    createdAt: task.createdAt || null,
  }))
}

const normalizeCampaign = (campaign) => {
  const safeKpis = campaign?.kpis || {
    primary: { name: '', baseline: 0, target: 0, current: 0 },
    reach: { name: 'Reach', baseline: 0, target: 0, current: 0 },
    click: { name: 'Clicks', baseline: 0, target: 0, current: 0 },
    convert: { name: 'Conversions', baseline: 0, target: 0, current: 0 }
  }

  const buildDefaultPhase = (phase) => ({
    phase,
    phaseObjective: phase === 'Conversion' ? safeKpis.primary?.name || 'Primary KPI' : phase,
    messageFocus: '',
    targetCohorts: Array.isArray(campaign?.cohorts) ? campaign.cohorts : [],
    channelMix: Array.isArray(campaign?.channels) ? campaign.channels : [],
  })

  const timeline = campaign?.timeline || (
    Array.isArray(campaign?.sequencing)
      ? {
          weeks: campaign.sequencing.map(w => ({
            week: w.week,
            phase: w.phase,
            moveIds: w.moves || []
          }))
        }
      : { weeks: [] }
  )

  const defaultBlueprint = {
    objective: {
      text: campaign?.objective || '',
      primaryKpi: safeKpis.primary,
    },
    phases: DEFAULT_CAMPAIGN_PHASES.map(buildDefaultPhase),
    kpiTree: {
      primary: safeKpis.primary,
      stages: {
        reach: safeKpis.reach,
        click: safeKpis.click,
        convert: safeKpis.convert,
      },
      leadingIndicators: [],
      healthRules: [],
    },
  }

  const rawBlueprint = campaign?.blueprint || {}
  const rawObjective = rawBlueprint?.objective || {}
  const rawKpiTree = rawBlueprint?.kpiTree || {}
  const rawStages = rawKpiTree?.stages || {}

  const phases = Array.isArray(rawBlueprint?.phases) && rawBlueprint.phases.length
    ? rawBlueprint.phases.map(p => ({
        ...buildDefaultPhase(p?.phase || 'Awareness'),
        ...p,
      }))
    : defaultBlueprint.phases

  const blueprint = {
    ...defaultBlueprint,
    ...rawBlueprint,
    objective: {
      ...defaultBlueprint.objective,
      ...rawObjective,
      text: rawObjective?.text ?? campaign?.objective ?? '',
      primaryKpi: rawObjective?.primaryKpi || safeKpis.primary,
    },
    phases,
    kpiTree: {
      ...defaultBlueprint.kpiTree,
      ...rawKpiTree,
      primary: rawKpiTree?.primary || safeKpis.primary,
      stages: {
        ...defaultBlueprint.kpiTree.stages,
        ...rawStages,
        reach: rawStages?.reach || safeKpis.reach,
        click: rawStages?.click || safeKpis.click,
        convert: rawStages?.convert || safeKpis.convert,
      },
      leadingIndicators: Array.isArray(rawKpiTree?.leadingIndicators) ? rawKpiTree.leadingIndicators : [],
      healthRules: Array.isArray(rawKpiTree?.healthRules) ? rawKpiTree.healthRules : [],
    },
  }

  const strategyVersionId = campaign?.strategyVersionId || 1

  return {
    ...campaign,
    kpis: safeKpis,
    timeline,
    blueprint,
    strategyVersionId,
  }
}

const normalizeMove = (move) => {
  const tasks = Array.isArray(move?.tasks)
    ? move.tasks
    : toMoveTasksFromChecklist(move?.checklistItems || [])

  const checklistItems = Array.isArray(move?.checklistItems)
    ? move.checklistItems
    : toChecklistFromMoveTasks(tasks)

  return {
    ...move,
    status: move?.status || 'pending',
    checklistItems,
    tasks,
    plan: move?.plan || {
      durationDays: move?.durationDays || 7,
      startDate: move?.startDate || null,
      endDate: move?.endDate || null,
      dayPlan: [],
    },
    generation: move?.generation || null,
    tracking: move?.tracking || {
      metric: move?.metric || '',
      updates: [],
    },
    result: move?.result || {
      outcome: null,
      learning: '',
      completedAt: null,
    },
  }
}

// Mock data generators
const generateMockStrategy = () => ({
  id: generateId(),
  versionNumber: 1,
  status: 'locked',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  payload: {
    brandRules: {
      tone: 'professional',
      voice: 'confident',
      tabooWords: ['cheap', 'basic', 'simple'],
      examples: ['We help ambitious founders...', 'Transform your marketing...']
    },
    offer: {
      pricing: '₹5,000 - ₹25,000/month',
      guarantee: '14-day results guarantee',
      constraints: ['B2B only', 'Tech-enabled businesses'],
      bonuses: ['Strategy session', 'Competitor analysis'],
      eligibility: 'Companies with ₹50L+ annual revenue'
    },
    proofInventory: [
      { id: '1', type: 'case-study', title: 'TechStartup 3x Pipeline', url: '#' },
      { id: '2', type: 'testimonial', title: 'CEO Quote - Acme Inc', content: 'RaptorFlow transformed our outbound...' },
      { id: '3', type: 'metric', title: '87% increase in qualified leads', value: 87 }
    ],
    claimLedger: [
      { id: '1', claim: '3x pipeline in 90 days', proofId: '1', status: 'proven' },
      { id: '2', claim: 'AI-powered campaign optimization', proofId: null, status: 'assumption' }
    ]
  }
})

const generateMockCohorts = () => [
  {
    id: 'cohort_1',
    name: 'Tech Founders',
    description: '25-40 year old tech startup founders in metros',
    tags: {
      common: ['startup', 'technology', 'growth', 'funding', 'saas'],
      special: ['series-a', 'product-market-fit', 'scaling', 'hiring']
    },
    channels: {
      'linkedin': 'recommended',
      'twitter': 'recommended',
      'instagram': 'risky',
      'whatsapp': 'recommended',
      'email': 'recommended',
      'youtube': 'risky'
    }
  },
  {
    id: 'cohort_2',
    name: 'Marketing Leaders',
    description: 'CMOs and Marketing Directors at mid-sized companies',
    tags: {
      common: ['marketing', 'branding', 'campaigns', 'roi', 'analytics'],
      special: ['demand-gen', 'abm', 'content-marketing', 'performance']
    },
    channels: {
      'linkedin': 'recommended',
      'twitter': 'risky',
      'instagram': 'notfit',
      'whatsapp': 'risky',
      'email': 'recommended',
      'youtube': 'recommended'
    }
  },
  {
    id: 'cohort_3',
    name: 'D2C Brand Owners',
    description: 'Founders of direct-to-consumer brands',
    tags: {
      common: ['ecommerce', 'd2c', 'brand', 'retail', 'consumer'],
      special: ['instagram-native', 'influencer', 'performance-marketing']
    },
    channels: {
      'linkedin': 'risky',
      'twitter': 'risky',
      'instagram': 'recommended',
      'whatsapp': 'recommended',
      'email': 'recommended',
      'youtube': 'recommended'
    }
  }
]

 const normalizePipelineItem = (item) => {
   const now = new Date().toISOString()
   const base = item || {}

   return {
     pipeline_item_id: base.pipeline_item_id || base.id || generateId(),
     title: base.title || 'Untitled work item',
     description: base.description || null,
     work_type: base.work_type || 'other',
     channel_id: base.channel_id || null,
     linked: {
       move_id: base?.linked?.move_id || null,
       campaign_id: base?.linked?.campaign_id || null,
       signal_id: base?.linked?.signal_id || null,
       duel_id: base?.linked?.duel_id || null,
     },
     inputs: {
       asset_refs: Array.isArray(base?.inputs?.asset_refs) ? base.inputs.asset_refs : [],
       proof_claim_ids: Array.isArray(base?.inputs?.proof_claim_ids) ? base.inputs.proof_claim_ids : [],
     },
     execution: {
       status: base?.execution?.status || 'backlog',
       owner_user_id: base?.execution?.owner_user_id || null,
       reviewer_user_id: base?.execution?.reviewer_user_id || null,
       approver_user_id: base?.execution?.approver_user_id || null,
       due_at: base?.execution?.due_at || null,
       scheduled_for: base?.execution?.scheduled_for || null,
       shipped_at: base?.execution?.shipped_at || null,
     },
     approvals: {
       required: Boolean(base?.approvals?.required),
       state: base?.approvals?.state || 'not_requested',
       requested_at: base?.approvals?.requested_at || null,
       approved_at: base?.approvals?.approved_at || null,
       approved_by_user_id: base?.approvals?.approved_by_user_id || null,
     },
     receipt: base.receipt
       ? {
         type: base.receipt.type || 'other',
         value: base.receipt.value || '',
         submitted_at: base.receipt.submitted_at || now,
       }
       : null,
     metrics_hook: {
       primary_metric: base?.metrics_hook?.primary_metric || null,
       events: Array.isArray(base?.metrics_hook?.events) ? base.metrics_hook.events : [],
     },
     created_at: base.created_at || now,
     updated_at: base.updated_at || now,
   }
 }

 const generateMockPipelineItems = () => {
   const now = Date.now()
   return [
     normalizePipelineItem({
       pipeline_item_id: 'pipe_1',
       title: 'LinkedIn post: proof-led angle (Time-to-value)',
       description: 'Turn the TTV insight into a single proof-led post. Include a clear CTA.',
       work_type: 'post',
       channel_id: 'linkedin',
       execution: {
         status: 'review',
         owner_user_id: 'me',
         reviewer_user_id: 'reviewer',
         due_at: new Date(now + 2 * 24 * 60 * 60 * 1000).toISOString(),
       },
       approvals: {
         required: false,
         state: 'not_requested',
       },
     }),
     normalizePipelineItem({
       pipeline_item_id: 'pipe_2',
       title: 'Landing page: demo request variant B',
       description: 'Swap hero headline to cost-of-inaction and add proof bar. Needs approval.',
       work_type: 'landing_page',
       channel_id: 'web',
       execution: {
         status: 'approval',
         owner_user_id: 'me',
         approver_user_id: 'approver',
         due_at: new Date(now + 3 * 24 * 60 * 60 * 1000).toISOString(),
       },
       approvals: {
         required: true,
         state: 'pending',
         requested_at: new Date(now - 6 * 60 * 60 * 1000).toISOString(),
       },
     }),
     normalizePipelineItem({
       pipeline_item_id: 'pipe_3',
       title: 'Ad creative set: 3 hooks + 2 visuals',
       work_type: 'ad',
       channel_id: 'meta',
       execution: {
         status: 'scheduled',
         owner_user_id: 'me',
         scheduled_for: new Date(now + 24 * 60 * 60 * 1000).toISOString(),
       },
     }),
     normalizePipelineItem({
       pipeline_item_id: 'pipe_4',
       title: 'Email: reactivation sequence (3-step)',
       work_type: 'email',
       channel_id: 'email',
       execution: {
         status: 'backlog',
       },
     }),
     normalizePipelineItem({
       pipeline_item_id: 'pipe_5',
       title: 'Ship: LinkedIn post (receipt required)',
       work_type: 'post',
       channel_id: 'linkedin',
       execution: {
         status: 'in_production',
         owner_user_id: 'me',
         due_at: new Date(now + 1 * 24 * 60 * 60 * 1000).toISOString(),
       },
     }),
   ]
 }

const generateMockCampaigns = () => [
  {
    id: 'camp_1',
    name: 'Q1 Pipeline Blitz',
    objective: 'Generate 50 qualified leads in 30 days',
    status: 'active',
    strategyVersionId: 1,
    cohorts: ['cohort_1', 'cohort_2'],
    channels: ['linkedin', 'email'],
    kpis: {
      primary: { name: 'Qualified Leads', baseline: 10, target: 50, current: 28 },
      reach: { name: 'Impressions', baseline: 5000, target: 50000, current: 32000 },
      click: { name: 'Clicks', baseline: 100, target: 1000, current: 620 },
      convert: { name: 'Conversions', baseline: 5, target: 50, current: 28 }
    },
    sequencing: [
      { week: 1, phase: 'Awareness', moves: ['move_1', 'move_2'] },
      { week: 2, phase: 'Engagement', moves: ['move_3'] },
      { week: 3, phase: 'Conversion', moves: ['move_4'] },
      { week: 4, phase: 'Close', moves: [] }
    ],
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: 'camp_2',
    name: 'Brand Authority Build',
    objective: 'Establish thought leadership with 100k reach',
    status: 'draft',
    strategyVersionId: 1,
    cohorts: ['cohort_1'],
    channels: ['linkedin', 'youtube'],
    kpis: {
      primary: { name: 'Total Reach', baseline: 20000, target: 100000, current: 0 },
      reach: { name: 'Followers', baseline: 500, target: 2000, current: 500 },
      click: { name: 'Profile Visits', baseline: 50, target: 500, current: 0 },
      convert: { name: 'Engagement Rate', baseline: 2, target: 5, current: 0 }
    },
    sequencing: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
]

const generateMockMoves = () => [
  {
    id: 'move_1',
    campaignId: 'camp_1',
    name: 'LinkedIn Thought Leadership Post',
    cohort: 'cohort_1',
    channel: 'linkedin',
    cta: 'Comment your biggest marketing challenge',
    metric: 'engagement',
    durationDays: 3,
    status: 'active',
    checklistItems: [
      { id: 'task_1', text: 'Write post copy', done: true },
      { id: 'task_2', text: 'Create carousel visual', done: true },
      { id: 'task_3', text: 'Schedule for 9 AM Tuesday', done: false },
      { id: 'task_4', text: 'Engage with comments for 2 hours', done: false }
    ],
    assets: ['asset_1', 'asset_2'],
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 'move_2',
    campaignId: 'camp_1',
    name: 'Email Outreach Sequence',
    cohort: 'cohort_2',
    channel: 'email',
    cta: 'Book a 15-min call',
    metric: 'replies',
    durationDays: 7,
    status: 'active',
    checklistItems: [
      { id: 'task_5', text: 'Finalize email copy', done: true },
      { id: 'task_6', text: 'Import target list', done: true },
      { id: 'task_7', text: 'Set up tracking', done: true },
      { id: 'task_8', text: 'Launch sequence', done: false }
    ],
    assets: ['asset_3'],
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 'move_3',
    campaignId: 'camp_1',
    name: 'Case Study Distribution',
    cohort: 'cohort_1',
    channel: 'linkedin',
    cta: 'Download full case study',
    metric: 'downloads',
    durationDays: 5,
    status: 'pending',
    checklistItems: [
      { id: 'task_9', text: 'Create case study PDF', done: false },
      { id: 'task_10', text: 'Write teaser post', done: false },
      { id: 'task_11', text: 'Set up landing page', done: false }
    ],
    assets: [],
    createdAt: new Date().toISOString()
  },
  {
    id: 'move_4',
    campaignId: 'camp_1',
    name: 'Webinar Invitation',
    cohort: 'cohort_1',
    channel: 'email',
    cta: 'Register for the webinar',
    metric: 'registrations',
    durationDays: 7,
    status: 'pending',
    checklistItems: [
      { id: 'task_12', text: 'Create webinar slides', done: false },
      { id: 'task_13', text: 'Write invitation email', done: false },
      { id: 'task_14', text: 'Set up registration page', done: false },
      { id: 'task_15', text: 'Send invitation', done: false }
    ],
    assets: [],
    createdAt: new Date().toISOString()
  }
]

const generateMockAssets = () => [
  {
    id: 'asset_1',
    moveId: 'move_1',
    type: 'post',
    channel: 'linkedin',
    content: `🎯 The #1 mistake I see founders make with their marketing...

They try to be everywhere at once.

Here's the truth: You don't need to be on 10 channels.
You need to DOMINATE 2.

After helping 50+ startups scale their pipeline, here's what works:

1️⃣ Pick channels where your ICP actually lives
2️⃣ Create content that solves ONE specific problem
3️⃣ Be consistent for 90 days minimum

The results? 3x pipeline. Every. Single. Time.

What's your biggest marketing challenge right now? 👇`,
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 'asset_2',
    moveId: 'move_1',
    type: 'carousel',
    channel: 'linkedin',
    content: 'Carousel: 5 Steps to 3x Your Pipeline',
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 'asset_3',
    moveId: 'move_2',
    type: 'email',
    channel: 'email',
    content: `Subject: Quick question about {{company}}'s growth

Hi {{firstName}},

I noticed {{company}} is hiring for marketing roles - congrats on the growth!

Quick question: Are you happy with your current pipeline?

Most marketing leaders I talk to are hitting a ceiling around the ₹50L-₹1Cr pipeline mark.

We've helped companies like [Similar Company] break through to ₹3Cr+ pipeline in 90 days.

Worth a 15-min chat to see if we can do the same for you?

Best,
[Name]`,
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
  }
]

const generateMockDuels = () => [
  {
    id: 'duel_1',
    name: 'Hook Duel — LinkedIn (Cohort 1)',
    goal: 'clicks',
    variable: 'hook',
    cohort: 'cohort_1',
    channel: 'linkedin',
    status: 'running',
    variants: [
      { id: 'var_1', label: 'A', content: 'The #1 mistake founders make...', smartLink: 'rf.to/a1x2', clicks: 45, leads: 3 },
      { id: 'var_2', label: 'B', content: "Why 90% of marketing fails...", smartLink: 'rf.to/b3y4', clicks: 67, leads: 5 },
      { id: 'var_3', label: 'C', content: 'I scaled 50 startups. Here\'s what works...', smartLink: 'rf.to/c5z6', clicks: 52, leads: 4 }
    ],
    winner: null,
    createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 'duel_2',
    name: 'CTA Duel — Email (Cohort 2)',
    goal: 'leads',
    variable: 'cta',
    cohort: 'cohort_2',
    channel: 'email',
    status: 'winner',
    variants: [
      { id: 'var_4', label: 'A', content: 'Book a 15-min call', smartLink: 'rf.to/d7w8', clicks: 120, leads: 12 },
      { id: 'var_5', label: 'B', content: 'Get your audit', smartLink: 'rf.to/e9v0', clicks: 95, leads: 18 }
    ],
    winner: 'var_5',
    promotedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
  }
]

const generateMockRadarScans = () => [
  {
    id: 'scan_1',
    type: 'small',
    cohort: 'cohort_1',
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    outputs: [
      { type: 'post', content: 'IPL finals coming up - perfect time to post about "winning strategies"', channel: 'linkedin' },
      { type: 'post', content: 'Budget season trends - CFOs looking for ROI proof', channel: 'linkedin' }
    ]
  },
  {
    id: 'scan_2',
    type: 'big',
    cohort: 'cohort_1',
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    outputs: [
      {
        type: 'move',
        suggestedMove: {
          name: 'Budget Season Outreach',
          cohort: 'cohort_1',
          channel: 'email',
          cta: 'Get your Q2 marketing plan',
          metric: 'replies',
          durationDays: 5,
          reason: 'Q2 budget planning season - CFOs are finalizing marketing budgets'
        }
      }
    ]
  }
]

const generateMockTrailTargets = () => [
  { id: 'target_1', name: 'Rahul Sharma', company: 'TechCorp', channel: 'linkedin', handle: 'rahulsharma', status: 'new' },
  { id: 'target_2', name: 'Priya Patel', company: 'GrowthCo', channel: 'linkedin', handle: 'priyapatel', status: 'contacted' },
  { id: 'target_3', name: 'Amit Kumar', company: 'ScaleUp', channel: 'email', handle: 'amit@scaleup.io', status: 'replied' },
  { id: 'target_4', name: 'Sneha Gupta', company: 'MarketEdge', channel: 'linkedin', handle: 'snehagupta', status: 'booked' },
  { id: 'target_5', name: 'Vikram Singh', company: 'DataDriven', channel: 'email', handle: 'vikram@datadriven.in', status: 'contacted' }
]

const generateMockSignals = () => []

// Initial state
const initialState = {
  // Current plan
  currentPlan: 'glide',
  
  // Usage tracking
  usage: {
    // ...
    radarScansToday: 2,
    blackBoxDuelsThisMonth: 5,
    museGenerationsThisMonth: 45,
    lastReset: new Date().toISOString()
  },
  
  // Strategy versions
  strategyVersions: [generateMockStrategy()],
  currentStrategyVersion: 1,
  
  // Cohorts/ICPs
  cohorts: generateMockCohorts(),
  
  // Campaigns
  campaigns: generateMockCampaigns(),

  primaryCampaignId: null,
  
  // Moves
  moves: generateMockMoves(),
  
  // Assets
  assets: generateMockAssets(),
  
  // Radar scans
  radarScans: generateMockRadarScans(),
  
  // Black Box duels
  duels: generateMockDuels(),

  // Signals
  signals: generateMockSignals(),

  // Execution (Pipeline)
  pipelineItems: generateMockPipelineItems(),
  
  // Trail targets
  trailTargets: generateMockTrailTargets(),
  
  // UI state
  museDrawerOpen: false,
  museContext: null, // { moveId, campaignId, assetType }
  selectedCampaignId: null,
  selectedMoveId: null,
  selectedDuelId: null,
  selectedSignalId: null
}

const useRaptorflowStore = create(
  persist(
    (set, get) => ({
      ...initialState,

      // ============================================
      // PLAN & LIMITS
      // ============================================
      getPlanLimits: () => PLAN_LIMITS[get().currentPlan] || PLAN_LIMITS.glide,
      
      canUseRadar: () => {
        const { usage, currentPlan } = get()
        const limits = PLAN_LIMITS[currentPlan]
        return usage.radarScansToday < limits.radarScansPerDay
      },
      
      canUseBlackBox: () => {
        const { usage, currentPlan } = get()
        const limits = PLAN_LIMITS[currentPlan]
        return usage.blackBoxDuelsThisMonth < limits.blackBoxDuelsPerMonth
      },
      
      canUseMuse: () => {
        const { usage, currentPlan } = get()
        const limits = PLAN_LIMITS[currentPlan]
        return usage.museGenerationsThisMonth < limits.museGenerationsPerMonth
      },

      // ============================================
      // STRATEGY
      // ============================================
      getCurrentStrategy: () => {
        const { strategyVersions, currentStrategyVersion } = get()
        return strategyVersions.find(s => s.versionNumber === currentStrategyVersion)
      },
      
      createStrategyDraft: () => {
        const { strategyVersions } = get()
        const currentVersion = get().getCurrentStrategy()
        const newVersion = {
          ...currentVersion,
          id: generateId(),
          versionNumber: strategyVersions.length + 1,
          status: 'draft',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        set({ strategyVersions: [...strategyVersions, newVersion] })
        return newVersion
      },
      
      updateStrategyDraft: (versionNumber, payload) => {
        set(state => ({
          strategyVersions: state.strategyVersions.map(s =>
            s.versionNumber === versionNumber && s.status === 'draft'
              ? { ...s, payload: { ...s.payload, ...payload }, updatedAt: new Date().toISOString() }
              : s
          )
        }))
      },
      
      lockStrategy: (versionNumber) => {
        set(state => ({
          strategyVersions: state.strategyVersions.map(s =>
            s.versionNumber === versionNumber
              ? { ...s, status: 'locked', updatedAt: new Date().toISOString() }
              : s
          ),
          currentStrategyVersion: versionNumber
        }))
      },

      addProofToCurrentStrategy: (proof) => {
        const { strategyVersions, currentStrategyVersion } = get()
        const current = strategyVersions.find(s => s.versionNumber === currentStrategyVersion)
        if (!current) return null

        const newProof = { id: generateId(), ...proof }
        const next = {
          ...current,
          payload: {
            ...current.payload,
            proofInventory: [...(current.payload?.proofInventory || []), newProof]
          },
          updatedAt: new Date().toISOString()
        }

        set({
          strategyVersions: strategyVersions.map(s =>
            s.versionNumber === currentStrategyVersion ? next : s
          )
        })

        emitNotification(
          {
            level: 'success',
            title: 'Proof added',
            detail: newProof.title || 'New proof added to Strategy.',
            href: '/app/settings?tab=strategy',
          },
          { toast: true }
        )

        return newProof
      },

      // ============================================
      // CAMPAIGNS
      // ============================================
      getCampaign: (id) => {
        const found = get().campaigns.find(c => c.id === id)
        return found ? normalizeCampaign(found) : undefined
      },
      
      getActiveCampaigns: () => get().campaigns.filter(c => c.status === 'active').map(normalizeCampaign),

      setPrimaryCampaignId: (id) => set({ primaryCampaignId: id || null }),

      getPrimaryCampaign: () => {
        const { primaryCampaignId, campaigns } = get()
        const byId = primaryCampaignId ? campaigns.find(c => c.id === primaryCampaignId) : null
        if (byId) return normalizeCampaign(byId)
        const firstActive = campaigns.find(c => c.status === 'active')
        if (firstActive) return normalizeCampaign(firstActive)
        const firstAny = campaigns[0]
        return firstAny ? normalizeCampaign(firstAny) : null
      },

      getCampaignPhase: (campaignId) => {
        const campaign = get().getCampaign(campaignId)
        if (!campaign) return 'Awareness'
        const first = campaign?.timeline?.weeks?.[0]?.phase || campaign?.sequencing?.[0]?.phase
        return first || 'Awareness'
      },

      getCampaignHealth: (campaignId) => {
        const campaign = get().getCampaign(campaignId)
        if (!campaign) return null

        const moves = get().getMovesByCampaign(campaignId)
        const taskTotals = moves.reduce(
          (acc, m) => {
            const total = (m.checklistItems || []).length
            const done = (m.checklistItems || []).filter(t => t.done).length
            return { total: acc.total + total, done: acc.done + done }
          },
          { total: 0, done: 0 }
        )

        const execution = taskTotals.total > 0 ? Math.round((taskTotals.done / taskTotals.total) * 100) : 0

        const tree = campaign?.blueprint?.kpiTree || {}
        const getPercent = (kpi) => {
          const current = Number(kpi?.current || 0)
          const target = Number(kpi?.target || 0)
          if (!Number.isFinite(target) || target <= 0) return 0
          return Math.round((current / target) * 100)
        }

        const primaryKpi = tree?.primary || campaign.kpis?.primary
        const stages = tree?.stages || {}
        const performance = getPercent(primaryKpi)

        const metrics = {
          primary: getPercent(primaryKpi),
          reach: getPercent(stages?.reach || campaign.kpis?.reach),
          click: getPercent(stages?.click || campaign.kpis?.click),
          convert: getPercent(stages?.convert || campaign.kpis?.convert),
        }

        const rules = Array.isArray(tree?.healthRules) ? tree.healthRules : []
        if (rules.length === 0) {
          return {
            execution,
            performance,
            phase: get().getCampaignPhase(campaignId),
            rag: null,
            issues: [],
          }
        }
        const issues = rules
          .map(r => {
            const metric = r?.metric || 'primary'
            const operator = r?.operator || '>='
            const threshold = Number(r?.threshold || 0)
            const severity = r?.severity || 'warn'
            const value = Number(metrics?.[metric] || 0)

            const ok = operator === '<=' ? value <= threshold : value >= threshold
            if (ok) return null
            return {
              id: r?.id || `${metric}_${operator}_${threshold}_${severity}`,
              metric,
              operator,
              threshold,
              value,
              severity,
            }
          })
          .filter(Boolean)

        const rag = issues.some(i => i.severity === 'fail')
          ? 'red'
          : issues.length
            ? 'amber'
            : 'green'

        return {
          execution,
          performance,
          phase: get().getCampaignPhase(campaignId),
          rag,
          issues,
        }
      },

      getCampaignKpiRollup: (campaignId) => {
        const campaign = get().getCampaign(campaignId)
        if (!campaign) return null

        const moves = get().getMovesByCampaign(campaignId)
        const totals = { primary: 0, reach: 0, click: 0, convert: 0 }
        const sources = { primary: [], reach: [], click: [], convert: [] }

        moves.forEach(m => {
          const metric = (m?.tracking?.metric || m?.metric || '').toString().toLowerCase()
          if (!['primary', 'reach', 'click', 'convert'].includes(metric)) return
          const updates = Array.isArray(m?.tracking?.updates) ? m.tracking.updates : []
          const sum = updates.reduce((acc, u) => acc + Number(u?.value || 0), 0)
          totals[metric] += sum
          if (sum > 0) sources[metric].push({ moveId: m.id, name: m.name, sum })
        })

        return { totals, sources }
      },

      applyCampaignKpiRollup: (campaignId) => {
        const campaign = get().getCampaign(campaignId)
        const rollup = get().getCampaignKpiRollup(campaignId)
        if (!campaign || !rollup) return

        const nextKpis = {
          ...(campaign.kpis || {}),
          primary: { ...(campaign.kpis?.primary || {}), current: Number(rollup.totals.primary || 0) },
          reach: { ...(campaign.kpis?.reach || {}), current: Number(rollup.totals.reach || 0) },
          click: { ...(campaign.kpis?.click || {}), current: Number(rollup.totals.click || 0) },
          convert: { ...(campaign.kpis?.convert || {}), current: Number(rollup.totals.convert || 0) },
        }

        const tree = campaign?.blueprint?.kpiTree || {}
        const nextTree = {
          ...tree,
          primary: { ...(tree.primary || {}), current: Number(rollup.totals.primary || 0) },
          stages: {
            ...(tree.stages || {}),
            reach: { ...(tree.stages?.reach || {}), current: Number(rollup.totals.reach || 0) },
            click: { ...(tree.stages?.click || {}), current: Number(rollup.totals.click || 0) },
            convert: { ...(tree.stages?.convert || {}), current: Number(rollup.totals.convert || 0) },
          }
        }

        get().updateCampaign(campaignId, {
          kpis: nextKpis,
          blueprint: {
            ...(campaign.blueprint || {}),
            kpiTree: nextTree,
            objective: {
              ...(campaign.blueprint?.objective || {}),
              primaryKpi: nextTree.primary,
            }
          }
        })
      },
      
      createCampaign: (campaign) => {
        const newCampaign = normalizeCampaign({
          id: generateId(),
          ...campaign,
          strategyVersionId: get().currentStrategyVersion,
          status: 'draft',
          kpis: campaign.kpis || {
            primary: { name: '', baseline: 0, target: 0, current: 0 },
            reach: { name: 'Reach', baseline: 0, target: 0, current: 0 },
            click: { name: 'Clicks', baseline: 0, target: 0, current: 0 },
            convert: { name: 'Conversions', baseline: 0, target: 0, current: 0 }
          },
          sequencing: campaign.sequencing || [],
          timeline: campaign.timeline,
          blueprint: campaign.blueprint,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
        set(state => ({ campaigns: [...state.campaigns, newCampaign] }))

        emitNotification(
          {
            level: 'success',
            title: 'Campaign created',
            detail: newCampaign.name || 'Draft campaign created.',
            href: `/app/campaigns/${newCampaign.id}`,
          },
          { toast: true }
        )

        return newCampaign
      },
      
      updateCampaign: (id, updates) => {
        const prev = get().campaigns.find(c => c.id === id)
        set(state => ({
          campaigns: state.campaigns.map(c =>
            c.id === id ? { ...c, ...updates, updatedAt: new Date().toISOString() } : c
          )
        }))

        const nextStatus = updates?.status
        if (prev && typeof nextStatus === 'string' && nextStatus !== prev.status) {
          const title = nextStatus === 'active' ? 'Campaign activated' : 'Campaign updated'
          emitNotification(
            {
              level: 'success',
              title,
              detail: prev.name || 'Campaign status changed.',
              href: `/app/campaigns/${id}`,
            },
            { toast: true }
          )
        }
      },
      
      deleteCampaign: (id) => {
        const prev = get().campaigns.find(c => c.id === id)
        set(state => ({
          campaigns: state.campaigns.filter(c => c.id !== id),
          moves: state.moves.map(m => (m.campaignId === id ? { ...m, campaignId: null } : m))
        }))

        emitNotification(
          {
            level: 'info',
            title: 'Campaign removed',
            detail: prev?.name || 'Campaign deleted.',
          },
          { toast: true }
        )
      },
      
      getChannelFit: (cohortId, channel) => {
        const cohort = get().cohorts.find(c => c.id === cohortId)
        if (!cohort) return 'risky'
        return cohort.channels[channel] || 'risky'
      },

      // ============================================
      // MOVES
      // ============================================
      getMove: (id) => {
        const found = get().moves.find(m => m.id === id)
        return found ? normalizeMove(found) : undefined
      },
      
      getMovesByCampaign: (campaignId) => get().moves.filter(m => m.campaignId === campaignId).map(normalizeMove),
      
      getActiveMoves: () => get().moves.filter(m => m.status === 'active').map(normalizeMove),

      getGeneratingMoves: () => get().moves.filter(m => m.status === 'generating').map(normalizeMove),

      getMoveDayNumber: (moveId) => {
        const move = get().getMove(moveId)
        if (!move) return 1
        const durationDays = move?.plan?.durationDays || move?.durationDays || 7
        return getDayNumberFromStart(move?.plan?.startDate || move?.startDate, durationDays)
      },

      getMoveTasksForDay: (moveId, dayNumber) => {
        const move = get().getMove(moveId)
        if (!move) return []
        const day = clamp(dayNumber || 1, 1, move?.plan?.durationDays || move?.durationDays || 7)
        return (move.tasks || []).filter(t => (t.day || 1) === day)
      },

      getMoveReadiness: (moveId) => {
        const move = get().getMove(moveId)
        if (!move) return { ready: false, gates: [] }

        const campaign = move?.campaignId ? get().getCampaign(move.campaignId) : null
        const strategy = get().getCurrentStrategy?.()

        const proofCount = (strategy?.payload?.proofInventory || []).length
        const gates = [
          {
            id: 'has_objective',
            label: 'Objective is defined',
            ok: Boolean(campaign?.objective || move?.plan?.objective),
            detail: campaign?.objective || move?.plan?.objective || 'Add a clear objective.',
          },
          {
            id: 'has_cohort',
            label: 'Cohort is selected',
            ok: Boolean(move?.cohort),
            detail: move?.cohort ? `Cohort: ${move.cohort}` : 'Select a cohort to target.',
          },
          {
            id: 'has_channel',
            label: 'Primary channel is set',
            ok: Boolean(move?.channel),
            detail: move?.channel ? `Channel: ${move.channel}` : 'Pick a channel to execute on.',
          },
          {
            id: 'has_metric',
            label: 'Success metric is set',
            ok: Boolean(move?.tracking?.metric || move?.metric),
            detail: move?.tracking?.metric || move?.metric || 'Set a measurable success metric.',
          },
          {
            id: 'strategy_locked',
            label: 'Strategy is pinned (locked)',
            ok: strategy?.status === 'locked',
            detail: strategy?.status === 'locked' ? `Pinned v${strategy?.versionNumber}` : 'Lock Strategy to pin assumptions.',
          },
          {
            id: 'has_proof',
            label: 'Proof inventory has at least 1 item',
            ok: proofCount > 0,
            detail: proofCount > 0 ? `${proofCount} proof items` : 'Add one proof item (case study, stat, quote).',
          },
        ]

        const ready = gates.every(g => g.ok)
        return { ready, gates }
      },

      fixMoveReadiness: (moveId, gateId) => {
        const move = get().getMove(moveId)
        if (!move) return

        if (gateId === 'has_objective') {
          const campaign = move?.campaignId ? get().getCampaign(move.campaignId) : null
          if (campaign?.id && !campaign?.objective) {
            get().updateCampaign(campaign.id, { objective: 'Define the objective for this campaign' })
            return
          }
          if (!campaign?.id) {
            const currentPlan = move?.plan || {}
            get().updateMove(moveId, {
              plan: {
                ...currentPlan,
                objective: currentPlan?.objective || 'Define the objective for this move',
              }
            })
          }
          return
        }

        if (gateId === 'has_cohort') {
          const first = get().cohorts?.[0]?.id
          if (first) get().updateMove(moveId, { cohort: first })
          return
        }

        if (gateId === 'has_channel') {
          get().updateMove(moveId, { channel: 'linkedin' })
          return
        }

        if (gateId === 'has_metric') {
          const metric = move?.tracking?.metric || move?.metric || 'engagement'
          get().updateMove(moveId, { metric, tracking: { ...(move.tracking || {}), metric } })
          return
        }

        if (gateId === 'strategy_locked') {
          const current = get().getCurrentStrategy?.()
          if (current?.versionNumber) get().lockStrategy(current.versionNumber)
          return
        }

        if (gateId === 'has_proof') {
          get().addProofToCurrentStrategy?.({
            title: 'Example proof',
            type: 'case_study',
            url: 'https://example.com',
            note: 'Replace with a real proof item.'
          })
        }
      },

      startMoveGeneration: (moveId) => {
        const readiness = get().getMoveReadiness(moveId)
        if (!readiness?.ready) return { ok: false, readiness }

        set(state => ({
          moves: state.moves.map(m =>
            m.id === moveId
              ? {
                  ...m,
                  status: 'generating',
                  generation: {
                    status: 'running',
                    startedAt: new Date().toISOString(),
                    step: 'planning',
                  },
                }
              : m
          )
        }))

        setTimeout(() => {
          const current = get().moves.find(m => m.id === moveId)
          if (!current || current.status !== 'generating') return
          get().updateMove(moveId, {
            status: 'active',
            generation: {
              ...(current.generation || {}),
              status: 'complete',
              completedAt: new Date().toISOString(),
              step: 'done',
            }
          })
        }, 1100)

        return { ok: true }
      },
      
      getTodayChecklist: () => {
        const activeMoves = get().getActiveMoves()
        const tasks = []
        activeMoves.forEach(move => {
          const durationDays = move?.plan?.durationDays || move?.durationDays || 7
          const today = getDayNumberFromStart(move?.plan?.startDate || move?.startDate, durationDays)
          ;(move.tasks || [])
            .filter(t => (t.day || 1) === today)
            .filter(t => t.status !== 'done')
            .forEach(t => {
              tasks.push({
                id: t.id,
                text: t.text,
                done: t.status === 'done',
                day: t.day || 1,
                moveId: move.id,
                moveName: move.name,
              })
            })
        })
        return tasks
      },
      
      createMove: (move) => {
        const newMove = normalizeMove({
          id: generateId(),
          ...move,
          status: 'pending',
          checklistItems: move.checklistItems || toChecklistFromMoveTasks(move.tasks || []),
          assets: [],
          createdAt: new Date().toISOString()
        })
        set(state => ({ moves: [...state.moves, newMove] }))

        emitNotification(
          {
            level: 'success',
            title: 'Move created',
            detail: newMove.name || 'New move created.',
            href: `/app/moves/${newMove.id}`,
          },
          { toast: true }
        )

        return newMove
      },

      attachMoveToCampaign: (moveId, campaignId) => {
        if (!moveId) return
        const campaign = campaignId ? get().getCampaign(campaignId) : null
        set(state => ({
          moves: state.moves.map(m => {
            if (m.id !== moveId) return m
            const next = { ...m, campaignId: campaignId || null }
            if (campaignId && campaign) {
              if (!next.cohort && Array.isArray(campaign.cohorts) && campaign.cohorts.length) {
                next.cohort = campaign.cohorts[0]
              }
              if (!next.channel && Array.isArray(campaign.channels) && campaign.channels.length) {
                next.channel = campaign.channels[0]
              }
            }
            return next
          })
        }))

        if (campaignId) {
          emitNotification(
            {
              level: 'success',
              title: 'Move attached',
              detail: campaign?.name || 'Move attached to campaign.',
              href: `/app/moves/${moveId}`,
            },
            { toast: true }
          )
        }
      },

      detachMoveFromCampaign: (moveId) => {
        if (!moveId) return
        set(state => ({
          moves: state.moves.map(m => (m.id === moveId ? { ...m, campaignId: null } : m))
        }))

        emitNotification(
          {
            level: 'info',
            title: 'Move detached',
            detail: 'Move is now standalone.',
            href: `/app/moves/${moveId}`,
          },
          { toast: true }
        )
      },
      
      updateMove: (id, updates) => {
        const prev = get().moves.find(m => m.id === id)
        set(state => ({
          moves: state.moves.map(m => {
            if (m.id !== id) return m

            const next = { ...m, ...updates }
            const nextStatus = updates?.status
            if (nextStatus === 'active') {
              const durationDays = next?.plan?.durationDays || next?.durationDays || 7
              const hasStart = Boolean(next?.plan?.startDate || next?.startDate)
              const startDate = hasStart ? (next?.plan?.startDate || next?.startDate) : new Date().toISOString()
              const endDate = next?.plan?.endDate || next?.endDate || new Date(Date.now() + durationDays * 24 * 60 * 60 * 1000).toISOString()

              next.plan = {
                ...(next.plan || {}),
                durationDays,
                startDate,
                endDate,
              }

              if (!next.startDate) next.startDate = startDate
              if (!next.endDate) next.endDate = endDate
              if (!next.durationDays) next.durationDays = durationDays
            }

            return next
          })
        }))

        const nextStatus = updates?.status
        if (prev && typeof nextStatus === 'string' && nextStatus !== prev.status) {
          const title = nextStatus === 'completed' ? 'Move completed' : 'Move updated'
          emitNotification(
            {
              level: nextStatus === 'completed' ? 'success' : 'info',
              title,
              detail: prev.name || 'Move status changed.',
              href: `/app/moves/${id}`,
            },
            { toast: nextStatus === 'completed' }
          )
        }
      },

      attachProofToTask: (moveId, taskId, proof) => {
        const payload = {
          url: proof?.url || '',
          note: proof?.note || '',
          createdAt: new Date().toISOString(),
        }

        set(state => ({
          moves: state.moves.map(m => {
            if (m.id !== moveId) return m

            const baseTasks = Array.isArray(m.tasks) ? m.tasks : toMoveTasksFromChecklist(m.checklistItems || [])
            const nextTasks = baseTasks.map(t => (t.id === taskId ? { ...t, proof: payload } : t))
            const nextChecklist = (m.checklistItems || toChecklistFromMoveTasks(baseTasks)).map(c =>
              c.id === taskId ? { ...c, proof: payload } : c
            )

            return { ...m, tasks: nextTasks, checklistItems: nextChecklist }
          })
        }))
      },

      // ============================================
      // EXECUTION (PIPELINE)
      // ============================================
      getPipelineItem: (id) => {
        const items = Array.isArray(get().pipelineItems) ? get().pipelineItems : []
        return items.find(i => i.pipeline_item_id === id)
      },

      addPipelineItem: (payload) => {
        const now = new Date().toISOString()
        const created = normalizePipelineItem({
          ...payload,
          created_at: now,
          updated_at: now,
          execution: {
            status: payload?.execution?.status || 'backlog',
            owner_user_id: payload?.execution?.owner_user_id || null,
            reviewer_user_id: payload?.execution?.reviewer_user_id || null,
            approver_user_id: payload?.execution?.approver_user_id || null,
            due_at: payload?.execution?.due_at || null,
            scheduled_for: payload?.execution?.scheduled_for || null,
            shipped_at: null,
          },
          approvals: {
            required: Boolean(payload?.approvals?.required),
            state: 'not_requested',
            requested_at: null,
            approved_at: null,
            approved_by_user_id: null,
          },
          receipt: null,
        })

        set(state => ({ pipelineItems: [created, ...(state.pipelineItems || [])] }))

        emitNotification(
          {
            level: 'success',
            title: 'Added to Execution',
            detail: created.title,
          },
          { toast: true }
        )

        return created
      },

      updatePipelineItem: (id, updates) => {
        if (!id) return
        const now = new Date().toISOString()
        set(state => ({
          pipelineItems: (state.pipelineItems || []).map(item =>
            item.pipeline_item_id === id
              ? normalizePipelineItem({
                ...item,
                ...updates,
                execution: { ...item.execution, ...(updates?.execution || {}) },
                approvals: { ...item.approvals, ...(updates?.approvals || {}) },
                inputs: { ...item.inputs, ...(updates?.inputs || {}) },
                linked: { ...item.linked, ...(updates?.linked || {}) },
                metrics_hook: { ...item.metrics_hook, ...(updates?.metrics_hook || {}) },
                updated_at: now,
              })
              : item
          )
        }))
      },

      deletePipelineItem: (id) => {
        if (!id) return
        set(state => ({
          pipelineItems: (state.pipelineItems || []).filter(i => i.pipeline_item_id !== id)
        }))
      },

      setPipelineItemStatus: (id, status) => {
        if (!id || !status) return
        const now = new Date().toISOString()
        set(state => ({
          pipelineItems: (state.pipelineItems || []).map(item =>
            item.pipeline_item_id === id
              ? { ...item, execution: { ...item.execution, status }, updated_at: now }
              : item
          )
        }))
      },

      assignPipelineItem: (id, assignment) => {
        if (!id) return
        const now = new Date().toISOString()
        set(state => ({
          pipelineItems: (state.pipelineItems || []).map(item => {
            if (item.pipeline_item_id !== id) return item
            const nextStatus = item.execution?.status === 'backlog' ? 'in_production' : item.execution?.status
            return {
              ...item,
              execution: {
                ...item.execution,
                status: nextStatus,
                owner_user_id: assignment?.owner_user_id ?? item.execution?.owner_user_id ?? null,
                reviewer_user_id: assignment?.reviewer_user_id ?? item.execution?.reviewer_user_id ?? null,
                approver_user_id: assignment?.approver_user_id ?? item.execution?.approver_user_id ?? null,
              },
              updated_at: now,
            }
          })
        }))

        emitNotification(
          {
            level: 'info',
            title: 'Assigned',
            detail: 'Execution item updated',
          },
          { toast: true }
        )
      },

      requestPipelineApproval: (id, config) => {
        if (!id) return
        const now = new Date().toISOString()
        const required = Boolean(config?.required)
        set(state => ({
          pipelineItems: (state.pipelineItems || []).map(item => {
            if (item.pipeline_item_id !== id) return item
            const nextApprovals = {
              ...item.approvals,
              required,
              state: required ? 'pending' : 'not_required',
              requested_at: required ? now : null,
            }
            const nextStatus = required ? 'approval' : item.execution?.status
            return {
              ...item,
              approvals: nextApprovals,
              execution: { ...item.execution, status: nextStatus },
              updated_at: now,
            }
          })
        }))

        emitNotification(
          {
            level: required ? 'info' : 'success',
            title: required ? 'Approval requested' : 'No approval required',
            detail: required ? 'Waiting for approval' : 'Ready to ship when scheduled',
          },
          { toast: true }
        )
      },

      schedulePipelineItem: (id, schedule) => {
        if (!id) return
        const now = new Date().toISOString()
        const scheduled_for = schedule?.scheduled_for || null
        set(state => ({
          pipelineItems: (state.pipelineItems || []).map(item => {
            if (item.pipeline_item_id !== id) return item
            const nextStatus = scheduled_for ? 'scheduled' : item.execution?.status
            return {
              ...item,
              execution: {
                ...item.execution,
                scheduled_for,
                status: nextStatus,
              },
              updated_at: now,
            }
          })
        }))

        emitNotification(
          {
            level: 'success',
            title: scheduled_for ? 'Scheduled' : 'Schedule cleared',
            detail: scheduled_for ? 'Item added to calendar' : 'No publish time set',
          },
          { toast: true }
        )
      },

      markPipelineItemShipped: (id, receipt) => {
        if (!id) return
        const now = new Date().toISOString()
        const type = receipt?.type
        const value = receipt?.value

        if (!type || !value) {
          set(state => ({
            pipelineItems: (state.pipelineItems || []).map(item =>
              item.pipeline_item_id === id
                ? { ...item, execution: { ...item.execution, status: 'blocked' }, updated_at: now }
                : item
            )
          }))

          emitNotification(
            {
              level: 'error',
              title: 'Receipt required',
              detail: 'Add a receipt (URL, ad id, screenshot, etc.) before marking shipped.',
            },
            { toast: true }
          )
          return
        }

        set(state => ({
          pipelineItems: (state.pipelineItems || []).map(item =>
            item.pipeline_item_id === id
              ? {
                ...item,
                receipt: { type, value, submitted_at: now },
                execution: { ...item.execution, status: 'shipped', shipped_at: now },
                updated_at: now,
              }
              : item
          )
        }))

        emitNotification(
          {
            level: 'success',
            title: 'Shipped',
            detail: 'Receipt captured',
          },
          { toast: true }
        )
      },

      logPipelineResult: (id, result) => {
        if (!id) return
        const now = new Date().toISOString()
        const event = {
          id: generateId(),
          primary_metric: result?.primary_metric || null,
          note: result?.note || null,
          created_at: now,
        }

        set(state => ({
          pipelineItems: (state.pipelineItems || []).map(item => {
            if (item.pipeline_item_id !== id) return item
            const prev = item.metrics_hook || { primary_metric: null, events: [] }
            const primary_metric = result?.primary_metric || prev.primary_metric
            const events = Array.isArray(prev.events) ? [...prev.events, event] : [event]
            return {
              ...item,
              metrics_hook: { primary_metric, events },
              updated_at: now,
            }
          })
        }))

        emitNotification(
          {
            level: 'info',
            title: 'Result logged',
            detail: 'Recorded outcome note',
          },
          { toast: true }
        )
      },

      addTrackingUpdate: (moveId, update) => {
        const payload = {
          value: typeof update?.value === 'number' ? update.value : Number(update?.value || 0),
          at: update?.at || new Date().toISOString(),
        }

        set(state => ({
          moves: state.moves.map(m => {
            if (m.id !== moveId) return m
            const current = normalizeMove(m)
            const nextTracking = {
              ...(current.tracking || {}),
              updates: [...(current.tracking?.updates || []), payload],
            }
            return { ...m, tracking: nextTracking }
          })
        }))

        const updated = get().moves.find(m => m.id === moveId)
        const normalized = updated ? normalizeMove(updated) : null
        const campaignId = normalized?.campaignId
        const metric = (normalized?.tracking?.metric || normalized?.metric || '').toString().toLowerCase()
        if (campaignId && ['primary', 'reach', 'click', 'convert'].includes(metric)) {
          get().applyCampaignKpiRollup?.(campaignId)
        }
      },

      completeMove: (moveId, result) => {
        set(state => ({
          moves: state.moves.map(m => {
            if (m.id !== moveId) return m
            const current = normalizeMove(m)
            const nextResult = {
              ...(current.result || {}),
              outcome: result?.outcome || current.result?.outcome || null,
              learning: typeof result?.learning === 'string' ? result.learning : (current.result?.learning || ''),
              completedAt: new Date().toISOString(),
            }
            return { ...m, status: 'completed', result: nextResult }
          })
        }))

        const prev = get().moves.find(m => m.id === moveId)
        emitNotification(
          {
            level: 'success',
            title: 'Move completed',
            detail: prev?.name || 'Move marked complete.',
            href: `/app/moves/${moveId}`,
          },
          { toast: true }
        )
      },
      
      toggleTaskDone: (moveId, taskId) => {
        const prevMove = get().moves.find(m => m.id === moveId)
        const prevTask = prevMove?.checklistItems?.find(t => t.id === taskId)
        set(state => ({
          moves: state.moves.map(m =>
            m.id === moveId
              ? {
                  ...m,
                  checklistItems: (m.checklistItems || []).map(t =>
                    t.id === taskId ? { ...t, done: !t.done } : t
                  ),
                  tasks: (Array.isArray(m.tasks) ? m.tasks : toMoveTasksFromChecklist(m.checklistItems || [])).map(t =>
                    t.id === taskId ? { ...t, status: t.status === 'done' ? 'todo' : 'done' } : t
                  )
                }
              : m
          )
        }))

        if (prevMove && prevTask && prevTask.done === false) {
          emitNotification(
            {
              level: 'success',
              title: 'Task completed',
              detail: prevTask.text || prevMove.name || 'Checklist item completed.',
              href: `/app/moves/${moveId}`,
            },
            { toast: false }
          )

          const nextMove = get().moves.find(m => m.id === moveId)
          const allDone = nextMove?.checklistItems?.length
            ? nextMove.checklistItems.every(t => t.done)
            : false
          if (allDone) {
            emitNotification(
              {
                level: 'success',
                title: 'Move checklist complete',
                detail: nextMove?.name || 'All tasks completed.',
                href: `/app/moves/${moveId}`,
              },
              { toast: true }
            )
          }
        }
      },
      
      addTaskToMove: (moveId, taskText) => {
        const id = generateId()
        const day = get().getMoveDayNumber?.(moveId) || 1
        const newChecklist = { id, text: taskText, done: false }
        const newTask = { id, text: taskText, day, status: 'todo', proof: null, createdAt: new Date().toISOString() }
        set(state => ({
          moves: state.moves.map(m =>
            m.id === moveId
              ? {
                  ...m,
                  checklistItems: [...(m.checklistItems || []), newChecklist],
                  tasks: [...(Array.isArray(m.tasks) ? m.tasks : toMoveTasksFromChecklist(m.checklistItems || [])), newTask]
                }
              : m
          )
        }))
      },

      setTaskDay: (moveId, taskId, dayNumber) => {
        set(state => ({
          moves: state.moves.map(m => {
            if (m.id !== moveId) return m

            const current = normalizeMove(m)
            const durationDays = current?.plan?.durationDays || current?.durationDays || 7
            const day = clamp(Number(dayNumber || 1), 1, Math.max(durationDays, 1))

            const nextTasks = (current.tasks || []).map(t => (t.id === taskId ? { ...t, day } : t))
            const nextChecklist = (current.checklistItems || []).map(c => (c.id === taskId ? { ...c, day } : c))

            return { ...m, tasks: nextTasks, checklistItems: nextChecklist }
          })
        }))
      },
      
      deleteMove: (id) => {
        set(state => ({
          moves: state.moves.filter(m => m.id !== id),
          assets: state.assets.filter(a => a.moveId !== id)
        }))
      },

      // ============================================
      // MUSE (Assets)
      // ============================================
      openMuseDrawer: (context) => {
        set({ museDrawerOpen: true, museContext: context })
      },
      
      closeMuseDrawer: () => {
        set({ museDrawerOpen: false, museContext: null })
      },
      
      generateAsset: (moveId, assetType, channel) => {
        // Increment usage
        set(state => ({
          usage: {
            ...state.usage,
            museGenerationsThisMonth: state.usage.museGenerationsThisMonth + 1
          }
        }))
        
        // Generate mock asset
        const templates = {
          post: `🎯 Here's a powerful insight for {{cohort}}...

[Hook that grabs attention]

The problem most people face:
• Point 1
• Point 2
• Point 3

Here's what works instead:

1️⃣ First do this
2️⃣ Then this
3️⃣ Finally this

The result? [Outcome they want]

What's your take? 👇`,
          email: `Subject: Quick question about {{company}}

Hi {{firstName}},

[Personalized opener based on trigger]

I noticed [observation about their company].

Most [role] I talk to are struggling with [pain point].

We've helped companies like [similar company] achieve [specific result].

Worth a quick chat?

Best,
[Name]`,
          dm: `Hey {{firstName}}!

Saw your post about [topic] - really resonated with me.

Quick question: [relevant question to their situation]?

We're helping [similar companies] with exactly this. Would love to share what's working.

No pitch, just insights. Interested?`,
          landing: `# [Headline: Outcome + Timeframe]

## [Subheadline: For who + main benefit]

[Hero section with key value prop]

### What You'll Get:
- Benefit 1
- Benefit 2
- Benefit 3

### How It Works:
1. Step 1
2. Step 2
3. Step 3

[CTA Button: Action + Benefit]`
        }
        
        const newAsset = {
          id: generateId(),
          moveId,
          type: assetType,
          channel,
          content: templates[assetType] || templates.post,
          createdAt: new Date().toISOString()
        }
        
        set(state => ({
          assets: [...state.assets, newAsset],
          moves: state.moves.map(m =>
            m.id === moveId
              ? { ...m, assets: [...m.assets, newAsset.id] }
              : m
          )
        }))
        
        return newAsset
      },
      
      getAssetsByMove: (moveId) => get().assets.filter(a => a.moveId === moveId),
      
      updateAsset: (id, content) => {
        set(state => ({
          assets: state.assets.map(a =>
            a.id === id ? { ...a, content } : a
          )
        }))
      },
      
      deleteAsset: (id) => {
        const asset = get().assets.find(a => a.id === id)
        if (!asset) return
        
        set(state => ({
          assets: state.assets.filter(a => a.id !== id),
          moves: state.moves.map(m =>
            m.id === asset.moveId
              ? { ...m, assets: m.assets.filter(aId => aId !== id) }
              : m
          )
        }))
      },

      // ============================================
      // RADAR
      // ============================================
      runRadarScan: (type, cohortId, focus) => {
        if (!get().canUseRadar()) return null
        
        // Increment usage
        set(state => ({
          usage: { ...state.usage, radarScansToday: state.usage.radarScansToday + 1 }
        }))
        
        const cohortIds = Array.isArray(cohortId) ? cohortId : [cohortId]
        const primaryCohortId = cohortIds[0]
        const cohort = get().cohorts.find(c => c.id === primaryCohortId)
        const cohortLabel = cohortIds.length > 1 ? `${cohortIds.length} cohorts` : (cohort?.name || 'your audience')
        const focusKey = focus || 'trends'

        const focusPhrases = {
          trends: {
            small: `Trending in ${cohortLabel}: budget season discussions - perfect time for ROI content`,
            reason: 'Fresh engagement signals detected for this cohort - strike while hot'
          },
          competitors: {
            small: `Competitor momentum spotted in ${cohortLabel}: new positioning claims - time to respond with a sharp comparison`,
            reason: 'Competitive narrative is shifting - own the frame before they do'
          },
          objections: {
            small: `Recurring objection in ${cohortLabel}: "this takes too long" - publish a proof-led breakdown`,
            reason: 'Objection clusters are rising - address friction with proof + clarity'
          },
          launch: {
            small: `Launch window signal in ${cohortLabel}: feature releases + event chatter - publish "what changed" content`,
            reason: 'Launch-adjacent attention is peaking - ride the wave with a focused move'
          },
          hiring: {
            small: `Hiring & headcount chatter in ${cohortLabel} - publish an operator's playbook and capture intent`,
            reason: 'Decision-makers are in hiring mode - align content with the moment'
          }
        }
        const focusPack = focusPhrases[focusKey] || focusPhrases.trends
        
        // Generate mock scan results
        const smallOutputs = [
          { type: 'post', content: focusPack.small, channel: 'linkedin' },
          { type: 'post', content: 'Industry event coming up - opportunity for a proof-led breakdown', channel: 'linkedin' },
          { type: 'post', content: 'Short contrarian take: what most teams get wrong this week (then your framework)', channel: 'twitter' }
        ]
        
        const bigOutputs = [
          {
            type: 'move',
            suggestedMove: {
              name: `${cohort?.name || 'Audience'} ${focusKey === 'competitors' ? 'Comparison' : focusKey === 'objections' ? 'Objection Proof' : focusKey === 'launch' ? 'Launch Moment' : focusKey === 'hiring' ? 'Hiring Signal' : 'Engagement'} Push`,
              cohort: primaryCohortId,
              channel: Object.entries(cohort?.channels || {}).find(([_, fit]) => fit === 'recommended')?.[0] || 'linkedin',
              cta: 'Download our guide',
              metric: 'downloads',
              durationDays: 5,
              reason: focusPack.reason
            }
          }
        ]
        
        const newScan = {
          id: generateId(),
          type,
          cohort: primaryCohortId,
          cohorts: cohortIds,
          focus: focusKey,
          createdAt: new Date().toISOString(),
          outputs: type === 'small' ? smallOutputs : bigOutputs
        }
        
        set(state => ({ radarScans: [newScan, ...state.radarScans] }))
        return newScan
      },
      
      convertRadarToMove: (scanId, campaignId) => {
        const scan = get().radarScans.find(s => s.id === scanId)
        if (!scan) return null
        
        const suggestedMove = scan.outputs.find(o => o.type === 'move')?.suggestedMove
        if (!suggestedMove) return null
        
        return get().createMove({
          ...suggestedMove,
          campaignId,
          checklistItems: [
            { id: generateId(), text: 'Review suggested approach', done: false },
            { id: generateId(), text: 'Generate assets', done: false },
            { id: generateId(), text: 'Execute move', done: false }
          ]
        })
      },

      // ============================================
      // BLACK BOX (Duels)
      // ============================================
      getDuel: (id) => get().duels.find(d => d.id === id),
      
      getActiveDuels: () => get().duels.filter(d => d.status === 'running'),

      toggleDuelPaused: (duelId) => {
        set(state => ({
          duels: state.duels.map(d => {
            if (d.id !== duelId) return d
            if (d.status === 'winner' || d.status === 'archived') return d
            if (d.status === 'paused') return { ...d, status: 'running' }
            if (d.status === 'running') return { ...d, status: 'paused' }
            return d
          })
        }))
      },

      duplicateDuel: (duelId) => {
        const duel = get().getDuel(duelId)
        if (!duel) return null

        const duplicated = {
          ...duel,
          id: generateId(),
          name: duel.name ? `${duel.name} (Copy)` : `${duel.variable} Duel (Copy)`,
          status: 'running',
          winner: null,
          promotedAt: null,
          createdAt: new Date().toISOString(),
          variants: duel.variants.map(v => ({
            ...v,
            id: generateId(),
            clicks: 0,
            leads: 0
          }))
        }

        set(state => ({ duels: [duplicated, ...state.duels] }))
        return duplicated
      },

      archiveDuel: (duelId) => {
        set(state => ({
          duels: state.duels.map(d =>
            d.id === duelId ? { ...d, status: 'archived', archivedAt: new Date().toISOString() } : d
          )
        }))
      },
      
      createDuel: (duel) => {
        if (!get().canUseBlackBox()) return null
        
        // Increment usage
        set(state => ({
          usage: {
            ...state.usage,
            blackBoxDuelsThisMonth: state.usage.blackBoxDuelsThisMonth + 1
          }
        }))
        
        const newDuel = {
          id: generateId(),
          ...duel,
          name:
            duel.name ||
            `${(duel.variable || 'custom').toString().replace(/(^\w)/, s => s.toUpperCase())} Duel`,
          signalId: duel.signalId || null,
          status: 'running',
          variants: duel.variants.map((v, i) => ({
            id: generateId(),
            label: String.fromCharCode(65 + i), // A, B, C...
            content: v.content,
            notes: v.notes || '',
            smartLink: `rf.to/${Math.random().toString(36).substring(2, 6)}`,
            clicks: 0,
            leads: 0
          })),
          winner: null,
          createdAt: new Date().toISOString()
        }
        
        set(state => ({ duels: [newDuel, ...state.duels] }))
        return newDuel
      },
      
      simulateClicks: (duelId, variantId, clicks, leads = 0) => {
        set(state => ({
          duels: state.duels.map(d =>
            d.id === duelId
              ? {
                  ...d,
                  variants: d.variants.map(v =>
                    v.id === variantId
                      ? { ...v, clicks: v.clicks + clicks, leads: v.leads + leads }
                      : v
                  )
                }
              : d
          )
        }))
      },
      
      crownWinner: (duelId) => {
        const duel = get().getDuel(duelId)
        if (!duel) return null
        
        // Find winner based on goal
        let winner
        if (duel.goal === 'clicks') {
          winner = duel.variants.reduce((a, b) => a.clicks > b.clicks ? a : b)
        } else {
          winner = duel.variants.reduce((a, b) => a.leads > b.leads ? a : b)
        }
        
        set(state => ({
          duels: state.duels.map(d =>
            d.id === duelId
              ? { ...d, status: 'winner', winner: winner.id, crownedAt: new Date().toISOString() }
              : d
          )
        }))
        
        return winner
      },
      
      promoteWinner: (duelId) => {
        const duel = get().getDuel(duelId)
        if (!duel || !duel.winner) return
        
        set(state => ({
          duels: state.duels.map(d =>
            d.id === duelId
              ? { ...d, promotedAt: new Date().toISOString() }
              : d
          )
        }))
        
        // In a real app, this would update Strategy defaults
        console.log('Winner promoted to Strategy defaults')
      },

      // ============================================
      // SIGNALS
      // ============================================
      getSignal: (id) => get().signals.find(s => s.id === id),

      createSignal: (signal) => {
        const now = new Date().toISOString()
        const newSignal = {
          id: generateId(),
          title: signal?.title || 'Untitled Signal',
          statement: signal?.statement || '',
          zone: signal?.zone || 'activation',
          status: signal?.status || 'triage',
          effort: signal?.effort || 'medium',
          primaryMetric: signal?.primaryMetric || null,
          baseline: signal?.baseline || null,
          cohortIds: Array.isArray(signal?.cohortIds) ? signal.cohortIds : [],
          channelIds: Array.isArray(signal?.channelIds) ? signal.channelIds : [],
          evidenceRefs: Array.isArray(signal?.evidenceRefs) ? signal.evidenceRefs : [],
          ice: signal?.ice || { impact: 0, confidence: 0, ease: 0 },
          linked: { duelIds: [], moveIds: [] },
          notes: signal?.notes || '',
          createdAt: now,
          updatedAt: now,
        }
        set(state => ({ signals: [newSignal, ...(state.signals || [])] }))

        emitNotification(
          {
            level: 'info',
            title: 'Signal created',
            detail: newSignal.title,
            href: `/app/signals/${newSignal.id}`,
          },
          { toast: true }
        )

        return newSignal
      },

      updateSignal: (id, updates) => {
        const now = new Date().toISOString()
        set(state => ({
          signals: (state.signals || []).map(s =>
            s.id === id ? { ...s, ...updates, updatedAt: now } : s
          )
        }))
      },

      deleteSignal: (id) => {
        set(state => ({
          signals: (state.signals || []).filter(s => s.id !== id),
          selectedSignalId: state.selectedSignalId === id ? null : state.selectedSignalId,
        }))
      },

      addSignalEvidence: (signalId, evidence) => {
        if (!signalId || !evidence) return
        const key = `${evidence.type || 'evidence'}:${evidence.id || ''}:${evidence.label || ''}`
        set(state => ({
          signals: (state.signals || []).map(s => {
            if (s.id !== signalId) return s
            const current = Array.isArray(s.evidenceRefs) ? s.evidenceRefs : []
            const exists = current.some(ev => `${ev.type || 'evidence'}:${ev.id || ''}:${ev.label || ''}` === key)
            if (exists) return s
            return { ...s, evidenceRefs: [...current, evidence], updatedAt: new Date().toISOString() }
          })
        }))
      },

      linkSignalToDuel: (signalId, duelId) => {
        if (!signalId || !duelId) return
        set(state => ({
          signals: (state.signals || []).map(s => {
            if (s.id !== signalId) return s
            const linked = s.linked || { duelIds: [], moveIds: [] }
            const duelIds = Array.isArray(linked.duelIds) ? linked.duelIds : []
            const nextDuelIds = duelIds.includes(duelId) ? duelIds : [...duelIds, duelId]
            const currentEvidence = Array.isArray(s.evidenceRefs) ? s.evidenceRefs : []
            const duelEvidenceKey = `duel:${duelId}`
            const hasDuelEvidence = currentEvidence.some(ev => `${ev.type}:${ev.id}` === duelEvidenceKey)
            const nextEvidence = hasDuelEvidence
              ? currentEvidence
              : [...currentEvidence, { type: 'duel', id: duelId, label: 'Linked duel' }]

            const status = s.status === 'resolved' || s.status === 'archived' ? s.status : 'in_test'
            return {
              ...s,
              status,
              linked: { ...linked, duelIds: nextDuelIds },
              evidenceRefs: nextEvidence,
              updatedAt: new Date().toISOString(),
            }
          }),
          duels: (state.duels || []).map(d => (d.id === duelId ? { ...d, signalId } : d))
        }))
      },

      linkSignalToMove: (signalId, moveId) => {
        if (!signalId || !moveId) return
        set(state => ({
          signals: (state.signals || []).map(s => {
            if (s.id !== signalId) return s
            const linked = s.linked || { duelIds: [], moveIds: [] }
            const moveIds = Array.isArray(linked.moveIds) ? linked.moveIds : []
            const nextMoveIds = moveIds.includes(moveId) ? moveIds : [...moveIds, moveId]

            const currentEvidence = Array.isArray(s.evidenceRefs) ? s.evidenceRefs : []
            const moveEvidenceKey = `move:${moveId}`
            const hasMoveEvidence = currentEvidence.some(ev => `${ev.type}:${ev.id}` === moveEvidenceKey)
            const nextEvidence = hasMoveEvidence
              ? currentEvidence
              : [...currentEvidence, { type: 'move', id: moveId, label: 'Linked move' }]

            return {
              ...s,
              linked: { ...linked, moveIds: nextMoveIds },
              evidenceRefs: nextEvidence,
              updatedAt: new Date().toISOString(),
            }
          })
        }))
      },

      // ============================================
      // TRAIL
      // ============================================
      addTrailTarget: (target) => {
        const newTarget = {
          id: generateId(),
          ...target,
          status: 'new'
        }
        set(state => ({ trailTargets: [...state.trailTargets, newTarget] }))
        return newTarget
      },
      
      updateTargetStatus: (id, status) => {
        set(state => ({
          trailTargets: state.trailTargets.map(t =>
            t.id === id ? { ...t, status } : t
          )
        }))
      },
      
      deleteTrailTarget: (id) => {
        set(state => ({
          trailTargets: state.trailTargets.filter(t => t.id !== id)
        }))
      },

      // ============================================
      // UI STATE
      // ============================================
      setSelectedCampaign: (id) => set({ selectedCampaignId: id }),
      setSelectedMove: (id) => set({ selectedMoveId: id }),
      setSelectedDuel: (id) => set({ selectedDuelId: id }),
      setSelectedSignal: (id) => set({ selectedSignalId: id }),

      // ============================================
      // RESET
      // ============================================
      resetStore: () => set(initialState),
      
      seedDemoData: () => {
        set({
          strategyVersions: [generateMockStrategy()],
          primaryCampaignId: null,
          cohorts: generateMockCohorts(),
          campaigns: generateMockCampaigns(),
          moves: generateMockMoves(),
          assets: generateMockAssets(),
          radarScans: generateMockRadarScans(),
          duels: generateMockDuels(),
          trailTargets: generateMockTrailTargets(),
          signals: generateMockSignals(),
          pipelineItems: generateMockPipelineItems(),
        })
      }
    }),
    {
      name: 'raptorflow-app-store',
      version: 1,
      partialize: (state) => ({
        currentPlan: state.currentPlan,
        usage: state.usage,
        strategyVersions: state.strategyVersions,
        currentStrategyVersion: state.currentStrategyVersion,
        cohorts: state.cohorts,
        campaigns: state.campaigns,
        primaryCampaignId: state.primaryCampaignId,
        moves: state.moves,
        assets: state.assets,
        radarScans: state.radarScans,
        duels: state.duels,
        trailTargets: state.trailTargets,
        signals: state.signals,
        pipelineItems: state.pipelineItems
      })
    }
  )
)

export { PLAN_LIMITS, CHANNEL_FIT }
export default useRaptorflowStore
