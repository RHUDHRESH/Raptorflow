import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence, useInView } from 'framer-motion'
import { 
  Users, 
  Plus, 
  MoreHorizontal,
  Target,
  TrendingUp,
  ChevronRight,
  ChevronDown,
  User,
  Briefcase,
  AlertCircle,
  CheckCircle2,
  Search,
  Building2,
  Code,
  Brain,
  Activity,
  UserCheck,
  Globe,
  Zap,
  Shield,
  DollarSign,
  Clock,
  Star,
  Filter,
  Download,
  RefreshCw,
  Eye,
  Edit3,
  Copy
} from 'lucide-react'

// 6D ICP Dimensions
const ICP_DIMENSIONS = {
  firmographics: {
    label: 'Firmographics',
    icon: Building2,
    color: 'amber',
    description: 'Company characteristics'
  },
  technographics: {
    label: 'Technographics', 
    icon: Code,
    color: 'blue',
    description: 'Technology stack'
  },
  psychographics: {
    label: 'Psychographics',
    icon: Brain,
    color: 'purple',
    description: 'Motivations & triggers'
  },
  behavioral: {
    label: 'Behavioral Triggers',
    icon: Activity,
    color: 'emerald',
    description: 'In-market signals'
  },
  buying_committee: {
    label: 'Buying Committee',
    icon: UserCheck,
    color: 'pink',
    description: 'Key decision makers'
  },
  category_context: {
    label: 'Category Context',
    icon: Globe,
    color: 'cyan',
    description: 'Market position'
  }
}

