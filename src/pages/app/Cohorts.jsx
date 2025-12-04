import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Users, 
  Plus, 
  MoreHorizontal,
  Target,
  TrendingUp,
  ChevronRight,
  User,
  Briefcase,
  AlertCircle,
  CheckCircle2,
  Search
} from 'lucide-react'

const journeyStages = [
  { id: 'unaware', label: 'Unaware', color: 'bg-zinc-500' },
  { id: 'problem', label: 'Problem Aware', color: 'bg-red-500' },
  { id: 'solution', label: 'Solution Aware', color: 'bg-amber-500' },
  { id: 'product', label: 'Product Aware', color: 'bg-emerald-500' },
  { id: 'most', label: 'Most Aware', color: 'bg-blue-500' },
]

const CohortCard = ({ cohort, delay }) => {
  const [expanded, setExpanded] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="group bg-zinc-900/50 border border-white/5 rounded-xl overflow-hidden hover:border-amber-500/30 transition-all"
    >
      <div 
        className="p-5 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 ${cohort.color} rounded-lg flex items-center justify-center`}>
              <cohort.icon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-white font-medium">{cohort.name}</h3>
              <p className="text-xs text-white/40">{cohort.size} contacts</p>
            </div>
          </div>
          <button className="opacity-0 group-hover:opacity-100 p-1 hover:bg-white/10 rounded transition-all">
            <MoreHorizontal className="w-4 h-4 text-white/40" />
          </button>
        </div>

        <p className="text-sm text-white/50 mb-4 line-clamp-2">{cohort.description}</p>

        {/* Journey distribution */}
        <div className="mb-4">
          <div className="flex items-center gap-1 h-2 rounded-full overflow-hidden">
            {cohort.journey.map((stage, i) => (
              <div
                key={i}
                className={`h-full ${journeyStages[i].color}`}
                style={{ width: `${stage}%` }}
              />
            ))}
          </div>
        </div>

        {/* Quick stats */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-4">
            <span className="text-white/40">
              <Target className="w-3.5 h-3.5 inline mr-1" />
              {cohort.activeMovies} active moves
            </span>
          </div>
          <ChevronRight className={`w-4 h-4 text-white/20 transition-transform ${expanded ? 'rotate-90' : ''}`} />
        </div>
      </div>

      {/* Expanded content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-white/5"
          >
            <div className="p-5 space-y-4">
              {/* Journey breakdown */}
              <div>
                <h4 className="text-xs text-white/40 uppercase tracking-wider mb-3">Journey Distribution</h4>
                <div className="grid grid-cols-5 gap-2">
                  {journeyStages.map((stage, i) => (
                    <div key={stage.id} className="text-center">
                      <div className={`w-full h-1 ${stage.color} rounded mb-1`} />
                      <p className="text-lg font-light text-white">{cohort.journey[i]}%</p>
                      <p className="text-[10px] text-white/40">{stage.label}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Key triggers */}
              <div>
                <h4 className="text-xs text-white/40 uppercase tracking-wider mb-2">Key Triggers</h4>
                <div className="flex flex-wrap gap-2">
                  {cohort.triggers.map((trigger, i) => (
                    <span key={i} className="px-2 py-1 bg-white/5 rounded text-xs text-white/60">
                      {trigger}
                    </span>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 pt-2">
                <button className="flex-1 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-sm text-white/60 transition-colors">
                  Edit Cohort
                </button>
                <button className="flex-1 py-2 bg-amber-500/20 hover:bg-amber-500/30 rounded-lg text-sm text-amber-400 transition-colors">
                  Create Move
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

const Cohorts = () => {
  const [searchQuery, setSearchQuery] = useState('')

  const cohorts = [
    {
      id: 1,
      name: 'Tech Founders',
      description: 'Early-stage tech founders building B2B SaaS, looking for product-market fit',
      size: '2,340',
      icon: Briefcase,
      color: 'bg-amber-500/20',
      journey: [10, 25, 35, 20, 10],
      activeMovies: 5,
      triggers: ['Just raised funding', 'Launching soon', 'Pivoting', 'Scaling challenges'],
    },
    {
      id: 2,
      name: 'Early Adopters',
      description: 'Innovation-seekers who try new tools first and spread the word',
      size: '890',
      icon: TrendingUp,
      color: 'bg-emerald-500/20',
      journey: [5, 15, 30, 35, 15],
      activeMovies: 3,
      triggers: ['Product Hunt launch', 'New feature release', 'Competitor switch'],
    },
    {
      id: 3,
      name: 'SaaS Builders',
      description: 'Developers and technical founders building subscription businesses',
      size: '1,567',
      icon: User,
      color: 'bg-violet-500/20',
      journey: [20, 30, 25, 15, 10],
      activeMovies: 4,
      triggers: ['MRR milestone', 'Churn spike', 'Feature requests', 'Pricing changes'],
    },
    {
      id: 4,
      name: 'Growth Teams',
      description: 'Marketing and growth professionals at scaling startups',
      size: '456',
      icon: Target,
      color: 'bg-blue-500/20',
      journey: [15, 25, 30, 20, 10],
      activeMovies: 2,
      triggers: ['New quarter goals', 'Budget approval', 'Team expansion'],
    },
  ]

  const filteredCohorts = cohorts.filter(cohort =>
    cohort.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    cohort.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-light text-white">Cohorts</h1>
          <p className="text-white/40 mt-1">
            Understand and segment your target audiences
          </p>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Cohort
        </motion.button>
      </div>

      {/* Search */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="relative mb-6"
      >
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
        <input
          type="text"
          placeholder="Search cohorts..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-12 pr-4 py-3 bg-zinc-900/50 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:border-amber-500/50 focus:outline-none transition-colors"
        />
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="grid grid-cols-4 gap-4 mb-8"
      >
        {[
          { label: 'Total Cohorts', value: cohorts.length },
          { label: 'Total Contacts', value: '5.3K' },
          { label: 'Active Moves', value: '14' },
          { label: 'Avg Journey Score', value: '67%' },
        ].map((stat, i) => (
          <div key={i} className="bg-zinc-900/30 border border-white/5 rounded-lg p-4 text-center">
            <p className="text-2xl font-light text-white">{stat.value}</p>
            <p className="text-xs text-white/40 mt-1">{stat.label}</p>
          </div>
        ))}
      </motion.div>

      {/* Journey legend */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex items-center gap-6 mb-6 text-xs"
      >
        <span className="text-white/40">Journey stages:</span>
        {journeyStages.map((stage) => (
          <div key={stage.id} className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${stage.color}`} />
            <span className="text-white/60">{stage.label}</span>
          </div>
        ))}
      </motion.div>

      {/* Cohorts grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredCohorts.map((cohort, index) => (
          <CohortCard key={cohort.id} cohort={cohort} delay={0.25 + index * 0.05} />
        ))}
      </div>

      {filteredCohorts.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16"
        >
          <Users className="w-12 h-12 text-white/20 mx-auto mb-4" />
          <p className="text-white/40">No cohorts found</p>
        </motion.div>
      )}
    </div>
  )
}

export default Cohorts

