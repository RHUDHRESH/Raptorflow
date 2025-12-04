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
            <span className="text-white/60 truncate max-w-[120px]">{cohort.label}</span>
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
            {data.employee_range && (
              <div>
                <span className="text-xs text-white/40">Company Size</span>
                <p className="text-white">{data.employee_range}</p>
              </div>
            )}
            {data.revenue_range && (
              <div>
                <span className="text-xs text-white/40">Revenue</span>
                <p className="text-white">{data.revenue_range}</p>
              </div>
            )}
            {data.industries?.length > 0 && (
              <div className="col-span-2">
                <span className="text-xs text-white/40">Industries</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.industries.map((ind, i) => (
                    <span key={i} className="px-2 py-0.5 bg-white/5 rounded text-xs text-white/60">
                      {ind}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.stages?.length > 0 && (
              <div className="col-span-2">
                <span className="text-xs text-white/40">Stages</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.stages.map((stage, i) => (
                    <span key={i} className="px-2 py-0.5 bg-amber-500/10 rounded text-xs text-amber-300">
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
                <span className="text-xs text-emerald-400/60 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Must Have
                </span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.must_have.map((tech, i) => (
                    <span key={i} className="px-2 py-0.5 bg-emerald-500/10 rounded text-xs text-emerald-300">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.nice_to_have?.length > 0 && (
              <div>
                <span className="text-xs text-blue-400/60">Nice to Have</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.nice_to_have.map((tech, i) => (
                    <span key={i} className="px-2 py-0.5 bg-blue-500/10 rounded text-xs text-blue-300">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.red_flags?.length > 0 && (
              <div>
                <span className="text-xs text-red-400/60 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> Red Flags
                </span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {data.red_flags.map((flag, i) => (
                    <span key={i} className="px-2 py-0.5 bg-red-500/10 rounded text-xs text-red-300">
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
                <span className="text-xs text-white/40">Pain Points</span>
                <ul className="mt-2 space-y-1">
                  {data.pain_points.map((pain, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-white/60">
                      <span className="text-red-400 mt-1">•</span> {pain}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {data.motivations?.length > 0 && (
              <div>
                <span className="text-xs text-white/40">Motivations</span>
                <ul className="mt-2 space-y-1">
                  {data.motivations.map((mot, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-white/60">
                      <span className="text-emerald-400 mt-1">•</span> {mot}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )

      case 'behavioral':
        if (!Array.isArray(data) || data.length === 0) {
          return <p className="text-white/30 text-sm">No behavioral triggers defined</p>
        }
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
          return <p className="text-white/30 text-sm">No buying committee defined</p>
        }
        return (
          <div className="space-y-4">
            {data.map((person, i) => (
              <div key={i} className="p-4 bg-white/5 rounded-lg border border-white/5">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-8 bg-white/10 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white/60" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{person.role}</p>
                    <p className="text-xs text-white/40">{person.typical_title}</p>
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
                <span className="text-xs text-white/40">Market Position</span>
                <p className="text-white capitalize">{data.market_position}</p>
              </div>
            )}
            {data.current_solution && (
              <div>
                <span className="text-xs text-white/40">Current Solution</span>
                <p className="text-white text-sm">{data.current_solution}</p>
              </div>
            )}
            {data.switching_triggers?.length > 0 && (
              <div>
                <span className="text-xs text-white/40">Switching Triggers</span>
                <div className="flex flex-wrap gap-2 mt-2">
                  {data.switching_triggers.map((trig, i) => (
                    <span key={i} className="px-3 py-1.5 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-300">
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
            <h4 className="text-white font-medium">{COHORT_DIMENSIONS[dimension]?.label}</h4>
            <p className="text-xs text-white/40">{COHORT_DIMENSIONS[dimension]?.description}</p>
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

// Full Cohort Card
const FullCohortCard = ({ cohort, index, isExpanded, onToggle }) => {
  const colors = ['amber', 'blue', 'purple', 'emerald', 'pink']
  const baseColor = colors[index % colors.length]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`
        bg-zinc-900/50 border rounded-2xl overflow-hidden transition-all
        ${cohort.selected ? 'border-amber-500/30' : 'border-white/5'}
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
              <span className="text-2xl font-light text-white">{cohort.fit_score}</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xl font-medium text-white">{cohort.label}</h3>
                {cohort.selected && (
                  <span className="px-2 py-0.5 bg-emerald-500/20 rounded text-xs text-emerald-400">
                    Active
                  </span>
                )}
              </div>
              <p className="text-sm text-white/40 mt-1">{cohort.summary}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <Radio className="w-4 h-4 text-white/40" />
            </button>
            <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <Tags className="w-4 h-4 text-white/40" />
            </button>
            <ChevronDown className={`w-5 h-5 text-white/40 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
          </div>
        </div>

        {/* Quick stats */}
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-amber-400/60" />
            <span className="text-white/60">Fit: {cohort.fit_score}%</span>
          </div>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400/60" />
            <span className="text-white/60">
              {cohort.behavioral_triggers?.length || 0} triggers
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-400/60" />
            <span className="text-white/60">
              {cohort.buying_committee?.length || 0} personas
            </span>
          </div>
          {cohort.tags?.length > 0 && (
            <div className="flex items-center gap-2">
              <Tags className="w-4 h-4 text-purple-400/60" />
              <span className="text-white/60">
                {cohort.tags.length} tags
              </span>
            </div>
          )}
        </div>

        {/* Messaging angle */}
        {cohort.messaging_angle && (
          <div className="mt-4 p-3 bg-white/5 rounded-lg">
            <span className="text-xs text-white/40">Messaging Angle</span>
            <p className="text-white mt-1 italic">"{cohort.messaging_angle}"</p>
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
            className="border-t border-white/5"
          >
            <div className="p-6 space-y-4">
              {/* Fit reasoning */}
              {cohort.fit_reasoning && (
                <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                  <span className="text-xs text-emerald-400 font-medium">Fit Reasoning</span>
                  <p className="text-white/80 mt-1">{cohort.fit_reasoning}</p>
                </div>
              )}

              {/* Tags */}
              {cohort.tags?.length > 0 && (
                <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-xl">
                  <span className="text-xs text-purple-400 font-medium flex items-center gap-2">
                    <Tags className="w-4 h-4" />
                    Tags of Interest ({cohort.tags.length})
                  </span>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {cohort.tags.slice(0, 20).map((tag, i) => (
                      <span key={i} className="px-2 py-1 bg-purple-500/20 rounded-lg text-xs text-purple-300">
                        {tag}
                      </span>
                    ))}
                    {cohort.tags.length > 20 && (
                      <span className="px-2 py-1 bg-white/5 rounded-lg text-xs text-white/40">
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
              <div className="flex items-center gap-3 pt-4 border-t border-white/5">
                <button className="flex-1 py-3 bg-white/5 hover:bg-white/10 rounded-xl text-sm text-white/60 transition-colors flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Export Profile
                </button>
                <button className="flex-1 py-3 bg-purple-500/20 hover:bg-purple-500/30 rounded-xl text-sm text-purple-400 transition-colors flex items-center justify-center gap-2">
                  <Radio className="w-4 h-4" />
                  Open in Radar
                </button>
                <button className="flex-1 py-3 bg-amber-500/20 hover:bg-amber-500/30 rounded-xl text-sm text-amber-400 transition-colors flex items-center justify-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Create Campaign
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

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-zinc-900 border border-white/10 rounded-2xl max-w-lg w-full p-6"
      >
        <h2 className="text-xl font-medium text-white mb-4">Create New Cohort</h2>
        <p className="text-white/40 text-sm mb-6">
          Define your ideal customer profile. AI will generate the full 6D profile and 50 tags of interest.
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-white/60 mb-2">Cohort Name *</label>
            <input
              type="text"
              value={formData.label}
              onChange={(e) => setFormData({ ...formData, label: e.target.value })}
              placeholder="e.g., Growth-Stage SaaS Founders"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:border-amber-500/50 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm text-white/60 mb-2">Description *</label>
            <textarea
              value={formData.summary}
              onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
              placeholder="Describe this cohort in detail. The more specific, the better the AI can generate tags and insights."
              rows={4}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:border-amber-500/50 focus:outline-none resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-white/60 mb-2">Company Size</label>
              <select
                value={formData.employee_range}
                onChange={(e) => setFormData({ ...formData, employee_range: e.target.value })}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-amber-500/50 focus:outline-none"
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
              <label className="block text-sm text-white/60 mb-2">Revenue Range</label>
              <select
                value={formData.revenue_range}
                onChange={(e) => setFormData({ ...formData, revenue_range: e.target.value })}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white focus:border-amber-500/50 focus:outline-none"
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
            <label className="block text-sm text-white/60 mb-2">Industries (comma separated)</label>
            <input
              type="text"
              value={formData.industries}
              onChange={(e) => setFormData({ ...formData, industries: e.target.value })}
              placeholder="e.g., SaaS, Fintech, E-commerce"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:border-amber-500/50 focus:outline-none"
            />
          </div>
        </div>

        <div className="flex items-center gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 py-3 bg-white/5 hover:bg-white/10 rounded-xl text-white/60 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onSubmit(formData)}
            disabled={isLoading || !formData.label || !formData.summary}
            className="flex-1 py-3 bg-amber-500 hover:bg-amber-400 rounded-xl text-black font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Create Cohort
              </>
            )}
          </button>
        </div>
      </motion.div>
    </div>
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
          <h1 className="text-3xl font-light text-white">Cohorts</h1>
          <p className="text-white/40 mt-1">
            6-Dimensional Ideal Customer Profiles
          </p>
        </motion.div>

        <div className="flex items-center gap-3">
          {/* Plan info */}
          <div className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg">
            <span className="text-xs text-white/40">
              {cohorts.length} / {cohortLimit} cohorts
            </span>
          </div>

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
            onClick={() => canCreateMore ? setShowCreateModal(true) : null}
            disabled={!canCreateMore}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-colors ${
              canCreateMore 
                ? 'bg-amber-500 hover:bg-amber-400 text-black' 
                : 'bg-white/5 text-white/30 cursor-not-allowed'
            }`}
          >
            {canCreateMore ? (
              <>
                <Plus className="w-4 h-4" />
                Create Cohort
              </>
            ) : (
              <>
                <Lock className="w-4 h-4" />
                Limit Reached
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
          className="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center gap-3"
        >
          <Lock className="w-5 h-5 text-amber-400" />
          <div className="flex-1">
            <p className="text-amber-400 font-medium">Cohort limit reached</p>
            <p className="text-amber-400/60 text-sm">
              Your {planName} plan allows up to {cohortLimit} cohorts. Upgrade to create more.
            </p>
          </div>
          <button className="px-4 py-2 bg-amber-500 text-black rounded-lg text-sm font-medium">
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
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
          <input
            type="text"
            placeholder="Search cohorts..."
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
      )}

      {/* Graph View */}
      {view === 'graph' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h3 className="text-sm text-white/40 mb-4">Cohort Positioning Map</h3>
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
          className="text-center py-20 bg-zinc-900/30 border border-white/5 rounded-2xl"
        >
          <Users className="w-16 h-16 text-white/10 mx-auto mb-4" />
          <h3 className="text-xl text-white mb-2">No cohorts yet</h3>
          <p className="text-white/40 mb-6 max-w-md mx-auto">
            Create your first cohort to define your ideal customer profile. 
            AI will generate 50 tags of interest for Radar matching.
          </p>
          {canCreateMore && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-xl transition-colors inline-flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Create Your First Cohort
            </button>
          )}
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
