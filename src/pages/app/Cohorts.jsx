import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../../contexts/AuthContext'
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
  Copy,
  Lock,
  Sparkles,
  Radio,
  Tags
} from 'lucide-react'

import { Modal } from '@/components/system/Modal'
import { EmptyState } from '@/components/EmptyState'

// 6D Cohort Dimensions
const COHORT_DIMENSIONS = {
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

// Cohort limits by plan tier
const COHORT_LIMITS = {
  ascent: 3,
  glide: 5,
  soar: 10
}

// 2D Positioning Graph Component
const PositioningGraph = ({ cohorts }) => {
  const [hoveredCohort, setHoveredCohort] = useState(null)

  // Map cohorts to positions based on fit_score and urgency
  const getCohortPosition = (cohort) => {
    const urgency = cohort.behavioral_triggers?.reduce((sum, t) => sum + t.urgency_boost, 0) / (cohort.behavioral_triggers?.length || 1) || 50
    return {
      x: (cohort.fit_score / 100) * 100,
      y: 100 - (urgency / 40 * 100)
    }
  }

  const cohortColors = ['#f59e0b', '#3b82f6', '#8b5cf6', '#10b981', '#ec4899']

  if (cohorts.length === 0) {
    return (
      <div className="w-full aspect-[16/9] bg-zinc-900/50 border border-white/10 rounded-xl flex items-center justify-center">
        <div className="text-center">
          <Users className="w-12 h-12 text-white/20 mx-auto mb-3" />
          <p className="text-white/40">Create cohorts to see the positioning map</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative w-full aspect-[16/9] bg-zinc-900/50 border border-white/10 rounded-xl p-6">
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
        {[25, 50, 75].map(x => (
          <line 
            key={`v-${x}`}
            x1={`${x}%`} y1="0" x2={`${x}%`} y2="100%" 
            stroke="rgba(255,255,255,0.05)" 
            strokeDasharray="4,4"
          />
        ))}
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

      {/* Cohort Points */}
      <div className="absolute inset-6">
        {cohorts.map((cohort, index) => {
          const pos = getCohortPosition(cohort)
          const isHovered = hoveredCohort === cohort.id
          
          return (
            <motion.div
              key={cohort.id}
              initial={{ scale: 0 }}
              animate={{ 
                scale: isHovered ? 1.2 : 1,
                x: `${pos.x}%`,
                y: `${pos.y}%`
              }}
              className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer"
              style={{ left: 0, top: 0 }}
              onMouseEnter={() => setHoveredCohort(cohort.id)}
              onMouseLeave={() => setHoveredCohort(null)}
            >
              <div 
                className={`
                  relative flex items-center justify-center rounded-full border-2 transition-all
                  ${cohort.selected ? 'opacity-100' : 'opacity-50'}
                `}
                style={{
                  width: Math.max(40, cohort.fit_score / 2),
                  height: Math.max(40, cohort.fit_score / 2),
                  backgroundColor: `${cohortColors[index % cohortColors.length]}20`,
                  borderColor: cohortColors[index % cohortColors.length]
                }}
              >
                <span className="text-white font-medium text-sm">{cohort.fit_score}</span>
              </div>

              <AnimatePresence>
                {isHovered && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute top-full mt-2 left-1/2 -translate-x-1/2 w-48 p-3 bg-zinc-800 border border-white/10 rounded-lg shadow-xl z-50"
                  >
                    <div className="font-medium text-white text-sm mb-1">{cohort.label}</div>
                    <div className="text-xs text-white/50">{cohort.messaging_angle}</div>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-xs text-white/40">Fit: {cohort.fit_score}%</span>
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
        {cohorts.slice(0, 5).map((cohort, index) => (
          <div key={cohort.id} className="flex items-center gap-2 text-xs">
            <div 
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: cohortColors[index % cohortColors.length] }}
            />
            <span className="text-ink-400 truncate max-w-[120px]">{cohort.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// Dimension Section Component
const DimensionSection = ({ dimension, data, color }) => {
  const [expanded, setExpanded] = useState(false)
  const Icon = COHORT_DIMENSIONS[dimension]?.icon || Target

  const renderContent = () => {
    if (!data) return <p className="text-ink-400 text-sm">No data available</p>

    switch (dimension) {
      case 'firmographics':
        return (
          <div className="grid grid-cols-2 gap-4">
            {data.employee_range && (
              <div>
                <span className="text-xs text-ink-400">Company size</span>
                <p className="text-ink">{data.employee_range}</p>
              </div>
            )}
            {data.revenue_range && (
              <div>
                <span className="text-xs text-ink-400">Revenue</span>
                <p className="text-ink">{data.revenue_range}</p>
              </div>
            )}
            {data.industries?.length > 0 && (
              <div className="col-span-2">
                <span className="text-xs text-ink-400">Industries</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.industries.map((ind, i) => (
                    <span key={i} className="px-2 py-0.5 bg-muted rounded text-xs text-ink-400">
                      {ind}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.stages?.length > 0 && (
              <div className="col-span-2">
                <span className="text-xs text-ink-400">Stages</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.stages.map((stage, i) => (
                    <span key={i} className="px-2 py-0.5 bg-signal-muted rounded text-xs text-primary">
                      {stage}
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
            {data.must_have?.length > 0 && (
              <div>
                <span className="text-xs text-ink-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-primary" strokeWidth={1.5} /> Must have
                </span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.must_have.map((tech, i) => (
                    <span key={i} className="px-2 py-0.5 bg-muted rounded text-xs text-ink">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.nice_to_have?.length > 0 && (
              <div>
                <span className="text-xs text-ink-400">Nice to have</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.nice_to_have.map((tech, i) => (
                    <span key={i} className="px-2 py-0.5 bg-muted rounded text-xs text-ink-400">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.red_flags?.length > 0 && (
              <div>
                <span className="text-xs text-ink-400 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3 text-primary" strokeWidth={1.5} /> Red flags
                </span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.red_flags.map((flag, i) => (
                    <span key={i} className="px-2 py-0.5 bg-signal-muted rounded text-xs text-primary">
                      {flag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      case 'psychographics':
        return (
          <div className="space-y-4">
            {data.pain_points?.length > 0 && (
              <div>
                <span className="text-xs text-ink-400">Pain points</span>
                <ul className="mt-2 space-y-1">
                  {data.pain_points.map((pain, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-ink-400">
                      <span className="text-primary mt-1">•</span> {pain}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {data.motivations?.length > 0 && (
              <div>
                <span className="text-xs text-ink-400">Motivations</span>
                <ul className="mt-2 space-y-1">
                  {data.motivations.map((mot, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-ink-400">
                      <span className="text-primary mt-1">•</span> {mot}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )

      case 'behavioral':
        if (!Array.isArray(data) || data.length === 0) {
          return <p className="text-ink-400 text-sm">No behavioral triggers defined</p>
        }
        return (
          <div className="space-y-3">
            {data.map((trigger, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-muted rounded-lg border border-border">
                <div className="flex-1">
                  <p className="text-sm text-ink">{trigger.signal}</p>
                  <p className="text-xs text-ink-400">{trigger.source}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-primary">+{trigger.urgency_boost}%</span>
                  <div className="w-16 h-2 bg-background rounded-full overflow-hidden border border-border">
                    <div 
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${Math.min(100, trigger.urgency_boost)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )

      case 'buying_committee':
        if (!Array.isArray(data) || data.length === 0) {
          return <p className="text-ink-400 text-sm">No buying committee defined</p>
        }
        return (
          <div className="space-y-4">
            {data.map((person, i) => (
              <div key={i} className="p-4 bg-muted rounded-lg border border-border">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-8 bg-background rounded-full flex items-center justify-center border border-border">
                    <User className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-ink">{person.role}</p>
                    <p className="text-xs text-ink-400">{person.typical_title}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )

      case 'category_context':
        return (
          <div className="space-y-4">
            {data.market_position && (
              <div>
                <span className="text-xs text-ink-400">Market position</span>
                <p className="text-ink capitalize">{data.market_position}</p>
              </div>
            )}
            {data.current_solution && (
              <div>
                <span className="text-xs text-ink-400">Current solution</span>
                <p className="text-ink text-sm">{data.current_solution}</p>
              </div>
            )}
            {data.switching_triggers?.length > 0 && (
              <div>
                <span className="text-xs text-ink-400">Switching triggers</span>
                <div className="flex flex-wrap gap-2 mt-2">
                  {data.switching_triggers.map((trig, i) => (
                    <span key={i} className="px-3 py-1.5 bg-signal-muted border border-primary/20 rounded-lg text-xs text-primary">
                      {trig}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="border border-border rounded-xl overflow-hidden bg-card"
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-muted transition-editorial"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-muted border border-border">
            <Icon className="w-5 h-5 text-ink-400" strokeWidth={1.5} />
          </div>
          <div className="text-left">
            <h4 className="text-ink font-medium">{COHORT_DIMENSIONS[dimension]?.label}</h4>
            <p className="text-xs text-ink-400">{COHORT_DIMENSIONS[dimension]?.description}</p>
          </div>
        </div>
        <ChevronDown className={`w-5 h-5 text-ink-400 transition-transform ${expanded ? 'rotate-180' : ''}`} strokeWidth={1.5} />
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-border"
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

// Full Cohort Card
const FullCohortCard = ({ cohort, index, isExpanded, onToggle }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-card border border-border rounded-2xl overflow-hidden transition-editorial"
    >
      {/* Header */}
      <div 
        className="p-6 cursor-pointer hover:bg-muted transition-editorial"
        onClick={onToggle}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-signal-muted border border-primary/20 flex items-center justify-center">
              <span className="text-2xl font-light text-primary">{cohort.fit_score}</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xl font-medium text-ink">{cohort.label}</h3>
                {cohort.selected && (
                  <span className="px-2 py-0.5 bg-signal-muted rounded text-xs text-primary border border-primary/20">
                    Active
                  </span>
                )}
              </div>
              <p className="text-sm text-ink-400 mt-1">{cohort.summary}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-muted rounded-lg transition-editorial">
              <Radio className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
            </button>
            <button className="p-2 hover:bg-muted rounded-lg transition-editorial">
              <Tags className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
            </button>
            <ChevronDown className={`w-5 h-5 text-ink-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} strokeWidth={1.5} />
          </div>
        </div>

        {/* Quick stats */}
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
            <span className="text-ink-400">Fit: {cohort.fit_score}%</span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
            <span className="text-ink-400">
              {cohort.behavioral_triggers?.length || 0} triggers
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
            <span className="text-ink-400">
              {cohort.buying_committee?.length || 0} personas
            </span>
          </div>
          {cohort.tags?.length > 0 && (
            <div className="flex items-center gap-2">
              <Tags className="w-4 h-4 text-ink-400" strokeWidth={1.5} />
              <span className="text-ink-400">
                {cohort.tags.length} tags
              </span>
            </div>
          )}
        </div>

        {/* Messaging angle */}
        {cohort.messaging_angle && (
          <div className="mt-4 p-3 bg-muted rounded-lg border border-border">
            <span className="text-xs text-ink-400">Messaging angle</span>
            <p className="text-ink mt-1 italic">"{cohort.messaging_angle}"</p>
          </div>
        )}
      </div>

      {/* Expanded content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-border"
          >
            <div className="p-6 space-y-4">
              {/* Fit reasoning */}
              {cohort.fit_reasoning && (
                <div className="p-4 bg-signal-muted border border-primary/20 rounded-xl">
                  <span className="text-xs text-primary font-medium">Fit reasoning</span>
                  <p className="text-ink mt-1">{cohort.fit_reasoning}</p>
                </div>
              )}

              {/* Tags */}
              {cohort.tags?.length > 0 && (
                <div className="p-4 bg-card border border-border rounded-xl">
                  <span className="text-xs text-ink font-medium flex items-center gap-2">
                    <Tags className="w-4 h-4 text-primary" strokeWidth={1.5} />
                    Tags of interest ({cohort.tags.length})
                  </span>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {cohort.tags.slice(0, 20).map((tag, i) => (
                      <span key={i} className="px-2 py-1 bg-muted rounded-lg text-xs text-ink">
                        {tag}
                      </span>
                    ))}
                    {cohort.tags.length > 20 && (
                      <span className="px-2 py-1 bg-muted rounded-lg text-xs text-ink-400">
                        +{cohort.tags.length - 20} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* 6D Dimensions */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <DimensionSection 
                  dimension="firmographics" 
                  data={cohort.firmographics} 
                  color="amber" 
                />
                <DimensionSection 
                  dimension="technographics" 
                  data={cohort.technographics} 
                  color="blue" 
                />
                <DimensionSection 
                  dimension="psychographics" 
                  data={cohort.psychographics} 
                  color="purple" 
                />
                <DimensionSection 
                  dimension="behavioral" 
                  data={cohort.behavioral_triggers} 
                  color="emerald" 
                />
                <DimensionSection 
                  dimension="buying_committee" 
                  data={cohort.buying_committee} 
                  color="pink" 
                />
                <DimensionSection 
                  dimension="category_context" 
                  data={cohort.category_context} 
                  color="cyan" 
                />
              </div>

              {/* Actions */}
              <div className="flex items-center gap-3 pt-4 border-t border-border">
                <button className="flex-1 py-3 bg-card border border-border hover:border-border-dark rounded-xl text-sm text-ink-400 transition-editorial flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" strokeWidth={1.5} />
                  Export profile
                </button>
                <button className="flex-1 py-3 bg-muted border border-border hover:border-border-dark rounded-xl text-sm text-ink transition-editorial flex items-center justify-center gap-2">
                  <Radio className="w-4 h-4 text-primary" strokeWidth={1.5} />
                  Open in Radar
                </button>
                <button className="flex-1 py-3 bg-primary text-primary-foreground hover:opacity-95 rounded-xl text-sm transition-editorial flex items-center justify-center gap-2">
                  <Sparkles className="w-4 h-4" strokeWidth={1.5} />
                  Create campaign
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Create Cohort Modal
const CreateCohortModal = ({ isOpen, onClose, onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    label: '',
    summary: '',
    employee_range: '',
    industries: '',
    revenue_range: ''
  })

  return (
    <Modal
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) onClose()
      }}
      title="Create cohort"
      description="Define your ideal customer profile. We'll generate the full 6D profile and tags."
      contentClassName="max-w-lg"
    >
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-muted-foreground mb-2">Cohort name *</label>
          <input
            type="text"
            value={formData.label}
            onChange={(e) => setFormData({ ...formData, label: e.target.value })}
            placeholder="e.g., Growth-stage SaaS founders"
            className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>

        <div>
          <label className="block text-sm text-muted-foreground mb-2">Description *</label>
          <textarea
            value={formData.summary}
            onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
            placeholder="Describe this cohort in detail. The more specific, the better the tags."
            rows={4}
            className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Company size</label>
            <select
              value={formData.employee_range}
              onChange={(e) => setFormData({ ...formData, employee_range: e.target.value })}
              className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value="">Select size</option>
              <option value="1-10">1-10 employees</option>
              <option value="11-50">11-50 employees</option>
              <option value="51-200">51-200 employees</option>
              <option value="201-1000">201-1000 employees</option>
              <option value="1000+">1000+ employees</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Revenue range</label>
            <select
              value={formData.revenue_range}
              onChange={(e) => setFormData({ ...formData, revenue_range: e.target.value })}
              className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value="">Select range</option>
              <option value="Pre-revenue">Pre-revenue</option>
              <option value="$0-$1M">$0-$1M</option>
              <option value="$1M-$5M">$1M-$5M</option>
              <option value="$5M-$20M">$5M-$20M</option>
              <option value="$20M+">$20M+</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm text-muted-foreground mb-2">Industries (comma separated)</label>
          <input
            type="text"
            value={formData.industries}
            onChange={(e) => setFormData({ ...formData, industries: e.target.value })}
            placeholder="e.g., SaaS, Fintech, E-commerce"
            className="w-full px-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>

        <div className="pt-2 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-md border border-border bg-transparent text-foreground hover:bg-muted transition-editorial"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => onSubmit(formData)}
            disabled={isLoading || !formData.label || !formData.summary}
            className="px-4 py-2 rounded-md bg-primary text-primary-foreground hover:opacity-95 transition-editorial disabled:opacity-50 inline-flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Creating…
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Create cohort
              </>
            )}
          </button>
        </div>
      </div>
    </Modal>
  )
}

// Main Cohorts Component
const Cohorts = () => {
  const { profile } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedCohort, setExpandedCohort] = useState(null)
  const [view, setView] = useState('cards')
  const [cohorts, setCohorts] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Get cohort limit based on plan
  const planName = profile?.plan?.toLowerCase() || 'ascent'
  const cohortLimit = COHORT_LIMITS[planName] || 3
  const canCreateMore = cohorts.length < cohortLimit

  const filteredCohorts = cohorts.filter(cohort =>
    cohort.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (cohort.summary || '').toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleCreateCohort = async (formData) => {
    setIsLoading(true)
    // TODO: Call API to create cohort and generate tags
    // Simulated for now
    setTimeout(() => {
      const newCohort = {
        id: `cohort-${Date.now()}`,
        label: formData.label,
        summary: formData.summary,
        fit_score: 75,
        fit_reasoning: 'AI will analyze and provide reasoning',
        messaging_angle: 'AI will generate messaging',
        selected: true,
        tags: [], // Will be generated by CohortTagGeneratorAgent
        firmographics: {
          employee_range: formData.employee_range,
          revenue_range: formData.revenue_range,
          industries: formData.industries.split(',').map(s => s.trim()).filter(Boolean)
        },
        technographics: {},
        psychographics: {},
        behavioral_triggers: [],
        buying_committee: [],
        category_context: {}
      }
      setCohorts([...cohorts, newCohort])
      setShowCreateModal(false)
      setIsLoading(false)
    }, 2000)
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="font-serif text-headline-md text-ink">Cohorts</h1>
          <p className="text-body-sm text-ink-400 mt-1">6-dimensional ideal customer profiles</p>
        </motion.div>

        <div className="flex items-center gap-3">
          {/* Plan info */}
          <div className="px-4 py-2 bg-card border border-border rounded-lg">
            <span className="text-xs text-ink-400">
              {cohorts.length} / {cohortLimit} cohorts
            </span>
          </div>

          <div className="flex items-center bg-muted border border-border rounded-lg p-1">
            <button
              onClick={() => setView('cards')}
              className={`px-4 py-2 rounded text-sm transition-colors ${
                view === 'cards' ? 'bg-background text-foreground' : 'text-ink-400 hover:text-ink'
              }`}
            >
              Cards
            </button>
            <button
              onClick={() => setView('graph')}
              className={`px-4 py-2 rounded text-sm transition-colors ${
                view === 'graph' ? 'bg-background text-foreground' : 'text-ink-400 hover:text-ink'
              }`}
            >
              Graph
            </button>
          </div>

          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={() => canCreateMore ? setShowCreateModal(true) : null}
            disabled={!canCreateMore}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-colors ${
              canCreateMore 
                ? 'bg-primary text-primary-foreground hover:opacity-95 transition-editorial' 
                : 'bg-muted text-ink-300 cursor-not-allowed'
            }`}
          >
            {canCreateMore ? (
              <>
                <Plus className="w-4 h-4" strokeWidth={1.5} />
                Create cohort
              </>
            ) : (
              <>
                <Lock className="w-4 h-4" strokeWidth={1.5} />
                Limit reached
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* Limit warning */}
      {!canCreateMore && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mb-6 p-4 bg-signal-muted border border-primary/20 rounded-xl flex items-center gap-3"
        >
          <Lock className="w-5 h-5 text-primary" strokeWidth={1.5} />
          <div className="flex-1">
            <p className="text-ink font-medium">Cohort limit reached</p>
            <p className="text-ink-400 text-sm">
              Your {planName} plan allows up to {cohortLimit} cohorts. Upgrade to create more.
            </p>
          </div>
          <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:opacity-95 transition-editorial">
            Upgrade Plan
          </button>
        </motion.div>
      )}

      {/* Search & Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex items-center gap-4 mb-6"
      >
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-ink-400" strokeWidth={1.5} />
          <input
            type="text"
            placeholder="Search cohorts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-background border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-editorial"
          />
        </div>
        <button className="flex items-center gap-2 px-4 py-3 bg-card border border-border rounded-xl text-ink-400 hover:text-ink hover:border-border-dark transition-editorial">
          <Filter className="w-4 h-4" strokeWidth={1.5} />
          Filter
        </button>
        <button className="flex items-center gap-2 px-4 py-3 bg-card border border-border rounded-xl text-ink-400 hover:text-ink hover:border-border-dark transition-editorial">
          <Download className="w-4 h-4" strokeWidth={1.5} />
          Export All
        </button>
      </motion.div>

      {/* Stats */}
      {cohorts.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="grid grid-cols-4 gap-4 mb-8"
        >
          {[
            { label: 'Total Cohorts', value: filteredCohorts.length, icon: Users },
            { label: 'Active', value: filteredCohorts.filter(i => i.selected).length, icon: CheckCircle2 },
            { label: 'Avg Fit Score', value: filteredCohorts.length > 0 ? `${Math.round(filteredCohorts.reduce((s, i) => s + i.fit_score, 0) / filteredCohorts.length)}%` : '-', icon: Target },
            { label: 'Active Triggers', value: filteredCohorts.reduce((s, i) => s + (i.behavioral_triggers?.length || 0), 0), icon: Activity },
          ].map((stat, i) => (
            <div key={i} className="bg-card border border-border rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-light text-ink">{stat.value}</p>
                  <p className="text-xs text-ink-400 mt-1">{stat.label}</p>
                </div>
                <stat.icon className="w-8 h-8 text-ink-300" strokeWidth={1.5} />
              </div>
            </div>
          ))}
        </motion.div>
      )}

      {/* Graph View */}
      {view === 'graph' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h3 className="text-sm text-ink-400 mb-4">Cohort positioning map</h3>
          <PositioningGraph cohorts={filteredCohorts} />
        </motion.div>
      )}

      {/* Cohort Cards */}
      {cohorts.length > 0 ? (
        <div className="space-y-4">
          {filteredCohorts.map((cohort, index) => (
            <FullCohortCard
              key={cohort.id}
              cohort={cohort}
              index={index}
              isExpanded={expandedCohort === cohort.id}
              onToggle={() => setExpandedCohort(expandedCohort === cohort.id ? null : cohort.id)}
            />
          ))}
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="py-10"
        >
          <EmptyState
            icon={Users}
            title="No cohorts yet"
            description="Create your first cohort to define your ideal customer profile."
            action={canCreateMore ? 'Create your first cohort' : undefined}
            onAction={canCreateMore ? () => setShowCreateModal(true) : undefined}
          />
        </motion.div>
      )}

      {/* Create Modal */}
      <CreateCohortModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateCohort}
        isLoading={isLoading}
      />
    </div>
  )
}

export default Cohorts
