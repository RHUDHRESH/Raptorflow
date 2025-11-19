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
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-display font-bold mb-2">Moves</h1>
          <p className="text-neutral-600">Track and manage your strategic moves</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors shadow-lg shadow-primary-600/20"
        >
          <Plus className="w-5 h-5" />
          New Move
        </motion.button>
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
            className="w-full pl-12 pr-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="pl-12 pr-8 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500 appearance-none"
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
              className="block glass rounded-2xl p-6 hover:shadow-xl transition-all group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-neutral-900 mb-2 group-hover:text-primary-600 transition-colors">
                    {move.name}
                  </h3>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      "px-2 py-1 text-xs font-medium rounded-lg",
                      move.status === 'on-track' 
                        ? "bg-green-100 text-green-700" 
                        : move.status === 'at-risk'
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-blue-100 text-blue-700"
                    )}>
                      {move.status === 'on-track' ? 'On Track' : move.status === 'at-risk' ? 'At Risk' : 'Completed'}
                    </span>
                  </div>
                </div>
                <Target className="w-8 h-8 text-primary-500" />
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
                    className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-neutral-200">
                <div className="flex items-center gap-2 text-sm text-neutral-600">
                  <Clock className="w-4 h-4" />
                  {move.dueDate}
                </div>
                <ArrowRight className="w-5 h-5 text-neutral-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all" />
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

