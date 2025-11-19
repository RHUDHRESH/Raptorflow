import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Calendar, Target, CheckCircle2, Link2, TrendingUp, Plus, X } from 'lucide-react'
import { cn } from '../utils/cn'

const tabs = [
  { id: 'daily', label: 'Daily Logging', icon: Calendar },
  { id: 'review', label: 'Weekly Review', icon: TrendingUp },
  { id: 'assets', label: 'Linked Assets', icon: Link2 },
]

const mockMove = {
  id: 1,
  name: 'Launch Product Beta',
  description: 'Launch the beta version of our product to 100 early adopters',
  status: 'on-track',
  progress: 75,
  dueDate: '2025-12-15',
  dailyLogs: [
    { date: '2025-12-10', entry: 'Completed user authentication system', mood: 'good' },
    { date: '2025-12-09', entry: 'Fixed critical bug in payment processing', mood: 'neutral' },
    { date: '2025-12-08', entry: 'Started work on dashboard UI', mood: 'good' },
  ],
  weeklyReview: {
    decision: null,
    metrics: {
      completion: 75,
      velocity: 8.5,
      blockers: 2,
    },
    notes: '',
  },
  linkedAssets: [
    { id: 1, name: 'Product Roadmap', type: 'document', url: '#' },
    { id: 2, name: 'Beta Testers List', type: 'spreadsheet', url: '#' },
    { id: 3, name: 'Design Mockups', type: 'design', url: '#' },
  ],
}

export default function MoveDetail() {
  const { id } = useParams()
  const [activeTab, setActiveTab] = useState('daily')
  const [newLogEntry, setNewLogEntry] = useState('')
  const [showAddAsset, setShowAddAsset] = useState(false)

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/moves"
          className="p-2 rounded-lg hover:bg-neutral-100 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-4xl font-display font-bold mb-2">{mockMove.name}</h1>
          <p className="text-neutral-600">{mockMove.description}</p>
        </div>
        <div className="text-right">
          <div className="text-sm text-neutral-600 mb-1">Due Date</div>
          <div className="text-lg font-semibold">{mockMove.dueDate}</div>
        </div>
      </div>

      {/* Progress Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-8"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900 mb-2">Progress</h2>
            <div className="text-4xl font-bold text-primary-600">{mockMove.progress}%</div>
          </div>
          <div className={cn(
            "px-4 py-2 rounded-xl font-medium",
            mockMove.status === 'on-track' 
              ? "bg-green-100 text-green-700" 
              : "bg-yellow-100 text-yellow-700"
          )}>
            {mockMove.status === 'on-track' ? 'On Track' : 'At Risk'}
          </div>
        </div>
        <div className="w-full h-3 bg-neutral-200 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${mockMove.progress}%` }}
            transition={{ duration: 1 }}
            className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full"
          />
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="glass rounded-2xl overflow-hidden">
        <div className="border-b border-neutral-200">
          <div className="flex">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "flex-1 flex items-center justify-center gap-2 px-6 py-4 font-medium transition-colors relative",
                    isActive
                      ? "text-primary-600"
                      : "text-neutral-600 hover:text-neutral-900"
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
                    />
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-8">
          <AnimatePresence mode="wait">
            {activeTab === 'daily' && (
              <motion.div
                key="daily"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold">Daily Logs</h3>
                  <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
                    <Plus className="w-4 h-4" />
                    Add Entry
                  </button>
                </div>
                <div className="space-y-4">
                  {mockMove.dailyLogs.map((log, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="p-4 rounded-xl border border-neutral-200 hover:bg-neutral-50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-neutral-400" />
                          <span className="text-sm font-medium text-neutral-900">{log.date}</span>
                        </div>
                        <div className={cn(
                          "w-2 h-2 rounded-full",
                          log.mood === 'good' ? "bg-green-500" : "bg-yellow-500"
                        )} />
                      </div>
                      <p className="text-neutral-700">{log.entry}</p>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'review' && (
              <motion.div
                key="review"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <h3 className="text-xl font-bold mb-6">Weekly Review</h3>
                
                {/* Metrics */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  {Object.entries(mockMove.weeklyReview.metrics).map(([key, value]) => (
                    <div key={key} className="p-4 rounded-xl bg-neutral-50">
                      <div className="text-sm text-neutral-600 mb-1 capitalize">{key}</div>
                      <div className="text-2xl font-bold text-neutral-900">{value}</div>
                    </div>
                  ))}
                </div>

                {/* Decision */}
                <div>
                  <h4 className="text-lg font-semibold mb-4">Decision</h4>
                  <div className="grid grid-cols-3 gap-4">
                    {['Scale', 'Tweak', 'Kill'].map((decision) => (
                      <motion.button
                        key={decision}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={cn(
                          "p-6 rounded-xl border-2 font-semibold transition-all",
                          decision === 'Scale' 
                            ? "border-green-500 bg-green-50 text-green-700 hover:bg-green-100"
                            : decision === 'Tweak'
                            ? "border-yellow-500 bg-yellow-50 text-yellow-700 hover:bg-yellow-100"
                            : "border-red-500 bg-red-50 text-red-700 hover:bg-red-100"
                        )}
                      >
                        {decision}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">Review Notes</label>
                  <textarea
                    rows={4}
                    placeholder="Add your review notes..."
                    className="w-full px-4 py-3 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                  />
                </div>
              </motion.div>
            )}

            {activeTab === 'assets' && (
              <motion.div
                key="assets"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold">Linked Assets</h3>
                  <button
                    onClick={() => setShowAddAsset(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    Add Asset
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {mockMove.linkedAssets.map((asset) => (
                    <motion.div
                      key={asset.id}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="p-4 rounded-xl border border-neutral-200 hover:bg-neutral-50 transition-colors cursor-pointer"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <Link2 className="w-5 h-5 text-primary-600" />
                        <span className="px-2 py-1 text-xs font-medium bg-primary-100 text-primary-700 rounded-lg">
                          {asset.type}
                        </span>
                      </div>
                      <h4 className="font-semibold text-neutral-900 mb-1">{asset.name}</h4>
                      <a href={asset.url} className="text-sm text-primary-600 hover:underline">
                        View →
                      </a>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

