import { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Target, Plus, Search, Filter, ArrowRight, CheckCircle2, Clock, AlertCircle } from 'lucide-react'
import { cn } from '../utils/cn'

const moves = [
  { id: 1, name: 'Launch Product Beta', status: 'on-track', progress: 75, dueDate: '2025-12-15' },
  { id: 2, name: 'Acquire 100 Customers', status: 'at-risk', progress: 45, dueDate: '2025-12-20' },
  { id: 3, name: 'Build ICP Database', status: 'on-track', progress: 90, dueDate: '2025-12-10' },
  { id: 4, name: 'Implement Analytics Dashboard', status: 'on-track', progress: 60, dueDate: '2025-12-25' },
  { id: 5, name: 'Weekly Review Process', status: 'completed', progress: 100, dueDate: '2025-12-05' },
]

export default function Moves() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')

  const filteredMoves = moves.filter(move => {
    const matchesSearch = move.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterStatus === 'all' || move.status === filterStatus
    return matchesSearch && matchesFilter
  })

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card flex flex-col gap-6 p-8 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <p className="micro-label mb-2">Runway Plays</p>
          <h1 className="font-serif text-4xl md:text-6xl text-black leading-[1.1] tracking-tight antialiased mb-2">
            Moves in Motion
          </h1>
          <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-neutral-400">
            Live capsules & edits
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/moves/war-room"
            className="inline-flex items-center gap-2 border border-neutral-900 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-900 hover:bg-neutral-900 hover:text-white transition-colors"
          >
            <Target className="w-4 h-4" />
            War Room
          </Link>
          <Link
            to="/moves/library"
            className="inline-flex items-center gap-2 border border-neutral-200 px-6 py-3 text-[10px] font-mono uppercase tracking-[0.3em] text-neutral-600 hover:border-neutral-900 hover:text-neutral-900 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Library
          </Link>
        </div>
      </motion.div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
          <input
            type="text"
            placeholder="Search moves..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full border-b-2 border-neutral-200 bg-transparent py-4 pl-12 pr-4 focus:outline-none focus:border-neutral-900 transition-all font-serif text-lg"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="appearance-none border-b-2 border-neutral-200 bg-transparent py-4 pl-12 pr-8 focus:outline-none focus:border-neutral-900 transition-all font-serif text-lg"
          >
            <option value="all">All Status</option>
            <option value="on-track">On Track</option>
            <option value="at-risk">At Risk</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      {/* Moves Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredMoves.map((move, index) => (
          <motion.div
            key={move.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
          >
            <Link
              to={`/moves/${move.id}`}
              className="block runway-card p-6 hover:shadow-xl transition-all group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-neutral-900 mb-2 group-hover:text-neutral-700 transition-colors">
                    {move.name}
                  </h3>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      "px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.2em] border",
                      move.status === 'on-track' 
                        ? "bg-green-50 text-green-900 border-green-200" 
                        : move.status === 'at-risk'
                        ? "bg-yellow-50 text-yellow-900 border-yellow-200"
                        : "bg-blue-50 text-blue-900 border-blue-200"
                    )}>
                      {move.status === 'on-track' ? 'On Track' : move.status === 'at-risk' ? 'At Risk' : 'Completed'}
                    </span>
                  </div>
                </div>
                <Target className="w-8 h-8 text-neutral-700" />
              </div>

              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-neutral-600">Progress</span>
                  <span className="text-lg font-bold text-neutral-900">{move.progress}%</span>
                </div>
                <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${move.progress}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                    className="h-full bg-gradient-to-r from-neutral-700 to-neutral-900 rounded-full"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-neutral-200">
                <div className="flex items-center gap-2 text-sm text-neutral-600">
                  <Clock className="w-4 h-4" />
                  {move.dueDate}
                </div>
                <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-neutral-900 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