// Sample full 6D ICP data
const SAMPLE_ICPS = [
  {
    id: 'icp-1',
    label: 'Desperate Scaler',
    summary: 'High-growth B2B SaaS companies burning cash on scattered GTM, need unified execution immediately',
    fit_score: 92,
    fit_reasoning: 'Perfect alignment with positioning, high urgency triggers, budget available',
    messaging_angle: 'Stop the bleeding. Get control of your GTM in 30 days.',
    selected: true,
    firmographics: {
      employee_range: '51-200',
      revenue_range: '$2M-$10M ARR',
      industries: ['Software / SaaS', 'Fintech', 'B2B Tech'],
      stages: ['Series A', 'Series B'],
      regions: ['North America', 'India', 'Europe'],
      exclude: ['Consumer apps', 'Hardware']
    },
    technographics: {
      must_have: ['HubSpot OR Salesforce', 'Slack', 'Modern analytics stack'],
      nice_to_have: ['Notion', 'Linear', 'Figma'],
      red_flags: ['No CRM', 'Legacy on-prem systems']
    },
    psychographics: {
      pain_points: [
        'Burning $50K+/mo on marketing with unclear ROI',
        'Founder still doing most of sales calls',
        'Metrics scattered across 10+ tools',
        'No systematic way to track what works'
      ],
      motivations: [
        'Need predictable pipeline before next board meeting',
        'Want to delegate GTM without losing control',
        'Prove product-market fit with data'
      ],
      internal_triggers: [
        'Just raised funding - pressure to grow',
        'Board asking for GTM metrics',
        'Marketing hire quit, need to systematize'
      ],
      buying_constraints: [
        'Need to show ROI in 30-60 days',
        'Limited bandwidth for complex implementations',
        'Previous agency burned them'
      ]
    },
    behavioral_triggers: [
      { signal: 'Recently raised Series A/B', source: 'Crunchbase', urgency_boost: 30 },
      { signal: 'Hiring marketing roles', source: 'LinkedIn Jobs', urgency_boost: 25 },
      { signal: 'Visited competitor pricing pages', source: 'Intent data', urgency_boost: 40 },
      { signal: 'Downloaded GTM playbook', source: 'Our content', urgency_boost: 35 }
    ],
    buying_committee: [
      { 
        role: 'Decision Maker', 
        typical_title: 'CEO / Founder',
        concerns: ['ROI timeline', 'Time investment', 'Track record'],
        success_criteria: ['Clear pipeline growth', 'Reduced chaos']
      },
      {
        role: 'Champion',
        typical_title: 'Head of Marketing / Growth',
        concerns: ['Ease of use', 'Integration with stack', 'Day-to-day workload'],
        success_criteria: ['Better attribution', 'More bandwidth']
      },
      {
        role: 'Economic Buyer',
        typical_title: 'CFO / Finance Lead',
        concerns: ['Cost vs. agency alternative', 'Measurable outcomes'],
        success_criteria: ['Cost per qualified lead down', 'Clear reporting']
      }
    ],
    category_context: {
      market_position: 'challenger',
      current_solution: 'Scattered tools + occasional agency help',
      switching_triggers: ['Agency contract ending', 'Marketing lead left', 'Investor pressure']
    },
    qualification_questions: [
      'What are you spending monthly on marketing right now?',
      'How do you currently track what\'s working?',
      'When is your next board meeting?',
      'What happened with your last marketing hire/agency?'
    ]
  },
  {
    id: 'icp-2',
    label: 'Frustrated Optimizer',
    summary: 'Marketing leaders at scale-ups who tried multiple tools/agencies and are sick of guesswork',
    fit_score: 85,
    fit_reasoning: 'Strong problem-solution fit, proven budget, sophisticated buyer',
    messaging_angle: 'You\'ve tried the tools. Now try a system.',
    selected: true,
    firmographics: {
      employee_range: '201-1000',
      revenue_range: '$10M-$50M ARR',
      industries: ['Enterprise SaaS', 'Fintech', 'MarTech'],
      stages: ['Series B', 'Series C'],
      regions: ['United States', 'Europe'],
      exclude: ['Pre-revenue', 'B2C']
    },
    technographics: {
      must_have: ['Salesforce', 'Marketing automation (HubSpot/Marketo)', 'BI tool'],
      nice_to_have: ['Snowflake', 'dbt', 'Attribution tool'],
      red_flags: ['Still using spreadsheets for tracking', 'No marketing ops']
    },
    psychographics: {
      pain_points: [
        'Have 5+ marketing tools that don\'t talk to each other',
        'Can\'t prove marketing impact to board',
        'Team drowning in reporting instead of strategy',
        'Previous tools overpromised and underdelivered'
      ],
      motivations: [
        'Finally get a single source of truth',
        'Prove marketing team\'s value',
        'Spend less time in spreadsheets'
      ],
      internal_triggers: [
        'New CMO wants to restructure',
        'Board asking for better metrics',
        'Preparing for Series C'
      ],
      buying_constraints: [
        'Enterprise security requirements',
        'Need to justify to CFO',
        'Integration complexity concerns'
      ]
    },
    behavioral_triggers: [
      { signal: 'Searching for "marketing attribution"', source: 'G2/Capterra', urgency_boost: 25 },
      { signal: 'Attending marketing ops webinars', source: 'Event data', urgency_boost: 20 },
      { signal: 'Following GTM influencers', source: 'LinkedIn', urgency_boost: 15 }
    ],
    buying_committee: [
      { 
        role: 'Decision Maker', 
        typical_title: 'CMO / VP Marketing',
        concerns: ['Will this finally work?', 'Integration complexity'],
        success_criteria: ['Unified dashboard', 'Board-ready reports']
      },
      {
        role: 'Champion',
        typical_title: 'Marketing Ops Lead',
        concerns: ['Implementation burden', 'Data quality'],
        success_criteria: ['Less manual work', 'Reliable data']
      },
      {
        role: 'Technical Eval',
        typical_title: 'IT / Data Team',
        concerns: ['Security', 'API stability', 'Data governance'],
        success_criteria: ['SOC2 compliance', 'Clean integration']
      }
    ],
    category_context: {
      market_position: 'leader',
      current_solution: 'Multiple point solutions + custom dashboards',
      switching_triggers: ['Contract renewals', 'New CMO', 'Board pressure for metrics']
    },
    qualification_questions: [
      'How many marketing tools are you currently using?',
      'How long does it take to build your monthly board report?',
      'What happened with your last marketing technology purchase?'
    ]
  },
  {
    id: 'icp-3',
    label: 'Risk Mitigator',
    summary: 'Conservative buyers who need assurance and proof before committing',
    fit_score: 72,
    fit_reasoning: 'Good fit but longer sales cycle, needs more nurturing',
    messaging_angle: 'De-risk your GTM investment. See proof before you commit.',
    selected: false,
    firmographics: {
      employee_range: '501-2000',
      revenue_range: '$50M-$200M',
      industries: ['Enterprise Software', 'Financial Services', 'Healthcare Tech'],
      stages: ['Series C+', 'Private Equity'],
      regions: ['North America', 'Europe'],
      exclude: ['Early stage', 'Fast-moving consumer']
    },
    technographics: {
      must_have: ['Enterprise CRM', 'Security certifications', 'Established data stack'],
      nice_to_have: ['CDP', 'Advanced analytics'],
      red_flags: ['Moving fast culture', 'Startup mentality']
    },
    psychographics: {
      pain_points: [
        'Previous investments didn\'t deliver promised ROI',
        'Stakeholder alignment is hard',
        'Risk of picking wrong vendor'
      ],
      motivations: [
        'Find a reliable long-term partner',
        'Minimize implementation risk',
        'Get guaranteed outcomes'
      ],
      internal_triggers: [
        'Annual planning cycle',
        'New leadership with mandate',
        'Competitive pressure'
      ],
      buying_constraints: [
        'Long procurement process',
        'Multiple stakeholder sign-off',
        'Proof requirements before pilot'
      ]
    },
    behavioral_triggers: [
      { signal: 'Downloading case studies', source: 'Website', urgency_boost: 15 },
      { signal: 'Requesting references', source: 'Sales touch', urgency_boost: 30 },
      { signal: 'Long sales cycle behavior', source: 'CRM', urgency_boost: 10 }
    ],
    buying_committee: [
      { 
        role: 'Decision Maker', 
        typical_title: 'CRO / CEO',
        concerns: ['Proven ROI', 'References from peers'],
        success_criteria: ['Case studies', 'Pilot success']
      },
      {
        role: 'Economic Buyer',
        typical_title: 'CFO',
        concerns: ['Total cost of ownership', 'Payback period'],
        success_criteria: ['Clear ROI model', 'Risk mitigation']
      },
      {
        role: 'End User',
        typical_title: 'Marketing Team',
        concerns: ['Learning curve', 'Day-to-day usability'],
        success_criteria: ['Easy adoption', 'Good support']
      }
    ],
    category_context: {
      market_position: 'leader',
      current_solution: 'In-house team + consultants',
      switching_triggers: ['Budget cycle', 'Competitive loss wake-up call']
    },
    qualification_questions: [
      'What would success look like for a pilot?',
      'Who else needs to be involved in this decision?',
      'What\'s your timeline for implementation?'
    ]
  }
]

