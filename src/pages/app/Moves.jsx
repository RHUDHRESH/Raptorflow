import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Plus, 
  Filter, 
  Search,
  MoreHorizontal,
  Clock,
  CheckCircle2,
  Circle,
  ArrowRight,
  Calendar,
  Users,
  Zap
} from 'lucide-react'

const statusColors = {
  active: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', dot: 'bg-emerald-400' },
  pending: { bg: 'bg-amber-500/10', text: 'text-amber-400', dot: 'bg-amber-400' },
  completed: { bg: 'bg-white/5', text: 'text-white/40', dot: 'bg-white/40' },
  draft: { bg: 'bg-zinc-500/10', text: 'text-zinc-400', dot: 'bg-zinc-400' },
}

const MoveCard = ({ move, delay }) => {
  const status = statusColors[move.status]
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="group bg-zinc-900/50 border border-white/5 rounded-xl p-5 hover:border-amber-500/30 transition-all cursor-pointer"
    >
      <div className="flex items-start justify-between mb-4">
        <span className={`px-2 py-1 rounded text-xs font-medium ${status.bg} ${status.text}`}>
          {move.status}
        </span>
        <button className="opacity-0 group-hover:opacity-100 p-1 hover:bg-white/10 rounded transition-all">
          <MoreHorizontal className="w-4 h-4 text-white/40" />
        </button>
      </div>
      
      <h3 className="text-white font-medium mb-2">{move.title}</h3>
      <p className="text-sm text-white/40 line-clamp-2 mb-4">{move.description}</p>
      
      <div className="flex items-center gap-4 text-xs text-white/40">
        <div className="flex items-center gap-1">
          <Calendar className="w-3.5 h-3.5" />
          <span>{move.date}</span>
        </div>
        <div className="flex items-center gap-1">
          <Users className="w-3.5 h-3.5" />
          <span>{move.cohort}</span>
        </div>
      </div>

      {/* Progress bar for active moves */}
      {move.status === 'active' && move.progress && (
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-white/40">Progress</span>
            <span className="text-amber-400">{move.progress}%</span>
          </div>
          <div className="h-1 bg-white/10 rounded-full overflow-hidden">
            <div 
              className="h-full bg-amber-500 rounded-full"
              style={{ width: `${move.progress}%` }}
            />
          </div>
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs text-white/30">{move.campaign}</span>
        </div>
        <ArrowRight className="w-4 h-4 text-white/20 group-hover:text-amber-400 transition-colors" />
      </div>
    </motion.div>
  )
}

const Moves = () => {
  const [filter, setFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  const moves = [
    {
      id: 1,
      title: 'LinkedIn Thought Leadership Series',
      description: 'Publish 3 posts on strategic positioning and founder journey to build authority.',
      status: 'active',
      date: 'Dec 4 - Dec 18',
      cohort: 'Tech Founders',
      campaign: 'Q1 Awareness',
      progress: 45,
    },
    {
      id: 2,
      title: 'Product Hunt Launch',
      description: 'Coordinate full PH launch with community support, hunter outreach, and social amplification.',
      status: 'pending',
      date: 'Dec 20',
      cohort: 'Early Adopters',
      campaign: 'Launch Campaign',
    },
    {
      id: 3,
      title: 'Email Nurture Sequence',
      description: 'Set up 5-email sequence for new signups moving from Problem Aware to Solution Aware.',
      status: 'active',
      date: 'Dec 1 - Dec 30',
      cohort: 'Newsletter Subs',
      campaign: 'Q1 Awareness',
      progress: 80,
    },
    {
      id: 4,
      title: 'Twitter/X Growth Sprint',
      description: 'Daily posting + engagement strategy to grow founder following.',
      status: 'draft',
      date: 'Jan 2024',
      cohort: 'SaaS Builders',
      campaign: 'Growth',
    },
    {
      id: 5,
      title: 'Case Study: Early Customer',
      description: 'Document success story from beta user for social proof.',
      status: 'completed',
      date: 'Nov 15 - Nov 30',
      cohort: 'Prospects',
      campaign: 'Social Proof',
    },
    {
      id: 6,
      title: 'Partnership Outreach',
      description: 'Reach out to 10 complementary tools for co-marketing opportunities.',
      status: 'pending',
      date: 'Dec 15',
      cohort: 'Partners',
      campaign: 'Partnerships',
    },
  ]

  const filteredMoves = moves.filter(move => {
    if (filter !== 'all' && move.status !== filter) return false
    if (searchQuery && !move.title.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })

  const filterOptions = [
    { value: 'all', label: 'All Moves' },
    { value: 'active', label: 'Active' },
    { value: 'pending', label: 'Pending' },
    { value: 'completed', label: 'Completed' },
    { value: 'draft', label: 'Drafts' },
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-light text-white">Moves</h1>
          <p className="text-white/40 mt-1">
            Tactical sprints that drive your strategy forward
          </p>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Move
        </motion.button>
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-6"
      >
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
          <input
            type="text"
            placeholder="Search moves..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-zinc-900/50 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-amber-500/50 focus:outline-none transition-colors"
          />
        </div>

        {/* Filter tabs */}
        <div className="flex items-center gap-1 p-1 bg-zinc-900/50 rounded-lg border border-white/5">
          {filterOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setFilter(option.value)}
              className={`px-3 py-1.5 rounded-md text-sm transition-all ${
                filter === option.value
                  ? 'bg-white/10 text-white'
                  : 'text-white/40 hover:text-white/60'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Stats bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="grid grid-cols-4 gap-4 mb-8"
      >
        {[
          { label: 'Total', value: moves.length, icon: Zap },
          { label: 'Active', value: moves.filter(m => m.status === 'active').length, color: 'text-emerald-400' },
          { label: 'Pending', value: moves.filter(m => m.status === 'pending').length, color: 'text-amber-400' },
          { label: 'Completed', value: moves.filter(m => m.status === 'completed').length, color: 'text-white/40' },
        ].map((stat, i) => (
          <div key={i} className="bg-zinc-900/30 border border-white/5 rounded-lg p-4">
            <p className={`text-2xl font-light ${stat.color || 'text-white'}`}>{stat.value}</p>
            <p className="text-xs text-white/40 mt-1">{stat.label}</p>
          </div>
        ))}
      </motion.div>

      {/* Moves grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <AnimatePresence mode="popLayout">
          {filteredMoves.map((move, index) => (
            <MoveCard key={move.id} move={move} delay={0.2 + index * 0.05} />
          ))}
        </AnimatePresence>
      </div>

      {filteredMoves.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16"
        >
          <p className="text-white/40">No moves found</p>
        </motion.div>
      )}
    </div>
  )
}

export default Moves

