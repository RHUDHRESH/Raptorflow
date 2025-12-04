import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Grid3X3,
  Plus,
  Eye,
  Zap,
  ArrowRight,
  Calendar,
  Filter
} from 'lucide-react'

// Journey stages
const journeyStages = [
  'Unaware',
  'Problem Aware', 
  'Solution Aware',
  'Product Aware',
  'Most Aware'
]

// Sample moves mapped to journey stages and cohorts
const matrixData = {
  'Tech Founders': {
    'Unaware': [],
    'Problem Aware': [
      { id: 1, title: 'LinkedIn Series', status: 'active' },
    ],
    'Solution Aware': [
      { id: 2, title: 'Webinar', status: 'pending' },
      { id: 3, title: 'Email Nurture', status: 'active' },
    ],
    'Product Aware': [
      { id: 4, title: 'Product Demo', status: 'pending' },
    ],
    'Most Aware': [
      { id: 5, title: 'Case Study', status: 'completed' },
    ],
  },
  'Early Adopters': {
    'Unaware': [],
    'Problem Aware': [
      { id: 6, title: 'Twitter Growth', status: 'draft' },
    ],
    'Solution Aware': [],
    'Product Aware': [
      { id: 7, title: 'PH Launch', status: 'pending' },
    ],
    'Most Aware': [],
  },
  'SaaS Builders': {
    'Unaware': [
      { id: 8, title: 'Community Post', status: 'active' },
    ],
    'Problem Aware': [],
    'Solution Aware': [
      { id: 9, title: 'Partnership', status: 'pending' },
    ],
    'Product Aware': [],
    'Most Aware': [],
  },
}

const MoveCell = ({ moves, cohort, stage }) => {
  const [isHovered, setIsHovered] = useState(false)

  const statusColors = {
    active: 'bg-emerald-500',
    pending: 'bg-amber-500',
    completed: 'bg-white/30',
    draft: 'bg-zinc-500',
  }

  return (
    <div 
      className="min-h-[100px] p-2 border border-white/5 bg-zinc-900/30 hover:bg-zinc-900/50 transition-colors group relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {moves.length > 0 ? (
        <div className="space-y-1.5">
          {moves.map((move) => (
            <motion.div
              key={move.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-2 bg-zinc-800/50 border border-white/5 rounded-lg cursor-pointer hover:border-amber-500/30 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className={`w-1.5 h-1.5 rounded-full ${statusColors[move.status]}`} />
                <span className="text-xs text-white/80 truncate">{move.title}</span>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="h-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <button className="p-2 hover:bg-white/5 rounded-lg transition-colors">
            <Plus className="w-4 h-4 text-white/30" />
          </button>
        </div>
      )}

      {/* Hover add button */}
      {moves.length > 0 && isHovered && (
        <button className="absolute bottom-2 right-2 p-1 bg-amber-500/20 hover:bg-amber-500/30 rounded transition-colors">
          <Plus className="w-3 h-3 text-amber-400" />
        </button>
      )}
    </div>
  )
}

const Matrix = () => {
  const cohorts = Object.keys(matrixData)

  return (
    <div className="max-w-full mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-light text-white">Matrix</h1>
          <p className="text-white/40 mt-1">
            Map your moves across cohorts and journey stages
          </p>
        </motion.div>

        <div className="flex items-center gap-3">
          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-2 px-4 py-2 bg-zinc-900/50 border border-white/10 text-white/60 hover:text-white rounded-lg transition-colors"
          >
            <Filter className="w-4 h-4" />
            Filter
          </motion.button>
          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Move
          </motion.button>
        </div>
      </div>

      {/* Legend */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex items-center gap-6 mb-6 text-xs"
      >
        <span className="text-white/40">Status:</span>
        {[
          { label: 'Active', color: 'bg-emerald-500' },
          { label: 'Pending', color: 'bg-amber-500' },
          { label: 'Completed', color: 'bg-white/30' },
          { label: 'Draft', color: 'bg-zinc-500' },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${item.color}`} />
            <span className="text-white/60">{item.label}</span>
          </div>
        ))}
      </motion.div>

      {/* Matrix grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="border border-white/5 rounded-xl overflow-hidden"
      >
        {/* Header row - Journey stages */}
        <div className="grid" style={{ gridTemplateColumns: '180px repeat(5, 1fr)' }}>
          <div className="p-4 bg-zinc-900/50 border-b border-r border-white/5">
            <div className="flex items-center gap-2 text-white/40">
              <Grid3X3 className="w-4 h-4" />
              <span className="text-xs uppercase tracking-wider">Cohort / Stage</span>
            </div>
          </div>
          {journeyStages.map((stage, i) => (
            <div 
              key={stage} 
              className="p-4 bg-zinc-900/50 border-b border-r border-white/5 last:border-r-0"
            >
              <div className="flex items-center gap-2">
                <span className="text-xs text-amber-400 font-mono">{i + 1}</span>
                <span className="text-xs text-white/60 uppercase tracking-wider">{stage}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Data rows - Cohorts */}
        {cohorts.map((cohort) => (
          <div 
            key={cohort} 
            className="grid" 
            style={{ gridTemplateColumns: '180px repeat(5, 1fr)' }}
          >
            <div className="p-4 bg-zinc-900/30 border-b border-r border-white/5 flex items-center">
              <span className="text-sm text-white font-medium">{cohort}</span>
            </div>
            {journeyStages.map((stage) => (
              <MoveCell 
                key={`${cohort}-${stage}`}
                moves={matrixData[cohort][stage] || []}
                cohort={cohort}
                stage={stage}
              />
            ))}
          </div>
        ))}
      </motion.div>

      {/* Journey flow */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-8 p-6 bg-zinc-900/30 border border-white/5 rounded-xl"
      >
        <h3 className="text-white font-medium mb-4">Journey Flow</h3>
        <div className="flex items-center justify-between">
          {journeyStages.map((stage, i) => (
            <React.Fragment key={stage}>
              <div className="text-center">
                <div className={`w-12 h-12 mx-auto rounded-full flex items-center justify-center ${
                  i === 0 ? 'bg-zinc-700' :
                  i === journeyStages.length - 1 ? 'bg-emerald-500/20 border-2 border-emerald-500' :
                  'bg-amber-500/20'
                }`}>
                  <span className="text-sm font-medium text-white">{i + 1}</span>
                </div>
                <p className="text-xs text-white/40 mt-2 max-w-[80px]">{stage}</p>
              </div>
              {i < journeyStages.length - 1 && (
                <ArrowRight className="w-5 h-5 text-white/20" />
              )}
            </React.Fragment>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

export default Matrix

