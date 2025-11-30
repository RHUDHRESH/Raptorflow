import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileText, Calendar, Filter, Search, ArrowRight, CheckCircle2, Clock } from 'lucide-react'
import { cn } from '../utils/cn'
import {
  HeroSection,
  LuxeCard,
  LuxeBadge,
  FilterPills,
  EmptyState,
  staggerContainer,
  fadeInUp
} from '../components/ui/PremiumUI'

const historyItems = [
  {
    id: 1,
    type: 'move',
    action: 'Completed',
    title: 'Launch Product Beta',
    date: '2025-12-10',
    details: 'Move completed successfully',
    daysAgo: 2,
  },
  {
    id: 2,
    type: 'review',
    action: 'Weekly Review',
    title: 'Q4 Week 2 Review',
    date: '2025-12-08',
    details: '3 moves scaled, 1 tweaked',
    daysAgo: 4,
  },
  {
    id: 3,
    type: 'strategy',
    action: 'Updated',
    title: 'Strategy Refresh',
    date: '2025-12-05',
    details: 'Strategy wizard completed',
    daysAgo: 7,
  },
  {
    id: 4,
    type: 'icp',
    action: 'Created',
    title: 'Enterprise SaaS CTOs',
    date: '2025-12-03',
    details: 'New ICP profile added',
    daysAgo: 9,
  },
]

const filterOptions = [
  { label: 'All Types', value: 'all' },
  { label: 'Moves', value: 'move' },
  { label: 'Reviews', value: 'review' },
  { label: 'Strategy', value: 'strategy' },
  { label: 'ICPs', value: 'icp' },
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
      case 'move': return 'neutral'
      case 'review': return 'info'
      case 'strategy': return 'success'
      case 'icp': return 'warning'
      default: return 'neutral'
    }
  }

  return (
    <motion.div
      className="max-w-[1440px] mx-auto px-6 py-8 space-y-8"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={staggerContainer}
    >
      {/* Hero */}
      <motion.div variants={fadeInUp}>
        <HeroSection
          title="Activity History"
          subtitle="Track all your moves, reviews, and strategic updates in one place."
          metrics={[
            { label: 'Total Activities', value: historyItems.length.toString() },
            { label: 'This Month', value: '12' },
            { label: 'Last Activity', value: `${historyItems[0]?.daysAgo}d ago` }
          ]}
        />
      </motion.div>

      {/* Filters */}
      <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
          <input
            type="text"
            placeholder="Search history..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-1 focus:ring-neutral-900 transition-all"
          />
        </div>
        <FilterPills
          filters={filterOptions}
          activeFilter={filterType}
          onChange={setFilterType}
        />
      </motion.div>

      {/* History Timeline */}
      <motion.div variants={fadeInUp}>
        <LuxeCard className="p-8">
          {filteredItems.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No activities found"
              description="Try adjusting your search or filters."
            />
          ) : (
            <div className="space-y-6">
              {filteredItems.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex gap-6 pb-6 border-b border-neutral-200 last:border-0 last:pb-0 group"
                >
                  <div className="flex flex-col items-center shrink-0">
                    <div className="w-12 h-12 rounded-xl bg-neutral-100 flex items-center justify-center mb-2 group-hover:bg-neutral-900 group-hover:text-white transition-colors">
                      <Calendar className="w-6 h-6" />
                    </div>
                    {index < filteredItems.length - 1 && (
                      <div className="w-0.5 flex-1 bg-neutral-200 mt-2" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <LuxeBadge variant={getTypeColor(item.type)} className="capitalize">
                            {item.type}
                          </LuxeBadge>
                          <span className="text-sm font-medium text-neutral-600">{item.action}</span>
                        </div>
                        <h3 className="text-lg font-medium text-neutral-900 mb-1">{item.title}</h3>
                        <p className="text-sm text-neutral-600">{item.details}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="text-sm font-medium text-neutral-900">{item.date}</div>
                        <div className="text-xs text-neutral-500">{item.daysAgo} days ago</div>
                      </div>
                    </div>
                    <button className="flex items-center gap-2 text-sm text-neutral-600 hover:text-neutral-900 font-medium mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                      View Details
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </LuxeCard>
      </motion.div>
    </motion.div>
  )
}