// 2D Positioning Graph Component
const PositioningGraph = ({ icps }) => {
  const canvasRef = useRef(null)
  const containerRef = useRef(null)
  const [hoveredICP, setHoveredICP] = useState(null)

  // Map ICPs to positions based on fit_score and urgency
  const getICPPosition = (icp, index) => {
    // X axis: Fit Score (0-100)
    // Y axis: Urgency (derived from behavioral triggers)
    const urgency = icp.behavioral_triggers?.reduce((sum, t) => sum + t.urgency_boost, 0) / (icp.behavioral_triggers?.length || 1) || 50
    return {
      x: (icp.fit_score / 100) * 100, // percentage
      y: 100 - (urgency / 40 * 100) // invert for visual (higher urgency = higher on graph)
    }
  }

  const icpColors = ['#f59e0b', '#3b82f6', '#8b5cf6']

  return (
    <div ref={containerRef} className="relative w-full aspect-[16/9] bg-zinc-900/50 border border-white/10 rounded-xl p-6">
      {/* Axes labels */}
      <div className="absolute left-0 top-0 bottom-0 flex items-center -translate-x-full pr-4">
        <span className="text-[10px] uppercase tracking-wider text-white/40 -rotate-90 whitespace-nowrap">
          Urgency / In-Market Signals →
        </span>
      </div>
      <div className="absolute bottom-0 left-0 right-0 flex justify-center translate-y-full pt-4">
        <span className="text-[10px] uppercase tracking-wider text-white/40">
          Fit Score → (Higher = Better Fit)
        </span>
      </div>

      {/* Grid lines */}
      <svg className="absolute inset-6 overflow-visible" preserveAspectRatio="none">
        {/* Vertical grid */}
        {[25, 50, 75].map(x => (
          <line 
            key={`v-${x}`}
            x1={`${x}%`} y1="0" x2={`${x}%`} y2="100%" 
            stroke="rgba(255,255,255,0.05)" 
            strokeDasharray="4,4"
          />
        ))}
        {/* Horizontal grid */}
        {[25, 50, 75].map(y => (
          <line 
            key={`h-${y}`}
            x1="0" y1={`${y}%`} x2="100%" y2={`${y}%`} 
            stroke="rgba(255,255,255,0.05)" 
            strokeDasharray="4,4"
          />
        ))}
        
        {/* Quadrant labels */}
        <text x="12%" y="20%" fill="rgba(255,255,255,0.2)" fontSize="10" textAnchor="middle">
          Low Fit + High Urgency
        </text>
        <text x="88%" y="20%" fill="rgba(16,185,129,0.3)" fontSize="10" textAnchor="middle">
          🎯 Sweet Spot
        </text>
        <text x="12%" y="85%" fill="rgba(255,255,255,0.15)" fontSize="10" textAnchor="middle">
          Nurture
        </text>
        <text x="88%" y="85%" fill="rgba(255,255,255,0.2)" fontSize="10" textAnchor="middle">
          High Fit + Low Urgency
        </text>
      </svg>

      {/* ICP Points */}
      <div className="absolute inset-6">
        {icps.map((icp, index) => {
          const pos = getICPPosition(icp, index)
          const isHovered = hoveredICP === icp.id
          
          return (
            <motion.div
              key={icp.id}
              initial={{ scale: 0 }}
              animate={{ 
                scale: isHovered ? 1.2 : 1,
                x: `${pos.x}%`,
                y: `${pos.y}%`
              }}
              className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer"
              style={{ left: 0, top: 0 }}
              onMouseEnter={() => setHoveredICP(icp.id)}
              onMouseLeave={() => setHoveredICP(null)}
            >
              {/* Bubble */}
              <div 
                className={`
                  relative flex items-center justify-center rounded-full border-2 transition-all
                  ${icp.selected ? 'opacity-100' : 'opacity-50'}
                `}
                style={{
                  width: Math.max(40, icp.fit_score / 2),
                  height: Math.max(40, icp.fit_score / 2),
                  backgroundColor: `${icpColors[index]}20`,
                  borderColor: icpColors[index]
                }}
              >
                <span className="text-white font-medium text-sm">{icp.fit_score}</span>
              </div>

              {/* Tooltip */}
              <AnimatePresence>
                {isHovered && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute top-full mt-2 left-1/2 -translate-x-1/2 w-48 p-3 bg-zinc-800 border border-white/10 rounded-lg shadow-xl z-50"
                  >
                    <div className="font-medium text-white text-sm mb-1">{icp.label}</div>
                    <div className="text-xs text-white/50">{icp.messaging_angle}</div>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-white/40">Fit: {icp.fit_score}%</span>
                      <span className="text-xs" style={{ color: icpColors[index] }}>
                        {icp.selected ? '✓ Selected' : 'Not selected'}
                      </span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        })}
      </div>

      {/* Legend */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        {icps.map((icp, index) => (
          <div key={icp.id} className="flex items-center gap-2 text-xs">
            <div 
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: icpColors[index] }}
            />
            <span className="text-white/60">{icp.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// Dimension Section Component
const DimensionSection = ({ dimension, data, color }) => {
  const [expanded, setExpanded] = useState(false)
  const Icon = ICP_DIMENSIONS[dimension]?.icon || Target

  const colorClasses = {
    amber: 'border-amber-500/30 bg-amber-500/5',
    blue: 'border-blue-500/30 bg-blue-500/5',
    purple: 'border-purple-500/30 bg-purple-500/5',
    emerald: 'border-emerald-500/30 bg-emerald-500/5',
    pink: 'border-pink-500/30 bg-pink-500/5',
    cyan: 'border-cyan-500/30 bg-cyan-500/5'
  }

  const iconColorClasses = {
    amber: 'text-amber-400 bg-amber-500/20',
    blue: 'text-blue-400 bg-blue-500/20',
    purple: 'text-purple-400 bg-purple-500/20',
    emerald: 'text-emerald-400 bg-emerald-500/20',
    pink: 'text-pink-400 bg-pink-500/20',
    cyan: 'text-cyan-400 bg-cyan-500/20'
  }

  const renderContent = () => {
    if (!data) return <p className="text-white/30 text-sm">No data available</p>

    switch (dimension) {
      case 'firmographics':
        return (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-xs text-white/40">Company Size</span>
              <p className="text-white">{data.employee_range}</p>
            </div>
            <div>
              <span className="text-xs text-white/40">Revenue</span>
              <p className="text-white">{data.revenue_range}</p>
            </div>
            <div className="col-span-2">
              <span className="text-xs text-white/40">Industries</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {data.industries?.map((ind, i) => (
                  <span key={i} className="px-2 py-0.5 bg-white/5 rounded text-xs text-white/60">
                    {ind}
                  </span>
                ))}
              </div>
            </div>
            <div className="col-span-2">
              <span className="text-xs text-white/40">Stages</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {data.stages?.map((stage, i) => (
                  <span key={i} className="px-2 py-0.5 bg-amber-500/10 rounded text-xs text-amber-300">
                    {stage}
                  </span>
                ))}
              </div>
            </div>
            {data.exclude?.length > 0 && (
              <div className="col-span-2">
                <span className="text-xs text-red-400/60">Exclude</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.exclude?.map((exc, i) => (
                    <span key={i} className="px-2 py-0.5 bg-red-500/10 rounded text-xs text-red-300">
                      {exc}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      case 'technographics':
        return (
          <div className="space-y-4">
            <div>
              <span className="text-xs text-emerald-400/60 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Must Have
              </span>
              <div className="flex flex-wrap gap-1 mt-1">
                {data.must_have?.map((tech, i) => (
                  <span key={i} className="px-2 py-0.5 bg-emerald-500/10 rounded text-xs text-emerald-300">
                    {tech}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="text-xs text-blue-400/60">Nice to Have</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {data.nice_to_have?.map((tech, i) => (
                  <span key={i} className="px-2 py-0.5 bg-blue-500/10 rounded text-xs text-blue-300">
                    {tech}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="text-xs text-red-400/60 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> Red Flags
              </span>
              <div className="flex flex-wrap gap-1 mt-1">
                {data.red_flags?.map((flag, i) => (
                  <span key={i} className="px-2 py-0.5 bg-red-500/10 rounded text-xs text-red-300">
                    {flag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )

      case 'psychographics':
        return (
          <div className="space-y-4">
            <div>
              <span className="text-xs text-white/40">Pain Points</span>
              <ul className="mt-2 space-y-1">
                {data.pain_points?.map((pain, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-white/60">
                    <span className="text-red-400 mt-1">•</span> {pain}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <span className="text-xs text-white/40">Motivations</span>
              <ul className="mt-2 space-y-1">
                {data.motivations?.map((mot, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-white/60">
                    <span className="text-emerald-400 mt-1">•</span> {mot}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <span className="text-xs text-white/40">Internal Triggers</span>
              <ul className="mt-2 space-y-1">
                {data.internal_triggers?.map((trig, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-white/60">
                    <Zap className="w-3 h-3 text-amber-400 mt-1 flex-shrink-0" /> {trig}
                  </li>
                ))}
              </ul>
            </div>
            {data.buying_constraints?.length > 0 && (
              <div>
                <span className="text-xs text-white/40">Buying Constraints</span>
                <ul className="mt-2 space-y-1">
                  {data.buying_constraints?.map((con, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-white/60">
                      <Shield className="w-3 h-3 text-orange-400 mt-1 flex-shrink-0" /> {con}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )

      case 'behavioral':
        return (
          <div className="space-y-3">
            {data.map((trigger, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm text-white">{trigger.signal}</p>
                  <p className="text-xs text-white/40">{trigger.source}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-emerald-400">+{trigger.urgency_boost}%</span>
                  <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full"
                      style={{ width: `${trigger.urgency_boost}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )

      case 'buying_committee':
        return (
          <div className="space-y-4">
            {data.map((person, i) => (
              <div key={i} className="p-4 bg-white/5 rounded-lg border border-white/5">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-white/10 rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 text-white/60" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{person.role}</p>
                      <p className="text-xs text-white/40">{person.typical_title}</p>
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-xs text-red-400/60">Concerns</span>
                    <ul className="mt-1 space-y-0.5">
                      {person.concerns?.map((c, j) => (
                        <li key={j} className="text-xs text-white/50">• {c}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <span className="text-xs text-emerald-400/60">Success Criteria</span>
                    <ul className="mt-1 space-y-0.5">
                      {person.success_criteria?.map((s, j) => (
                        <li key={j} className="text-xs text-white/50">• {s}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )

      case 'category_context':
        return (
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <span className="text-xs text-white/40">Market Position</span>
                <p className="text-white capitalize">{data.market_position}</p>
              </div>
              <div className="flex-1">
                <span className="text-xs text-white/40">Current Solution</span>
                <p className="text-white text-sm">{data.current_solution}</p>
              </div>
            </div>
            <div>
              <span className="text-xs text-white/40">Switching Triggers</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {data.switching_triggers?.map((trig, i) => (
                  <span key={i} className="px-3 py-1.5 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-300">
                    {trig}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )

      default:
        return <pre className="text-xs text-white/40">{JSON.stringify(data, null, 2)}</pre>
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`border rounded-xl overflow-hidden ${colorClasses[color] || colorClasses.amber}`}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconColorClasses[color]}`}>
            <Icon className="w-5 h-5" />
          </div>
          <div className="text-left">
            <h4 className="text-white font-medium">{ICP_DIMENSIONS[dimension]?.label}</h4>
            <p className="text-xs text-white/40">{ICP_DIMENSIONS[dimension]?.description}</p>
          </div>
        </div>
        <ChevronDown className={`w-5 h-5 text-white/40 transition-transform ${expanded ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-white/5"
          >
            <div className="p-4">
              {renderContent()}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Full ICP Card with all 6 dimensions
const FullICPCard = ({ icp, index, isExpanded, onToggle }) => {
  const colors = ['amber', 'blue', 'purple']
  const baseColor = colors[index % colors.length]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`
        bg-zinc-900/50 border rounded-2xl overflow-hidden transition-all
        ${icp.selected ? 'border-amber-500/30' : 'border-white/5'}
      `}
    >
      {/* Header */}
      <div 
        className="p-6 cursor-pointer hover:bg-white/5 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-4">
            <div className={`w-14 h-14 rounded-xl bg-${baseColor}-500/20 flex items-center justify-center`}>
              <span className="text-2xl font-light text-white">{icp.fit_score}</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xl font-medium text-white">{icp.label}</h3>
                {icp.selected && (
                  <span className="px-2 py-0.5 bg-emerald-500/20 rounded text-xs text-emerald-400">
                    Selected
                  </span>
                )}
              </div>
              <p className="text-sm text-white/40 mt-1">{icp.summary}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <Copy className="w-4 h-4 text-white/40" />
            </button>
            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <Edit3 className="w-4 h-4 text-white/40" />
            </button>
            <ChevronDown className={`w-5 h-5 text-white/40 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
          </div>
        </div>

        {/* Quick stats */}
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-amber-400/60" />
            <span className="text-white/60">Fit: {icp.fit_score}%</span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400/60" />
            <span className="text-white/60">
              {icp.behavioral_triggers?.length || 0} triggers
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-400/60" />
            <span className="text-white/60">
              {icp.buying_committee?.length || 0} personas
            </span>
          </div>
        </div>

        {/* Messaging angle */}
        <div className="mt-4 p-3 bg-white/5 rounded-lg">
          <span className="text-xs text-white/40">Messaging Angle</span>
          <p className="text-white mt-1 italic">"{icp.messaging_angle}"</p>
        </div>
      </div>

      {/* Expanded content with all 6D dimensions */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-white/5"
          >
            <div className="p-6 space-y-4">
              {/* Fit reasoning */}
              <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                <span className="text-xs text-emerald-400 font-medium">Fit Reasoning</span>
                <p className="text-white/80 mt-1">{icp.fit_reasoning}</p>
              </div>

              {/* 6D Dimensions */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <DimensionSection 
                  dimension="firmographics" 
                  data={icp.firmographics} 
                  color="amber" 
                />
                <DimensionSection 
                  dimension="technographics" 
                  data={icp.technographics} 
                  color="blue" 
                />
                <DimensionSection 
                  dimension="psychographics" 
                  data={icp.psychographics} 
                  color="purple" 
                />
                <DimensionSection 
                  dimension="behavioral" 
                  data={icp.behavioral_triggers} 
                  color="emerald" 
                />
                <DimensionSection 
                  dimension="buying_committee" 
                  data={icp.buying_committee} 
                  color="pink" 
                />
                <DimensionSection 
                  dimension="category_context" 
                  data={icp.category_context} 
                  color="cyan" 
                />
              </div>

              {/* Qualification Questions */}
              <div className="p-4 bg-white/5 rounded-xl">
                <h4 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-amber-400" />
                  Qualification Questions
                </h4>
                <ol className="space-y-2">
                  {icp.qualification_questions?.map((q, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-white/60">
                      <span className="w-5 h-5 rounded bg-white/10 flex items-center justify-center text-xs text-white/40 flex-shrink-0">
                        {i + 1}
                      </span>
                      {q}
                    </li>
                  ))}
                </ol>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-3 pt-4 border-t border-white/5">
                <button className="flex-1 py-3 bg-white/5 hover:bg-white/10 rounded-xl text-sm text-white/60 transition-colors">
                  Export Profile
                </button>
                <button className="flex-1 py-3 bg-amber-500/20 hover:bg-amber-500/30 rounded-xl text-sm text-amber-400 transition-colors">
                  Create Campaign for this ICP
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Missing import
const MessageSquare = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
)

// Main Cohorts Component
const Cohorts = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedICP, setExpandedICP] = useState(null)
  const [view, setView] = useState('cards') // 'cards' | 'graph'

  const filteredICPs = SAMPLE_ICPS.filter(icp =>
    icp.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    icp.summary.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-light text-white">ICPs & Cohorts</h1>
          <p className="text-white/40 mt-1">
            6-Dimensional Ideal Customer Profiles
          </p>
        </motion.div>

        <div className="flex items-center gap-3">
          <div className="flex items-center bg-white/5 rounded-lg p-1">
            <button
              onClick={() => setView('cards')}
              className={`px-4 py-2 rounded text-sm transition-colors ${
                view === 'cards' ? 'bg-white/10 text-white' : 'text-white/40 hover:text-white/60'
              }`}
            >
              Cards
            </button>
            <button
              onClick={() => setView('graph')}
              className={`px-4 py-2 rounded text-sm transition-colors ${
                view === 'graph' ? 'bg-white/10 text-white' : 'text-white/40 hover:text-white/60'
              }`}
            >
              Graph
            </button>
          </div>

          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Regenerate ICPs
          </motion.button>
        </div>
      </div>

      {/* Search & Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex items-center gap-4 mb-6"
      >
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
          <input
            type="text"
            placeholder="Search ICPs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-zinc-900/50 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:border-amber-500/50 focus:outline-none transition-colors"
          />
        </div>
        <button className="flex items-center gap-2 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white/60 hover:border-white/20 transition-colors">
          <Filter className="w-4 h-4" />
          Filter
        </button>
        <button className="flex items-center gap-2 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white/60 hover:border-white/20 transition-colors">
          <Download className="w-4 h-4" />
          Export All
        </button>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="grid grid-cols-4 gap-4 mb-8"
      >
        {[
          { label: 'Total ICPs', value: filteredICPs.length, icon: Users },
          { label: 'Selected', value: filteredICPs.filter(i => i.selected).length, icon: CheckCircle2 },
          { label: 'Avg Fit Score', value: `${Math.round(filteredICPs.reduce((s, i) => s + i.fit_score, 0) / filteredICPs.length)}%`, icon: Target },
          { label: 'Active Triggers', value: filteredICPs.reduce((s, i) => s + (i.behavioral_triggers?.length || 0), 0), icon: Activity },
        ].map((stat, i) => (
          <div key={i} className="bg-zinc-900/30 border border-white/5 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-light text-white">{stat.value}</p>
                <p className="text-xs text-white/40 mt-1">{stat.label}</p>
              </div>
              <stat.icon className="w-8 h-8 text-white/10" />
            </div>
          </div>
        ))}
      </motion.div>

      {/* Graph View */}
      {view === 'graph' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h3 className="text-sm text-white/40 mb-4">ICP Positioning Map</h3>
          <PositioningGraph icps={filteredICPs} />
        </motion.div>
      )}

      {/* ICP Cards */}
      <div className="space-y-4">
        {filteredICPs.map((icp, index) => (
          <FullICPCard
            key={icp.id}
            icp={icp}
            index={index}
            isExpanded={expandedICP === icp.id}
            onToggle={() => setExpandedICP(expandedICP === icp.id ? null : icp.id)}
          />
        ))}
      </div>

      {filteredICPs.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16"
        >
          <Users className="w-12 h-12 text-white/20 mx-auto mb-4" />
          <p className="text-white/40">No ICPs found</p>
        </motion.div>
      )}
    </div>
  )
}

export default Cohorts
