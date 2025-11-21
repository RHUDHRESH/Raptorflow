import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileText, Calendar, Filter, Search, ArrowRight } from 'lucide-react'
import { cn } from '../utils/cn'

const historyItems = [
  {
    id: 1,
    type: 'move',
    action: 'Completed',
    title: 'Launch Product Beta',
    date: '2025-12-10',
    details: 'Move completed successfully',
  },
  {
    id: 2,
    type: 'review',
    action: 'Weekly Review',
    title: 'Q4 Week 2 Review',
    date: '2025-12-08',
    details: '3 moves scaled, 1 tweaked',
  },
  {
    id: 3,
    type: 'strategy',
    action: 'Updated',
    title: 'Strategy Refresh',
    date: '2025-12-05',
    details: 'Strategy wizard completed',
  },
  {
    id: 4,
    type: 'icp',
    action: 'Created',
    title: 'Enterprise SaaS CTOs',
    date: '2025-12-03',
    details: 'New ICP profile added',
  },
]

export default function History() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState('all')

  const filteredItems = historyItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterType === 'all' || item.type === filterType
    return matchesSearch && matchesFilter
  })

  const getTypeColor = (type) => {
    switch (type) {
      case 'move': return 'bg-neutral-100 text-neutral-900'
      case 'review': return 'bg-neutral-100 text-neutral-900'
      case 'strategy': return 'bg-green-100 text-green-700'
      case 'icp': return 'bg-blue-100 text-blue-700'
      default: return 'bg-neutral-100 text-neutral-700'
    }
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10 text-neutral-900"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white" />
        <div className="relative z-10 flex items-center gap-4">
          <div className="w-16 h-16 rounded-full border border-neutral-200 bg-white flex items-center justify-center">
            <FileText className="w-8 h-8 text-neutral-900" />
          </div>
          <div>
            <p className="micro-label">Archive Ledger</p>
            <h1 className="text-4xl font-display">Document the Runs</h1>
            <p className="text-sm uppercase tracking-[0.3em] text-neutral-500">
              Every move logged like a runway note
            </p>
          </div>
        </div>
      </motion.div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
          <input
            type="text"
            placeholder="Search history..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="pl-12 pr-8 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 appearance-none"
          >
            <option value="all">All Types</option>
            <option value="move">Moves</option>
            <option value="review">Reviews</option>
            <option value="strategy">Strategy</option>
            <option value="icp">ICPs</option>
          </select>
        </div>
      </div>

      {/* History Timeline */}
      <div className="runway-card p-8">
        <div className="space-y-6">
          {filteredItems.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex gap-6 pb-6 border-b border-neutral-200 last:border-0 last:pb-0"
            >
              <div className="flex flex-col items-center">
                <div className={cn(
                  "w-12 h-12 rounded-xl flex items-center justify-center mb-2",
                  getTypeColor(item.type)
                )}>
                  <Calendar className="w-6 h-6" />
                </div>
                <div className="w-0.5 h-full bg-neutral-200" />
              </div>
              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className={cn(
                        "px-2 py-1 text-xs font-medium rounded-lg",
                        getTypeColor(item.type)
                      )}>
                        {item.type}
                      </span>
                      <span className="text-sm font-medium text-neutral-600">{item.action}</span>
                    </div>
                    <h3 className="text-lg font-bold text-neutral-900 mb-1">{item.title}</h3>
                    <p className="text-sm text-neutral-600">{item.details}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-neutral-900">{item.date}</div>
                    <div className="text-xs text-neutral-500">2 days ago</div>
                  </div>
                </div>
                <button className="flex items-center gap-2 text-sm text-neutral-900 hover:text-neutral-800 font-medium mt-2">
                  View Details
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}

